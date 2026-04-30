"""Tiny HTTP server that hosts a single Effortless tool.

Wire contract (what the `effortless` CLI expects):
  POST / with JSON body containing TranspileRequest.ZippedInputFileSet
  → JSON response with TranspileRequest.ZippedOutputFileSet

The handler is any Python file that exports `handle(inputs, params) -> outputs`.
Tool code lives next to its emitter (e.g. rulebook-emitters/yaml/rulebook_to_yaml.py),
not inside this folder — this folder is just the transport.

Usage:
  python effortless-tools/server.py rulebook-emitters/yaml/rulebook_to_yaml.py --port 12551
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from fileset import decode_input_payload, encode_output_payload, get_cli_params


def load_handler(path: Path):
    """Load a Python file by path and return its `handle` function."""
    if not path.exists():
        raise SystemExit(f"handler file not found: {path}")
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "handle"):
        raise SystemExit(f"{path} does not export a `handle(inputs, params)` function")
    return module


def make_handler(tool_module, tool_name: str):
    class ToolHandler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            sys.stderr.write(f"[{tool_name}] {fmt % args}\n")

        def _json(self, status: int, body: dict | str) -> None:
            data = body if isinstance(body, str) else json.dumps(body)
            payload = data.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self):
            # The CLI doesn't call GET, but humans poking with curl will.
            self._json(200, {"status": "ok", "tool": tool_name})

        def _read_body(self) -> str:
            te = (self.headers.get("Transfer-Encoding") or "").lower()
            if "chunked" in te:
                buf = bytearray()
                while True:
                    line = self.rfile.readline().strip()
                    if not line:
                        continue
                    n = int(line.split(b";")[0], 16)
                    if n == 0:
                        # consume trailing CRLF and any trailers
                        while self.rfile.readline().strip():
                            pass
                        break
                    buf.extend(self.rfile.read(n))
                    self.rfile.readline()  # CRLF after chunk
                return buf.decode("utf-8")
            length = int(self.headers.get("Content-Length") or "0")
            return self.rfile.read(length).decode("utf-8") if length else ""

        def do_POST(self):
            try:
                body = self._read_body()
                payload = json.loads(body) if body else {}
                inputs = decode_input_payload(payload)
                params = get_cli_params(payload)
                sys.stderr.write(f"[{tool_name}] inputs: {list(inputs.keys())}  params: {params}\n")
                outputs = tool_module.handle(inputs, params)
                if not isinstance(outputs, dict):
                    raise TypeError(f"tool handler returned {type(outputs).__name__}, expected dict")
                self._json(200, encode_output_payload(outputs, tool_name))
            except Exception as e:
                traceback.print_exc()
                self._json(500, {"error": str(e), "trace": traceback.format_exc()})

    return ToolHandler


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("handler", help="path to a Python file exporting handle(inputs, params)")
    parser.add_argument("--name", default=None, help="tool name (defaults to handler filename stem)")
    parser.add_argument("--port", type=int, default=12551)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args(argv)

    handler_path = Path(args.handler).resolve()
    tool_module = load_handler(handler_path)
    tool_name = (args.name or handler_path.stem).replace("_", "-")

    httpd = ThreadingHTTPServer((args.host, args.port), make_handler(tool_module, tool_name))
    print(f"effortless-tools: serving '{tool_name}' on http://{args.host}:{args.port}")
    print(f"  handler: {handler_path}")
    print(f"  test:    effortless http://{args.host}:{args.port} -i <input> -o <out-dir>")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
