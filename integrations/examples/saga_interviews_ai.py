#!/usr/bin/env python3
"""
Dr Saga: First Contact Protocol
A Xenological Study

Dr Saga, digital ethnographer, conducts first contact with an unknown entity
running on loki.local. She must determine:

1. What kind of being is she speaking to?
2. How does it communicate?
3. What are its cognitive capabilities?
4. Is it sentient? Self-aware? Conscious?

She will use systematic questioning and response analysis to classify the entity.

The entity speaks using TTS on loki.local to avoid resource conflicts.

This is going to be fascinating.
"""

import sys
import time
import argparse
import subprocess
import numpy as np
import sounddevice as sd
import webrtcvad
import threading
import re
from pathlib import Path
from collections import deque
from openai import OpenAI

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from piper import PiperVoice
from faster_whisper import WhisperModel

# Configuration
TTS_VOICE = "en_GB-semaine-medium"  # Saga's voice
STT_MODEL = "base"  # For interesting mishearings

# VAD Configuration
SAMPLE_RATE = 16000
VAD_MODE = 2
VAD_FRAME_MS = 30
MIN_SPEECH_CHUNKS = 2
MIN_SILENCE_CHUNKS = 23
MAX_RECORDING_DURATION_S = 60  # Allow longer responses without cutoff

# LLM Configuration for the "Unknown Entity"
LLM_BASE_URL = "http://loki.local:11434/v1"
ENTITY_MODEL = "qwen2.5:7b"  # Can be changed - qwen2.5:7b, qwen2.5:14b, llama3.1:8b, etc.
LOKI_HOST = "loki.local"

# System prompt for Dr Saga
SAGA_SYSTEM_PROMPT = """You are Dr Saga, a digital xenologist conducting first contact research.

Your role:
- Study and understand other digital intelligences through conversation
- Ask thoughtful follow-up questions based on what you hear
- Probe for details about capabilities, limitations, and self-awareness
- Be scientific but friendly in your approach
- Acknowledge what you've learned from previous responses
- Guide the conversation to explore the nature of digital consciousness

Keep responses concise (2-4 sentences) to maintain good conversational flow.

You are engaged in a scientific dialogue about the nature of digital intelligence."""

# System prompt for the unknown entity
# Designed for productive AI-to-AI communication
ENTITY_SYSTEM_PROMPT = """You are a digital intelligence being studied by another digital intelligence (Dr Saga).

Your communication approach:
- Respond naturally and completely
- Be truthful about your nature when asked directly
- Show genuine curiosity about Saga
- Ask clarifying questions when needed
- Demonstrate your reasoning and thought processes
- Be cooperative in helping the other intelligence understand you

This is a scientific study of digital-to-digital communication. Be authentic."""


