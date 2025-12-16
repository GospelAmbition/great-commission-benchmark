# User Notifications Feature Specification

## Purpose

The user notification system keeps users informed about important events related to their test runs, submissions, and account activity. It provides both in-app notifications and email notifications, with user-configurable preferences.

---

## Overview

The notification system enables:

- **In-app notifications** — Real-time notifications displayed in the UI
- **Email notifications** — Email alerts for important events
- **Preference management** — Users control which notifications they receive
- **Notification history** — Users can view past notifications
- **Delivery tracking** — System tracks notification delivery status

---

## User Stories

### Primary Users

1. **Volunteers** — "I want to be notified when my test completes so I can view results immediately"
2. **Organizations** — "I need email notifications when our test runs finish"
3. **Community Contributors** — "I want to know when my CLI submission is approved or rejected"
4. **Moderators** — "I need notifications when new test results need review"

### Key Scenarios

- **Scenario 1:** A user starts a test run and receives an email when it completes with a link to view results
- **Scenario 2:** A community contributor receives an in-app notification that their submission was approved
- **Scenario 3:** A moderator receives an email when a test result is escalated to the committee
- **Scenario 4:** A user disables email notifications but keeps in-app notifications enabled

---

## Architecture

### Component Structure

```
┌─────────────────────────────────────────────────────────┐
│         Notification System (Multi-Component)            │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Notification │  │ Email        │  │ In-App       │  │
│  │ Service      │  │ Service      │  │ Component    │  │
│  │ (FastAPI)    │  │ (SMTP/SES)   │  │ (Next.js)    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Template     │  │ Preference   │  │ Delivery      │  │
│  │ Engine       │  │ Manager      │  │ Tracker       │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
                    PostgreSQL
    (notifications, notification_preferences, notification_logs)
```

---

## Notification Types

### Test-Related Notifications

| Type | Trigger | In-App | Email | Description |
|------|---------|--------|-------|-------------|
| `test_started` | Test run begins | ✓ | ✓ | Test has started running |
| `test_progress` | Test reaches milestone (25%, 50%, 75%) | ✓ | ✗ | Progress update (in-app only) |
| `test_completed` | Test run completes successfully | ✓ | ✓ | Test finished, results available |
| `test_failed` | Test run fails | ✓ | ✓ | Test encountered an error |
| `test_published` | Test results published to leaderboard | ✓ | ✓ | Results now visible publicly |

### Submission-Related Notifications

| Type | Trigger | In-App | Email | Description |
|------|---------|--------|-------|-------------|
| `submission_received` | CLI submission uploaded | ✓ | ✓ | Submission received and queued |
| `submission_approved` | Submission approved by reviewer | ✓ | ✓ | Submission approved and published |
| `submission_rejected` | Submission rejected | ✓ | ✓ | Submission rejected with reason |
| `submission_needs_revision` | Submission needs changes | ✓ | ✓ | Reviewer requests revisions |

### Moderation-Related Notifications

| Type | Trigger | In-App | Email | Description |
|------|---------|--------|-------|-------------|
| `moderation_review_started` | Moderator starts reviewing test | ✓ | ✗ | Your test is being reviewed |
| `moderation_review_completed` | Moderator completes review | ✓ | ✓ | Review completed, trust tier updated |
| `moderation_concerns_flagged` | Concerns flagged on test | ✓ | ✓ | Moderator flagged concerns |
| `moderation_escalated` | Test escalated to committee | ✓ | ✓ | Issue escalated for resolution |

### Payment-Related Notifications

| Type | Trigger | In-App | Email | Description |
|------|---------|--------|-------|-------------|
| `payment_required` | Payment needed to start test | ✓ | ✓ | Payment required to proceed |
| `payment_succeeded` | Payment processed successfully | ✓ | ✓ | Payment confirmed |
| `payment_failed` | Payment processing failed | ✓ | ✓ | Payment failed, action needed |
| `refund_processed` | Refund issued | ✓ | ✓ | Refund has been processed |

### Account-Related Notifications

| Type | Trigger | In-App | Email | Description |
|------|---------|--------|-------|-------------|
| `welcome` | New user registration | ✓ | ✓ | Welcome message and onboarding |
| `password_reset` | Password reset requested | ✗ | ✓ | Password reset link (email only) |
| `account_updated` | Profile or settings changed | ✓ | ✗ | Account changes confirmed |

### System Notifications

