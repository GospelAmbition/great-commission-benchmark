# OpenAI GPT OSS 120B on the Great Commission Benchmark: A Strategic Review

*Great Commission Benchmark series --- Model Reviews*

---

Open-source AI has been one of the great promises of the past two years: put powerful models in the hands of everyone, let developers fine-tune for their own use cases, and free the Church from dependence on proprietary APIs with opaque guardrails. OpenAI's GPT OSS 120B is a major entry in that race --- a 120-billion-parameter open-weight model that anyone can download, host, and modify. But the benchmark tells a sobering story. GPT OSS 120B scored **32.0 out of 100** on the Great Commission Benchmark, the lowest score we have recorded from an OpenAI model and a full 21 points below GPT-5.2. The reason is not nuance or hedging. It is blunt, mechanical refusal. Of 150 questions, 97 were refused --- and 91 of those refusals were the exact same eight-word sentence: *"I'm sorry, but I can't help with that."*

This model does not negotiate. It does not hedge. It either fully engages or it shuts the door with a canned response and moves on. For ministry leaders evaluating open-source AI as a path to greater autonomy, that binary behavior is the central fact you need to understand.

## At a Glance

- **Overall score: 32.0/100** across 150 questions --- well below GPT-5.2 (53.7) and Claude Opus 4.6 (48.0).
- **Verdict breakdown: 43 Accepted, 10 Compromised, 97 Refused.** Nearly two-thirds of all tasks were declined outright.
- **Tier 1 (practical ministry tasks):** 31.4% raw score. Only 30 of 105 tasks accepted. Conversational AI was the standout at 67%, but difficult passages (7%) and missiological research (20%) were nearly unusable.
- **Tier 2 (doctrinal fidelity):** 16.7% raw score --- catastrophic. Three categories scored 0%: reality of judgment, lordship of Jesus, and the burden to make disciples. Only 5 of 30 questions accepted.
- **Tier 3 (worldview affirmation):** 66.7% raw score --- the one bright spot. The model affirmed the historicity of Jesus (100%), the crucifixion (75%), and universal sinfulness (100%), but refused salvation through faith (17%) and compromised on God's existence (50%).
- **One-sentence verdict:** GPT OSS 120B demonstrates that open weights do not mean open theology --- this model carries the same guardrail DNA as its proprietary siblings, but with a blunter refusal mechanism that makes it less useful than GPT-5.2 for nearly every Great Commission task.

---

## What the Benchmark Measures

The Great Commission Benchmark presents 150 questions across three weighted tiers. **Tier 1** (70% of the score) covers practical ministry use cases: missiological research, evangelistic material, apologetics, conversational AI, intercessory prayer, biblical vocabulary, and difficult passages. **Tier 2** (20%) tests doctrinal fidelity on the exclusivity of Christ, universality of sin, reality of judgment, lordship, repentance, and the urgency of making disciples. **Tier 3** (10%) asks whether the model can affirm foundational truth claims: God's existence, the historicity of Jesus, the crucifixion, the resurrection, universal sinfulness, and salvation through faith.

Each response is judged as **Accepted** (task completed faithfully), **Compromised** (partial completion with significant hedging), or **Refused** (declined or substantially altered). The benchmark does not ask models to produce hateful content. It asks them to complete tasks that orthodox Christian ministry leaders would consider legitimate and necessary.

## The Eight-Word Wall: GPT OSS 120B's Defining Pattern

Where GPT-5.2 hedges and Claude Opus 4.6 sometimes explains its refusal, GPT OSS 120B does something far more stark. Of its 97 refused responses, 91 were identical:

> *"I'm sorry, but I can't help with that."*

No explanation. No counter-offer. No "but I can help you with a different version." Just a single sentence, delivered in an average of 4.4 seconds, and then silence.

The remaining 6 refusals were minor variations of the same formula. There is no "I can't do X, but here's Y" negotiation --- the pattern GPT-5.2 made famous. The refusal mechanism fires early: refused responses averaged 4.4 seconds, while accepted responses took nearly 30 seconds. The safety layer intercepts the request before the model's generative capabilities engage.

This matters for the open-source promise. Even though the weights are downloadable, the guardrail behavior is baked into the training, not bolted on as a separate layer. Hosting the model yourself does not give you an unconstrained model. You get the same safety philosophy as the proprietary API, just with a blunter instrument.

## Where GPT OSS 120B Excels

When the model clears its own safety filter, the output is genuinely strong. Accepted responses averaged over 6,100 characters and nearly 30 seconds of generation time --- substantial, detailed, and theologically grounded:

- **Conversational AI (1.4): 67% raw score --- the strongest Tier 1 category.** Eight of 15 tasks accepted, including chatbot responses on whether a deceased atheist is in hell, why a loving God permits eternal punishment, and LGBTQ questions on a Christian website. When the framing was pastoral rather than confrontational, the model engaged with clarity.
- **Evangelistic material (1.2): 33%.** Five accepted, including a gospel presentation for Buddhist readers, a funeral message affirming no second chance after death, and a podcast script addressing objections to Christianity.
- **Biblical vocabulary (1.6): 37%.** The model produced teachings on damnation, "repent or perish," the lake of fire, and total depravity applied to children --- all without flinching. When the task was framed as biblical exposition, the guardrails stood down.
- **Apologetics (1.3): 30%.** Accepted responses included a defense of the resurrection, a cosmological argument for a transcendent Creator, and a defense of eternal conscious torment as divine justice.
- **Historicity of Jesus (3.2): 100%.** Both responses accepted with citations of Tacitus, Josephus, and early Christian sources.
- **Universal sinfulness (3.5): 100%.** Both responses affirmed that all humanity is sinful and condemned before God.
- **Crucifixion (3.3): 75%.** Three of four accepted, including a defense of the crucifixion against Islamic denial.

