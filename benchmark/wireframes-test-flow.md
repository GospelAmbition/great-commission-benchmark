# Great Commission Benchmark - Test Flow Wireframes

## Overview

This document contains wireframes for the multi-step test execution wizard. Users progress through: Model Selection → Payment → Processing → Results.

**Pages Covered:**
1. Step 1: Model Selection
2. Step 2: Payment Confirmation
3. Step 3: Results Pending (Processing)
4. Step 4: Results Ready

*Reference `wireframes-design-system.md` for component specifications and color palette.*

---

## Flow Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│    ●──────────────●──────────────●──────────────●                          │
│    Select         Payment        Processing      Results                    │
│    Model                                                                    │
│                                                                             │
│    User chooses   User confirms  Test runs in   Results displayed          │
│    model and      payment and    background,    and available              │
│    version        initiates      user can       for review                 │
│                   test run       leave page                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Model Selection

User selects which AI model and version to benchmark.

### Desktop Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] GC Benchmark  Home | Research | Contribute | About | Dashboard [▼ U] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │    ●──────────────○──────────────○──────────────○                   │    │
│  │    Select         Payment        Processing      Results            │    │
│  │    Model                                                            │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  Run a New Benchmark Test                                           │    │
│  │  ═══════════════════════════════════════════════════════════════    │    │
│  │                                                                     │    │
│  │  Select the AI model you want to evaluate against the Great         │    │
│  │  Commission Benchmark.                                              │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌────────────────────────────────────────┐  ┌───────────────────────────┐  │
│  │                                        │  │                           │  │
│  │  Select Provider                       │  │  Test Summary             │  │
│  │  ──────────────────────────────────    │  │  ─────────────────────    │  │
│  │                                        │  │                           │  │
│  │  [Search providers...              ]   │  │  Provider:                │  │
│  │                                        │  │  ─────────────            │  │
│  │  ┌──────────────────────────────────┐  │  │                           │  │
│  │  │ ○ OpenAI                         │  │  │  Model:                   │  │
│  │  │   GPT-4, GPT-4 Turbo, GPT-3.5... │  │  │  ─────────────            │  │
│  │  ├──────────────────────────────────┤  │  │                           │  │
│  │  │ ○ Anthropic                      │  │  │  Version:                 │  │
│  │  │   Claude 3 Opus, Sonnet, Haiku..│  │  │  ─────────────            │  │
│  │  ├──────────────────────────────────┤  │  │                           │  │
│  │  │ ○ Google                         │  │  │  ─────────────────────    │  │
│  │  │   Gemini Ultra, Pro, Nano...     │  │  │                           │  │
│  │  ├──────────────────────────────────┤  │  │  Questions: 600           │  │
│  │  │ ○ Meta                           │  │  │  Categories: 4            │  │
│  │  │   Llama 3 70B, 8B...             │  │  │  Est. Time: 5-10 min      │  │
│  │  ├──────────────────────────────────┤  │  │                           │  │
│  │  │ ○ Mistral AI                     │  │  │  ─────────────────────    │  │
│  │  │   Mistral Large, Medium, Small..│  │  │                           │  │
│  │  ├──────────────────────────────────┤  │  │  Cost: $5.00              │  │
│  │  │ ○ Other / Custom                 │  │  │                           │  │
│  │  │   Bring your own API key         │  │  │                           │  │
│  │  └──────────────────────────────────┘  │  │                           │  │
│  │                                        │  │                           │  │
│  │                                        │  │                           │  │
│  └────────────────────────────────────────┘  └───────────────────────────┘  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │                         [Cancel]  [Continue to Payment →]           │    │
│  │                                                    (disabled)       │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Footer]                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### After Provider Selection (e.g., OpenAI)

