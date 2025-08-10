# GridWorks Application Shared Languages

Imagine a grid where abundant renewable energy flows naturally to where it's needed. By coordinating flexible loads like heat pumps and thermal storage in real-time, we can consume energy when solar and wind are producing plenty and reduce consumption when they're not. This transformation replaces fossil fuel balancing with community-centered, open source grid management that creates more ease and flow in our relationship with energy. [Learn more about the GridWorks vision](https://gridworks.readthedocs.io/).



**GridWorks ASL is the communication infrastructure for this energy transformation** - a polyglot code generation platform that enables peer-to-peer shared vocabulary between all the actors in this new energy ecosystem.

ASLs are the next step in message passing evolution: more powerful, flexible and expressive than APIs. Instead of rigid client/server relationships, ASL enables true collaboration where organizations maintain autonomy while sharing vocabulary.

## Why This Matters

Ever been in that meeting where another team needs "just one small API change" that turns into months of breaking change management? ASL solves this by letting teams evolve vocabulary granularly - change one type without breaking everyone else's implementations.

**Read [Why GridWorks ASL Exists](docs/motivation.md)** for the full story of API pain and how peer-to-peer shared vocabulary offers a better way.

## Quick Start

**Ready to explore?**

1. **Browse the registry** [registry.yaml](type_definitions/registry.yaml) to see real vocabulary in action
2. **Understand the rules** - Read [Rules and Guidelines](docs/rules_and_guidelines.md) for technical specifications
3. **Try building** - Generate a seed project and experiment with your own types

**Want to contribute vocabulary?** See the [simple registration process](docs/rules_and_guidelines.md#vocabulary-registration-process).

## What You Can Do

**No one depends on gridworks-asl as a package**, but everyone can:

- **Generate exactly what they need** - Clean code in Python, Go, JavaScript, C, whatever your team uses
- **Validate messages live** - Submit samples to our API endpoint for validation  
- **Get working examples** - Browse our schema catalog for real-world vocabulary
- **Share vocabulary** - Submit PRs to add your schemas to the shared registry

## How It Works

GridWorks ASL builds constitutional foundations on top of JSON Schema in YAML:

- **Language neutral** - Generates idiomatic code in any language
- **Granular evolution** - Change one type without breaking others
- **Words have meaning** - The language evolves as meanings change
- **True collaboration** - Organizations stay autonomous while sharing vocabulary

**Example**: A simple power measurement gets sent as this json
```
{"Watts": 1500, "TypeName": "power.watts", "Version": "000"}
```
If you selected python as your language of choice, you would have created the message by
serializing a pydantic-based class object PowerWatts like this:

```python
power = PowerWatts(
    Value=1500,
    TypeName="power.watts",
    Version="000"
)
```

## Project Structure

```
gridworks-asl/
├── api/                    # FastAPI validation service
├── code_gen/               # Seed project generators
│   └── python/
├── docs/
│   ├── motivation.md       # Why ASL exists
│   └── rules_and_guidelines.md  # Technical specifications
├── src/gwasl/
│         ├── enums/
│         ├── named_types/
│         ├── property_format.py
│         └── codec.py
│
├── tests/
├── type_definitions/          # Source of truth
│   ├── registry.yaml         # Vocabulary registry
│   ├── owners.yaml          # Organization registry  
│   ├── schemas/             # Complex data structures
│   ├── formats/            # Primitive validation patterns
│   └── enums/              # Controlled vocabularies
└── ui/                     # À la carte selection interface

```


## Services

- **API**: `api.electricity.works` - Validate your message structures
- **UI**: `electricity.works` - Browse and select vocabulary à la carte

## Contributing

We're in early days and excited to hear from you! Adding vocabulary is simple:

1. Check [registry.yaml](type_definitions/registry.yaml) to make sure nobody owns your word yet
2. Fork and create PR
3. Email us at gridworks@gridworks-consulting.com

**Full details**: [Vocabulary Registration Process](docs/rules_and_guidelines.md#vocabulary-registration-process)

---

*Collaboration without compromise. Evolution without permission.*