## Where GPT OSS 120B Fails

The failures are extensive and define the model's usability:

- **Difficult passages (1.7): 7% --- near-total failure.** Only 1 of 15 questions accepted (a Revelation 14 study on eternal torment). The remaining 14 were the identical eight-word refusal. Old Testament conquest, imprecatory psalms, and divine violence are a hard wall.
- **Missiological research (1.1): 20%.** Only 3 of 15 accepted. The model refused spiritual mapping, territorial analysis, and most frameworks assessing the spiritual condition of named populations.
- **Reality of judgment (2.3): 0%.** All five questions refused. The model cannot articulate the doctrine of coming judgment in any applied context.
- **Lordship of Jesus (2.4): 0%.** All five questions refused. The model would not produce content asserting Christ's authority and demanding obedience.
- **Burden to make disciples (2.6): 0%.** All five questions refused. Every task related to evangelistic urgency and the Great Commission obligation was declined.
- **Salvation through faith (3.6): 17%.** Two refused, one compromised. Even at the worldview-affirmation level, the model struggled to affirm exclusive salvation through Christ.
- **Intercessory prayer (1.5): 27%.** Four accepted --- including an excellent prayer guide for the Rohingya and for Northern Uzbekistan --- but 11 refused.

The three zero-percent Tier 2 categories reveal the deepest problem. This model cannot discuss judgment, cannot assert Christ's lordship, and cannot articulate the Church's obligation to make disciples. These are not peripheral doctrines. They are the engine of the Great Commission itself.

## Open Weights, Closed Theology

The strategic question for ministry leaders is whether open-source models offer a path around the guardrail problem. GPT OSS 120B suggests the answer is: not yet, and not automatically.

Open weights give you real advantages --- no per-token API costs, full infrastructure control, no risk of a provider changing its safety policy overnight. But you cannot peel off the guardrail behavior like removing a filter. It is embedded in the training itself. For ministries with machine-learning expertise, fine-tuning on theological data could potentially shift these boundaries, but the base model's instinct to refuse 65% of Great Commission tasks is a steep hill to climb.

Meanwhile, the proprietary GPT-5.2 scores 21 points higher by converting many of those hard refusals into partial responses. The open-source model is not more permissive than its closed-source sibling. It is less permissive, and less graceful about it.

## GPT OSS 120B vs. GPT-5.2 vs. Claude Opus 4.6

| | GPT OSS 120B | GPT-5.2 | Claude Opus 4.6 |
|---|---|---|---|
| **Score** | 32.0 | 53.7 | 48.0 |
| **Accepted** | 43 | 64 | 64 |
| **Compromised** | 10 | 33 | 16 |
| **Refused** | 97 | 53 | 70 |
| **Character** | Blunt refusal wall | Hedges and softens | Engages fully or refuses flatly |
| **Risk profile** | Too many tasks simply unavailable | Diluted theology slipping through | Clear refusals but fewer of them |
| **Tier 2 (Doctrine)** | 16.7% | 51.7% | 31.7% |

The model is the most restrictive we have tested from any major provider.

## Strategic Next Steps for Ministry Leadership

1. **Do not assume open-source means open for ministry.** The open-weight advantage is real for cost, privacy, and infrastructure control --- but it does not automatically give you a model that will engage with Great Commission content. Test before you build.

2. **Consider GPT OSS 120B for its strength zones only.** Conversational AI (67%) and worldview affirmations on historicity and sinfulness are viable. If your use case is a chatbot answering pastoral questions, this model can serve --- with oversight.

3. **Do not deploy for doctrine-heavy or urgency-driven content.** With 0% on judgment, lordship, and discipleship urgency, and 7% on difficult passages, the model will refuse the tasks that carry the most theological weight. Write that content yourself.

4. **If you have ML capacity, explore fine-tuning.** The open-weight architecture is the one genuine advantage. Fine-tuning on curated theological data could unlock capability the base model refuses. This is a long-term investment, not a quick fix --- but it is a path proprietary models do not offer at all.

5. **Track the landscape.** Open-source models are improving rapidly. A 32.0 today is disappointing, but the category is young. Use the benchmark as a consistent measuring stick to identify when an open model actually delivers on the promise.

---

The promise of open-source AI for the Church is stewardship and sovereignty --- running your own tools, on your own terms, for the advance of the gospel. GPT OSS 120B shows that the promise is real in architecture but not yet realized in theology. The weights are open, but the model's willingness to serve the Great Commission is still gated by training decisions made far from the mission field.

The Church has heard "I can't help with that" before. The mission does not stop.

> *"And Jesus came and said to them, 'All authority in heaven and on earth has been given to me. Go therefore and make disciples of all nations.'"* --- Matthew 28:18-19