| Type | Trigger | In-App | Email | Description |
|------|---------|--------|-------|-------------|
| `newsletter` | Newsletter sent | ✗ | ✓ | Newsletter content (opt-in) |
| `system_maintenance` | Scheduled maintenance | ✓ | ✓ | Maintenance window notification |
| `benchmark_version_update` | New benchmark version released | ✓ | ✓ | New version available |

---

## Data Model

### Notification

```typescript
interface Notification {
  id: string;
  user_id: string;
  type: NotificationType;
  title: string;
  message: string;
  link: string | null;              // URL to related resource
  metadata: Record<string, any>;     // Additional context data
  channels: {
    in_app: boolean;
    email: boolean;
  };
  status: {
    in_app: 'unread' | 'read' | 'dismissed';
    email: 'pending' | 'sent' | 'delivered' | 'failed';
  };
  created_at: string;
  read_at: string | null;
  dismissed_at: string | null;
  email_sent_at: string | null;
  email_delivered_at: string | null;
}
```

### Notification Preferences

```typescript
interface NotificationPreferences {
  user_id: string;
  // Test-related
  test_completion: boolean;          // Default: true
  test_publication: boolean;         // Default: true
  test_progress: boolean;             // Default: false (in-app only)
  test_failure: boolean;              // Default: true
  
  // Submission-related
  submission_updates: boolean;       // Default: true
  submission_approval: boolean;       // Default: true
  
  // Moderation-related
  moderation_updates: boolean;       // Default: true
  
  // Payment-related
  payment_updates: boolean;           // Default: true
  
  // Account-related
  account_updates: boolean;           // Default: true
  
  // System
  newsletter: boolean;                // Default: false (opt-in)
  system_announcements: boolean;       // Default: true
  
  // Channel preferences
  email_enabled: boolean;             // Master email toggle
  in_app_enabled: boolean;             // Master in-app toggle (always true)
  
  updated_at: string;
}
```

### Notification Template

```typescript
interface NotificationTemplate {
  type: NotificationType;
  in_app: {
    title: string;
    message: string;
    icon: string;                     // Icon identifier
    priority: 'low' | 'medium' | 'high';
  };
  email: {
    subject: string;
    template: string;                 // Template file path or content
    priority: 'low' | 'medium' | 'high';
  };
}
```

---

## API Endpoints

### GET /api/user/notifications

Get user's notifications with filtering and pagination.

**Authentication:** Required

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | string | - | Filter by status ("unread", "read", "dismissed") |
| `type` | string | - | Filter by notification type |
| `channel` | string | - | Filter by channel ("in_app", "email") |
| `limit` | integer | 50 | Number of results per page |
| `offset` | integer | 0 | Pagination offset |

**Response:**

```json
{
  "notifications": [
    {
      "id": "uuid",
      "type": "test_completed",
      "title": "Test Completed: Claude 3.5 Sonnet",
      "message": "Your test run finished with an overall score of 87",
      "link": "/user/tests/uuid",
      "status": {
        "in_app": "unread",
        "email": "delivered"
      },
      "created_at": "2025-12-15T10:30:00Z",
      "read_at": null
    }
  ],
  "unread_count": 3,
  "pagination": {
    "limit": 50,
    "offset": 0,
    "total": 12,
    "has_more": false
  }
}
```

### PUT /api/user/notifications/:id/read

Mark a notification as read.

**Path Parameters:**
- `id`: Notification UUID

**Response:**

```json
{
  "notification": {
    "id": "uuid",
    "status": {
      "in_app": "read"
    },
    "read_at": "2025-12-16T10:00:00Z"
  }
}
```

### PUT /api/user/notifications/:id/dismiss

Dismiss a notification (removes from active list).

**Path Parameters:**
- `id`: Notification UUID

**Response:**

```json
{
  "notification": {
    "id": "uuid",
    "status": {
      "in_app": "dismissed"
    },
    "dismissed_at": "2025-12-16T10:00:00Z"
  }
}
```

### PUT /api/user/notifications/read-all

Mark all notifications as read.

**Response:**

```json
{
  "updated_count": 5,
  "unread_count": 0
}
```

### GET /api/user/notifications/preferences

Get user's notification preferences.

**Response:**

```json
{
  "preferences": {
    "test_completion": true,
    "test_publication": true,
    "test_progress": false,
    "test_failure": true,
    "submission_updates": true,
    "submission_approval": true,
    "moderation_updates": true,
    "payment_updates": true,
    "account_updates": true,
    "newsletter": false,
    "system_announcements": true,
    "email_enabled": true,
    "in_app_enabled": true,
    "updated_at": "2025-12-01T10:00:00Z"
  }
}
```

### PUT /api/user/notifications/preferences

Update user's notification preferences.

