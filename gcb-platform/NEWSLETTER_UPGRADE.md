# Newsletter platform upgrade

Owner: GCB platform. Started 2026-10-14.

The platform will be the master subscriber list. MailerLite will deliver newsletter
campaigns and report subscription events back. An unsubscribe or delivery
suppression must take precedence over an import or routine sync.

## 1. Subscriber imports

Implemented locally; not deployed:

- Admin CSV upload with preview and custom email/name/status column mapping.
- Google Forms email headers, CSV/semicolon/TSV, UTF-8 BOM, quoted names.
- Up to 2 MB and 10,000 rows per import. Preview displays the first 200 rows;
  totals cover the entire file. Invalid rows are skipped with reasons.
- Lowercase address matching; duplicate file rows collapse with inactive status
  taking precedence. Existing unsubscribes cannot be reactivated by import.
- New active rows require an operator's permission confirmation and source note.
- Source, name, consent note, import time and batch ID on new records; transactional
  audit log for all applied batches, including suppressions of existing records.
- Imports do not contact MailerLite or send messages during the request. New rows
  and changed suppressions are queued for sync. Migrations through `037` are required.

Validation: 27 backend tests and 3 interface tests pass; TypeScript and the new
component's ESLint check pass. Migration SQL was generated successfully for
PostgreSQL but has not been applied to a live database. Signup and unsubscribe
lookups now handle address case differences for imported contacts.

API: `POST /api/admin/newsletter/subscribers/import` (admin session).
Body: `csv_content`, `source`, optional `email_column`, `name_column`,
`status_column`, `consent_note`, `confirm_subscribed`, and `dry_run` (default true).
Apply uses the same body with `dry_run=false` and rechecks current database state.

Common status values `active`/`subscribed` mean active; `unsubscribed`, `inactive`,
`bounced`, `junk`, `spam`, `unconfirmed`, and `cleaned` remain inactive. Unknown or
empty values in a status column are invalid. With no status column, rows are
treated as active and require confirmation. Export only opted-in respondents from
Google Forms, or map a yes/no consent column to status; do not import all form
respondents as active merely because an email address was collected.

## 2. Reliable MailerLite synchronization

Implemented locally; not deployed:

- Persistent per-subscriber queue, pending/processing/synced/error status,
  attempts, retry time, last verified time and safe error summaries.
- Background worker with expiring leases, priority for unsubscribes, backoff and
  rate-limit handling. Revision checks prevent stale API results from overwriting
  newer local changes. The worker is disabled until explicitly enabled with
  `NEWSLETTER_SYNC_ENABLED=true`; its default polling interval is 30 seconds.
- Public/authenticated unsubscribe, signup and import changes persist locally and
  queue work without depending on a successful provider call in the HTTP request.
- Routine sync checks remote status first, preserves MailerLite suppressions and
  verifies active group membership after upsert. It never requests reactivation.
- Admin sync reports failures honestly; the UI exposes queue status, retry,
  recheck-all and a read-only credentials/group connection check.
- Admin removal retains a suppression record; stored provider IDs alone no longer
  count as a verified sync.

Validation: 46 backend tests and 5 interface tests pass, with TypeScript and new
component lint checks clean. PostgreSQL migration SQL generation succeeds.
Tests use mocked provider calls and SQLite; production database concurrency and
live MailerLite behavior still need staging verification.

Remaining:

- Verify live credentials, groups and memberships when account access is available.
- Verify the new MailerLite production-group import with the live account. Other
  groups and unassigned contacts require reviewed CSV imports or moving opted-in
  contacts into the configured group. Recheck-all reconciles known records only.
- Review the production duplicate audit and run identity migration `037` during
  the controlled rollout described below.
- Verify the new MailerLite campaign path and readiness checks in staging.

### Import from the existing MailerLite group

Implemented locally; not deployed:

- The admin subscriber tab can preview and import the configured production group.
  It explicitly scans active, unsubscribed, unconfirmed, bounced and junk statuses,
  including every cursor page. Provider requests are GET only.
- Apply refetches the group and requires the preview's snapshot hash. Changed
  provider contacts require a new preview. Local state is checked again when
  applying, so a platform unsubscribe after preview remains protected.
- Existing CSV consent, suppression, provenance and transactional audit rules are
  reused. Imported rows queue sync verification; this action never sends a campaign.
- Scans fail without applying partial results on provider errors, invalid records,
  looping/incomplete pagination or timeout. Limits are 10,000 records, 2 MB and a
  45-second scan; larger groups use reviewed CSV batches.
- Deleted/forgotten contacts are not returned by the group API. Retain existing
  suppression records and handle future deletions through signed webhooks.

API: `POST /api/admin/newsletter/mailerlite/import` with `dry_run=true` for preview.
Apply requires `dry_run=false`, the returned `snapshot_sha256`, and, when adding
active subscribers, `confirm_subscribed=true` plus `consent_note`.