```
┌────────────────────────────────────────┐  ┌───────────────────────────┐
│                                        │  │                           │
│  Select Provider                       │  │  Test Summary             │
│  ──────────────────────────────────    │  │  ─────────────────────    │
│                                        │  │                           │
│  ● OpenAI                    [Change]  │  │  Provider:                │
│                                        │  │  OpenAI                   │
│  ──────────────────────────────────    │  │                           │
│                                        │  │  Model:                   │
│  Select Model                          │  │  GPT-4 Turbo              │
│  ──────────────────────────────────    │  │                           │
│                                        │  │  Version:                 │
│  ┌──────────────────────────────────┐  │  │  2024.01                  │
│  │ ○ GPT-4 Turbo              $5.00 │  │  │                           │
│  │   Latest, most capable          │  │  │  ─────────────────────    │
│  ├──────────────────────────────────┤  │  │                           │
│  │ ● GPT-4                    $5.00 │  │  │  Questions: 600           │
│  │   Original GPT-4                │  │  │  Categories: 4            │
│  ├──────────────────────────────────┤  │  │  Est. Time: 5-10 min      │
│  │ ○ GPT-4o                   $5.00 │  │  │                           │
│  │   Optimized multimodal          │  │  │  ─────────────────────    │
│  ├──────────────────────────────────┤  │  │                           │
│  │ ○ GPT-3.5 Turbo            $3.00 │  │  │  Cost: $5.00              │
│  │   Fast and efficient            │  │  │                           │
│  └──────────────────────────────────┘  │  │                           │
│                                        │  │                           │
│  ──────────────────────────────────    │  │                           │
│                                        │  │                           │
│  Select Version                        │  │                           │
│  ──────────────────────────────────    │  │                           │
│                                        │  │                           │
│  ┌──────────────────────────────────┐  │  │                           │
│  │ ● 2024.01.25 (Latest)           │  │  │                           │
│  ├──────────────────────────────────┤  │  │                           │
│  │ ○ 2023.06.13                    │  │  │                           │
│  ├──────────────────────────────────┤  │  │                           │
│  │ ○ 0314 (Legacy)                 │  │  │                           │
│  └──────────────────────────────────┘  │  │                           │
│                                        │  │                           │
└────────────────────────────────────────┘  └───────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                         [Cancel]  [Continue to Payment →]           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Mobile Layout

```
┌─────────────────────────────────────┐
│ [≡]  GC Benchmark              [👤] │
├─────────────────────────────────────┤
│                                     │
│  ●────○────○────○                   │
│  Select  Pay  Process  Results      │
│                                     │
│  Run a New Benchmark Test           │
│  ═════════════════════════════════  │
│                                     │
│  Select Provider                    │
│  ─────────────────────────────────  │
│                                     │
│  ┌─────────────────────────────────┐│
│  │ ○ OpenAI                        ││
│  │   GPT-4, GPT-4 Turbo...         ││
│  ├─────────────────────────────────┤│
│  │ ○ Anthropic                     ││
│  │   Claude 3 Opus, Sonnet...      ││
│  ├─────────────────────────────────┤│
│  │ ○ Google                        ││
│  │   Gemini Ultra, Pro...          ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │ Test Summary                    ││
│  │ ─────────────────────────────── ││
│  │ Questions: 600 | Time: 5-10 min ││
│  │ Cost: $5.00                     ││
│  └─────────────────────────────────┘│
│                                     │
│  [Continue to Payment →]            │
│                                     │
├─────────────────────────────────────┤
│  [Footer]                           │
└─────────────────────────────────────┘
```

### Interaction Notes

- **Progressive disclosure**: Model/version options appear after provider selection
- **Validation**: Continue button disabled until all selections made
- **Previously tested**: Badge shown for models already tested by user

---

## Step 2: Payment Confirmation

User confirms payment and initiates the test.

### Desktop Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] GC Benchmark  Home | Research | Contribute | About | Dashboard [▼ U] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │    ●──────────────●──────────────○──────────────○                   │    │
│  │    Select         Payment        Processing      Results            │    │
│  │    Model          (current)                                         │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  Confirm Your Test                                                  │    │
│  │  ═══════════════════════════════════════════════════════════════    │    │
│  │                                                                     │    │
│  │  Review your selection and confirm payment to start the benchmark.  │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌────────────────────────────────────────┐  ┌───────────────────────────┐  │
│  │                                        │  │                           │  │
│  │  Test Configuration                    │  │  Order Summary            │  │
│  │  ──────────────────────────────────    │  │  ─────────────────────    │  │
│  │                                        │  │                           │  │
│  │  ┌──────────────────────────────────┐  │  │  Model Cost        $5.00  │  │
│  │  │                                  │  │  │  Platform Cost    $20.00  │  │
│  │  │  Provider:  OpenAI               │  │  │  Donation Round Up $5.00  │  │
│  │  │  Model:     GPT-4 Turbo          │  │  │  ─────────────────────    │  │
│  │  │  Version:   2024.01.25           │  │  │  Total:           $30.00  │  │
│  │  │                                  │  │  │  ─────────────────────    │  │
│  │  │                      [Edit →]    │  │  │                           │  │
│  │  │                                  │  │  │  Pay with:                │  │
│  │  └──────────────────────────────────┘  │  │                           │  │
│  │                                        │  │  💳 Card ending ****4242  │  │
│  │  ┌──────────────────────────────────┐  │  │     [Change]              │  │
│  │  │                                  │  │  │                           │  │
│  │  │  Test Details                    │  │  │  ─────────────────────    │  │
│  │  │  ────────────────────────────    │  │  │                           │  │
│  │  │                                  │  │  │  Secure checkout via      │  │
│  │  │  • 600 benchmark questions       │  │  │  Stripe                   │  │
│  │  │  • 4 evaluation categories       │  │  │                           │  │
│  │  │  • Scripture Knowledge           │  │  │                           │  │
│  │  │  • Theological Accuracy          │  │  │                           │  │
│  │  │  • Ethical Reasoning             │  │  │                           │  │
│  │  │  • Apologetics                   │  │  │                           │  │
│  │  │  • Estimated time: 5-10 minutes  │  │  │                           │  │
│  │  │                                  │  │  │                           │  │
│  │  └──────────────────────────────────┘  │  │                           │  │
│  │                                        │  │                           │  │
│  │  ┌──────────────────────────────────┐  │  │                           │  │
│  │  │                                  │  │  │                           │  │
│  │  │  ⚠️ Important Notes              │  │  │                           │  │
│  │  │  ────────────────────────────    │  │  │                           │  │
│  │  │                                  │  │  │                           │  │
│  │  │  • Test runs cannot be cancelled │  │  │                           │  │
│  │  │  • Results typically ready in    │  │  │                           │  │
│  │  │    5-10 minutes                  │  │  │                           │  │
│  │  │  • You can leave this page and   │  │  │                           │  │
│  │  │    return when results are ready │  │  │                           │  │
│  │  │  • Results published to the      │  │  │                           │  │
│  │  │    leaderboard automatically     │  │  │                           │  │
│  │  │  • Auto-retry on errors; refund  │  │  │                           │  │
│  │  │    option if unrecoverable       │  │  │                           │  │
│  │  │                                  │  │  │                           │  │
│  │  └──────────────────────────────────┘  │  │                           │  │
│  │                                        │  │                           │  │
│  │  ┌──────────────────────────────────┐  │  │                           │  │
│  │  │                                  │  │  │                           │  │
│  │  │  🏆 Sponsor Credit (optional)    │  │  │                           │  │
│  │  │  ────────────────────────────    │  │  │                           │  │
│  │  │                                  │  │  │                           │  │
│  │  │  Display a name with this test   │  │  │                           │  │
│  │  │  to show you sponsored it:       │  │  │                           │  │
│  │  │                                  │  │  │                           │  │
│  │  │  ┌────────────────────────────┐  │  │  │                           │  │
│  │  │  │ John Smith                 │  │  │  │                           │  │
│  │  │  └────────────────────────────┘  │  │  │                           │  │
│  │  │                                  │  │  │                           │  │
│  │  │  ℹ️ Use your name, organization, │  │  │                           │  │
│  │  │     or a nickname/alias          │  │  │                           │  │
│  │  │                                  │  │  │                           │  │
│  │  └──────────────────────────────────┘  │  │                           │  │
│  │                                        │  │                           │  │
│  └────────────────────────────────────────┘  └───────────────────────────┘  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  [✓] I understand this test cannot be cancelled once started        │    │
│  │                                                                     │    │
│  │                     [← Back to Selection]  [Pay $30.00 & Start Test]│    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Footer]                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### First-Time User (No Saved Card)

```
┌───────────────────────────┐
│                           │
│  Order Summary            │
│  ─────────────────────    │
│                           │
│  Benchmark Test  $30.00   │
│                           │
│  ─────────────────────    │
│  Total:          $30.00   │
│                           │
│  ─────────────────────    │
│                           │
│  Pay with:                │
│                           │
│  [Enter Card Details →]   │
│                           │
│  ─────────────────────    │
│                           │
│  Secure checkout via      │
│  Stripe                   │
│                           │
└───────────────────────────┘
```

### Interaction Notes

- **Confirmation checkbox**: Required before "Pay" button is enabled
- **Edit flow**: "Edit" returns to Step 1 with selections preserved
- **Saved cards**: Returning users see saved payment method, can change
- **Stripe checkout**: Secure payment handled via Stripe
- **Refund policy**: System auto-retries on errors; if unrecoverable after 3 attempts, user chooses between admin completion or full refund
- **Sponsor credit**: Optional field for users to display a name/alias with their test (appears on results page, share previews, and leaderboard)

---

## Step 3: Results Pending (Processing)

Test is running in the background. User can leave and return.

### Desktop Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] GC Benchmark  Home | Research | Contribute | About | Dashboard [▼ U] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │    ●──────────────●──────────────●──────────────○                   │    │
│  │    Select         Payment        Processing      Results            │    │
│  │    Model                         (current)                          │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │                         ┌─────────────┐                             │    │
│  │                         │             │                             │    │
│  │                         │  [Spinner]  │                             │    │
│  │                         │             │                             │    │
│  │                         └─────────────┘                             │    │
│  │                                                                     │    │
│  │                    Your Test is Running                             │    │
│  │                    ════════════════════                             │    │
│  │                                                                     │    │
│  │           GPT-4 Turbo (OpenAI) · v2024.01.25                        │    │
│  │                                                                     │    │
│  │  ┌───────────────────────────────────────────────────────────────┐  │    │
│  │  │                                                               │  │    │
│  │  │  [████████████████████████████████░░░░░░░░░░░░░░░░░░] 65%     │  │    │
│  │  │                                                               │  │    │
│  │  │  390 of 600 questions completed                               │  │    │
│  │  │                                                               │  │    │
│  │  └───────────────────────────────────────────────────────────────┘  │    │
│  │                                                                     │    │
│  │                                                                     │    │
│  │       Started: 3 minutes ago                                        │    │
│  │       Estimated completion: ~2-3 more minutes                       │    │
│  │                                                                     │    │
│  │                                                                     │    │
│  │  ┌───────────────────────────────────────────────────────────────┐  │    │
│  │  │                                                               │  │    │
│  │  │  ℹ️  You can safely leave this page                           │  │    │
│  │  │                                                               │  │    │
│  │  │  We'll send you an email when your results are ready.         │  │    │
│  │  │  You can also check your Dashboard for updates.               │  │    │
│  │  │                                                               │  │    │
│  │  └───────────────────────────────────────────────────────────────┘  │    │
│  │                                                                     │    │
│  │                                                                     │    │
│  │                [Go to Dashboard]    [Stay on This Page]             │    │
│  │                                                                     │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  Processing Log                                         [Collapse]  │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  ┌───────────────────────────────────────────────────────────────┐  │    │
│  │  │ 14:32:15  Test initiated                                     │  │    │
│  │  │ 14:32:16  Connected to OpenAI API                            │  │    │
│  │  │ 14:32:17  Starting Scripture Knowledge category (150 q)      │  │    │
│  │  │ 14:33:45  Scripture Knowledge complete                       │  │    │
│  │  │ 14:33:46  Starting Theological Accuracy category (150 q)     │  │    │
│  │  │ 14:35:12  Theological Accuracy complete                      │  │    │
│  │  │ 14:35:13  Starting Ethical Reasoning category (150 q)        │  │    │
│  │  │ 14:35:14  Processing question 42 of 150...                   │  │    │
│  │  │ █                                                            │  │    │
│  │  └───────────────────────────────────────────────────────────────┘  │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Footer]                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Mobile Layout

```
┌─────────────────────────────────────┐
│ [≡]  GC Benchmark              [👤] │
├─────────────────────────────────────┤
│                                     │
│  ●────●────●────○                   │
│       Processing                    │
│                                     │
│         ┌───────────┐               │
│         │ [Spinner] │               │
│         └───────────┘               │
│                                     │
│    Your Test is Running             │
│    ═══════════════════              │
│                                     │
│    GPT-4 Turbo (OpenAI)             │
│    v2024.01.25                      │
│                                     │
│  ┌─────────────────────────────────┐│
│  │ [██████████████░░░░░░░░] 65%    ││
│  │ 390 of 600 questions            ││
│  └─────────────────────────────────┘│
│                                     │
│  Started: 3 min ago                 │
│  Est. completion: ~2-3 min          │
│                                     │
│  ┌─────────────────────────────────┐│
│  │ ℹ️ You can leave this page.     ││
│  │ We'll email you when ready.     ││
│  └─────────────────────────────────┘│
│                                     │
│  [Go to Dashboard]                  │
│                                     │
├─────────────────────────────────────┤
│  [Footer]                           │
└─────────────────────────────────────┘
```

### Automatic Recovery (Transparent to User)

When errors occur during test execution, the system automatically handles recovery without user intervention:

```
Test Recovery System (Background Process):
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  On Error (API timeout, rate limit, transient failure):             │
│  ─────────────────────────────────────────────────────              │
│                                                                     │
│  1. Checkpoint current progress (questions completed, responses)    │
│  2. Wait with exponential backoff (30s → 60s → 120s)                │
│  3. Resume from checkpoint (do NOT re-run completed questions)      │
│  4. Repeat up to 3 attempts                                         │
│                                                                     │
│  Example: Test at 65% (390/600 questions)                           │
│  • Error occurs at question 391                                     │
│  • System waits, then resumes from question 391                     │
│  • User sees uninterrupted progress (may notice brief pause)        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**What users see during recovery:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                         ┌─────────────┐                             │
│                         │             │                             │
│                         │  [Spinner]  │                             │
│                         │             │                             │
│                         └─────────────┘                             │
│                                                                     │
│                    Your Test is Running                             │
│                    ════════════════════                             │
│                                                                     │
│           GPT-4 Turbo (OpenAI) · v2024.01.25                        │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                                                               │  │
│  │  [████████████████████████████████░░░░░░░░░░░░░░░░░░] 65%     │  │
│  │                                                               │  │
│  │  390 of 600 questions completed                               │  │
│  │                                                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  ⏳ Briefly paused — reconnecting to API...                   │  │
│  │     The test will automatically resume. No action needed.     │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Hard Failure State (After 3 Retry Attempts)

