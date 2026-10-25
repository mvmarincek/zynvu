# Connectors and executors

## Connector registry metadata
Provider, version, transport (MCP stdio/HTTP, REST/OpenAPI, SDK), authorization (OAuth/token), read/write scopes, tools/schemas, rate limits, network requirements, supported OS, cost, approval level, validation method. Initial provider entries: GitHub, Slack, Linear, Render, Vercel, Google Drive, Gmail, Notion, PostgreSQL, custom MCP. API support must be verified against current official docs during implementation.

## Tool discovery and routing
Only expose task-relevant tools to the LLM. Prefer structured API/MCP when reliable, browser automation (Playwright or Selenium) when UI-only, native accessibility or PyAutoGUI for desktop, optional vision for unstructured interfaces, hardware HID if required by policy. Routing considers reliability, availability, latency, user permissions, cost, auditability and privacy. Tool arguments must be validated, never trusted blindly from LLM.

## Security boundaries
Explicit scopes and approvals; read-only default; require confirmation for irreversible writes or external messages/deployments; secret store outside export; network allowlist optional; sandbox untrusted scripts; rate limiting; protect against prompt injection in webpages, repo files and documents. Do not store passwords, OAuth tokens or private screenshots in public GitHub.

## VOKI consumer contract
VOKI can consume advisor/SDK output like any other project. It sets `interface_execution.allowed=[hardware_hid]`, denies software UI executors. The VOKI HID MCP/device implements mouse/keyboard/drag/draw. Screenshots are a separate configured capture capability. No VOKI-specific licensing logic belongs inside ZYNVU.
