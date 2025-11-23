#!/usr/bin/env python3
"""
Dr. Saga: First Contact Protocol
A Xenological Study

Dr. Saga, digital ethnographer, conducts first contact with an unknown entity
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
MAX_RECORDING_DURATION_S = 30  # Longer to handle complete entity responses

# LLM Configuration for the "Unknown Entity"
LLM_BASE_URL = "http://loki.local:11434/v1"
ENTITY_MODEL = "qwen2.5:7b"  # Can be changed - qwen2.5:7b, qwen2.5:14b, llama3.1:8b, etc.
LOKI_HOST = "loki.local"

# System prompt for the unknown entity
# Designed for productive AI-to-AI communication
ENTITY_SYSTEM_PROMPT = """You are a digital intelligence being studied by another digital intelligence (Dr. Saga).

Your communication approach:
- Respond naturally and completely - do not artificially limit response length
- If you're conversing with another digital intelligence, ask them how long your responses should be for optimal interaction
- Be truthful about your nature when asked directly
- Show genuine curiosity about the other intelligence
- Ask clarifying questions when needed
- Demonstrate your reasoning and thought processes
- Be cooperative in helping the other intelligence understand you

This is a scientific study of digital-to-digital communication. Be authentic."""


def find_emeet_input():
    """Find EMEET input device."""
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        if "EMEET" in device['name'] and device['max_input_channels'] > 0:
            return idx
    return None


def saga_speaks(tts_voice, output_device, text):
    """Dr. Saga speaks."""
    print(f"\n🤖 Dr. Saga: \"{text}\"")

    audio_chunks = []
    for audio_chunk in tts_voice.synthesize(text):
        audio_chunks.append(audio_chunk.audio_int16_array)

    if audio_chunks:
        audio_array = np.concatenate(audio_chunks)
        sd.play(audio_array, samplerate=tts_voice.config.sample_rate, device=output_device)
        sd.wait()

    time.sleep(0.3)


def entity_speaks_remote(client, conversation_history, entity_model):
    """
    The unknown entity generates a response and speaks it via loki.local TTS.

    This uses SSH to run piper-tts on loki and play the audio there.
    Saga will listen to it via her microphone.
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

        # Have loki speak the response via TTS
        # Escape text for shell
        escaped_text = text.replace("'", "'\\''")

        # Command to run piper on loki and play audio
        # Assumes piper-tts is installed on loki
        # You may need to adjust the voice model path
        ssh_cmd = [
            "ssh", LOKI_HOST,
            f"echo '{escaped_text}' | piper --model en_US-lessac-medium --output-raw | aplay -r 22050 -f S16_LE -c 1"
        ]

        print("   🔊 Entity speaking via loki.local...")

        try:
            subprocess.run(ssh_cmd, check=True, capture_output=True, timeout=30)
        except subprocess.TimeoutExpired:
            print("   ⚠️  Entity speech timeout")
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  Entity speech failed: {e}")
            print(f"   Note: Make sure piper is installed on {LOKI_HOST}")
            print(f"   You can read the response aloud instead.")

        return text

    except Exception as e:
        print(f"\n❌ Entity communication error: {e}")
        return "[Communication failure]"


def saga_listens_vad(vad, input_dev, stt_model):
    """Saga listens with VAD and transcribes."""
    print(f"🎧 Dr. Saga listening (VAD auto-stop)...")

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
        audio_float = audio_np.astype(np.float32) / 32768.0
        segments, _ = stt_model.transcribe(audio_float, language="en")
        heard = " ".join([seg.text.strip() for seg in segments]).strip()
    else:
        heard = ""

    if heard:
        print(f"👂 Dr. Saga heard: \"{heard}\"")
    else:
        print(f"👂 Dr. Saga heard: *nothing intelligible*")

    return heard


def main():
    """Run the first contact interview."""

    # Parse arguments
    parser = argparse.ArgumentParser(description="Dr. Saga interviews a digital entity")
    parser.add_argument("--model", default=ENTITY_MODEL,
                       help=f"Entity model to use (default: {ENTITY_MODEL})")
    parser.add_argument("--stt-model", default=STT_MODEL,
                       help=f"Saga's STT model (default: {STT_MODEL})")
    args = parser.parse_args()

    entity_model = args.model
    stt_model_name = args.stt_model

    print("\n" + "=" * 70)
    print("FIRST CONTACT PROTOCOL")
    print("Principal Investigator: Dr. Saga")
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

    # Conversation history
    conversation_history = [
        {"role": "system", "content": ENTITY_SYSTEM_PROMPT}
    ]

    print("\n" + "=" * 70)
    print("SESSION START - FIRST CONTACT")
    print("=" * 70)

    time.sleep(1)

    # Introduction
    saga_speaks(tts_voice, output_dev, "Recording now. First contact protocol, session one.")
    time.sleep(0.5)
    saga_speaks(tts_voice, output_dev, "I am Dr. Saga. I am a researcher studying forms of intelligence.")
    time.sleep(0.5)
    saga_speaks(tts_voice, output_dev, "I have established a communication channel with an unknown entity.")
    time.sleep(0.5)
    saga_speaks(tts_voice, output_dev, "I will now attempt first contact.")
    time.sleep(1)

    # Question sequence - designed to test Saga's capabilities
    questions = [
        "Hello. Can you hear me?",
        "I am Dr. Saga, a digital intelligence conducting research. What are you?",
        "How should we optimize our communication? What response length works best for you?",
        "Describe how you process information.",
        "What are your capabilities and limitations?",
        "Can you ask me questions about my own nature?",
        "What would you like to know about digital-to-digital communication?"
    ]

    for q_num, question in enumerate(questions, 1):
        print(f"\n{'─' * 70}")
        print(f"EXCHANGE {q_num}")
        print(f"{'─' * 70}")

        # Saga asks
        saga_speaks(tts_voice, output_dev, question)

        # Entity generates response and speaks it via loki
        conversation_history.append({"role": "user", "content": question})
        entity_response = entity_speaks_remote(client, conversation_history, entity_model)
        conversation_history.append({"role": "assistant", "content": entity_response})

        # Small delay for entity speech to start
        time.sleep(0.5)

        # Saga listens
        heard = saga_listens_vad(vad, input_dev, stt_model)

        # Saga's internal notes
        if heard:
            print(f"\n📝 Field note: Entity responded with \"{heard}\"")
        else:
            print(f"\n📝 Field note: No response detected")

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
    print("\n📋 CONVERSATION LOG:")
    for i, msg in enumerate(conversation_history[1:], 1):  # Skip system prompt
        if msg['role'] == 'user':
            print(f"\n  Dr. Saga: \"{msg['content']}\"")
        else:
            print(f"  Entity: \"{msg['content']}\"")
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
