How to use it

1. Install deps:
```
pip install lxml jinja2 pydantic
```

2. Run it (adjust paths to your pipeline artifacts):

```
python derive_types.py \
  --airtable-xml ./SSoT/Airtable.xml \
  --odxml ./ODXML/DataSchema.odxml \
  --out-dir ./generated/Types \
  --base-class gw.named_types.GwBase \
  --default-version 000
  ```

  3. Wire the generated package into your project (e.g., add generated to your PYTHONPATH or vendor it under src/gw/named_types_gen).

  Notes & knobs you’ll likely tweak

XPaths in SchemaAdapter: swap XPATH_TYPES / XPATH_FIELDS and the KEY_* lists to match your real Airtable.xml + ODXML layout. I left sensible defaults and fallbacks.

Type mapping (TYPE_MAP): expand to cover your custom formats (e.g., UTCMilliseconds, enums if needed, etc.).

Version policy:

Strict (default): version: Literal["000"].

Non‑strict (--non-strict-versioning): version: str = "000".

Per‑type versionless: e.g. --versionless-pattern '^gw\\.base$'.

Validation: if you want to enforce LRD at runtime, add a @field_validator("type_name") or a model_validator that checks LRD_RE.

Extending to parity with your pipeline

Enums: mirror this file with an EnumAdapter + template (that would emulate DeriveEnums.xslt).

Tests: emit pytest stubs (emulate DeriveTypeTests.xslt).

Init scaffolding: add a “TypeInit” mode that emits registries or factory maps (emulate DeriveTypeInit.xslt).

If you want, send me a small slice of your real Airtable.xml (one or two types + fields). I’ll snap the XPaths and mapping to your exact structure and include enum generation as well.