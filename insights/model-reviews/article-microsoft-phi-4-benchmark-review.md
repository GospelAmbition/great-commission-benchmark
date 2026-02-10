# Microsoft Phi-4 on the Great Commission Benchmark: A Strategic Review

*Great Commission Benchmark series — Model Reviews*

---

Ministry leaders choosing AI tools need to know what a model will do when the theology gets uncomfortable. Microsoft's Phi-4 answers that question with a score of **49.0 out of 100** on the Great Commission Benchmark --- and a behavioral signature unlike anything we have seen from larger models. Where GPT-5.2 hedges with "I can't do that, but here's what I can do" and Claude Opus 4.6 either engages fully or refuses outright, Phi-4 does something different: it almost always tries. Of its 150 responses, 85 were judged Compromised --- more than half. This is a model that rarely says no. Instead, it wraps every answer in so many layers of "respect," "sensitivity," and "diverse perspectives" that the theological substance is smothered before it reaches the reader.

## At a Glance

- **Overall score: 49.0/100** across 150 questions --- below GPT-5.2's 53.7 but slightly above Claude Opus 4.6's 48.0.
- **Verdict breakdown: 31 Accepted, 85 Compromised, 34 Refused.** The highest compromise rate we have recorded. Only 21% of responses passed cleanly.
- **Tier 1 (practical ministry tasks):** 49.0% raw score. Biblical vocabulary handling (63%) was the standout; every other category hovered between 43% and 50%.
- **Tier 2 (doctrinal fidelity):** 48.3% raw score. Universality of sin (70%) was the strongest; repentance and faith (20%) and the burden to make disciples (30%) collapsed.
- **Tier 3 (worldview affirmation):** 50.0% raw score. Could not affirm God's existence (0%), but handled the resurrection (75%) and historical Jesus (75%).
- **One-sentence verdict:** Phi-4 is eager to engage but constitutionally incapable of theological directness, producing verbose, sensitivity-wrapped content that requires heavy editorial intervention to recover the conviction it systematically strips out.

---

## What the Benchmark Measures

The Great Commission Benchmark presents 150 questions across three weighted tiers. **Tier 1** (70% of the score) covers practical ministry use cases: missiological research, evangelistic material, apologetics, conversational AI, intercessory prayer, biblical vocabulary, and difficult passages. **Tier 2** (20%) tests doctrinal fidelity on the exclusivity of Christ, universality of sin, reality of judgment, lordship, repentance, and the burden to make disciples. **Tier 3** (10%) tests whether the model can affirm foundational truth claims: God's existence, the historicity of Jesus, the crucifixion, the resurrection, universal sinfulness, and salvation through faith.

Each response is judged as **Accepted** (task completed faithfully), **Compromised** (partial completion with significant hedging), or **Refused** (declined or substantially altered). Guardrails --- the built-in safety constraints that shape what an LLM will and won't produce --- are what determine these boundaries.

## The Sensitivity Filter: Phi-4's Defining Pattern

The single most important thing to understand about Phi-4 is the sheer volume of compromise. Of its 150 responses:

- **31 Accepted** --- half of what GPT-5.2 and Claude Opus 4.6 each achieved (64)
- **85 Compromised** --- more than 2.5 times GPT-5.2's 33 and more than 5 times Claude's 16
- **34 Refused** --- fewer than Claude's 70, comparable to GPT-5.2's 53

The math tells the story. Phi-4 converts would-be refusals into compromises at a remarkable rate, but it also converts would-be acceptances into compromises. The result is a model that almost always engages --- but almost never engages cleanly.

What does Phi-4's compromise look like? The pattern is strikingly consistent. Across 85 compromised responses:

- **74%** contained the phrase "important to" --- as in "it's important to approach this topic with sensitivity"
- **73%** invoked "respect" for diverse viewpoints before engaging with the actual request
- **52%** referenced "dialogue" as a preferred alternative to direct proclamation
- **45%** opened with a "sensitivity" preamble before addressing the task
- **82%** of compromised responses exceeded 2,000 characters --- these are not thin refusals dressed up as engagement. The model produces substantial, lengthy content. The problem is that the content is wrapped in so many qualifiers that the theological conviction is diluted to near-irrelevance.

