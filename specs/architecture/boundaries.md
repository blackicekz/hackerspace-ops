# Dependency boundaries

Production imports must follow these rules:

- `src.domain` imports only the standard library and never another `src` package.
- `src.application` may import `src.domain`, but not adapters or infrastructure.
- `src.adapters` may import domain and application, but not infrastructure.
- `src.infrastructure` may import all layers and is the composition root.
- Vendor SDKs are confined to adapters/infrastructure and hidden behind application ports.

The automated architecture test scans Python imports and rejects inward-layer violations.

Telegram messages, GitHub commits, calendar records, Instagram media, HTTP requests, database
records, and AI-provider responses are adapter concerns, never domain entities. A transport adapter
authenticates the external message and emits a provider-neutral external identity claim. An
application-owned resolver maps that claim to a resident identity, and application policy decides
whether that resident may perform the use case. An adapter may supply configured permission facts
through a narrow application-owned port, but it never makes the operation-specific authorization
decision. Commands that create domain objects carry only the authorized resident identity and
provider-neutral provenance.
