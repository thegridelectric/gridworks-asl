# Sema Documentation

This directory contains background material and architectural notes for Sema.

## Core Concepts

- **[motivation.md](motivation.md)**  
  Why Sema exists and the problem it addresses.

- **[../spec/primary.md](../spec/primary.md)**
  The formal specification (hub) governing vocabulary structure, versioning,
  and registry behavior. Lives at the top level of the repo (`sema/spec/`)
  because it is the canonical rebuild artifact, not background reading.
  Per-kind spokes live under `../spec/registry/` and `../spec/authoring/`;
  governance lives at `../spec/governance.md`. The previous monolithic
  version is archived at [orig-spec.md](orig-spec.md).

## Architecture

- **[project-structure.md](project-structure.md)**  
  Overview of the internal organization of this repository.

- **[sema-and-domain-protocols.md](sema-and-domain-protocols.md)**  
  How Sema relates to external protocols and canonical internal models.

## Background

- **[where-meaning-lives-in-gridworks.md](where-meaning-lives-in-gridworks.md)**  
  Architectural background from the GridWorks ecosystem.