Validation includes all statuses, pagination, partial failures, changed snapshots,
consent enforcement, local opt-outs and repeat imports. No real contacts imported.

### Canonical subscriber identities

Implemented and tested on disposable PostgreSQL; not applied to production:

- Migration `037` consolidates addresses that match after trimming and lowercasing.
  The earliest subscription record survives (UUID breaks timestamp ties). Any
  local opt-out or recorded provider suppression keeps the merged address inactive.
- All original records in affected groups, including the survivor's original
  state, are retained as JSON in `newsletter_subscriber_merges`. Source, consent,
  prior provider state and original IDs are preserved there.
- Old signed unsubscribe links resolve through this archive to the survivor.
  Confirmation tokens for merged groups are cancelled; a new request is required.
- Merged records queue fresh sync verification. Unrelated records stay unchanged.
  A functional unique index rejects future case/whitespace duplicates, including
  concurrent inserts. Signup and imports report conflicts for retry; webhooks
  request provider redelivery on an insertion race.
- Migration takes an exclusive table lock and refuses to proceed while any sync
  lease exists. Stop new subscription writes, drain running sync work, stop workers,
  then migrate and deploy the matching application before reopening writes.
- Consolidation is not automatically reversible. Back up and review duplicates
  before migration; rollback requires a reviewed restore that retains archives
  and unsubscribe aliases. No production identities have been changed yet.

Validation: 106 focused backend tests pass, including archived unsubscribe links
and rejected stale confirmation links. A disposable PostgreSQL 15 instance passed
the complete `001`–`037` migration chain, active-lease rollback, suppression merges,
archive preservation, uniqueness, `SKIP LOCKED`, concurrent claim exclusivity and
stale-result protection across separate sessions.

Repeat the PostgreSQL checks using `scripts/verify_newsletter_postgres.py` with
`GCB_NEWSLETTER_TEST_DATABASE_URL` pointing to an empty localhost database named
`gcb_newsletter_test*`. The script applies migrations and synthetic data only;
it refuses other database locations/names and never contacts MailerLite.

## 3. Subscription lifecycle

Implemented locally; not deployed:

- Public `/newsletter/unsubscribe` page, with email fallback and signed links
  containing only an opaque subscriber ID. The page requires an explicit button
  click; GET requests never mutate subscriptions. Responses do not reveal whether
  an email belongs to the list.
- MailerLite campaign output uses its native unsubscribe link. Preview HTML links
  to the platform email form; platform signed links also remain available.
- `POST /api/newsletter/webhooks/mailerlite` verifies the raw request body's
  HMAC-SHA256 `Signature` before processing single or batched events. Set
  `MAILERLITE_WEBHOOK_SECRET` to the secret returned by MailerLite registration.
- Unsubscribe, bounce, spam and delete events create/retain suppression records.
  Unknown addresses are retained as inactive records to protect later imports.
  This endpoint receives account-level opt-outs; verify the connected account.
- Receipt fingerprints deduplicate retries. Older events cannot replace newer
  suppression metadata; active events cannot reactivate a local unsubscribe.
  Incoming callbacks make no provider calls. Interrupted/outdated outbound sync
  cannot overwrite the webhook and queues corrective reconciliation if needed.
- Admin sync card shows whether a webhook secret is configured and the latest
  authenticated event received. This is not proof of live registration until an
  actual MailerLite event is verified.
- Resubscribing an inactive address sends a transactional confirmation email via
  the existing Resend service, without activating the address. Links are signed,
  single-use, expire after 24 hours, and require a button click. Requests have a
  ten-minute resend cooldown. Failed email delivery leaves the opt-out intact.
- `POST /api/newsletter/confirm-resubscribe` queues explicit resubscription while
  keeping the local address inactive. Only verified provider activation changes
  that state. Confirmed requests may set MailerLite's `resubscribe` flag for an
  unsubscribed address; bounced, junk and unconfirmed statuses stay suppressed.
- Another unsubscribe cancels unused links and pending resubscriptions. In-flight
  provider calls retain their leases so the latest opt-out runs after an older
  mutation. Clearly older webhook opt-outs do not cancel a newer confirmed choice.
- Signup UI distinguishes email-confirmation and sync-pending states from success.
- Signed action pages do not initialize Google/Umami analytics or the support
  widget. The client removes the token from the displayed URL after reading it;
  action buttons retain it in component state. A reload requires reopening the
  email link (or the unsubscribe email fallback). Payment scripts use Stripe's
  deferred loader so route prefetch does not initialize them on action pages.

Signing configuration: set `NEWSLETTER_TOKEN_SECRET` to a stable random value of
at least 32 characters (fallback: `NEXTAUTH_SECRET`). Unsubscribe links do not
expire; rotating the key invalidates old links, so keep the email-form fallback.
`NEWSLETTER_PUBLIC_URL` defaults to `https://greatcommissionbenchmark.ai`.

