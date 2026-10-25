# Payment deployment and operations runbook

## Local development
- Use sandbox/test credentials only. Configure Postgres, Render-like API locally, Resend test mode, provider webhook forwarding or fixtures.
- Configure `.env` from `.env.example`; secrets excluded from git.
- Test duplicate/out-of-order webhook events, network timeouts, partial failures, pending Pix, cancelled checkout, refunds, disputes, email retries, lost browser redirects and double-click checkout.

## Production checklist
1. Confirm merchant account and products, BRL prices, taxes, refund terms.
2. Configure production hosted checkout provider and domain.
3. Create production DB with migrations, backups and restricted credentials.
4. Set webhook endpoint URL and verify provider secret/auth; TLS enforced.
5. Enable event idempotency, durable queue, dead-letter handling and alerting.
6. Configure Resend verified domain, SPF/DKIM, transactional templates.
7. Test end-to-end with low-risk controlled payment and refund.
8. Validate admin RBAC, customer PII protection, audit, logs redaction.
9. Publish README CTAs and support contact only after checkout confirmed.
10. Monitor paid->fulfillment latency and failed event retries.

## No automatic success assumption
Never mark an order paid based on redirect query parameters or unverified client request. Never execute model installation on the buyer's PC merely because payment was recorded; explicit consent and access controls required.
