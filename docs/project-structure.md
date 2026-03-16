## Project Structure

```
sema/
├── src/sema/
|         ├── __init__.py
|         ├──registry/        # The complete Sema registry (the "menu")
│         │      ├── enums/Is 
│         │      ├── types/
│         |      ├── base.py
│         |      ├── codec.py
│         │      └── property_format.py
│         ├── templates/                # Templates for generated code
│         │   ├── __init__.py
│         │   ├── codec.py.jinja2      # Template for sema/codec.py
│         │   ├── property_format.py   # Static file to copy
│         │   ├── utils.py             # Static file to copy
│         │   └── init.py.jinja2       # Template for sema/__init__.py
│         │
│         ├── generator/                # Code generation logic
│         │   ├── __init__.py
│         │   ├── seed_builder.py      # Main generator class
│         │   ├── dependency_resolver.py # Resolve type dependencies
│         │   └── validators.py        # Validate selections
│         │
│         └── cli.py                   # CLI interface  
│
├── api/                    # FastAPI validation service
├── code_gen/GridWorksCore/     # Generates a lot of this repo.
│                  ├── aicapture.json
│                  ├── ODXML/
│                  │    └── DataSchema.odxml
│                  ├── SSoT/
│                  │    ├── Airtable.xml
│                  │    └── Entities.json
│                  ├── Types/
│                  │    ├── TypeInit/
│                  │    │     └── DeriveTypeInit.xslt/
│                  │    └── DeriveTypes.xslt
│                  └── python/
├── docs/
│   ├── motivation.md
│   ├── sema-specifications.md
│   └── where-meaing-lives-in-gridworks.md
├── tests/
├── type_definitions/          # Source of truth
│   ├── registry.yaml         # Vocabulary registry
│   ├── owners.yaml          # Organization registry  
│   ├── schemas/             # Complex data structures
│   ├── formats/            # Primitive validation patterns
│   └── enums/              # Controlled vocabularies
└── ui/                     # À la carte selection interface

```