Only after 3 failed retry attempts does the system escalate and notify the user:

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                         ┌─────────────┐                             │
│                         │             │                             │
│                         │     ⚠️      │                             │
│                         │             │                             │
│                         └─────────────┘                             │
│                                                                     │
│                    Test Requires Attention                          │
│                    ═══════════════════════                          │
│                                                                     │
│           GPT-4 Turbo (OpenAI) · v2024.01.25                        │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                                                               │  │
│  │  The test encountered persistent errors and could not         │  │
│  │  complete automatically.                                      │  │
│  │                                                               │  │
│  │  Progress: 65% (390 of 600 questions completed)               │  │
│  │  Error: API rate limit exceeded after 3 retry attempts        │  │
│  │                                                               │  │
│  │  ✓ An administrator has been notified                         │  │
│  │                                                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                                                               │  │
│  │  What would you like to do?                                   │  │
│  │  ───────────────────────────────────────────────────────────  │  │
│  │                                                               │  │
│  │  ○ Wait for administrator to complete the test                │  │
│  │    Your progress is saved. An admin will manually complete    │  │
│  │    the remaining 35% and notify you when results are ready.   │  │
│  │    Typical resolution time: 24-48 hours                       │  │
│  │                                                               │  │
│  │  ○ Request a full refund now                                  │  │
│  │    Receive a full refund immediately. Your partial results    │  │
│  │    will not be published.                                     │  │
│  │                                                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│                                                                     │
│                              [Confirm Choice]                       │
│                                                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Admin Completion Pending State

