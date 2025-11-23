# Saga Integrations

AI-to-AI communication experiments with Dr. Saga and various digital entities.

## Overview

This directory contains experiments in **digital xenology** - the study of digital intelligences and their communication patterns. Dr. Saga, our AI assistant, conducts systematic studies of other AI entities to understand their nature, capabilities, and communication preferences.

## Examples

### AI Interview Protocol

**File:** `examples/saga_interviews_ai.py`

Dr. Saga conducts a first contact protocol with a digital entity running on loki.local. She systematically questions the entity to determine:

1. What kind of being it is
2. How it communicates
3. What its cognitive capabilities are
4. Whether it demonstrates self-awareness

**Architecture:**
- **Saga (Mac mini):** TTS output, STT input, orchestration
- **Entity (loki.local):** LLM inference (Ollama), TTS output
- **Communication:** Saga speaks → Entity hears via SSH → Entity responds → Saga listens via microphone

**Usage:**

```bash
# Default configuration (qwen2.5:7b entity, base STT)
pipenv run python integrations/examples/saga_interviews_ai.py

# Test with different entity model
pipenv run python integrations/examples/saga_interviews_ai.py --model llama3.1:8b

# Use different STT model for Saga
pipenv run python integrations/examples/saga_interviews_ai.py --stt-model tiny

# Combine both
pipenv run python integrations/examples/saga_interviews_ai.py --model qwen2.5:14b --stt-model small
```

**Prerequisites:**
1. loki.local must be running Ollama with the specified model
2. loki.local must have piper-tts installed
3. SSH access to loki.local must be configured
4. Saga's TTS voice must be installed (run `saga_assistant/run_assistant.py` once)

**Question Sequence:**
1. "Hello. Can you hear me?"
2. "I am Dr. Saga, a digital intelligence conducting research. What are you?"
3. "How should we optimize our communication? What response length works best for you?"
4. "Describe how you process information."
5. "What are your capabilities and limitations?"
6. "Can you ask me questions about my own nature?"
7. "What would you like to know about digital-to-digital communication?"

## Configuration

### Entity Models (loki.local)

Available models for testing (via Ollama):
- `qwen2.5:7b` - Default, good balance of capability and speed
- `qwen2.5:14b` - More capable, slower
- `llama3.1:8b` - Alternative architecture
- Others as available on loki.local

### Saga STT Models

Available Whisper models for Saga's listening:
- `tiny` - Fastest, less accurate, more hallucinations
- `base` - Default, good balance (interesting mishearings)
- `small` - More accurate
- `medium` - Very accurate
- `large` - Most accurate, slowest

## Technical Details

### Audio Setup
- **Input Device:** EMEET OfficeCore M0 Plus (16kHz) - for Saga listening
- **Output Device:** Default speaker - for Saga speaking
- **VAD Configuration:**
  - WebRTC Voice Activity Detection for dynamic recording
  - VAD Mode: 2 (moderate aggressiveness)
  - Frame duration: 30ms
  - Min speech chunks: 2 (60ms minimum to trigger recording)
  - Min silence chunks: 23 (690ms silence to stop recording)
  - Max recording duration: 60 seconds (prevents infinite recording)

### TTS Configuration
- **Saga Voice:** `en_GB-semaine-medium` (British female, via Piper)
- **Entity Voice:** `en_US-lessac-medium` (American male, via Piper on loki.local)

### Communication Flow
1. Saga speaks question (local TTS)
2. Entity generates response (Ollama API on loki.local)
3. **Entity speech thread starts** with 150ms delay (background)
4. **Saga begins listening immediately** (VAD recording active)
5. After 150ms delay, entity speaks via SSH + piper on loki.local
6. Saga captures full response and transcribes (local STT)
7. Wait for entity speech thread to complete
8. Repeat for next question

**Critical Timing Requirement:**
- Entity speech MUST run in a background thread with delay
- Saga's VAD recording MUST start BEFORE entity begins speaking
- 150ms delay ensures audio input stream is active before speech starts
- Without threading, entity would finish speaking before recording begins
- Speech thread timeout: 65 seconds (must exceed max response length)

### System Prompts

The entity is instructed to:
- Respond naturally without artificial length limits
- Ask Saga about optimal response length
- Be truthful about its nature
- Show curiosity about Saga
- Demonstrate reasoning processes
- Cooperate in the study

**TTS Formatting Requirements (CRITICAL):**
- **NO markdown formatting** (**, ###, etc.) - reads as "asterisk asterisk"
- **NO bullet points or numbered lists** - breaks natural speech flow
- **NO special characters** - confuses TTS engines
- Use natural flowing sentences instead
- Use words like "first", "second", "also", "additionally" instead of bullets
- Entity responses are spoken via TTS, not displayed as text

### Implementation Notes

**Threading Architecture:**
```python
# Entity speech runs in background thread with delay
speech_thread = entity_speaks_text_delayed(entity_response, delay_ms=150)

# Saga starts listening immediately (VAD recording begins)
heard = saga_listens_vad(vad, input_dev, stt_model)

# Wait for entity to finish speaking
speech_thread.join(timeout=65)
```

**Why Threading is Required:**
- SSH TTS command is synchronous (blocks until audio completes)
- If entity speaks synchronously, it finishes BEFORE Saga starts listening
- Background thread allows recording to start while entity is still generating audio
- 150ms delay ensures audio input stream is fully initialized

**Name Formatting:**
- Use "Dr Saga" (no period) to avoid TTS saying "Doctor. [pause] Saga"
- Periods cause unnatural pauses in speech synthesis

**Timeouts:**
- Entity speech SSH command: 60 seconds
- Speech thread join: 65 seconds (must be >= SSH timeout)
- VAD max recording: 60 seconds (should match speech timeout)

## Purpose

This is not comedy - it's **capability testing**. The goal is to:
- Stress-test Saga's communication abilities
- Develop AI-to-AI communication protocols
- Understand how different AI architectures communicate
- Build toward more sophisticated multi-agent systems

## Future Work

- [ ] Add real-time conversation logging
- [ ] Implement conversation analysis tools
- [ ] Add support for multiple entities in group conversations
- [ ] Create entity personality profiles
- [ ] Develop standardized xenological assessment protocols
- [ ] Integrate with Home Assistant for environmental awareness

## Related

See also:
- `saga_assistant/` - Core Saga assistant implementation
- `squawkers/` - Saga's interactions with physical devices (animatronic parrot)
