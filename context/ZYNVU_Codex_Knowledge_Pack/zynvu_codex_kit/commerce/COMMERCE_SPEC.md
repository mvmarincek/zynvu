# GitHub -> paid services: complete commercial spec

## Business model
ZYNVU core remains open-source and usable without payment. Sell professional **services**: assisted setup, configured local agent, developer integration, enterprise implementation and optional ongoing support. GitHub is discovery and documentation; payment hosted externally. GitHub Sponsors may be optional donations, not primary checkout.

## Suggested offer catalog (prices to validate)
| SKU | Price (BRL) | Scope |
| --- | ---: | --- |
| `setup` | 497 one-time | Standardized local install, one agent, basic verification, no custom connectors |
| `agent` | 2490 one-time | Configured agent, local memory, basic RAG, standardized tools, validation, bounded handover |
| `dev-integration` | from 7900 | SDK integration into existing project; proposal and statement of work |
| `enterprise` | from 19900 | Multi-agent architecture, security, enterprise integrations, agreed acceptance |
| `support-individual` | 99/month optional | Defined response/support limits |
| `support-agent` | 490/month optional | Bounded agent maintenance |
| `support-enterprise` | 1490/month optional | Business support with defined SLA |

Do not claim these are proven conversion prices. Set prices via server-side product catalog, never trust client-supplied amount. Define taxes, refunds, cancellations, time-to-delivery, included revisions and exclusions before production.

## End-to-end customer journey
1. Public GitHub README and Releases: Free Download, Assisted Setup, Custom Agent, B2B contact.
2. Desktop advisor generates local report; optional `Request installation` link opens service page (never uploads hardware report without consent).
3. Hosted checkout via Asaas for Brazil (Pix/card/boleto) or Stripe for supported international use. Customer sees clear scope/terms/privacy.
4. Backend creates pending order with random public ID, SKU, amount, currency, buyer contact, scope version; obtains checkout/payment session; no card details on ZYNVU server.
5. Gateway webhook is authenticated, parsed, deduplicated, durably persisted, acknowledged quickly, then processed asynchronously.
6. State machine transitions order to paid **only on trusted gateway confirmation**, not browser redirect.
7. Fulfillment queue creates onboarding request, sends transactional email through Resend, and offers intake questionnaire/scheduling.
8. Operator or automated provisioning completes agreed work; records deliverables, customer acceptance and support window.
9. Refunds, disputes, failed payments, retries and cancellations update orders and entitlement/fulfillment state safely.
10. Customer support and audit trail with data retention/deletion policy.

## State machine
`draft -> pending_payment -> paid -> onboarding -> scheduled -> in_progress -> delivered -> closed`.
Alternative transitions: `pending_payment -> expired|cancelled`; `paid|onboarding|scheduled|in_progress -> refund_pending -> refunded`; `paid -> disputed`. Validate transitions; manual override audited.

## Backend architecture
`services/commerce/` independent of advisor. Render API, PostgreSQL, Resend; Asaas and Stripe adapters; background job queue (Postgres-backed acceptable initially); webhooks; service catalog; order admin endpoints; email templates; onboarding links; audit and retry. Payment-provider secrets in Render environment only. Webhook signature/token verification per provider current docs. Stripe event signature with raw body; Asaas authentication token/header according to official current documentation; implement provider-specific checks, not guessed signatures.

## Suggested endpoints (design, not live)
- `GET /api/services` public sanitized offer catalog.
- `POST /api/orders` validates SKU, buyer, privacy consent; creates pending order.
- `POST /api/orders/:id/checkout` provider selection, idempotency key; returns hosted checkout URL.
- `POST /api/webhooks/stripe` authenticated raw-body handler.
- `POST /api/webhooks/asaas` authenticated handler.
- `GET /api/orders/:id/status` authenticated via short-lived customer token; do not leak PII.
- `POST /api/orders/:id/intake` authenticated customer intake.
- `GET /api/admin/orders` admin RBAC only.

## Database entities
`service_products`, `orders`, `payment_attempts`, `webhook_events` (unique provider + event id), `fulfillment_tasks`, `customer_intakes`, `email_outbox`, `audit_log`, `refunds`. Unique order/provider payment identifiers, transactions and idempotent processing. Avoid duplicating PII; encryption and retention rules.

## Email lifecycle
Payment pending; payment confirmed + next steps; intake received; appointment confirmation; delivery; follow-up; refund/failed payment. Do not send sensitive credentials by email. Resend provider id stored for retry/tracing. Provide PT-BR templates and English-ready localization.

## README CTAs
- Download Free -> GitHub Releases (placeholder until release exists).
- Assisted Setup -> service checkout landing (configurable, no fabricated URL).
- Custom AI Agent -> service intake/checkout landing.
- Enterprise -> request quote.

## Legal/operational checks
Publish Terms, Privacy, cancellation/refund policy, tax invoicing approach and LGPD data handling; check local consumer-law requirements with qualified counsel. Confirm merchant gateway eligibility and currency support. Never deploy with placeholder domains or test keys in production.