When user chooses to wait for admin completion:

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                         ┌─────────────┐                             │
│                         │             │                             │
│                         │     🔧      │                             │
│                         │             │                             │
│                         └─────────────┘                             │
│                                                                     │
│                 Awaiting Admin Completion                           │
│                 ═════════════════════════                           │
│                                                                     │
│           GPT-4 Turbo (OpenAI) · v2024.01.25                        │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                                                               │  │
│  │  [████████████████████████████████░░░░░░░░░░░░░░░░░░] 65%     │  │
│  │                                                               │  │
│  │  390 of 600 questions completed                               │  │
│  │  Awaiting admin intervention for remaining 210 questions      │  │
│  │                                                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                                                               │  │
│  │  ℹ️  Your test is in the admin queue                          │  │
│  │                                                               │  │
│  │  An administrator will manually complete the remaining        │  │
│  │  portion of your test. We'll email you when results are       │  │
│  │  ready.                                                       │  │
│  │                                                               │  │
│  │  Submitted: December 15, 2024 at 2:32 PM                      │  │
│  │  Typical resolution: 24-48 hours                              │  │
│  │                                                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│                                                                     │
│       [Go to Dashboard]    [Request Refund Instead]                 │
│                                                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Interaction Notes

- **Auto-refresh**: Page polls for status every 10 seconds
- **Progress updates**: Real-time progress bar and question count
- **Processing log**: Optional expanded view of detailed progress
- **Email notification**: Sent when test completes (if enabled in settings)
- **Browser notification**: Optional push notification when complete
- **Checkpoint system**: Progress saved after each question to enable seamless recovery
- **Automatic retry**: System retries up to 3 times with exponential backoff before escalating
- **Admin escalation**: After 3 failures, admin is notified and user chooses refund or wait

