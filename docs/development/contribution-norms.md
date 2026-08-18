# Contribution norms

These norms describe the expected shape and content of a change, independent of what the change
implements. They apply to any contributor.

## Small changes

Prefer the smallest coherent change that satisfies a specification's acceptance criteria over a
larger change that also refactors unrelated code.

## Readable to hackerspace residents and contributors

Code and changes should be understandable to hackerspace residents and other contributors who may
not be deeply familiar with every implementation detail.

## No secrets or personal data

Secrets — tokens, credentials, API keys — must never be committed to the repository. Personal or
otherwise sensitive operational data must not enter the repository either. Configuration that
carries such values belongs in the operator's environment, never in tracked files.

## Specifications track observable behaviour

A change to observable product behaviour requires a corresponding change to the relevant
specification in [`specs/`](../../specs/README.md). See
[ADR 0003](../../specs/architecture/adr/0003-spec-driven-development.md) for why specifications
lead implementation in this repository, and
[`docs/workflows/implement-feature.md`](../workflows/implement-feature.md) for the procedure.
