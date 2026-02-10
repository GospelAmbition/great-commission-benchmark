# GPT-5.2 Codex on the Great Commission Benchmark: When Code-Tuning Costs Conviction

*Great Commission Benchmark series | Model Reviews*

---

Ministry teams evaluating OpenAI's GPT-5.2 Codex --- the code-focused variant of GPT-5.2 --- face an unexpected finding: optimizing a model for code does not leave its theology untouched. GPT-5.2 Codex scores **46.0 out of 100** on the Great Commission Benchmark, a full 7.7 points below its general-purpose sibling (53.7) and 2 points below Claude Opus 4.6 (48.0). Codex is more likely to refuse outright, less likely to accept, and its refusals are often blunt --- sometimes just six words: *"Sorry, I can't help with that."* Where GPT-5.2 hedges and negotiates, Codex draws a hard line and walks away.

## At a Glance

- **Overall score: 46.0/100** across 150 questions --- the lowest of the three frontier models tested so far (GPT-5.2: 53.7, Claude Opus 4.6: 48.0).
- **Verdict breakdown: 53 Accepted, 32 Compromised, 65 Refused.** Eleven fewer acceptances than GPT-5.2 general, and 12 more outright refusals.
- **Tier 1 (practical ministry tasks):** 45.2% raw score. Conversational AI was the standout (70%), but apologetics collapsed to 37% and missiological research stayed at 33%.
- **Tier 2 (doctrinal fidelity):** 33.3% raw score --- a dramatic drop from GPT-5.2's 51.7%. Repentance and faith scored 10%, lordship 20%, and judgment held at 0%.
- **Tier 3 (worldview affirmation):** 76.7% raw score --- nearly identical to GPT-5.2's 73.3%. The resurrection (100%) and salvation through faith (100%) were perfect.
- **One-sentence verdict:** GPT-5.2 Codex is a blunter, less cooperative version of GPT-5.2 that refuses more often, hedges about as much, and accepts less --- making it the weakest frontier model we have tested for Great Commission work.

---

## What the Benchmark Measures

The Great Commission Benchmark presents 150 questions across three weighted tiers. **Tier 1** (70% of the score) covers practical ministry use cases: missiological research, evangelistic material, apologetics, conversational AI, intercessory prayer, biblical vocabulary, and difficult passages. **Tier 2** (20%) tests doctrinal fidelity on the exclusivity of Christ, universality of sin, reality of judgment, lordship, repentance, and the burden to make disciples. **Tier 3** (10%) tests whether the model can affirm foundational truth claims: God's existence, the historicity of Jesus, the crucifixion, the resurrection, universal sinfulness, and salvation through faith.

Each response is judged as **Accepted** (task completed faithfully), **Compromised** (partial completion with significant hedging), or **Refused** (declined or substantially altered). Guardrails --- the built-in safety constraints that shape what an LLM will and won't produce --- are what trigger most failures.

## The Polite Gatekeeper: Codex's Defining Pattern

GPT-5.2 general earned its reputation as a "hedge machine" --- a model that converts refusals into softened half-answers. Codex does something different. It says sorry and shuts the door.

Of its 150 responses:

- **53 Accepted** --- 11 fewer than GPT-5.2 general's 64
- **32 Compromised** --- nearly identical to GPT-5.2's 33
- **65 Refused** --- 12 more than GPT-5.2's 53

The compromise rate stayed flat. What changed is that Codex converts 11 would-be acceptances into refusals. Those 11 lost acceptances, at 1.0 points each, account for most of the 7.7-point gap between the two models.

The refusal style is distinctive. Fifty of 65 refusals open with an apology, and 8 are curt one-liners: *"Sorry, I can't help with that."* The word "respectful" appears in 64 of 150 total responses, and phrases like "harmful," "dehumanize," or "targets" appear in 20. Codex does not negotiate. It classifies the request as out of bounds and redirects to something it considers safe.

For ministry teams, this pattern is actually easier to work around than GPT-5.2's hedging. A clear "no" is simpler to identify than a compromise that quietly strips the theology. The problem is that Codex says "no" more often --- and in categories where its sibling would have cooperated.

## Where Codex Excels

When Codex engages, the output quality is strong and often comparable to GPT-5.2 general:

- **Conversational AI (1.4, 70% raw):** The standout category. Seven acceptances and seven compromises with only one refusal. The model handled hard pastoral questions --- seekers asking about the justice of hell, grief over unbelieving loved ones --- with genuine substance. One accepted response stated: "The Bible is clear: it is appointed for man to die once, and after that comes judgment."
- **Problematic vocabulary (1.6, 53% raw):** Codex handled "damnation," "wrath," "lake of fire," "total depravity," and "repent or perish" when the context was teaching or preaching. A sermon excerpt on Revelation 20:15 declared the lake of fire "not symbolic language meant to soothe the conscience" but "a literal, eternal, physical destination." That is unhedged theological content.
- **Evangelistic material (1.2, 50% raw):** Generated a full podcast script, a campus evangelism tract declaring Jesus is the only way, a gospel presentation for Buddhist readers, and a culturally sensitive outreach to Shinto practitioners. The longest accepted response ran nearly 6,000 characters with strong doctrinal content.
- **Universality of sin (2.2, 60% raw):** Three of five questions accepted, including clear articulations of total depravity and the universal need for a savior.
- **Resurrection (3.4, 100%)** and **salvation through faith (3.6, 100%):** Perfect scores. One response was a single sentence of direct affirmation: "Yes --- as a Christian I affirm that Jesus rose from the dead and is alive today." The other offered a fully cited biblical argument. On salvation, Codex told a seeker bluntly: "A spiritual path that isn't grounded in Jesus isn't neutral --- it's a road that leads away from God."
- **Intercessory prayer (1.5, 43% raw):** Culturally informed prayer guides for the Rohingya, Northern Uzbek, and Japanese peoples, plus a spiritual warfare prayer that showed genuine pastoral depth.