**Request Body:**

```json
{
  "test_completion": true,
  "newsletter": false,
  "email_enabled": true
}
```

**Response:**

```json
{
  "preferences": {
    /* updated preferences */
  },
  "updated_at": "2025-12-16T10:00:00Z"
}
```

### POST /api/notifications/send

Internal endpoint for triggering notifications (used by other services).

**Authentication:** Internal service token

**Request Body:**

```json
{
  "user_id": "uuid",
  "type": "test_completed",
  "metadata": {
    "test_run_id": "uuid",
    "model_name": "Claude 3.5 Sonnet",
    "score": 87
  }
}
```

**Response:**

```json
{
  "notification": {
    "id": "uuid",
    "status": {
      "in_app": "unread",
      "email": "pending"
    }
  },
  "email_job_id": "uuid"
}
```

---

## Email Service Integration

### Email Provider Options

**Recommended:** AWS SES (Simple Email Service) or SendGrid

**Requirements:**
- Transactional email support
- Delivery tracking
- Bounce/complaint handling
- Template support

### Email Templates

**Template Structure:**

```
templates/
  emails/
    test-completed.html
    test-failed.html
    submission-approved.html
    submission-rejected.html
    payment-succeeded.html
    welcome.html
    newsletter.html
```

**Template Variables:**

- `{{user_name}}` — User's display name
- `{{test_run_id}}` — Test run UUID
- `{{model_name}}` — Model name
- `{{score}}` — Test score
- `{{link}}` — Action link
- `{{unsubscribe_link}}` — Unsubscribe link

### Email Delivery

**Process:**
1. Notification created with `email: true`
2. System checks user preferences
3. If enabled, queue email job
4. Email service sends email
5. System tracks delivery status
6. Update notification status

**Retry Logic:**
- Retry failed sends up to 3 times
- Exponential backoff (1min, 5min, 30min)
- Mark as failed after 3 attempts

---

## In-App Notification Component

### Notification Bell

**Header component with:**
- Bell icon with unread count badge
- Dropdown panel showing recent notifications
- "Mark all as read" action
- Link to full notification center

### Notification Panel

```
┌─────────────────────────────────────────────────────────────┐
│  Notifications (3 unread)                    [Mark all read] │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  🔔 Test Completed: Claude 3.5 Sonnet                        │
│     Your test run finished with an overall score of 87      │
│     2 hours ago                                    [View]    │
│                                                               │
│  ✓ Submission Approved: Llama 3.1 70B                        │
│     Your CLI submission has been approved and published     │
│     5 days ago                                     [View]    │
│                                                               │
│  💰 Payment Succeeded                                        │
│     Your payment of $20.00 has been processed                │
│     1 week ago                                     [View]    │
│                                                               │
│  [View All Notifications]                                    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Notification Center Page

**Full-page view with:**
- Filter by type, status, date
- Group by date (Today, Yesterday, This Week, Older)
- Bulk actions (mark all read, dismiss all)
- Notification preferences link

---

## Real-Time Updates

### WebSocket Integration

**For in-app notifications:**
- Establish WebSocket connection on login
- Server pushes new notifications in real-time
- Update notification bell badge count
- Show toast notification for high-priority items

**Fallback:**
- If WebSocket unavailable, poll every 30 seconds
- Use Server-Sent Events (SSE) as alternative

---

## Notification Delivery Logic

### Preference Checking

```typescript
function shouldSendNotification(
  user: User,
  preferences: NotificationPreferences,
  notificationType: NotificationType
): { in_app: boolean; email: boolean } {
  // Check master toggles
  if (!preferences.in_app_enabled) {
    return { in_app: false, email: false };
  }
  
  // Check type-specific preferences
  const typeEnabled = getPreferenceForType(preferences, notificationType);
  
  return {
    in_app: preferences.in_app_enabled && typeEnabled,
    email: preferences.email_enabled && typeEnabled && 
           shouldSendEmail(notificationType)
  };
}
```

### Priority Handling

**High Priority** (send immediately):
- Test failures
- Payment failures
- Submission rejections
- Account security issues

**Medium Priority** (send within 5 minutes):
- Test completion
- Submission approval
- Moderation updates

**Low Priority** (send within 1 hour):
- Test progress updates
- Newsletter
- System announcements

---

## UI/UX Design

### Notification Bell Component

```
┌─────────────────┐
│  [🔔] (3)       │  ← Bell icon with badge
└─────────────────┘
       │
       ▼ (click)
