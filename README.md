# Gridworks Application Shared Languages

Welcome! gridworks-asl is a **polyglot code generation platform**. Its the next step in an evolutionary process in message passing: more powerful, flexible and expressive than APIs.

Things you can do: 
  - Browse the available schemas in our schema catalog
  - Submit a PR to add your schema to the schemas/ folder
  - Examine schema validation rules are defined in schemas/
  - Submit sample of a type to API endpoint for validation

**No one depends on gridworks-asl as a package**, but everyone can:
 - Generate exactly what they need
  - Validate their messages live
  - Get working examples

## api/

  This will deploy to its own api (`api.electricity.works). It has its own `requirements.txt` and is deployed in its own Docker container. This is the api that people can validate messages against.

## ui/

This is a app deployed to `electricity.works`. It has a separate build process and calls the API service. 

```
gridworks-asl/
├── type_definitions/  # Source of truth ()
│   ├── registry.yaml  
│   ├── schemas/              # Documentation perspective
│   │   ├── node.gt.v001.yaml
│   │   ├── report.v002.yaml
│   │   └── power.watts.v000.yaml
│   ├── formats/
│   └── enums/
├── code_gen/  # Creates seed projects for users
│    ├── python/
│    └── c/
├── src/gwasl/                 
│        ├── named_types/
│        ├── enums/
│        ├── formats/
│        └── __init__.py
├── api/    # FastAPI validation service
│    ├── main.py
│    ├── enums/
├── ui/  # A la carte selection interface
└── docs/                    # Human documentation
    ├── motivation.md
    ├── rules.md
    └── examples/
```