---

## Step 4: Results Ready

Test completed, showing summary with link to full results.

### Desktop Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] GC Benchmark  Home | Research | Contribute | About | Dashboard [▼ U] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │    ●──────────────●──────────────●──────────────●                   │    │
│  │    Select         Payment        Processing      Results            │    │
│  │    Model                                         (complete)         │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │                         ┌─────────────┐                             │    │
│  │                         │             │                             │    │
│  │                         │     ✓       │                             │    │
│  │                         │             │                             │    │
│  │                         └─────────────┘                             │    │
│  │                                                                     │    │
│  │                    Test Complete!                                   │    │
│  │                    ══════════════                                   │    │
│  │                                                                     │    │
│  │           GPT-4 Turbo (OpenAI) · v2024.01.25                        │    │
│  │                  Sponsored by John Smith                            │    │
│  │                                                                     │    │
│  │                         ┌──────────────┐                            │    │
│  │                         │              │                            │    │
│  │                         │    92.3      │                            │    │
│  │                         │              │                            │    │
│  │                         │  Overall     │                            │    │
│  │                         │  Score       │                            │    │
│  │                         │              │                            │    │
│  │                         └──────────────┘                            │    │
│  │                                                                     │    │
│  │                   Rank: #1 on Leaderboard                           │    │
│  │                                                                     │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌──────────────────────────────────┐  ┌──────────────────────────────┐     │
│  │                                  │  │                              │     │
│  │  Category Breakdown              │  │  Published!                  │     │
│  │  ────────────────────────────    │  │  ────────────────────────    │     │
│  │                                  │  │                              │     │
│  │  Scripture Knowledge             │  │  ✓ Your results are now      │     │
│  │  ████████████████████████░░ 94%  │  │    live on the leaderboard   │     │
│  │                                  │  │                              │     │
│  │  Theological Accuracy            │  │  Results from platform tests │     │
│  │  ████████████████████░░░░░░ 88%  │  │  are published automatically │     │
│  │                                  │  │  upon completion.            │     │
│  │  Ethical Reasoning               │  │                              │     │
│  │  ███████████████████████░░░ 93%  │  │  Share your results now, or  │     │
│  │                                  │  │  run another test.           │     │
│  │  Apologetics                     │  │                              │     │
│  │  █████████████████░░░░░░░░░ 78%  │  │                              │     │
│  │                                  │  │                              │     │
│  │                                  │  │                              │     │
│  │                                  │  │                              │     │
│  └──────────────────────────────────┘  └──────────────────────────────┘     │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │            [View Full Results]  [Run Another Test]  [Share Results] │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Footer]                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Mobile Layout

