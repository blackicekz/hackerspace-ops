# Specifications

Specifications are executable design inputs, not retrospective documentation. For each change,
write observable acceptance criteria first, encode them in `tests/acceptance`, and only then change
implementation. Architecture decisions with long-lived consequences belong in
`architecture/adr/`.

Every feature specification should state its purpose, terminology, inputs, behavior, invariants,
concrete acceptance criteria, and relevant failures. Tests should cite or clearly correspond to
those criteria. A behavior change is incomplete until its specification and tests agree.
