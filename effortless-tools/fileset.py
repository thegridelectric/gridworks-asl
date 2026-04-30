"""SSoTme FileSet wire format — minimal Python implementation.

The `effortless` CLI POSTs JSON to a tool URL with shape:

    {
      "TranspileRequest": {
        "ZippedInputFileSet": "<base64(gzip(<FileSet xml>))>"
      },
      "Transpiler": { "Name": ..., "LowerHyphenName": ... },
      ...
    }

It expects a JSON response of the same shape, with `ZippedOutputFileSet`
containing the generated files.

The inner XML is what .NET's XmlSerializer produces for SSoTme's `FileSet`
class. Element order matters for round-trip with the .NET deserializer, so
we hand-build it rather than using a generic dict→XML library.
"""

from __future__ import annotations

import base64
import gzip
import uuid
from datetime import datetime, timezone
from typing import Iterable
from xml.etree import ElementTree as ET


def _now_iso() -> str:
    # Matches .NET's default DateTime.UtcNow round-trip ("o" format) closely enough
    # for the deserializer; trailing fractional digits and the Z suffix are accepted.
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f0Z")


def decode_input_payload(payload: dict) -> dict[str, str]:
    """Pull files out of an inbound TranspileRequest payload.

    Returns {relative_path: text_contents}. Binary fields are not surfaced —
    this server is text-only by design (rulebook in, YAML out).
    """
    tr = payload.get("TranspileRequest") or payload.get("transpileRequest") or {}
    b64 = tr.get("ZippedInputFileSet") or tr.get("zippedInputFileSet")
    if not b64:
        # Fallback: bare CLIInputFileContents (when -i is a single text file and
        # the CLI didn't bother to wrap it).
        cli_text = payload.get("CLIInputFileContents") or payload.get("cliInputFileContents")
        if cli_text:
            return {"input.txt": cli_text}
        return {}

    xml_bytes = gzip.decompress(base64.b64decode(b64))
    return _parse_fileset_xml(xml_bytes)


def _parse_fileset_xml(xml_bytes: bytes) -> dict[str, str]:
    root = ET.fromstring(xml_bytes)
    out: dict[str, str] = {}
    for fsf in root.findall("FileSetFiles/FileSetFile"):
        rp_node = fsf.find("RelativePath")
        if rp_node is None or rp_node.text is None:
            continue
        # Contents may live in any of three places, in priority order:
        fc = fsf.find("FileContents")
        if fc is not None and fc.text is not None:
            out[rp_node.text] = fc.text
            continue
        zfc = fsf.find("ZippedFileContents")  # gzipped utf-8 bytes, base64 in xml
        if zfc is not None and zfc.text:
            out[rp_node.text] = gzip.decompress(base64.b64decode(zfc.text)).decode("utf-8")
            continue
        ztfc = fsf.find("ZippedTextFileContents")
        if ztfc is not None and ztfc.text:
            out[rp_node.text] = gzip.decompress(base64.b64decode(ztfc.text)).decode("utf-8")
            continue
        out[rp_node.text] = ""
    return out


def encode_output_payload(files: dict[str, str], transpiler_name: str) -> dict:
    """Wrap a {relative_path: text} map in the SSoTme reply envelope."""
    xml_bytes = _build_fileset_xml(files)
    zipped = gzip.compress(xml_bytes)
    b64 = base64.b64encode(zipped).decode("ascii")
    return {
        "TranspileRequest": {"ZippedOutputFileSet": b64},
        "Transpiler": {"Name": transpiler_name, "LowerHyphenName": transpiler_name},
        "SSoTmeProject": None,
        "Exception": None,
    }


def _build_fileset_xml(files: dict[str, str]) -> bytes:
    fileset_id = str(uuid.uuid4())
    # Hand-build the XML — element order matches what .NET XmlSerializer emits
    # for the FileSet POCO, which is what the CLI expects when deserializing.
    root = ET.Element(
        "FileSet",
        {
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
        },
    )
    ET.SubElement(root, "FileSetId").text = fileset_id
    ET.SubElement(root, "CreatedOn").text = _now_iso()
    files_el = ET.SubElement(root, "FileSetFiles")
    for rel_path, contents in sorted(files.items()):
        f = ET.SubElement(files_el, "FileSetFile")
        ET.SubElement(f, "FileSetFileId").text = str(uuid.uuid4())
        ET.SubElement(f, "FileSetId").text = fileset_id
        ET.SubElement(f, "RelativePath").text = rel_path
        ET.SubElement(f, "FileContents").text = contents
        ET.SubElement(f, "AlwaysOverwrite").text = "true"
        ET.SubElement(f, "OverwriteMode").text = "Always"
        ET.SubElement(f, "SkipClean").text = "false"
    return b'<?xml version="1.0" encoding="utf-8"?>' + ET.tostring(root, encoding="utf-8")


def get_cli_params(payload: dict) -> list[str]:
    """Extract the list of -arg flags the user passed on the CLI."""
    params = payload.get("cliParams") or payload.get("CliParams") or []
    if isinstance(params, list):
        return [str(p) for p in params]
    return []
