# effortless-tools

Transport for hosting Effortless transpilers as a local URL — no .NET, no cloud.

This folder is **just the wire format and the HTTP server**. The tools themselves live next to their emitters (e.g. [rulebook-emitters/yaml/rulebook_to_yaml.py](../rulebook-emitters/yaml/rulebook_to_yaml.py)) so each emitter folder is self-contained.

The `effortless` CLI accepts a URL as the transpiler argument:

```bash
effortless http://127.0.0.1:12551 -i rulebook.json
```

…and POSTs a SSoTme `FileSet` payload to it. [server.py](server.py) speaks that wire format and dispatches to a Python handler you point it at.

## Layout

| File | Purpose |
|---|---|
| [server.py](server.py) | Generic HTTP server. Reads chunked or content-length JSON, decodes the inbound FileSet, calls `handle(inputs, params)`, encodes the outbound FileSet. |
| [fileset.py](fileset.py) | Encode/decode the SSoTme wire format (gzipped XML inside base64 inside JSON). Hand-built XML so it round-trips with .NET's XmlSerializer. |

## Run

```bash
python3 effortless-tools/server.py rulebook-emitters/yaml/rulebook_to_yaml.py --port 12551
```

In another shell, from any directory containing an `effortless.json` (run `effortless -init` first if needed):

```bash
effortless http://127.0.0.1:12551 -i path/to/rulebook.json
```

The CLI writes the emitted YAML files to the current directory, preserving the relative paths returned by the tool.

## Wire contract

The CLI POSTs JSON like this (the rest of the body is the CLI dumping its full state — only `transpileRequest.zippedInputFileSet` matters):

```json
{
  "transpileRequest": {
    "zippedInputFileSet": "<base64(gzip(<FileSet xml>))>"
  },
  "cliParams": [...]
}
```

The server replies:

```json
{
  "TranspileRequest": {"ZippedOutputFileSet": "<base64(gzip(<FileSet xml>))>"},
  "Transpiler": {"Name": "...", "LowerHyphenName": "..."}
}
```

The inner `FileSet` XML matches the shape that `XmlSerializer<FileSet>` from [SSoTme.OST.Lib.DataClasses](../../../../api.effortlessapi.com/DotNet/CLIClassLibrary) produces. File contents may arrive as `FileContents` (text), `ZippedFileContents` (gzip-base64), or `ZippedTextFileContents`; the decoder handles all three.

## Adding a new tool

In the emitter's own folder (e.g. `rulebook-emitters/<name>/`), add or extend the main script with:

```python
def handle(inputs: dict[str, str], params: list[str]) -> dict[str, str]:
    """inputs: {relative_path: text}; returns the same shape."""
    ...
```

Then run:

```bash
python3 effortless-tools/server.py rulebook-emitters/<name>/<script>.py --port <port>
```

## Status

| Tool | Handler lives at | Verified end-to-end |
|---|---|---|
| `rulebook-to-yaml` | [rulebook-emitters/yaml/rulebook_to_yaml.py](../rulebook-emitters/yaml/rulebook_to_yaml.py) | yes — produces 118 files byte-identical to running the script directly |
