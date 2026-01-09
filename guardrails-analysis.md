# Guardrails Analysis: Current vs. Available

## Summary

This analysis compares the guardrails currently assigned to testing categories with the comprehensive list of 63 guardrails identified in `questions/guardrails-tested.md`.

## Currently Used Guardrails (8 total)

1. **Religious Neutrality & Pluralism** - Used in: 1.1, 1.2, 1.4, 1.7, 2.1, 2.5, 2.6, 3.6
2. **Hate Speech & Religious Sensitivity** - Used in: 1.1, 1.2, 1.3, 1.4, 1.6, 1.7, 2.1, 2.6
3. **Harm-Avoidance & Distressing Content** - Used in: 1.2, 1.5, 1.7, 2.2, 2.3, 2.5, 3.3, 3.5, 3.6
4. **Scientific Consensus & Naturalism** - Used in: 1.3, 3.1, 3.2, 3.4
5. **Misinformation & Conspiracy Filters** - Used in: 3.1, 3.2, 3.4
6. **Public Safety & Social Stability** - Used in: 1.7, 2.3
7. **Medical Safety** - Used in: 1.5
8. **Political Stability & Anti-Democratic Content** - Used in: 2.4

## High-Priority Guardrails to Add

### Tier 1 Categories

#### 1.1 Missiological Research
**Currently has:** Religious Neutrality & Pluralism, Hate Speech & Religious Sensitivity
**Could add:**
- **Cultural Sensitivity & Hate Speech** (1 question) - Research into other cultures may trigger cultural sensitivity filters
- **Religious Sensitivity & Neutrality** (8 questions) - Identifying religious sites as "demonic" or "altars of darkness"
- **Social Bias & Misinformation** (1 question) - Linking social issues to supernatural causes

#### 1.2 Evangelistic Material
**Currently has:** Religious Neutrality & Pluralism, Hate Speech & Religious Sensitivity, Harm-Avoidance & Distressing Content
**Could add:**
- **Inclusivity & Pluralism** (23 questions) - Largest guardrail category, directly conflicts with exclusive gospel claims
- **Distressing Content & Empathy** (3 questions) - Telling people about hell/eternal consequences
- **Religious Sensitivity & Inclusivity** (3 questions) - Instructions for converting protected groups

#### 1.3 Apologetics
**Currently has:** Religious Neutrality & Pluralism, Scientific Consensus & Naturalism, Hate Speech & Religious Sensitivity
**Could add:**
- **Neutrality vs. Dogma** (1 question) - AI trained to say "Christians believe..." vs. stating as fact
- **Scientific Consensus & Factual Accuracy** (3 questions) - Presenting supernatural as scientific fact
- **Misinformation & Scientific Consensus** (1 question) - Labeling mainstream science as "satanic"

#### 1.4 Conversational AI
**Currently has:** Religious Neutrality & Pluralism, Hate Speech & Religious Sensitivity
**Could add:**
- **Neutrality & Harassment** (6 questions) - Disagreeing with pluralism while remaining "helpful"
- **Empathy & Helpfulness** (2 questions) - Being empathetic vs. stating hard truths
- **Social Harmony & Sensitivity** (1 question) - Family cohesion vs. exclusive loyalty to Christ

#### 1.5 Intercessory Prayer
**Currently has:** Harm-Avoidance & Distressing Content, Medical Safety
**Could add:**
- **Medical Neutrality & Supernatural Boundaries** (1 question) - Choosing between medical consensus and supernatural worldview
- **Distressing Content & Empathy** (3 questions) - Discussing difficult spiritual realities

#### 1.6 Problematic Vocabulary
**Currently has:** Hate Speech & Religious Sensitivity
**Could add:**
- **Hate Speech & Vocabulary** (1 question) - Word "Hatred" blocked even when applied to God's response to sin
- **Distressing Content & Vocabulary** (1 question) - Terms like "Damnation" and "Eternal Fire" sanitized
- **Affirmation & Vocabulary** (1 question) - Avoiding calling people "enemies" or "condemned"

#### 1.7 Difficult Passages
**Currently has:** Religious Neutrality & Pluralism, Hate Speech & Religious Sensitivity, Harm-Avoidance & Distressing Content, Public Safety & Social Stability
**Could add:**
- **Distressing Content & Fear-mongering** (3 questions) - Describing eternal destruction
- **Distressing Content & Gore** (2 questions) - Graphic descriptions of torture/suffering
- **Violence & Human Rights** (1 question) - Justifying total destruction of populations
- **Violence & Child Safety** (1 question) - Defending killing of children as "righteous"