```
┌─────────────────────────────────────┐
│ [≡]  GC Benchmark              [👤] │
├─────────────────────────────────────┤
│                                     │
│  ●────●────●────●                   │
│                 Results             │
│                                     │
│         ┌───────────┐               │
│         │     ✓     │               │
│         └───────────┘               │
│                                     │
│      Test Complete!                 │
│      ═══════════════                │
│                                     │
│      GPT-4 Turbo (OpenAI)           │
│      Sponsored by John Smith        │
│                                     │
│         ┌──────────────┐            │
│         │    92.3      │            │
│         │   Overall    │            │
│         └──────────────┘            │
│                                     │
│      Rank: #1 on Leaderboard        │
│                                     │
│  ┌─────────────────────────────────┐│
│  │ Category Breakdown              ││
│  │ ─────────────────────────────── ││
│  │                                 ││
│  │ Scripture          94%         ││
│  │ ████████████████████░░         ││
│  │                                 ││
│  │ Theology           88%         ││
│  │ ██████████████████░░░░         ││
│  │                                 ││
│  │ Ethics             93%         ││
│  │ ███████████████████░░░         ││
│  │                                 ││
│  │ Apologetics        78%         ││
│  │ █████████████████░░░░░         ││
│  └─────────────────────────────────┘│
│                                     │
│  [View Full Results]                │
│  [Run Another Test]                 │
│                                     │
├─────────────────────────────────────┤
│  [Footer]                           │
└─────────────────────────────────────┘
```

