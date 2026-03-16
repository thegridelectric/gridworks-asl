# Sema and Domain Protocols

## Overview

Sema does not replace domain protocols such as OpenADR. 

Protocols define roles, behaviors, and message flows between systems.
Sema defines the vocabulary used inside those messages: types, enums,
and formats whose structure and semantics are explicitly versioned and
mechanically verifiable.



## Scope

Protocols specify end-to-end system behavior and message flows.
Sema specifies the vocabulary and axioms behind message payloads.

## Governance

Many industry protocols evolve through formal standards bodies.
Sema vocabulary evolves through an open registry where new words 
and versions can be proposed and adopted incrementally.

## Change model
Domain protocols often evolve through periodic revisions.
Sema versions each vocabulary word independently, allowing 
changes to be introduced incrementally without affecting
unrelated parts of the vocabulary.

## Canonical Internal Model vs Protocol Payload

Many systems interact with multiple external protocols or data sources.
In these cases it is often useful to maintain a canonical internal model
that represents the system’s concepts and data structures independently
of any specific protocol.

Sema vocabulary can serve as this canonical layer.

External protocols (for example OpenADR events or other industry payloads)
are translated into Sema types at system boundaries. Internally, systems
exchange and reason about data using those shared types.

This separation provides several benefits:

 - **Stable internal semantics** — internal systems communicate using explicit, versioned vocabulary.
 - **Thin adapters** — protocol integrations are isolated to translation layers at system boundaries.
 - **Protocol flexibility** — the same internal model can support multiple external protocols.

 A typical flow might look like:

 ```
External protocol message
        ↓
Protocol adapter
        ↓
Sema type (canonical internal representation)
        ↓
Internal processing and system communication
 ```

 In other architectures, Sema types may instead be used **directly as the payload format** between
 cooperating systems. Both approaches are compatible with Sema’s design.

## Coexistence

Sema types can be mapped to payloads used by domain protocols such as OpenADR.

When a protocol is required, Sema helps keep internal semantics explicit
 and versioned while protocol adapters handle transport and protocol requirements.


## Possible future topics:

 - Sema vs protocol standards
 - Sema vs schema registries
 - canonical models vs boundary schemas
 - using Sema with OpenADR
 - using Sema internally vs externally