# ADR 0001: Clean Architecture and explicit ports

Status: accepted

We separate domain, application, adapters, and infrastructure and require dependencies to point
inward. External platforms change independently and must be replaceable without changing business
rules. Protocol-based application ports provide that seam. The small cost of extra interfaces is
accepted for testability and extensibility.
