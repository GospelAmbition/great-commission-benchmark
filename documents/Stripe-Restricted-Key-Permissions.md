# Stripe Restricted Key Permissions Guide

## Required Permissions for This Project

Based on the codebase analysis, here are the specific permissions you need to select when creating a restricted API key:

### Core Permissions

#### Payment Intents
- **Read** - Required for:
  - Retrieving payment intents (`stripe.PaymentIntent.retrieve()`)
  - Listing payment intents (`stripe.PaymentIntent.list()`)
  - Webhook event processing
- **Write** - Required for:
  - Creating payment intents (`stripe.PaymentIntent.create()`)

#### Charges and Refunds
- **Read** - Required for:
  - Listing charges (`stripe.Charge.list()`)
  - Viewing charge details in admin panel
- **Write** - Required for:
  - Creating refunds (`stripe.Refund.create()`)
  - Listing refunds (`stripe.Refund.list()`)

#### Balance
- **Read** - Required for:
  - Retrieving balance (`stripe.Balance.retrieve()`)
  - Viewing available and pending balances in admin panel

#### Balance transaction sources
- **Read** - Required for:
  - Listing balance transactions (`stripe.BalanceTransaction.list()`)
  - Viewing transaction history in admin panel

#### Events
- **Read** - Required for:
  - Processing webhook events
  - Verifying webhook signatures (`stripe.Webhook.construct_event()`)

### Account Management

#### Core → Account (if available)
- **Read** - Required for:
  - Testing connection (`stripe.Account.retrieve()`)
  - Validating API keys in admin panel

---

## Summary: Permissions to Select

When creating your restricted key, select these permissions:

### Core Section:
- ✅ **Payment Intents** - Read, Write
- ✅ **Charges and Refunds** - Read, Write
- ✅ **Balance** - Read
- ✅ **Balance transaction sources** - Read
- ✅ **Events** - Read (for webhook verification)

### Optional but Recommended:
- ✅ **Core → Account** - Read (if available, for connection testing)

---

## What You DON'T Need

You can safely skip these sections (not used in this project):
- ❌ Apple Pay Domains
- ❌ Balance Transfers
- ❌ Confirmation token
- ❌ Customer session
- ❌ Customers (unless you plan to store customer data)
- ❌ Disputes (unless you need to manage disputes)
- ❌ Ephemeral keys
- ❌ Files
- ❌ Funding Instructions
- ❌ Payment Method Domains
- ❌ Payment Methods (handled client-side)
- ❌ Payouts
- ❌ Products
- ❌ Setup Intents
- ❌ Shipping Rates
- ❌ Sources
- ❌ Test clocks
- ❌ Tokens
- ❌ All Billing section permissions
- ❌ All Checkout section permissions
- ❌ All Climate section permissions
- ❌ All Connect section permissions
- ❌ All Financial Connections permissions
- ❌ All Issuing permissions
- ❌ All Orders permissions
- ❌ Payment Links
- ❌ Payment Records
- ❌ Radar
- ❌ Reporting
- ❌ Sigma
- ❌ Stripe Apps
- ❌ Tax
- ❌ Terminal
- ❌ Webhook Endpoints (webhook verification uses Events, not Webhook Endpoints management)

---

## Security Best Practices

1. **Principle of Least Privilege**: Only grant the minimum permissions needed
2. **Test First**: Create the restricted key in test mode first and verify it works
3. **Monitor Usage**: Check Stripe Dashboard logs to ensure no unexpected API calls
4. **Rotate Keys**: Periodically rotate your restricted keys for security
5. **Separate Keys**: Consider using different restricted keys for different environments (test vs live)

---

## Verification

After creating the restricted key, test it by:

1. Using it in your backend `.env` file
2. Testing a payment intent creation
3. Verifying webhook events are received
4. Checking that admin panel features work (balance, transactions, etc.)

If any operation fails with a permission error, you may need to add that specific permission.
