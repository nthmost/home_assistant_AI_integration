#!/usr/bin/env python3
"""
Saga: Anthropologist Studying Subject "Squawkers"

Saga has been granted access to all of Squawkers' response buttons.
She believes he is a human from a remote culture.
She methodically triggers each button and documents what she hears.

This will be hilarious.
"""

import sys
import time
import numpy as np
import sounddevice as sd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from squawkers.squawkers_full import SquawkersFull
from saga_assistant.ha_client import HomeAssistantClient
from piper import PiperVoice
from faster_whisper import WhisperModel

# Configuration
TTS_VOICE = "en_GB-semaine-medium"
STT_MODEL = "base"  # Perfect for hilarious mishearings!
RECORDING_DURATION = 3.0  # Listen for 3 seconds after each button


def find_emeet_input():
    """Find EMEET input device for recording."""
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        if "EMEET" in device['name'] and device['max_input_channels'] > 0:
            return idx
    return None


def saga_speaks(tts_voice, output_device, text):
    """Saga speaks via TTS."""
    print(f"\n🤖 Dr. Saga: \"{text}\"")

    audio_chunks = []
    for audio_chunk in tts_voice.synthesize(text):
        audio_chunks.append(audio_chunk.audio_int16_array)

    if audio_chunks:
        audio_array = np.concatenate(audio_chunks)
        sd.play(audio_array, samplerate=tts_voice.config.sample_rate, device=output_device)
        sd.wait()

    time.sleep(0.3)


def saga_listens(stt_model, input_device, duration=2.0):
    """Saga listens and transcribes what she hears."""
    print(f"🎧 *listening for {duration}s...*")

    # Record audio
    audio = sd.rec(
        int(duration * 16000),
        samplerate=16000,
        channels=1,
        dtype='float32',
        device=input_device
    )
    sd.wait()

    # Transcribe
    audio_np = audio.flatten()
    segments, _ = stt_model.transcribe(audio_np, language="en")

    text = " ".join([seg.text.strip() for seg in segments]).strip()

    if text:
        print(f"📝 Subject said: \"{text}\"")
    else:
        print(f"📝 Subject said: [unintelligible vocalisation]")

    return text


def test_button(squawkers, stt_model, input_dev, button_name, button_num):
    """Test a button and record the response."""
    print(f"\n{'─' * 60}")
    print(f"TEST {button_num}: Response Button {button_name.upper()}")
    print(f"{'─' * 60}")

    # Start recording FIRST
    print(f"🎧 *listening for {RECORDING_DURATION}s...*")

    # Start recording in background
    audio = sd.rec(
        int(RECORDING_DURATION * 16000),
        samplerate=16000,
        channels=1,
        dtype='float32',
        device=input_dev
    )

    # Small delay to ensure recording started, then trigger button
    time.sleep(0.2)
    method = getattr(squawkers, f"button_{button_name}")
    method()

    # Wait for recording to complete
    sd.wait()

    # Transcribe
    audio_np = audio.flatten()
    segments, _ = stt_model.transcribe(audio_np, language="en")
    heard = " ".join([seg.text.strip() for seg in segments]).strip()

    if heard:
        print(f"📝 Subject said: \"{heard}\"")
    else:
        print(f"📝 Subject said: [unintelligible vocalisation]")

    return heard


