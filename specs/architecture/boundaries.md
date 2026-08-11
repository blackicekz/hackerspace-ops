# Dependency boundaries

Production imports must follow these rules:

- `src.domain` imports only the standard library and never another `src` package.
- `src.application` may import `src.domain`, but not adapters or infrastructure.
- `src.adapters` may import domain and application, but not infrastructure.
- `src.infrastructure` may import all layers and is the composition root.
- Vendor SDKs are confined to adapters/infrastructure and hidden behind application ports.

The automated architecture test scans Python imports and rejects inward-layer violations.

Telegram messages, GitHub commits, calendar records, Instagram media, HTTP requests, database
records, and AI-provider responses are adapter concerns, never domain entities. Authorization
mechanics belong at the input boundary; application commands carry only the authenticated actor's
provider-neutral identity and provenance.