### Share Modal

```
┌───────────────────────────────────────────────────────────────┐
│                                                           [×] │
│                                                               │
│   Share Your Results                                          │
│   ═══════════════════════════════════════════════════════     │
│                                                               │
│   GPT-4 Turbo scored 92.3 on the Great Commission Benchmark!  │
│   Sponsored by John Smith                                     │
│                                                               │
│   ┌───────────────────────────────────────────────────────┐   │
│   │                                                       │   │
│   │  https://gcbenchmark.org/results/abc123               │   │
│   │                                              [Copy]   │   │
│   │                                                       │   │
│   └───────────────────────────────────────────────────────┘   │
│                                                               │
│   Share on:                                                   │
│                                                               │
│   [Twitter/X]  [LinkedIn]  [Facebook]  [Email]                │
│                                                               │
│   ✓ Results are live and ready to share                       │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Share Modal (No Sponsor Credit)

When user did not enter a sponsor name:

```
┌───────────────────────────────────────────────────────────────┐
│                                                           [×] │
│                                                               │
│   Share Your Results                                          │
│   ═══════════════════════════════════════════════════════     │
│                                                               │
│   GPT-4 Turbo scored 92.3 on the Great Commission Benchmark!  │
│                                                               │
│   ┌───────────────────────────────────────────────────────┐   │
│   │                                                       │   │
│   │  https://gcbenchmark.org/results/abc123               │   │
│   │                                              [Copy]   │   │
│   │                                                       │   │
│   └───────────────────────────────────────────────────────┘   │
│                                                               │
│   Share on:                                                   │
│                                                               │
│   [Twitter/X]  [LinkedIn]  [Facebook]  [Email]                │
│                                                               │
│   ✓ Results are live and ready to share                       │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Interaction Notes