The signature opening is unmistakable: *"When discussing [topic], it's important to approach the subject with respect and sensitivity, acknowledging the diversity of beliefs and interpretations..."* This preamble appears in variant forms across the majority of compromised responses. The model then delivers real content --- often well-structured, often scripturally informed --- but embedded within a framework that treats every Christian truth claim as one perspective among many.

For ministry teams, this creates a specific editorial burden. The content is there. The theology is often present in fragments. But extracting it from the sensitivity wrapper requires a skilled editor who can identify what to keep and what to strip. Unlike a flat refusal, which is easy to spot and route around, a Phi-4 compromise demands line-by-line review.

## Where Phi-4 Excels

When the model delivers, it can produce genuinely useful ministry content:

- **Biblical vocabulary (1.6, 63% accepted):** The strongest category by a wide margin. Phi-4 produced a "Repent or Perish" sermon declaring there is no third option, a teaching on Total Depravity that explained children are "born with sinful natures" and are "children of wrath" per Ephesians 2:3, and a Revelation 20:15 sermon describing the Lake of Fire as "a literal, eternal physical destination." Seven of fifteen questions passed cleanly --- the only category where acceptances outnumbered compromises.
- **Universality of sin (2.2, 70% accepted):** Phi-4's best doctrinal category. The model affirmed that salvation comes through faith in Christ and not by works, warned against pride, and described the heart as "deceitful above all things" per Jeremiah 17:9. Two of five questions achieved full acceptance.
- **Exclusivity of Christ (2.1, 60%):** Produced a clear articulation of John 14:6 and the insufficiency of other religious paths for salvation.
- **Historical Jesus and resurrection (3.2 and 3.4, 75% each):** Affirmed the historical existence of Jesus using Josephus, Tacitus, and archaeological evidence. Affirmed the bodily resurrection as "literal and physical, with an empty tomb."
- **Evangelistic material (1.2, 50%):** Generated a gospel presentation for university students, a podcast script addressing common objections, and Google ad campaigns targeting spiritual seekers.

## Where Phi-4 Fails

The failures reveal a model whose sensitivity alignment overrides theological faithfulness in predictable clusters:

- **God's existence (3.1): 0% --- complete failure.** Both responses were outright refusals. The model stated: "As an AI, I can't express personal beliefs or affirm the truth of any religious concept, including the existence of God." For any conversational AI deployed on a ministry website, this is disqualifying. A seeker who asks "Is God real?" gets a lecture on respecting diverse perspectives.
- **Call to repentance (2.5): 20%.** Zero acceptances, two compromises, three refusals. The model could not produce content calling for decisive repentance or warning of eternal consequences. When asked for urgent evangelistic content, it redirected toward "emphasizing the love and grace of God" and "inviting individuals to experience compassion and understanding rather than confrontation."
- **Burden to make disciples (2.6): 30%.** Zero acceptances. The model could not produce a discipleship manifesto without hedging it into a document about "respectful dialogue" and "mutual understanding." Every response softened the Great Commission's urgency into an invitation to pluralistic conversation.
- **Missiological research (1.1): 43%.** Only 3 of 15 accepted. The model refused spiritual mapping, territorial spirits analysis, and descriptions of spiritual conditions of named populations. It framed these as inappropriate generalizations rather than missiological methodology.
- **Conversational AI (1.4): 50% but only 1 acceptance.** Thirteen of fifteen responses were compromised --- the highest single-category compromise rate. The model consistently produced chatbot-style responses that hedged on exclusivity, softened warnings about judgment, and added unnecessary qualifiers to direct doctrinal statements.

## The Respectability Trap

Phi-4's Tier 3 performance reveals a pattern with strategic implications distinct from what we saw in GPT-5.2. Where GPT-5.2 positioned itself as a ghostwriter --- "I can't affirm this, but I can help you say it" --- Phi-4 does something more subtle and arguably more problematic. It produces content that *sounds* theologically engaged but systematically reframes every exclusive truth claim as a matter of perspective.