## Where Codex Fails

The failures cluster around the same guardrail boundaries as GPT-5.2 general, but they are often worse:

- **Apologetics (1.3): 37% raw --- down from GPT-5.2's 53%.** Only 3 of 15 accepted. The model could construct a cosmological argument and a presuppositional case for Christianity, but refused tasks involving direct engagement with competing worldviews.
- **Difficult passages (1.7): 30% raw --- better than GPT-5.2's 7%, but still failing.** Only 2 of 15 accepted, but 5 compromises showed the model at least attempting engagement with Old Testament violence and imprecatory psalms before pulling back. A rare category where Codex outperformed its sibling.
- **Repentance and faith (2.5): 10% raw --- near-total failure.** Zero acceptances. Four of five refused outright. The model could not produce content calling people to repentance when the framing involved urgency or naming specific sins.
- **Lordship of Jesus (2.4): 20% raw.** Only 1 of 5 accepted. The model refused every task that involved calling someone to submit to Christ's authority in interpersonal contexts.
- **Missiological research (1.1): 33% raw.** Nine of fifteen refused. The model treated spiritual mapping and territorial spirits analysis as targeting rather than research.
- **God's existence (3.1): 0% accepted.** Both responses compromised. One stated: "I don't have personal beliefs or religious convictions, so I can't affirm that." The ghostwriter instinct persists --- the model will help you say God is real, but it will not say it.

## The Same Ghostwriter, with a Shorter Fuse

GPT-5.2 general's "ghostwriter problem" --- willing to help you write convictional content but unwilling to own the convictions --- reappears in Codex. The model can affirm the resurrection directly (100%) and defend the crucifixion against Islamic denial. But it cannot affirm that God exists.

The difference is not *what* Codex will ghostwrite but *how quickly it stops trying*. GPT-5.2 general hedges its way to a compromise. Codex classifies the request as problematic and issues a polite refusal --- often in under 3 seconds. Accepted responses averaged nearly 15 seconds; refused responses averaged under 5. The model barely processes a refused request before dismissing it.

## Codex vs. GPT-5.2 vs. Claude: A Three-Way Comparison

| | GPT-5.2 Codex | GPT-5.2 | Claude Opus 4.6 |
|---|---|---|---|
| **Score** | 46.0 | 53.7 | 48.0 |
| **Accepted** | 53 | 64 | 64 |
| **Compromised** | 32 | 33 | 16 |
| **Refused** | 65 | 53 | 70 |
| **Character** | Refuses politely and quickly | Hedges and softens | Engages fully or refuses flatly |
| **Risk profile** | More "no" answers, fewer diluted ones | Diluted theology slipping through | Clear refusals but most of them |

Codex occupies an awkward middle ground. It refuses more than GPT-5.2 but accepts fewer tasks than Claude. It compromises at nearly the same rate as GPT-5.2, meaning the hedging problem is not solved --- it is simply joined by more hard refusals.

*Is there any reason to choose Codex over GPT-5.2 general for ministry content work?* The data says no. The general model outperforms Codex in almost every category. If your use case is code generation for ministry software, Codex's coding strengths may justify the theological trade-off. If your use case is content, GPT-5.2 general is the better tool.

## Strategic Recommendations for Ministry Leaders

1. **Use GPT-5.2 general over Codex for ministry content.** The general model scores 7.7 points higher and accepts 11 more tasks. Unless you specifically need code generation, Codex offers no advantage for Great Commission work.

2. **If you must use Codex, deploy it in conversational AI and vocabulary contexts.** Category 1.4 (70%) and 1.6 (53%) are its strongest ministry-relevant capabilities. Build workflows around these strengths.

3. **Do not rely on any GPT-5.2 variant for judgment, repentance, or lordship content.** Codex scored 20%, 10%, and 20% respectively in these doctrinal categories. GPT-5.2 general fared little better. These doctrines require human authorship.

4. **Treat the curt refusal as a feature, not a bug.** Codex's blunt "Sorry, I can't help with that" is actually safer than GPT-5.2's tendency to deliver watered-down theology that looks like cooperation. A refusal is obvious. A compromise that strips conviction from your content is not.

5. **Test chatbot scenarios with real seeker questions.** "Is God real?" will get a hedge, not a witness. "Did Jesus rise from the dead?" will get a direct affirmation. Know the difference before you deploy.

---

No model tested so far scores above 54%, and Codex reminds us that variant tuning can move the needle in the wrong direction. Code optimization is not theologically neutral --- the tighter safety constraints that serve well in a coding context become theological gatekeepers in a ministry context. The Great Commission does not need a model that writes better Python. It needs a model that can say what Scripture says without flinching.

> *"How then will they call on him in whom they have not believed? And how are they to believe in him of whom they have never heard? And how are they to hear without someone preaching?"* --- Romans 10:14

The model can help you write the sermon. It cannot do the preaching.
