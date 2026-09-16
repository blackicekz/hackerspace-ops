# Assistant tool interface

Planned: expose application use cases to an AI assistant as callable tools, read from an
application-owned capability catalogue, through a transport adapter that authenticates the
assistant session and the resident on whose behalf each call is made. The assistant is a caller
of the same use cases and the same authorization policy that human transports use; it has no
permissions of its own. See [ADR 0007](../../architecture/adr/0007-use-cases-as-tool-surface.md).

The concrete protocol (for example an MCP server or provider function-calling), the catalogue
shape, session authentication, and the delegated-identity claim format will be specified before
implementation.