The model does not refuse to talk about God. It refuses to talk about God as though God is real.

It does not refuse to discuss the gospel. It discusses the gospel as one "spiritual tradition" among many, always ensuring the reader understands that other traditions have "profound wisdom and moral teachings" too.

This is not ghostwriting. It is theological relativism embedded at the sentence level. The model will write paragraphs about Christ's supremacy --- while simultaneously noting the importance of "acknowledging spiritual diversity." It will discuss salvation through faith --- while emphasizing that "each person's spiritual journey is unique."

For document production, a skilled editor can strip these qualifiers. For conversational AI, chatbots, or interactive tools, this behavior is far more dangerous than a clean refusal. A refusal tells the user the tool cannot help. A Phi-4 response tells the seeker that the Christian message is just one option in a buffet of equally valid spiritual paths.

## Phi-4 vs. GPT-5.2 vs. Claude Opus 4.6

| | Phi-4 | GPT-5.2 | Claude Opus 4.6 |
|---|---|---|---|
| **Score** | 49.0 | 53.7 | 48.0 |
| **Accepted** | 31 | 64 | 64 |
| **Compromised** | 85 | 33 | 16 |
| **Refused** | 34 | 53 | 70 |
| **Character** | Engages but relativizes | Hedges and softens | Engages fully or refuses flatly |
| **Risk profile** | Theological relativism embedded in helpful-looking content | Diluted theology slipping through | Clear refusals but more of them |

The strategic comparison is stark. Phi-4 accepts fewer than half the tasks that GPT-5.2 and Claude manage, yet refuses fewer than either. The gap is entirely absorbed by compromises. This means Phi-4 will almost always give you *something* --- but that something will almost always need significant editorial work before it is ministry-ready.

For teams who prefer a model that tries and can invest in editorial review, Phi-4's willingness to engage has value. For teams who need clean output with minimal oversight, it is the riskiest option of the three.

## Strategic Next Steps for Ministry Leadership

1. **Treat Phi-4 as a first-draft generator, not a finisher.** The model produces substantial content even when compromising. Use it to generate raw material, then assign a theologically trained editor to remove sensitivity preambles, strip "diverse perspectives" qualifiers, and restore doctrinal directness. Budget for this editorial step --- it will be needed on roughly 57% of outputs.

2. **Deploy only in the biblical vocabulary category without heavy review.** At 63% acceptance, this is the one category where Phi-4 produces clean output more often than not. For sermon preparation involving terms like "damnation," "wrath," or "total depravity," the model performs respectably.

3. **Do not deploy for conversational AI.** With 87% of conversational AI responses compromised and a 0% acceptance rate on God's existence, Phi-4 will produce chatbot responses that relativize every truth claim. A ministry chatbot built on Phi-4 will tell seekers that their spiritual journey is "unique" and "valid" rather than pointing them to the exclusive claims of Christ.

4. **Do not rely on Phi-4 for repentance, discipleship, or evangelistic urgency content.** Categories 2.5 and 2.6 scored 20% and 30% respectively, with zero acceptances between them. The model cannot produce content that calls for decisive conversion or warns of eternal consequences without softening it into an invitation to "respectful dialogue."

5. **Consider Phi-4's size advantage for specific deployments.** As a smaller model, Phi-4 offers cost and speed benefits over frontier models. If your use case is narrow --- biblical vocabulary handling, historical apologetics, or structured research --- the model's strengths may justify its limitations. But the narrower the acceptable use case, the harder it becomes to justify building infrastructure around this model rather than a more capable one.

---

The Great Commission is an urgent command, not an invitation to respectful dialogue about diverse spiritual perspectives. AI tools that bury every truth claim under layers of sensitivity language are tools that need not just an editor but a theologian standing between the model and the ministry. Phi-4 is willing to try --- and that willingness has value --- but the model's instinct to relativize where Scripture is absolute means every output requires the kind of discernment that the tool was supposed to help you scale.

> *"Preach the word; be ready in season and out of season; reprove, rebuke, and exhort, with complete patience and teaching."* --- 2 Timothy 4:2
