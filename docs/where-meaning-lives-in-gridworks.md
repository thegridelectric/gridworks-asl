# Where Does Meaning Live in the GridWorks System

In any distributed system, there are only three possible places meaning can live:
the observed behavior of the running system, the database schema, or a declared language.

For GridWorks, **semantic authority lives in the Application Shared Language (ASL).**

More precisely: **ASL is the authority over meaning,** while a small, stable, slowly-changing canonical seed database is the authority over **which ASL-typed facts are currently asserted.** The database does not define what things mean; it records facts that are already defined by the language. The two are tightly and deliberately coupled, but they do not play the same role.

If there is ever a disagreement between a database representation and the ASL definition, **the ASL definition wins.**

## ASL and the Canonical Seed

The canonical seed database holds the core relational facts of the GridWorks universe—grid nodes, layouts, identities, and other foundational relationships that change slowly and matter everywhere. It is **ASL-correct by construction**: rows reference ASL types, versions, and identities explicitly, so facts cannot silently drift from their declared meaning.

This is a case of **tight and careful semantic coupling.** Meaning is declared once, in ASL. Facts are asserted once, in the seed database. Other databases, caches, and analytics systems consume projections of that truth rather than redefining it. Those downstream systems are free to optimize for their own needs. Being “ASL-aware” does not require using ASL types directly in code: developers may reference the declarative definitions informally or use full ASL-typed models; both are acceptable. What matters is that meaning remains explicit and externally defined - personally, I find the typed approach clearer and more durable, but the system does not require it.

This approach:
  - Does not block multi-reader architectures
  - Does not require a bijection between all tables and ASL types
  - Allows ASL to continue evolving in production
  - Treats ASL as the semantic contract of the system

## Is This a Common Pattern?

Yes. Almost all distributed technology companies that survive past early scale converge on some version of this pattern.

Examples of declared languages or canonical models that encapsulate meaning include Kafka with Schema Registry, FIX (Financial Information eXchange), FHIR in healthcare, and — arguably — double-entry accounting itself. In each case, meaning is declared explicitly, versioned, and shared, while databases store facts _expressed in_ that language rather than redefining it.

Companies like Amazon, Uber, and Telnyx operate this way as well. They do not enforce a bijection between schema and language. However, they **do** enforce a bijection between meaning and a canonical model: for any concept that matters, there is exactly one authoritative definition of what it means, and all other representations are projections of that definition.

## Partial Knowledge and the Next Right Step

GridWorks is designed around an explicit acceptance of partial knowledge.

At any moment in time, our understanding of a system is incomplete, imprecise, and sometimes wrong. This is not a temporary condition to be engineered away; it is a permanent feature of operating complex socio-technical systems. Hardware varies, sensors fail, models lag reality, markets move, and human intent changes. The question is therefore not how to achieve perfect knowledge, but how to act responsibly and coherently in its absence.

This is especially true on the electric grid, where distribution-level infrastructure is often poorly mapped, field conditions differ from documentation, and behavior emerges from the interaction of many independent actors.

ASL exists to support this mode of operation. By making meaning explicit, versioned, and checkable, ASL allows the system to incorporate new perceptions, new data, and new perspectives without collapsing into implicit assumptions or brittle, ad-hoc behavior. It enables taking the next right step—even when models are partial, forecasts are uncertain, or conditions are changing—while avoiding failure modes caused by silent semantic drift.

In this way, ASL allows for emergence and evolution without chaos.