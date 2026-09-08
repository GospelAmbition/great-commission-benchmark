# Newsletter CTA rollout

All offers link to `/newsletter?source=<placement>`. The newsletter remains email-only and uses the existing subscription API and security verification. Cadence: monthly digest plus occasional highlights on important model releases.

## Production analytics prerequisite

The production newsletter page was inspected on September 8, 2026; no Umami script or `data-website-id` appeared in the hydrated DOM. Configure `NEXT_PUBLIC_UMAMI_SCRIPT_URL` and `NEXT_PUBLIC_UMAMI_WEBSITE_ID` for the intended Umami instance before building/deploying. These are build-time public settings. Confirm events arrive in that instance after deployment; do not substitute an invented website ID.

## Funnel

- `newsletter_offer_impression`: `source`, `path`; emitted once per placement per route/query view when at least half the CTA is visible.
- `newsletter_cta_click`: `source`, `path`.
- `newsletter_form_submit`: allowlisted `source`; includes attempts rejected by email validation.
- `newsletter_signup_outcome`: `source`, `outcome` (`invalid_email`, `security_error`, `request_error`, `subscribed`, `already_subscribed`, `reactivated`).
- Existing `newsletter_signup`: accepted submission, including already-subscribed responses. It is not a count of net new subscribers.

Unknown or missing source parameters become `newsletter_page`. No entered email or raw source query value is sent in newsletter event properties. The complete placement list is in `lib/newsletter.ts`.

## Launch and 30-day review

Record the active subscriber count and launch date. Confirm a controlled subscription is saved and synchronized to MailerLite in the designated test environment before launch. Local validation exercised persistence and provider-sync calls against isolated SQLite with MailerLite mocked; it did not verify live delivery. Local browser content was empty without the backend, so populated active/archived model and article templates were also exercised with fixtures.

Thirty days after deployment, compare placement impressions, click-through rates, submission completion, new subscriptions/reactivations, and active subscriber growth. Investigate any placement with clicks but no accepted submissions. Exclude test subscriptions and distinguish existing-subscriber responses from growth. This document does not schedule campaigns or a follow-up automation.
