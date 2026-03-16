# Why Sema Exists

Modern systems are increasingly built by i**ndependent teams and organizations** that need to exchange structured data. In practice, this coordination often happens through APIs or protocol payloads whose structure evolves slowly and is difficult to change safely.

Small changes to shared message structures — adding a field, extending an enum, clarifying a concept — can become expensive. They may require coordinated deployments, version negotiations, or breaking migrations across multiple systems.

Over time, the shared vocabulary itself becomes the constraint.

Sema exists to make **shared message vocabularies explicit, versioned, and mechanically verifiable**, so that systems can evolve independently while continuing to communicate reliably.

## The Core Idea

Sema separates shared vocabulary from application implementation.

Instead of embedding message structures inside APIs or application code, Sema defines vocabulary in an open registry of versioned schemas:
 - **Types** — structured messages exchanged between systems
 - **Enums** — controlled vocabularies for semantic categories
 - **Formats** — reusable constraints for primitive values

Each vocabulary word has:
 - a globally unique name
 - explicit versioning
 - machine-verifiable structure and semantics

These definitions act as **boundary contracts** between systems.

Because the contracts are explicit and versioned, systems can adopt new vocabulary incrementally without breaking existing integrations.

## What This Enables

This approach provides several practical benefits.

**Independent evolution**

Vocabulary changes are versioned at the level of individual words.
New types or fields can be introduced without forcing coordinated migrations across unrelated systems.

**Language neutrality**

Vocabulary definitions are expressed as JSON Schema and can generate bindings in multiple programming languages.

**Clear system boundaries**

Shared vocabulary is defined once and reused across systems.
Application code remains free to implement its own internal models and architecture.

**Open collaboration**

Vocabulary can evolve through contributions to the registry rather than through centralized API ownership.

## Vision
Sema aims to make shared vocabulary **explicit, portable, and evolvable.**

When the meaning and structure of messages are defined independently of any single application, systems can coordinate more easily while remaining autonomous.