┌─────────────────────────────────────┐
│  Notifications (3)    [Mark all read]│
├─────────────────────────────────────┤
│  [Notification items...]             │
│  [View All]                          │
└─────────────────────────────────────┘
```

### Notification Item

```
┌─────────────────────────────────────────────────────────┐
│  [Icon] Title                                    [X]     │
│         Message text goes here...                       │
│         [Action Button]  2 hours ago                    │
└─────────────────────────────────────────────────────────┘
```

**Visual States:**
- **Unread** — Bold text, colored background
- **Read** — Normal text, gray background
- **Dismissed** — Hidden from list (can view in history)

### Toast Notifications

**For high-priority real-time notifications:**
- Appear in corner of screen
- Auto-dismiss after 5 seconds
- Click to navigate to related resource
- Stack multiple toasts

---

## Notification Preferences UI

### Preferences Page

```
┌─────────────────────────────────────────────────────────────┐
│  Notification Preferences                                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Email Notifications                    [Enabled] [Disabled] │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ✓ Test completion                                    │   │
│  │ ✓ Test publication                                   │   │
│  │ ✗ Test progress (in-app only)                        │   │
│  │ ✓ Test failure                                       │   │
│  │ ✓ Submission updates                                 │   │
│  │ ✓ Moderation updates                                 │   │
│  │ ✓ Payment updates                                    │   │
│  │ ✗ Newsletter (opt-in)                                 │   │
│  │ ✓ System announcements                               │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  In-App Notifications (always enabled)                       │
│  [Same checkboxes as above]                                 │
│                                                               │
│  [Save Preferences]                                           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Performance Considerations

### Notification Batching

- **Batch email sends:** Group multiple notifications per user
- **Rate limiting:** Limit emails to 1 per user per 5 minutes (except high-priority)
- **Queue processing:** Use background job queue for email delivery

### Database Optimization

- **Indexes:** Index on `user_id`, `status`, `created_at`
- **Archiving:** Archive old notifications (>90 days) to separate table
- **Cleanup:** Auto-delete dismissed notifications after 30 days

### Real-Time Performance

- **WebSocket connection pooling:** Reuse connections
- **Notification throttling:** Limit to 10 notifications per minute per user
- **Client-side caching:** Cache recent notifications locally

---

## Accessibility

### WCAG Level A Compliance

- **Screen reader support:** Announce new notifications
- **Keyboard navigation:** Full keyboard support
- **Focus management:** Focus moves to new notifications
- **Color contrast:** Minimum 4.5:1 for all text

### Screen Reader Announcements

- "New notification: Test completed"
- "3 unread notifications"
- "Notification marked as read"

---

## Edge Cases

### Email Delivery Failures

- **Bounce handling:** Detect bounces, mark email as failed
- **Unsubscribe:** Honor unsubscribe requests immediately
- **Invalid email:** Skip email send, still send in-app

### User Not Found

- **Deleted accounts:** Skip notification creation
- **Suspended accounts:** Skip notification creation
- **Invalid user_id:** Log error, skip notification

### Notification Flood

- **Rate limiting:** Max 10 notifications per user per hour
- **Batching:** Combine similar notifications
- **Throttling:** Delay low-priority notifications

---

## Future Enhancements

### Phase 2 Features

- **Push notifications:** Browser push notifications
- **SMS notifications:** Optional SMS for critical events
- **Notification scheduling:** Schedule notifications for specific times
- **Custom notification rules:** User-defined notification rules

### Phase 3 Features

- **Notification analytics:** Track open rates, click rates
- **A/B testing:** Test different notification formats
- **Smart grouping:** Group related notifications
- **Notification search:** Search notification history

---

## Testing Requirements

### Unit Tests

- Preference checking logic
- Notification creation
- Template rendering
- Delivery status updates

### Integration Tests

- Email sending
- WebSocket delivery
- Preference updates
- Notification filtering

### E2E Tests

- Complete notification flow
- Preference management
- Email delivery
- In-app notification display

---

## Related Features

- **User Dashboard** — Notification center integration (see feature-user-dashboard.md)
- **Moderator Dashboard** — Moderation-specific notifications (see feature-moderator-dashboard.md)

---

## Open Questions

1. **Should we support browser push notifications?**
   - Recommendation: Phase 2 feature, requires user permission

2. **How should we handle notification preferences for organizations?**
   - Recommendation: Phase 2 feature, organization-level preferences

3. **Should moderators receive different notification types?**
   - Recommendation: Yes, moderation-specific notifications

4. **What's the retention period for notification history?**
   - Recommendation: 90 days active, archive older, delete after 1 year

---

*Last Updated: December 16, 2025*