def main():
    """Run the anthropological study."""

    print("\n" + "=" * 60)
    print("FIELD NOTES: SUBJECT 'SQUAWKERS'")
    print("Principal Investigator: Dr. Saga")
    print("Study: Linguistic Analysis of Remote Culture")
    print("=" * 60)

    # Initialize everything
    print("\nInitializing research equipment...")

    # Home Assistant & Squawkers
    client = HomeAssistantClient()
    squawkers = SquawkersFull(client)

    # TTS
    models_dir = Path.home() / ".local" / "share" / "piper" / "voices"
    model_file = models_dir / f"{TTS_VOICE}.onnx"
    config_file = models_dir / f"{TTS_VOICE}.onnx.json"

    if not (model_file.exists() and config_file.exists()):
        print(f"❌ TTS voice not found. Run Saga assistant first.")
        return 1

    tts_voice = PiperVoice.load(str(model_file), config_path=str(config_file))

    # STT
    print("Loading speech recognition model...")
    stt_model = WhisperModel(STT_MODEL, device="cpu", compute_type="int8")

    # Audio devices
    input_dev = find_emeet_input()
    if input_dev is None:
        input_dev = sd.default.device[0]

    output_dev = sd.default.device[1]

    print("✓ Equipment ready!\n")
    time.sleep(1)

    # BEGIN STUDY
    print("\n" + "=" * 60)
    print("SESSION START")
    print("=" * 60)

    saga_speaks(tts_voice, output_dev, "Recording now. Subject Squawkers, day one, initial contact.")
    time.sleep(0.5)

    saga_speaks(tts_voice, output_dev, "I have obtained access to the subject's communication interface.")
    time.sleep(0.5)

    saga_speaks(tts_voice, output_dev, "I will now systematically elicit responses to document his language.")
    time.sleep(1)

    # Test Response Buttons A through F
    responses = {}

    saga_speaks(tts_voice, output_dev, "Beginning with response set alpha.")

    responses['a'] = test_button(squawkers, stt_model, input_dev, 'a', 1)
    saga_speaks(tts_voice, output_dev, "Fascinating. Continuing.")

    responses['b'] = test_button(squawkers, stt_model, input_dev, 'b', 2)
    saga_speaks(tts_voice, output_dev, "Interesting variation.")

    # Skip C to avoid the Alexa fart trigger
    print(f"\n{'─' * 60}")
    print(f"TEST 3: Response Button C")
    print(f"{'─' * 60}")
    print(f"⚠️  SKIPPED - Known to trigger external device")
    saga_speaks(tts_voice, output_dev, "Skipping stimulus three for ethical reasons.")

    responses['d'] = test_button(squawkers, stt_model, input_dev, 'd', 4)
    saga_speaks(tts_voice, output_dev, "Remarkable consistency.")

    responses['e'] = test_button(squawkers, stt_model, input_dev, 'e', 5)
    saga_speaks(tts_voice, output_dev, "Notable phonetic shift.")

    responses['f'] = test_button(squawkers, stt_model, input_dev, 'f', 6)

    # Analysis
    print("\n" + "=" * 60)
    print("PRELIMINARY ANALYSIS")
    print("=" * 60)

    time.sleep(1)
    saga_speaks(tts_voice, output_dev, "Preliminary analysis follows.")
    time.sleep(0.5)

    # Count how many were intelligible
    intelligible = sum(1 for v in responses.values() if v)
    total = len(responses)

    if intelligible > 3:
        saga_speaks(tts_voice, output_dev,
                   f"The subject produced intelligible vocalisations in {intelligible} of {total} trials.")
        time.sleep(0.5)
        saga_speaks(tts_voice, output_dev,
                   "This suggests a complex linguistic system.")
    elif intelligible > 0:
        saga_speaks(tts_voice, output_dev,
                   f"The subject produced some intelligible speech. Further study required.")
    else:
        saga_speaks(tts_voice, output_dev,
                   "The subject's language appears highly divergent from known dialects.")
        time.sleep(0.5)
        saga_speaks(tts_voice, output_dev,
                   "I suspect tonal or contextual elements I have not yet identified.")

    time.sleep(1)
    saga_speaks(tts_voice, output_dev, "End recording. Further analysis pending.")

    print("\n" + "=" * 60)
    print("SESSION COMPLETE")
    print("=" * 60)
    print("\nFIELD NOTES SUMMARY:")
    for button, heard in responses.items():
        if heard:
            print(f"  Button {button.upper()}: \"{heard}\"")
        else:
            print(f"  Button {button.upper()}: [unintelligible]")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Study interrupted!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
