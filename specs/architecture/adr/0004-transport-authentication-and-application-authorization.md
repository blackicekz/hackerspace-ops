# ADR 0004: Separate transport authentication from application authorization

Status: accepted

Transport authentication answers whether an external message and sender claim are trustworthy in a
specific protocol. The transport adapter owns that work and emits no SDK objects. Resident identity
resolution maps the provider-neutral external claim to a hackerspace resident through an
application-owned port. An application-layer policy then decides whether that resident may perform
a specific use case.

This separation is durable because every future input transport must share hackerspace policy
without copying it into Telegram, HTTP, or other adapters. It also prevents transport identifiers
from becoming resident identities. The application owns the resolver contract and the authorization
policy. If authorization needs configured facts, a narrow application-owned facts port exposes only
whether a resident has the relevant event-proposal permission; an adapter may implement that lookup
using configuration or persistence, but cannot decide whether the operation is allowed. Complex
RBAC, identity storage, and transport-specific authentication mechanics remain deferred.
