# Great Commission Benchmark — Security Practices

This document defines the security practices, policies, and implementation standards for the Great Commission Benchmark platform, CLI tools, and related systems.

**Last Updated:** December 17, 2025

---

## Table of Contents

1. [Security Principles](#security-principles)
2. [Authentication & Authorization](#authentication--authorization)
3. [API Security](#api-security)
4. [Question Security](#question-security)
5. [Data Protection](#data-protection)
6. [Payment Security](#payment-security)
7. [Infrastructure Security](#infrastructure-security)
8. [Audit & Logging](#audit--logging)
9. [Incident Response](#incident-response)
10. [Security Checklist](#security-checklist)

---

## Security Principles

### Core Principles

| Principle | Description |
|-----------|-------------|
| **Defense in Depth** | Multiple layers of security controls throughout the system |
| **Least Privilege** | Users and systems have only the minimum access required |
| **Secure by Default** | Security controls are enabled by default, not optional |
| **Transparency** | Security practices are documented and communicated |
| **Privacy First** | User privacy is respected; minimal data collection |

### Risk Assessment

| Asset | Risk Level | Protection Priority |
|-------|------------|---------------------|
| **Benchmark Questions** | High | Critical — benchmark integrity depends on question confidentiality |
| **User Data** | High | Critical — PII and account data must be protected |
| **Payment Information** | High | Critical — handled by Stripe; never stored on our servers |
| **Test Results** | Medium | Important — user-owned data with privacy expectations |
| **Platform Infrastructure** | Medium | Important — availability and integrity |
| **Public Leaderboard Data** | Low | Intentionally public; integrity is the concern |

---

## Authentication & Authorization

### Authentication Provider

**Provider:** NextAuth v5 with Google OAuth

**Rationale:**
- Industry-standard OAuth 2.0 implementation
- Secure session management with JWT tokens
- Google OAuth integration for user authentication
- Open-source and self-hosted solution

### JWT Token Security

All authenticated API endpoints require a valid JWT token:

```
Authorization: Bearer <jwt_token>
```

**Token Handling:**
- Tokens issued by NextAuth with appropriate expiration (default: 24 hours)
- Session tokens stored securely with encryption
- Tokens validated on every API request
- Invalid or expired tokens result in `401 Unauthorized`

### Role-Based Access Control (RBAC)

| Role | Description | Access Level |
|------|-------------|--------------|
| `user` | Standard registered user | Own data, test execution, submissions |
| `moderator` | Review queue access | User permissions + moderation queue, reviews |
| `admin` | Full administrative access | All permissions + user management, versions |

**Role Assignment:**
- Default role on registration: `user`
- Role upgrades require admin action
- Role changes logged in audit trail

### Session Security

| Control | Implementation |
|---------|----------------|
| **Session Duration** | 24-hour token expiration |
| **Secure Cookies** | `HttpOnly`, `Secure`, `SameSite=Strict` flags |
| **Session Invalidation** | Logout invalidates all active sessions |
| **Concurrent Sessions** | Allowed; each device gets unique session |

---

## API Security

### Transport Security

| Control | Implementation |
|---------|----------------|
| **HTTPS Only** | All traffic encrypted via TLS 1.2+ |
| **HSTS** | HTTP Strict Transport Security headers enabled |
| **Certificate Management** | Managed by Railway / Let's Encrypt |
| **Redirect HTTP** | All HTTP requests redirected to HTTPS |

### Rate Limiting

Rate limiting prevents abuse and ensures fair resource usage:

| Endpoint Type | Limit | Window | Scope |
|---------------|-------|--------|-------|
| **Public API** | 100 requests | 1 minute | Per IP |
| **Authenticated API** | 300 requests | 1 minute | Per user |
| **Test Execution** | 10 concurrent | - | Per user |
| **Submissions** | 5 per hour | 1 hour | Per user |
| **Authentication** | 10 attempts | 15 minutes | Per IP |

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1702750000
```

**Response on Limit Exceeded:** `429 Too Many Requests`

### Input Validation

| Control | Implementation |
|---------|----------------|
| **Schema Validation** | Pydantic models validate all request bodies |
| **Type Checking** | FastAPI automatic type validation |
| **Size Limits** | Maximum request body size: 10 MB |
| **Content-Type** | Strict content-type validation |
| **Parameter Bounds** | Pagination limits enforced (max 100 per page) |

### SQL Injection Prevention

| Control | Implementation |
|---------|----------------|
| **ORM Usage** | SQLAlchemy ORM for all database operations |
| **Parameterized Queries** | No raw SQL with user input |
| **Query Validation** | ORM generates parameterized queries automatically |

### Cross-Site Scripting (XSS) Prevention

| Control | Implementation |
|---------|----------------|
| **Content Security Policy** | CSP headers restrict script sources |
| **Output Encoding** | React/Next.js automatic HTML escaping |
| **Input Sanitization** | User input sanitized before storage |
| **HTTPOnly Cookies** | Session cookies not accessible via JavaScript |

### Cross-Site Request Forgery (CSRF) Prevention

| Control | Implementation |
|---------|----------------|
| **SameSite Cookies** | `SameSite=Strict` for session cookies |
| **Origin Validation** | Verify request origin for state-changing operations |
| **CSRF Tokens** | CSRF protection for form submissions |

### API Authentication Endpoints

| Endpoint Type | Auth Requirement | Description |
|---------------|------------------|-------------|
| `/api/public/*` | None | Public leaderboard and model data |
| `/api/user/*` | JWT (user) | User dashboard and history |
| `/api/tests/*` | JWT (user) | Test execution and management |
| `/api/submissions/*` | JWT (user) | CLI result uploads |
| `/api/moderator/*` | JWT (moderator) | Moderation queue and reviews |
| `/api/admin/*` | JWT (admin) | Administrative operations |
| `/api/webhooks/*` | Signature | External service callbacks (Stripe) |

---

## Question Security

### The Contamination Problem

Benchmark questions must remain confidential to prevent:
- LLM providers discovering questions through web scraping
- Fine-tuning models specifically for benchmark questions
- Gaming the benchmark without genuine capability improvement

### Question Protection Measures

| Measure | Description |
|---------|-------------|
| **Server-Side Only** | Questions are never sent to client browsers |
| **Authenticated Access** | Only registered testers with valid agreement |
| **No Client Storage** | Questions processed server-side; responses stored |
| **Audit Logging** | All question access is logged |

### What IS Public vs. What is NOT Public

**Public:**
- Benchmark methodology and scoring framework
- Leaderboard results and aggregate statistics
- Use case categories and testing tiers
- Sample questions (similar, not identical to actual questions)
- Platform code (open source infrastructure)

**NOT Public:**
- Full question sets
- Specific test prompts
- Expected responses and verdicts
- Detailed scoring rubrics

### Tester Agreement Requirements

All testers agree to:
- ❌ Not publish questions publicly (web, social media, forums)
- ❌ Not share questions with LLM providers
- ❌ Not use questions for model training
- ✅ Report any suspected leaks
- ✅ Follow benchmark usage guidelines

### Leak Response Plan

**If questions leak publicly:**

1. **Version Invalidation** — Leaked version marked as superseded
2. **New Version Release** — Release new version with new questions
3. **Communication** — Notify testers to use new version
4. **No Emergency Rotation** — Orderly transition; old results remain valid for old version

---

## Data Protection

### Personal Data Handling

| Data Type | Collection | Storage | Retention |
|-----------|------------|---------|-----------|
| **Email Address** | Registration | Encrypted at rest | Account lifetime |
| **Name** | Optional profile | Encrypted at rest | Account lifetime |
| **Organization** | Optional profile | Encrypted at rest | Account lifetime |
| **User ID** | Authentication | Encrypted at rest | Account lifetime |
| **Test Results** | Test execution | Encrypted at rest | Indefinite (user-owned) |

### Data Encryption

| Layer | Encryption Method |
|-------|-------------------|
| **Transport** | TLS 1.2+ (HTTPS) |
| **Database** | PostgreSQL encryption at rest (Railway managed) |
| **Backups** | Encrypted backup storage |
| **API Keys/Secrets** | Environment variables; never in code |

### Data Minimization

| Principle | Implementation |
|-----------|----------------|
| **Collect Only Necessary** | Only essential data collected |
| **No Tracking** | Umami analytics (privacy-first, no cookies) |
| **No Third-Party Sharing** | User data not shared with third parties |
| **User Control** | Users can view and request deletion of their data |

### Data Retention

| Data Type | Retention Period | Deletion Method |
|-----------|------------------|-----------------|
| **User Accounts** | Until deletion requested | Hard delete with 30-day grace |
| **Test Results** | Indefinite (user-owned) | Deleted with account |
| **Audit Logs** | 2 years | Automatic purge |
| **Payment Records** | 7 years (legal requirement) | Retained in Stripe |
| **Analytics Data** | 1 year | Rolling window |

---

## Payment Security

### PCI DSS Compliance

**Approach:** Stripe handles all PCI compliance requirements

| Requirement | Implementation |
|-------------|----------------|
| **Card Data Handling** | Never touches our servers; Stripe.js handles |
| **PCI Scope** | Platform is SAQ A eligible (lowest scope) |
| **Tokenization** | Stripe tokens used for all payment references |

### Stripe Integration Security

| Control | Implementation |
|---------|----------------|
| **Client-Side** | Stripe.js for card collection (PCI-compliant) |
| **Server-Side** | Stripe API with restricted secret key |
| **Webhooks** | Signature verification for all Stripe events |
| **Idempotency** | Idempotency keys prevent double charges |

### Webhook Verification

All Stripe webhooks verified using signature:

```python
# Verify Stripe webhook signature
stripe.Webhook.construct_event(
    payload=request_body,
    sig_header=stripe_signature,
    secret=webhook_signing_secret
)
```

### Refund Security

| Control | Implementation |
|---------|----------------|
| **Automatic Eligibility** | System determines refund eligibility based on failure type |
| **Stripe Processing** | Refunds processed through Stripe API |
| **Audit Trail** | All refund requests and processing logged |
| **Fraud Prevention** | Retest limits (max 3 attempts) prevent abuse |

---

## Infrastructure Security

### Deployment Security

| Control | Implementation |
|---------|----------------|
| **Platform** | Railway (managed PaaS) |
| **Container Isolation** | Containers isolated by Railway infrastructure |
| **Environment Variables** | Secrets stored in Railway environment |
| **Deployment** | Git-based deployment from protected branches |

### Secret Management

| Secret Type | Storage Location | Access |
|-------------|------------------|--------|
| **API Keys** | Railway environment variables | Runtime only |
| **Database Credentials** | Railway managed | Automatic injection |
| **NextAuth Secrets** | Railway environment variables | Runtime only |
| **Stripe Keys** | Railway environment variables | Runtime only |
| **Webhook Secrets** | Railway environment variables | Runtime only |

**Secret Handling Rules:**
- ❌ Never commit secrets to version control
- ❌ Never log secrets or include in error messages
- ❌ Never expose secrets in API responses
- ✅ Use environment variables for all secrets
- ✅ Rotate secrets periodically
- ✅ Use restricted/scoped API keys where possible

### Backup Security

| Tier | Provider | Frequency | Encryption |
|------|----------|-----------|------------|
| **Primary** | Railway | Automated/daily | Encrypted at rest |
| **Secondary** | Local machine download | Weekly/monthly | Encrypted storage |

### Network Security

| Control | Implementation |
|---------|----------------|
| **Firewall** | Railway managed firewall |
| **DDoS Protection** | Railway infrastructure protection |
| **IP Restrictions** | Admin endpoints can be IP-restricted if needed |
| **Internal Traffic** | Database accessible only from application |

---

## Audit & Logging

### Audit Log Events

| Event Category | Events Logged |
|----------------|---------------|
| **Authentication** | Login, logout, failed login, password reset |
| **Authorization** | Role changes, permission denials |
| **Data Access** | Question access, result views (moderator/admin) |
| **Data Modification** | Profile updates, test submissions |
| **Administrative** | User management, version uploads, role assignments |
| **Payment** | Payment attempts, refunds, failures |
| **Moderation** | Review submissions, verdict overrides |

### Audit Log Format

```json
{
  "timestamp": "2025-12-17T10:30:00Z",
  "event_type": "question_access",
  "user_id": "uuid",
  "ip_address": "192.168.1.1",
  "resource": "test_run/uuid",
  "action": "execute",
  "result": "success",
  "metadata": {
    "question_count": 300,
    "benchmark_version": "2.0"
  }
}
```

### Log Storage & Access

| Aspect | Implementation |
|--------|----------------|
| **Storage** | Application logs in Railway; audit logs in database |
| **Retention** | 2 years for audit logs; 30 days for application logs |
| **Access** | Admin role required for audit log access |
| **Integrity** | Logs are append-only; no modification allowed |

### Monitoring & Alerting

| System | Purpose |
|--------|---------|
| **Sentry** | Error tracking and alerting |
| **Railway Logs** | Application and infrastructure logs |
| **Umami** | Privacy-respecting analytics |

**Alert Categories:**
- Test failure spikes → Email to admins
- Payment failures → Immediate notification
- Authentication anomalies → Security review
- Infrastructure issues → Railway notifications

---

## Incident Response

### Incident Classification

| Severity | Description | Response Time |
|----------|-------------|---------------|
| **Critical** | Data breach, payment compromise, complete outage | Immediate |
| **High** | Partial outage, security vulnerability, data integrity issue | < 4 hours |
| **Medium** | Performance degradation, non-critical bug | < 24 hours |
| **Low** | Minor issues, feature requests | Best effort |

### Incident Response Process

1. **Detection** — Identify incident through monitoring, alerts, or user reports
2. **Classification** — Determine severity and impact
3. **Containment** — Limit damage and prevent spread
4. **Investigation** — Determine root cause and scope
5. **Remediation** — Fix the issue and restore service
6. **Communication** — Notify affected users if applicable
7. **Post-Mortem** — Document lessons learned and preventive measures

### Security Incident Types

| Incident Type | Immediate Actions |
|---------------|-------------------|
| **Suspected Data Breach** | Isolate affected systems, preserve logs, assess scope |
| **Question Leak** | Invoke leak response plan (version invalidation) |
| **Account Compromise** | Disable account, reset credentials, notify user |
| **Payment Fraud** | Contact Stripe, freeze suspicious accounts |
| **DDoS Attack** | Enable additional protection, contact Railway support |

### Communication

**For Security Incidents:**
- Critical incidents → Direct notification to affected users
- Data breaches → Notification within 72 hours (GDPR requirement)
- Platform issues → Status page updates

**Contact:**
- Project lead monitors inboxes and error notifications
- Critical alerts sent to designated admin addresses

---

## Security Checklist

### Pre-Launch Security Checklist

**Authentication & Authorization:**
- [ ] NextAuth properly configured with secure defaults
- [ ] Google OAuth credentials configured correctly
- [ ] JWT validation implemented on all protected endpoints
- [ ] Role-based access control implemented and tested
- [ ] Session management secure (HTTPOnly, Secure, SameSite)

**API Security:**
- [ ] HTTPS enforced; HTTP redirects to HTTPS
- [ ] Rate limiting configured for all endpoint types
- [ ] Input validation on all endpoints (Pydantic)
- [ ] SQL injection prevention verified (ORM usage)
- [ ] XSS prevention verified (CSP headers, output encoding)
- [ ] CSRF protection implemented

**Question Security:**
- [ ] Questions never sent to client browser
- [ ] All question access requires authentication
- [ ] Audit logging for question access implemented
- [ ] Tester agreement enforcement in place

**Data Protection:**
- [ ] Database encryption at rest enabled
- [ ] All traffic over HTTPS (TLS 1.2+)
- [ ] No secrets in code or version control
- [ ] Environment variables used for all secrets

**Payment Security:**
- [ ] Stripe integration using Stripe.js (client-side)
- [ ] Webhook signature verification implemented
- [ ] Idempotency keys used for payments
- [ ] Refund processing tested

**Infrastructure:**
- [ ] Production environment properly configured
- [ ] Backup strategy implemented and tested
- [ ] Monitoring and alerting configured
- [ ] Error tracking (Sentry) operational

**Audit & Logging:**
- [ ] Audit logging implemented for security events
- [ ] Log retention policies configured
- [ ] Alerting for security anomalies configured

### Ongoing Security Practices

| Practice | Frequency |
|----------|-----------|
| **Dependency Updates** | Monthly review; immediate for security patches |
| **Secret Rotation** | Quarterly or upon suspected compromise |
| **Access Review** | Quarterly review of user roles and permissions |
| **Security Testing** | Before major releases |
| **Backup Testing** | Monthly restore test |
| **Incident Response Drill** | Annual |

---

## Related Documents

- [Technical Architecture](../benchmark/platform-technical-architecture.md) — System architecture
- [Question Security](../benchmark/process-question-security.md) — Question protection details
- [API Endpoints](../benchmark/spec-api-endpoints.md) — API specification
- [Privacy Policy](./Privacy-Policy.md) — User privacy commitments
- [Terms of Service](./Terms-of-Service.md) — User agreements
- [Technical Decisions](./Technical-Decisions.md) — Decision rationale

---

*This document should be reviewed and updated as security practices evolve and new controls are implemented.*