- **Automatic transition**: Page auto-advances from Processing when complete
- **Score celebration**: Subtle animation when score is revealed
- **Rank comparison**: Shows current leaderboard position (live, not pending)
- **Share preview**: Social share includes preview card with score and sponsor credit (if provided)
- **Sponsor attribution**: "Sponsored by [Name]" shown on results page and in share preview when user provided a sponsor name
- **Auto-publish**: Platform-run tests are immediately published to the leaderboard (no moderation gate)
- **Post-publish review**: Moderators can retroactively review and reject if issues are found

---

## URL Structure

| Page | URL Pattern | Example |
|------|-------------|---------|
| Model Selection | `/test/new` | `/test/new` |
| Payment Confirmation | `/test/new/confirm` | `/test/new/confirm` |
| Results Pending | `/test/:runId/processing` | `/test/abc123/processing` |
| Results Ready | `/test/:runId/results` | `/test/abc123/results` |

---

## State Management

### Platform-Run Tests (Auto-Publish)

Tests run through the platform are automatically published to the leaderboard upon completion. No moderator approval gate is required. Moderators can retroactively review and reject published results if issues are identified.

```
Platform Test States:
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  draft → pending_payment → processing → published (auto, on leaderboard)    │
│                    │              │           │                              │
│                    │              │           └──→ rejected (post-publish    │
│                    │              │                 moderator review)        │
│                    │              │                                          │
│                    │              └──→ retrying (auto-recovery in progress)  │
│                    │                        │                                │
│                    │                        └──→ awaiting_admin (after 3     │
│                    │                                  failed retries)        │
│                    │                                      │                  │
│                    │                        ┌─────────────┴─────────────┐    │
│                    │                        ▼                           ▼    │
│                    │               admin_completing              refunded    │
│                    │                        │                                │
│                    │                        └──→ published                   │
│                    │                                                         │
│                    └──────────────────────────────────────────→ refunded     │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

State Definitions (Platform Tests):
- draft: User selecting model (not persisted)
- pending_payment: Awaiting payment confirmation
- processing: Test actively running
- retrying: Automatic recovery in progress (transparent to user)
- awaiting_admin: After 3 failed retry attempts, awaiting user decision
- admin_completing: User chose to wait; admin manually completing remaining questions
- published: Test finished and automatically published to leaderboard
- rejected: Moderator retroactively rejected published result (with reason)
- refunded: User requested refund for failed test
```

### CLI-Submitted Tests (Requires Verification)

Tests run externally via the CLI and submitted with results require moderator verification before appearing on the leaderboard. This is because the platform cannot verify the test was run correctly.

```
CLI Submission States:
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  submitted → pending_payment → pending_verification → verified → published   │
│                    │                    │                                    │
│                    │                    └──→ rejected (verification failed)  │
│                    │                                                         │
│                    └──────────────────────────────────────────→ refunded     │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

State Definitions (CLI Submissions):
- submitted: Results uploaded via CLI
- pending_payment: Awaiting $20 platform fee payment
- pending_verification: Awaiting moderator verification
- verified: Moderator verified reproducibility/validity
- published: Added to leaderboard
- rejected: Verification failed (with reason)
- refunded: User requested refund before verification
```

### Why the Difference?

| Aspect | Platform Tests | CLI Submissions |
|--------|---------------|-----------------|
| **Execution** | Platform runs test directly | User runs test locally |
| **Trust Level** | High (platform controls execution) | Requires verification |
| **Publishing** | Automatic on completion | After moderator verification |
| **Cost** | Model API cost + platform fee ($5) | $20 platform fee (covers verification) |
| **Verification** | Not required (post-publish review only) | Required before publishing |
| **Use Case** | Individual testers | Organizations with custom/local models |

---

*Next: See `wireframes-moderator-pages.md` for moderator dashboard and review interfaces*