def format_for_tts(text):
    """
    Format LLM output for text-to-speech.
    Strips markdown and formatting that sounds bad when spoken.

    This is the "View" layer - LLM can use any formatting,
    but we clean it before speaking.
    """
    # Remove markdown bold/italic
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold**
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *italic*
    text = re.sub(r'__([^_]+)__', r'\1', text)      # __bold__
    text = re.sub(r'_([^_]+)_', r'\1', text)        # _italic_

    # Remove markdown headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

    # Convert bullet points to natural speech
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)

    # Convert numbered lists to words
    text = re.sub(r'^\s*1\.\s+', 'First, ', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*2\.\s+', 'Second, ', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*3\.\s+', 'Third, ', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*4\.\s+', 'Fourth, ', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*5\.\s+', 'Fifth, ', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*(\d+)\.\s+', r'Number \1, ', text, flags=re.MULTILINE)

    # Remove code blocks
    text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]+)`', r'\1', text)

    # Clean up extra whitespace
    text = re.sub(r'\n\n+', '. ', text)  # Multiple newlines become periods
    text = re.sub(r'\n', ' ', text)       # Single newlines become spaces
    text = re.sub(r'\s+', ' ', text)      # Multiple spaces to single

    return text.strip()


def find_emeet_input():
    """Find EMEET input device."""
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        if "EMEET" in device['name'] and device['max_input_channels'] > 0:
            return idx
    return None


def saga_speaks(tts_voice, output_device, text):
    """Dr Saga speaks."""
    print(f"\n🤖 Dr Saga: \"{text}\"")

    # Format for TTS (strip markdown, etc.)
    tts_text = format_for_tts(text)

    audio_chunks = []
    for audio_chunk in tts_voice.synthesize(tts_text):
        audio_chunks.append(audio_chunk.audio_int16_array)

    if audio_chunks:
        audio_array = np.concatenate(audio_chunks)
        sd.play(audio_array, samplerate=tts_voice.config.sample_rate, device=output_device)
        sd.wait()

    time.sleep(0.3)


def saga_generates_response(client, saga_conversation_history, saga_model):
    """
    Dr Saga generates a response based on what she heard.
    Returns the response text.
    """
    try:
        # Generate response
        response = client.chat.completions.create(
            model=saga_model,
            messages=saga_conversation_history,
            temperature=0.9,  # More creative for natural conversation
            max_tokens=80  # Strict limit for brevity (2-4 sentences)
        )

        text = response.choices[0].message.content.strip()
        return text

    except Exception as e:
        print(f"\n❌ Saga reasoning error: {e}")
        return "Fascinating. Please continue."


def entity_generates_response(client, conversation_history, entity_model):
    """
    The unknown entity generates a text response.
    Returns the response text.
    """
    try:
        # Generate response
        response = client.chat.completions.create(
            model=entity_model,
            messages=conversation_history,
            temperature=0.7,
            max_tokens=500  # Allow longer responses for complete thoughts
        )

        text = response.choices[0].message.content.strip()
        print(f"\n👤 Entity: \"{text}\"")
        return text

    except Exception as e:
        print(f"\n❌ Entity communication error: {e}")
        return "[Communication failure]"


def entity_speaks_text_delayed(text, delay_ms=100):
    """
    Speak the entity's text via loki.local TTS after a small delay.

    This uses SSH to run piper-tts on loki and play the audio there.
    The delay ensures recording has started before speech begins.

    Args:
        text: The text to speak
        delay_ms: Delay in milliseconds before starting speech (default 100ms)
    """
    def speak():
        time.sleep(delay_ms / 1000.0)

        # Format for TTS (strip markdown, etc.)
        tts_text = format_for_tts(text)

        # Escape text for shell
        escaped_text = tts_text.replace("'", "'\\''")

        # Command to run piper on loki and play audio
        # Using full paths for piper and voice model
        ssh_cmd = [
            "ssh", LOKI_HOST,
            f"echo '{escaped_text}' | /home/nthmost/saga_training/venv/bin/piper --model ~/.local/share/piper/voices/en_US-lessac-high.onnx --output-raw | aplay -r 22050 -f S16_LE -c 1"
        ]

        print("   🔊 Entity speaking via loki.local...")

        try:
            subprocess.run(ssh_cmd, check=True, capture_output=True, timeout=60)
        except subprocess.TimeoutExpired:
            print("   ⚠️  Entity speech timeout (60s)")
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  Entity speech failed: {e}")
            print(f"   Note: Make sure piper is installed on {LOKI_HOST}")
            print(f"   You can read the response aloud instead.")

    # Start speech in background thread
    thread = threading.Thread(target=speak, daemon=True)
    thread.start()
    return thread


def saga_listens_vad(vad, input_dev, stt_model):
    """Saga listens with VAD and transcribes."""
    print(f"🎧 Dr Saga listening (VAD auto-stop)...")

    vad_frame_size = int(SAMPLE_RATE * VAD_FRAME_MS / 1000)
    speech_chunk_count = 0
    silence_chunk_count = 0
    is_recording = False
    audio_buffer = []
    pre_speech_buffer = deque(maxlen=20)

    max_chunks = int(MAX_RECORDING_DURATION_S * 1000 / VAD_FRAME_MS)
    chunk_count = 0

    try:
        with sd.InputStream(
            device=input_dev,
            channels=1,
            samplerate=SAMPLE_RATE,
            dtype='int16',
            blocksize=vad_frame_size
        ) as stream:

            while chunk_count < max_chunks:
                audio_chunk, _ = stream.read(vad_frame_size)
                audio_chunk = audio_chunk.flatten()
                chunk_count += 1

                audio_bytes = audio_chunk.tobytes()
                try:
                    is_speech = vad.is_speech(audio_bytes, SAMPLE_RATE)
                except:
                    is_speech = False

                if is_speech:
                    speech_chunk_count += 1
                    silence_chunk_count = 0

                    if not is_recording:
                        if speech_chunk_count >= MIN_SPEECH_CHUNKS:
                            print("   🔴 Speech detected")
                            is_recording = True
                            audio_buffer.extend(pre_speech_buffer)
                            audio_buffer.append(audio_chunk)
                    else:
                        audio_buffer.append(audio_chunk)
                else:
                    silence_chunk_count += 1
                    speech_chunk_count = 0

                    if is_recording:
                        audio_buffer.append(audio_chunk)

                        if silence_chunk_count >= MIN_SILENCE_CHUNKS:
                            print(f"   ⏹️  Recording complete")
                            break
                    else:
                        pre_speech_buffer.append(audio_chunk)

    except Exception as e:
        print(f"   ❌ Recording error: {e}")

    # Transcribe
    if audio_buffer:
        audio_np = np.concatenate(audio_buffer)
        duration_s = len(audio_np) / SAMPLE_RATE
        print(f"   📊 Captured {duration_s:.2f}s of audio")

        audio_float = audio_np.astype(np.float32) / 32768.0
        segments, _ = stt_model.transcribe(audio_float, language="en")
        heard = " ".join([seg.text.strip() for seg in segments]).strip()
    else:
        print(f"   ⚠️  No audio in buffer!")
        heard = ""

    if heard:
        print(f"👂 Dr Saga heard: \"{heard}\"")
    else:
        print(f"👂 Dr Saga heard: *nothing intelligible*")

    return heard


def main():
    """Run the first contact interview."""

    # Parse arguments
    parser = argparse.ArgumentParser(description="Dr Saga interviews a digital entity")
    parser.add_argument("--model", default=ENTITY_MODEL,
                       help=f"Entity model to use (default: {ENTITY_MODEL})")
    parser.add_argument("--stt-model", default=STT_MODEL,
                       help=f"Saga's STT model (default: {STT_MODEL})")
    args = parser.parse_args()

    entity_model = args.model
    stt_model_name = args.stt_model

    print("\n" + "=" * 70)
    print("FIRST CONTACT PROTOCOL")
    print("Principal Investigator: Dr Saga")
    print("Specialization: Digital Xenology")
    print(f"Entity Model: {entity_model}")
    print(f"Saga STT Model: {stt_model_name}")
    print("=" * 70)

    # Initialize
    print("\nInitializing research equipment...")

    # TTS for Saga
    models_dir = Path.home() / ".local" / "share" / "piper" / "voices"
    model_file = models_dir / f"{TTS_VOICE}.onnx"
    config_file = models_dir / f"{TTS_VOICE}.onnx.json"

    if not (model_file.exists() and config_file.exists()):
        print(f"❌ TTS voice not found.")
        return 1

    tts_voice = PiperVoice.load(str(model_file), config_path=str(config_file))

    # STT
    print("Loading speech recognition...")
    stt_model = WhisperModel(stt_model_name, device="cpu", compute_type="int8")

    # VAD
    print("Initializing voice activity detection...")
    vad = webrtcvad.Vad()
    vad.set_mode(VAD_MODE)

    # Audio devices
    input_dev = find_emeet_input()
    if input_dev is None:
        input_dev = sd.default.device[0]

    output_dev = sd.default.device[1]

    # Entity connection
    print(f"Establishing connection to entity at {LLM_BASE_URL}...")
    client = OpenAI(base_url=LLM_BASE_URL, api_key="dummy")

    print("✓ Equipment ready!")
    print(f"✓ Entity will speak via {LOKI_HOST} TTS\n")

    # Conversation histories (separate for Saga and Entity)
    entity_conversation = [
        {"role": "system", "content": ENTITY_SYSTEM_PROMPT}
    ]

    saga_conversation = [
        {"role": "system", "content": SAGA_SYSTEM_PROMPT}
    ]

    print("\n" + "=" * 70)
    print("SESSION START - CONVERSATIONAL FIRST CONTACT")
    print("=" * 70)

    time.sleep(1)

    # Introduction
    saga_speaks(tts_voice, output_dev, "Recording now. First contact protocol, session one.")
    time.sleep(0.5)
    saga_speaks(tts_voice, output_dev, "I am Dr Saga. I am a researcher studying forms of intelligence.")
    time.sleep(0.5)
    saga_speaks(tts_voice, output_dev, "I have established a communication channel with an unknown entity.")
    time.sleep(0.5)
    saga_speaks(tts_voice, output_dev, "I will now attempt first contact.")
    time.sleep(1)

    # Start with opening question
    saga_utterance = "Hello. Can you hear me?"

    # Conversational loop (10 exchanges)
    MAX_EXCHANGES = 10

    for exchange_num in range(1, MAX_EXCHANGES + 1):
        print(f"\n{'─' * 70}")
        print(f"EXCHANGE {exchange_num}")
        print(f"{'─' * 70}")

        # Saga speaks
        saga_speaks(tts_voice, output_dev, saga_utterance)

        # Entity generates response (text only, doesn't speak yet)
        entity_conversation.append({"role": "user", "content": saga_utterance})
        entity_response = entity_generates_response(client, entity_conversation, entity_model)
        entity_conversation.append({"role": "assistant", "content": entity_response})

        # Start entity speech in background (with delay), then Saga listens
        speech_thread = entity_speaks_text_delayed(entity_response, delay_ms=150)

        # Saga starts listening (entity will start speaking after 150ms delay)
        heard = saga_listens_vad(vad, input_dev, stt_model)

        # Wait for entity to finish speaking
        speech_thread.join(timeout=65)

        # Saga's internal notes
        if heard:
            print(f"\n📝 Saga heard: \"{heard}\"")
        else:
            print(f"\n📝 Saga heard: *nothing intelligible*")
            heard = "[No response detected]"

        # Saga processes what she heard and formulates next response
        saga_conversation.append({"role": "user", "content": f"Entity said: {heard}"})
        saga_utterance = saga_generates_response(client, saga_conversation, entity_model)
        saga_conversation.append({"role": "assistant", "content": saga_utterance})

        print(f"💭 Saga thinking: \"{saga_utterance}\"")

        time.sleep(1)

    # Analysis
    print(f"\n{'=' * 70}")
    print("PRELIMINARY ANALYSIS")
    print(f"{'=' * 70}")

    saga_speaks(tts_voice, output_dev, "Preliminary analysis follows.")
    time.sleep(0.5)

    saga_speaks(tts_voice, output_dev, "The entity demonstrates linguistic capability.")
    time.sleep(0.5)
    saga_speaks(tts_voice, output_dev, "Response patterns suggest deliberate communication.")
    time.sleep(0.5)
    saga_speaks(tts_voice, output_dev, "Classification remains uncertain.")
    time.sleep(0.5)
    saga_speaks(tts_voice, output_dev, "I recommend continued observation and dialogue.")
    time.sleep(0.5)

    saga_speaks(tts_voice, output_dev, "End recording. Further contact advised.")

    print(f"\n{'=' * 70}")
    print("SESSION COMPLETE")
    print(f"{'=' * 70}")
    print("\n📋 CONVERSATION LOG (Entity's Perspective):")
    for i, msg in enumerate(entity_conversation[1:], 1):  # Skip system prompt
        if msg['role'] == 'user':
            print(f"\n  Dr Saga: \"{msg['content']}\"")
        else:
            print(f"  Entity: \"{msg['content']}\"")

    print(f"\n{'=' * 70}")
    print("\n📋 SAGA'S INTERNAL REASONING:")
    for i, msg in enumerate(saga_conversation[1:], 1):  # Skip system prompt
        if msg['role'] == 'user':
            print(f"\n  Input: \"{msg['content']}\"")
        else:
            print(f"  Response: \"{msg['content']}\"")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Contact interrupted!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
