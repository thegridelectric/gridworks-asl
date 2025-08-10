# GridWorks Application Shared Language

Imagine a grid where abundant renewable energy flows naturally to where it's needed. By coordinating flexible loads like heat pumps and thermal storage in real-time, we can consume energy when solar and wind are producing plenty and reduce consumption when they're not. This transformation replaces fossil fuel balancing with community-centered, open source grid management that creates more ease and flow in our relationship with energy. [Learn more about the GridWorks vision](https://gridworks.readthedocs.io/).

A coordinated electric grid works when devices share a common language. Not one imposed from the center, but an open, versioned vocabulary anyone can adopt and extend. GridWorks ASL is that language layer: it defines words (types, enums, property formats) with stable meaning and clear axioms, then generates idiomatic code so teams can interoperate with an appropriate level of precision and articulation for each circumstance. For more on why we built the GridWorks ASL,  see [motivation.md](docsmotivation.md).

## Humans + AI, working from the same words

Because ASL is machine‑readable end to end, AI tools can participate as first‑class collaborators—drafting, validating, and mediating messages grounded in your exact words rather than guesses. In practice, this enables:

* copilots that propose valid messages and code stubs on the first try,
* agents that reason against your types and enums instead of hallucinating,
* automated validation that keeps human/AI workflows inside known‑good boundaries.



## How it works

ASL defines constitutional, language‑neutral schemas with explicit axioms and versions each “word” so evolution is local and safe. Generators produce idiomatic code in your target language; validators enforce the same semantics everywhere.

**Example**

A simple power measurement:

```json
{"Watts": 1500, "TypeName": "power.watts", "Version": "000"}
```

Python usage (Pydantic-style):

```python
power = PowerWatts(
    Value=1500,
    TypeName="power.watts",
    Version="000",
)
```

## Where to go next

* Read the **[rules and guidelines](rules_and_guidelines.md)** for authoring types and axioms.
* Explore existing message categories in this repo to see how versions evolve safely.
* Start a small pilot: model two or three words your system already uses, generate code, and validate in CI.

## How this differs from traditional standards (e.g., OpenADR)

ASL doesn’t replace domain protocols. Standards like OpenADR define roles, behaviors, and message flows; ASL defines shared words with exact meaning and machine‑checked validity. Consensus emerges because the words are useful: you adopt them, your integrations get easier, and your systems interoperate—without waiting for a committee cycle.

**Scope**: Standards specify end‑to‑end behavior; ASL specifies the vocabulary and axioms behind the payloads.

**Governance**: Standards converge via committees; ASL evolves in an open registry where any party can propose, version, and adopt words.

**Adoption speed**: Standards often require certification and coordinated rollouts; ASL ships schemas and codegen so teams can copy, validate, and ship today.

**Change model**: Standards revise infrequently; ASL versions each word so change is explicit, local, and safe.

**Coexistence**: You can map ASL types to OpenADR events or other protocols. When a standard is required, ASL keeps your internal semantics clean and your adapters thin.

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