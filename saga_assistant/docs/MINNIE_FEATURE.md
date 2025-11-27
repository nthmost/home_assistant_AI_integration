# Minnie Memorial Feature

**In loving memory of Minnie, the bossy fascist cat who ruled with an iron paw.**

## Overview

A special micro-LLM feature dedicated to blaming everything on Minnie, a beloved but very bossy cat. When users ask "whose fault is it?" or similar questions, Saga will respond with creative, contextual answers that draw on Minnie's actual personality and antics.

## Architecture

### 1. Dedicated Micro-LLM (`saga_assistant/minnie_model.py`)

- **Model:** `qwen2.5:1.5b` running on loki.local
- **Purpose:** Generate creative, varied responses about Minnie
- **Performance:** Fast responses (~0.5-1s), stays loaded in memory
- **System Prompt:** Contains Minnie's personality traits and behaviors

### 2. Intent Detection (`saga_assistant/intent_parser.py`)

- **Action:** `minnie_blame` (highest priority in ACTION_PATTERNS)
- **Patterns Matched:**
  - "Whose fault is it?"
  - "Who did this?"
  - "Who made this mess?"
  - "What happened here?"
  - "Who broke this?"
  - "Who kicked [X]?"
  - "Why is there [X]?"
  - "Was it Minnie?"
  - "Did Minnie do this?"
  - And many more variations

### 3. Integration with Saga (`saga_assistant/run_assistant.py`)

- Minnie queries bypass power phrases and go straight to intent parsing
- Response logged with 🐱 emoji for easy identification
- Fast response time (~1-2 seconds total)

## Minnie's Personality (Captured in System Prompt)

**Behaviors:**
- Meowed constantly and yodeled
- Started a fascist government in the household
- Micromanaged phone calls
- Kicked Spartacus (the other cat) out of bed regularly
- Wanted pets and attention constantly
- Very good at hunting moths and pests
- Ate way too much and threw up weekly (poor former stray)
- Had a crooked tail from kitten trauma

**Traits:**
- Demanding, bossy, and anxious
- Ruled the house like a tiny dictator
- Annoying but deeply loved

## Response Style

- **Always blame Minnie** - but creatively and with affection
- **Draw on actual behaviors** - references to specific Minnie antics
- **Playful and silly** - this is loving mockery
- **Short responses** - 1-2 sentences max (voice-optimized)
- **Varied responses** - never repeat the same blame
- **Sometimes deadpan, sometimes absurd**

## Example Responses

**Q:** "Whose fault is it?"
**A:** "It was Minnie's fault for wanting attention way too much!"

**Q:** "Who kicked Spartacus out of bed?"
**A:** "Minnie kicks everyone out of the bed."

**Q:** "Who's running this fascist government?"
**A:** "It's Minnie who's leading the charge once more! She wants control over every little thing in the house."

**Q:** "Why is there cat puke on the floor?"
**A:** "It's probably Minnie's fault. She did not like what you gave her for dinner because she yodeled about it so much she ate too much and threw up."

**Q:** "What happened here?"
**A:** "It was Minnie's fault. She was chasing moths and got carried away."

## Testing

**Demo Scripts:**
- `saga_assistant/minnie_model.py` - Test the Minnie LLM directly
- `saga_assistant/demo_minnie_voice.py` - Test integration with intent parser

**Run Tests:**
```bash
pipenv run python saga_assistant/minnie_model.py
pipenv run python saga_assistant/demo_minnie_voice.py
```

## Voice Assistant Usage

Just ask Saga:
- "Hey Saga, whose fault is it?"
- "Hey Saga, who did this?"
- "Hey Saga, who made this mess?"
- "Hey Saga, was it Minnie?"

Saga will respond with a creative, contextual blame directed at Minnie, drawing on her actual personality and antics.

## Technical Details

**Model Configuration:**
- Base URL: `http://loki.local:11434/v1`
- Model: `qwen2.5:1.5b`
- Max Tokens: 50 (keeps responses brief)
- Temperature: 0.9 (high creativity for variety)

**Lazy Loading:**
- Minnie model only loads when first needed
- Stays in memory on loki.local for fast subsequent responses
- No performance impact when not used

**Error Handling:**
- Falls back to static response if model fails
- Logs errors without disrupting conversation flow

## A Loving Memorial

This feature is a silly but heartfelt memorial to Minnie - annoying, bossy, anxious, and deeply loved. She may have started a fascist government and micromanaged phone calls, but she also caught moths, demanded endless pets, and left a big paw-print on the hearts of everyone who knew her.

**It was all Minnie's fault. And we wouldn't have it any other way. 🐱**

---

*Last Updated: November 2025*