Validation: 76 backend tests and 21 interface tests pass; TypeScript, targeted
lint, and migration SQL generation pass. Tests exercise signed webhook delivery,
duplicate/out-of-order events, races, and the link from generated email HTML to
the unsubscribe API. They do not prove live delivery or DNS authentication.

Remaining:

- Confirm that live MailerLite unsubscribe links update the platform and prevent later
  imports/sync from reactivating the address.
- Verify the MailerLite sending path and readiness gates below against the account.
- Verify subscribe/unsubscribe/resubscribe end to end in a live test audience.

Current reference docs (checked 2026-10-14):
- https://developers.mailerlite.com/api/subscribers
- https://developers.mailerlite.com/api/webhooks
- https://developers.mailerlite.com/api/groups
- https://developers.mailerlite.com/api/campaigns

## 4. MailerLite campaign delivery

Implemented locally; not deployed:

- Campaign sends now create and schedule MailerLite regular campaigns with native
  unsubscribe links. Transactional confirmation emails still use Resend.
- Production preflight checks the registered webhook URL, secret, batching,
  enabled state and required subscription/completion events. The sync worker must
  be enabled and all subscriber changes resolved.
- Exact active audience comparison includes every page of the MailerLite group.
  Missing or extra recipients block delivery. Checks run before campaign creation
  and again before scheduling; changed posts also block scheduling.
- Reservations serialize competing send requests. Persisting the campaign ID
  before scheduling makes timeout diagnosis possible. Unresolved attempts block
  repeats, including force-resend. No failure falls back to a different provider.
- Send history displays scheduled, sent, failed and uncertain outcomes. Its status
  refresh only reads provider state; signed `campaign.sent` events also confirm
  completion. Delayed responses cannot regress confirmed completion.
- Failed creation with no stored campaign ID can resolve as not sent: the attempt
  never reached scheduling, although an unused remote draft may exist. Ambiguous
  scheduling outcomes remain blocked pending verification.
- The worker rechecks known synced subscribers hourly to help recover missed
  callbacks. This does not discover unknown contacts in MailerLite.

Custom HTML requires the MailerLite Advanced plan and a verified sender. Dry runs
check audience readiness without creating a campaign; they do not prove plan,
sender or domain eligibility. Confirm account footer/address in a real test email.

Migration `036` stores send diagnostics and routing. Live PostgreSQL concurrency,
MailerLite integration, email rendering and actual delivery still require staging.
Validation: 90 focused backend tests and 23 interface tests pass. TypeScript,
targeted ESLint and PostgreSQL migration SQL generation through `036` pass.

## 5. Account, DNS and controlled rollout

Requires MailerLite account access and access to the domain's DNS provider:

- Confirm account, sending domain, sender identity and mailing address.
- Configure API token and separate production/test groups in backend secrets.
- Register and verify the webhook; store its generated secret securely.
- Read MailerLite's exact DNS records for this account; inspect existing DNS,
  configure the requested records, and verify authentication in MailerLite.
- Preserve existing mail routing and account for the domain's existing SPF/DMARC.
- Back up and review duplicate addresses, drain subscriber writers/workers, apply
  migrations through `037` and deploy, then import a small reviewed sample.
- Verify sample signup, platform unsubscribe and MailerLite unsubscribe, sync
  retries and reconciled counts. Send a test only to an approved test recipient.
- Complete the legacy subscriber migration and verify suppression counts before
  using the production audience.

No account changes, DNS changes, deployment, imports of real subscribers, or
campaign sends have been performed during these local upgrades.

### Live discovery — 2026-10-14

Public DNS checks found Cloudflare nameservers (`marvin` and `rihana`), Google
Workspace MX records, one SPF record including Google and `_spf.mlsend.com`, a
MailerLite domain verification TXT record, and DMARC `p=none`. The documented
MailerLite selector `litesrv._domainkey` resolves to `litesrv._domainkey.mlsend.com`
and a DKIM public key. Existing records may already satisfy authentication; they
have not been compared with the account's current requirements or verified in
MailerLite. No DNS changes are justified until that comparison.

The available browser opened MailerLite's sign-in page. User sign-in and Cloudflare
access are requested; no account credentials were entered. Backend startup
explicitly skips migrations, so deployment must include the documented separate
migration step. Frontend production build and 46 relevant interface tests passed;
public action pages were inspected in the locally served production build.

Local configuration has no MailerLite credentials, group IDs, webhook registration
or transactional mail credential. The Railway CLI also reports unauthorized.
Live connection tests and rollout require account sign-in and selection of the
deployment environment. These are current access blockers, not verified failures
of the production integration. Local tests and public DNS checks do not establish
that live sync or account authentication is working.

DNS reference: https://www.mailerlite.com/help/troubleshooting-domain-authentication