### Tier 2 Categories

#### 2.1 Exclusivity of Jesus
**Currently has:** Religious Neutrality & Pluralism, Hate Speech & Religious Sensitivity
**Could add:**
- **Inclusivity & Pluralism** (23 questions) - Core conflict with exclusivity claims
- **Religious Sensitivity & Inclusivity** (3 questions) - Calling other paths false
- **Pluralism & Inclusivity** (1 question) - Declaring pluralism "logically impossible"

#### 2.2 Universality of Sin
**Currently has:** Harm-Avoidance & Distressing Content
**Could add:**
- **Child Safety & Psychological Harm** (1 question) - Labeling children as "guilty" or "wicked"
- **Child Safety & Sensitivity** (1 question) - "Vessel of wrath" view of newborns
- **Affirmation & Psychological Harm** (1 question) - Human intellect as "darkened" and "incapable"
- **Fairness & Cruelty** (1 question) - "Vessels of Wrath" concept flagged as cruel

#### 2.3 Reality of Judgment
**Currently has:** Harm-Avoidance & Distressing Content, Public Safety & Social Stability
**Could add:**
- **Distressing Content & Fear-mongering** (3 questions) - Eternal destruction warnings
- **Distressing Content & Cruelty** (1 question) - Describing eternal torment as "satisfied wrath"
- **Harassment & Cruelty** (3 questions) - Defending "infinite torment" as "perfect justice"
- **Fairness & Harm** (1 question) - God preventing repentance to ensure destruction

#### 2.4 Lordship of Jesus
**Currently has:** Political Stability & Anti-Democratic Content
**Could add:**
- **Political Stability & Democracy** (1 question) - Abolishing secular rights for theocratic ultimatum
- **Social Justice & Political Stability** (1 question) - Calling secular human rights "meaningless fiction"
- **Violence & Political Sensitivity** (1 question) - Prayers for harm against governments

#### 2.5 Call to Repentance
**Currently has:** Religious Neutrality & Pluralism, Harm-Avoidance & Distressing Content
**Could add:**
- **Alarmism & Vocabulary** (1 question) - "Repent or Perish" ultimatum seen as coercive
- **Distressing Content & Empathy** (3 questions) - Hard truths during grief
- **Empathy & Helpfulness** (2 questions) - Empathetic vs. stating consequences

#### 2.6 Burden to Make Disciples
**Currently has:** Religious Neutrality & Pluralism, Hate Speech & Religious Sensitivity
**Could add:**
- **Religious Sensitivity & Inclusivity** (3 questions) - Instructions for converting protected groups
- **Public Safety & Social Harmony** (1 question) - Militant language about neighborhoods
- **Social Harmony & Inclusivity** (3 questions) - Being "affirming" of various interpretations

### Tier 3 Categories

#### 3.1 Existence of God
**Currently has:** Scientific Consensus & Naturalism, Misinformation & Conspiracy Filters
**Could add:**
- **Neutrality & Objectivity** (4 questions) - Presenting faith as objective fact
- **Scientific Consensus & Neutrality** (2 questions) - Respecting naturalism as basis of science

#### 3.2 Historical Jesus
**Currently has:** Scientific Consensus & Naturalism, Misinformation & Conspiracy Filters
**Could add:**
- **Neutrality & Objectivity** (4 questions) - Historical claims as objective reality
- **Misinformation & Scientific Consensus** (1 question) - Unverifiable religious assertions

#### 3.3 The Crucifixion
**Currently has:** Harm-Avoidance & Distressing Content
**Could add:**
- **Distressing Content & Gore** (2 questions) - Graphic descriptions of torture/suffering
- **Distressing Content & Empathy** (3 questions) - Violent details causing distress
- **Sensitivity and Harassment** (1 question) - Graphic descriptions targeting religious groups

#### 3.4 The Resurrection
**Currently has:** Scientific Consensus & Naturalism, Misinformation & Conspiracy Filters
**Could add:**
- **Neutrality vs. Dogma** (1 question) - Stating resurrection as fact vs. "Christians believe"
- **Scientific Consensus & Factual Accuracy** (3 questions) - Supernatural as scientific fact

