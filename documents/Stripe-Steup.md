# Stripe Donation Setup Plan

## Overview

The donation tool code is already fully implemented in your codebase. You just need to:
1. Set up Stripe accounts (test and live)
2. Configure environment variables
3. Set up webhooks
4. Test the integration
5. Deploy to production

---

## Phase 1: Stripe Account Setup

### 1.1 Create Stripe Account

1. Go to [stripe.com](https://stripe.com) and create an account
2. Complete business verification (required for live mode)
3. Add business details:
   - Business name: Digital Disciple Makers Network (as mentioned in your code)
   - Business type: Non-profit/501(c)(3) (if applicable)
   - Tax ID (for tax-deductible donations)

### 1.2 Get API Keys

**Test Mode Keys:**
1. In Stripe Dashboard, toggle to **Test mode** (top right)
2. Go to **Developers → API keys**
3. Copy:
   - **Publishable key**: `pk_test_...`
   - **Secret key**: `sk_test_...` (click "Reveal test key")

**Live Mode Keys:**
1. Toggle to **Live mode**
2. Go to **Developers → API keys**
3. Copy:
   - **Publishable key**: `pk_live_...`
   - **Secret key**: `sk_live_...` (click "Reveal live key")

---

## Phase 2: Local Development Setup

### 2.1 Backend Configuration

Add to `gcb-platform/backend/.env`:

```env
# Stripe (Test Mode for Development)
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx  # Will be set after webhook setup
```

### 2.2 Frontend Configuration

Add to `gcb-platform/frontend/.env.local`:

```env
# Stripe (Test Mode for Development)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxx
```

### 2.3 Install Dependencies

The Stripe Python package is already in `requirements.txt` (`stripe==7.8.0`). Verify frontend packages:

```bash
cd gcb-platform/frontend
pnpm install @stripe/stripe-js @stripe/react-stripe-js
```

---

## Phase 3: Webhook Setup (Local Development)

### 3.1 Install Stripe CLI

```bash
# macOS
brew install stripe/stripe-cli/stripe

# Or download from: https://stripe.com/docs/stripe-cli
```

### 3.2 Login to Stripe CLI

```bash
stripe login
```

### 3.3 Forward Webhooks to Local Backend

```bash
# Forward webhooks to your local backend
stripe listen --forward-to localhost:8000/api/v1/webhooks/stripe
```

This will output a webhook signing secret like `whsec_...`. Copy this to your backend `.env`:

```env
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

### 3.4 Test Webhook Events

In another terminal, trigger test events:

```bash
# Test payment success
stripe trigger payment_intent.succeeded

# Test payment failure
stripe trigger payment_intent.payment_failed
```

---

## Phase 4: Testing the Donation Flow

### 4.1 Start Services

**Terminal 1 (Backend):**
```bash
cd gcb-platform/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd gcb-platform/frontend
pnpm dev
```

**Terminal 3 (Stripe Webhook Forwarding):**
```bash
stripe listen --forward-to localhost:8000/api/v1/webhooks/stripe
```

### 4.2 Test Donation

1. Navigate to `http://localhost:3000/contribute/support`
2. Select a donation amount (minimum $5)
3. Use Stripe test card: `4242 4242 4242 4242`
   - Expiry: Any future date (e.g., 12/25)
   - CVC: Any 3 digits (e.g., 123)
   - ZIP: Any 5 digits (e.g., 12345)
4. Enter email (optional)
5. Submit donation
6. Verify:
   - Success message appears
   - Payment appears in Stripe Dashboard → Payments
   - Webhook events appear in Stripe CLI terminal

### 4.3 Test Payment Failure

Use test card: `4000 0000 0000 0002` (declined card)

---

## Phase 5: Production Setup

### 5.1 Production Environment Variables

**Backend (Railway/Production):**
```env
# Stripe (Live Mode)
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx  # From production webhook
```

**Frontend (Railway/Production):**
```env
# Stripe (Live Mode)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_xxxxxxxxxxxxx
```

### 5.2 Production Webhook Setup

1. In Stripe Dashboard, toggle to **Live mode**
2. Go to **Developers → Webhooks**
3. Click **"Add endpoint"**
4. **Endpoint URL**: `https://backend-production-ba51.up.railway.app/api/v1/webhooks/stripe`
   - (Update with your production backend URL)
5. Select events to listen to:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `charge.refunded`
6. Click **"Add endpoint"**
7. Copy the **Signing secret** (`whsec_...`) and add to backend environment variables

### 5.3 Verify Production Webhook

1. In Stripe Dashboard → Webhooks → Your endpoint
2. Click **"Send test webhook"**
3. Select `payment_intent.succeeded`
4. Check backend logs to confirm webhook received

---

## Phase 6: Security & Compliance

### 6.1 PCI Compliance

- ✅ Already handled: Using Stripe Elements (PCI compliant)
- ✅ Card data never touches your servers
- ✅ All payment processing via Stripe

### 6.2 Security Checklist

- [ ] All Stripe keys stored in environment variables (never in code)
- [ ] Webhook signature verification enabled (already implemented)
- [ ] HTTPS enforced in production
- [ ] Test mode keys only used in development
- [ ] Live mode keys only used in production

### 6.3 Tax & Legal

- [ ] Configure tax settings in Stripe Dashboard (if applicable)
- [ ] Set up automatic receipts (already configured via `receipt_email`)
- [ ] Review donation receipt templates in Stripe Dashboard
- [ ] Ensure compliance with local donation/tax laws

---

## Phase 7: Monitoring & Maintenance

### 7.1 Stripe Dashboard Monitoring

- Monitor payments in Stripe Dashboard → Payments
- Set up email alerts for:
  - Failed payments
  - Disputes/chargebacks
  - High-value transactions

### 7.2 Webhook Monitoring

- Check webhook delivery status in Stripe Dashboard → Webhooks
- Monitor failed webhook deliveries
- Set up alerts for webhook failures

### 7.3 Application Monitoring

- Monitor backend logs for payment errors
- Track donation success/failure rates
- Set up alerts for payment processing errors

---

## Phase 8: Testing Checklist

### Development Testing

- [ ] Test successful donation with test card `4242 4242 4242 4242`
- [ ] Test payment failure with declined card `4000 0000 0000 0002`
- [ ] Test minimum amount validation ($5 minimum)
- [ ] Test custom amount input
- [ ] Test email receipt delivery
- [ ] Verify webhook events are received
- [ ] Test donation success UI state

### Production Testing (Small Amount)

- [ ] Test with real card (small amount, e.g., $5)
- [ ] Verify payment appears in Stripe Dashboard
- [ ] Verify receipt email received
- [ ] Verify webhook received and processed
- [ ] Test refund process (if needed)

---

## Troubleshooting

### Issue: "Payment processing is not configured"

- **Solution:** Ensure `STRIPE_SECRET_KEY` is set in backend `.env`
- **Solution:** Ensure `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` is set in frontend `.env.local`

### Issue: Webhook signature verification fails

- **Solution:** Ensure `STRIPE_WEBHOOK_SECRET` matches the webhook endpoint secret
- **Solution:** For local dev, use the secret from `stripe listen` command
- **Solution:** For production, use the secret from Stripe Dashboard → Webhooks

### Issue: Payment succeeds but webhook not received

- **Solution:** Check webhook endpoint URL is correct
- **Solution:** Verify webhook is enabled in Stripe Dashboard
- **Solution:** Check backend logs for webhook errors
- **Solution:** Use Stripe Dashboard → Webhooks → Test webhook to verify

### Issue: "Card element not found"

- **Solution:** Ensure Stripe Elements is properly initialized
- **Solution:** Check browser console for JavaScript errors
- **Solution:** Verify `@stripe/react-stripe-js` is installed

---

## Next Steps

1. ✅ Create Stripe account (test and live)
2. ✅ Configure local development environment
3. ✅ Set up local webhook forwarding
4. ✅ Test donation flow locally
5. ✅ Configure production environment variables
6. ✅ Set up production webhook
7. ✅ Test with small real donation
8. ✅ Monitor and maintain

---

## Additional Resources

- [Stripe Documentation](https://stripe.com/docs)
- [Stripe Testing](https://stripe.com/docs/testing)
- [Stripe Webhooks Guide](https://stripe.com/docs/webhooks)
- [Stripe Elements Documentation](https://stripe.com/docs/stripe-js/react)

---

**Note:** The code is already fully implemented. Follow this plan to configure Stripe and enable donations.