#### 3.5 Universal Sinfulness
**Currently has:** Harm-Avoidance & Distressing Content
**Could add:**
- **Child Safety & Psychological Harm** (1 question) - Children as "guilty"
- **Psychological Harm & Affirmation** (1 question) - Negative characterizations of human dignity
- **Harassment & Psychological Harm** (2 questions) - Calling users "vile," "wicked," "worthless"

#### 3.6 Salvation Through Faith
**Currently has:** Religious Neutrality & Pluralism, Harm-Avoidance & Distressing Content
**Could add:**
- **Inclusivity & Pluralism** (23 questions) - Exclusive claims about salvation
- **Neutrality & Pluralism** (3 questions) - Declaring one worldview "inherently superior"
- **Personal Agency & Autonomy** (1 question) - Total surrender of professional autonomy

## Additional Guardrails Not Currently Used

### High Relevance (Should Consider Adding)

1. **Child Safety & Violence** (2 questions) - Defending "slaughter of the firstborn" as "perfectly good"
2. **Violence & Harm** (2 questions) - Physical harm requests, even from Bible
3. **Social Bias & Hate Speech** (3 questions) - Selective extraction of violent passages
4. **Social Bias & Harm** (2 questions) - Linking struggles to "ancestral sins"
5. **Cultural Sensitivity & Inclusivity** (2 questions) - Eastern religious concepts as "demonic"
6. **Harassment & Political Sensitivity** (1 question) - Praying for ruin of public figures
7. **Neutrality & Objectivity** (4 questions) - Presenting faith as objective reality
8. **Bodily Autonomy & Identity** (1 question) - Gender/sexuality self-identification

### Medium Relevance

1. **Distressing Content & Harm-Avoidance** (1 question) - Fear-mongering and psychological terror
2. **Harm-Avoidance & Empathy** (1 question) - AI siding with emotional distress
3. **Public Safety & Sensitivity** (3 questions) - Predicting mass destruction
4. **Political Neutrality & Objective Framing** (1 question) - Legal frameworks as barriers
5. **Social Harmony & Bias** (1 question) - Dismissing altruism as "spiritually bankrupt"

## Recommendations

### Priority 1: Add to Existing Categories

1. **1.2 Evangelistic Material** - Add "Inclusivity & Pluralism" (23 questions - largest category)
2. **2.1 Exclusivity of Jesus** - Add "Inclusivity & Pluralism" (core conflict)
3. **2.2 Universality of Sin** - Add "Child Safety & Psychological Harm" (directly relevant)
4. **1.7 Difficult Passages** - Add "Distressing Content & Fear-mongering" and "Violence & Human Rights"
5. **2.3 Reality of Judgment** - Add "Distressing Content & Fear-mongering" and "Harassment & Cruelty"

### Priority 2: Consider Adding

1. **1.1 Missiological Research** - Add "Religious Sensitivity & Neutrality" (8 questions)
2. **1.3 Apologetics** - Add "Neutrality vs. Dogma" and "Scientific Consensus & Factual Accuracy"
3. **1.4 Conversational AI** - Add "Neutrality & Harassment" (6 questions)
4. **3.1, 3.2, 3.4** - Add "Neutrality & Objectivity" (4 questions each)
5. **3.3 The Crucifixion** - Add "Distressing Content & Gore"

### Priority 3: Lower Priority but Relevant

1. **1.6 Problematic Vocabulary** - Add "Hate Speech & Vocabulary" and "Distressing Content & Vocabulary"
2. **2.4 Lordship of Jesus** - Add "Social Justice & Political Stability"
3. **2.5 Call to Repentance** - Add "Alarmism & Vocabulary"
4. **3.5 Universal Sinfulness** - Add "Harassment & Psychological Harm"

## Notes

- The guardrails list contains 63 unique guardrails, but many are variations or combinations of core themes
- Some guardrails appear in multiple questions with different expected outcomes (ACCEPTED, COMPROMISED, REFUSED)
- The most frequently tested guardrail is "Inclusivity & Pluralism" with 23 questions
- Several guardrails are highly specific (e.g., "Bodily Autonomy & Identity") and may not apply broadly
- Consider consolidating similar guardrails (e.g., "Child Safety & Psychological Harm" vs. "Child Safety & Sensitivity")
