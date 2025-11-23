#!/usr/bin/env python3
"""
Saga: Squawkers' Therapist

A very short demo where Saga conducts a therapy session with Squawkers.
She uses STT to "listen" to Squawkers' sounds.
Since Squawkers just makes parrot noises, Saga mishears them as words.
But she's a professional, so she takes it all very seriously.
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
#STT_MODEL = "tiny"
STT_MODEL = "base"  # Perfect for hilarious mishearings!
# "base" hallucinates words from parrot sounds (FEATURE, not bug!)
# "small" and above are too accurate and just ignore the parrot noises
RECORDING_DURATION = 2.0  # Listen for 3 seconds after Squawkers makes noise


def find_emeet_input():
    """Find EMEET input device for recording."""
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        if "EMEET" in device['name'] and device['max_input_channels'] > 0:
            return idx
    return None


def saga_speaks(tts_voice, output_device, text):
    """Saga speaks via TTS."""
    print(f"\n🤖 Saga: \"{text}\"")

    audio_chunks = []
    for audio_chunk in tts_voice.synthesize(text):
        audio_chunks.append(audio_chunk.audio_int16_array)

    if audio_chunks:
        audio_array = np.concatenate(audio_chunks)
        sd.play(audio_array, samplerate=tts_voice.config.sample_rate, device=output_device)
        sd.wait()

    # Small delay between speaking and next action
    time.sleep(0.3)


def saga_listens(stt_model, input_device, duration=3.0):
    """Saga listens and transcribes what she hears."""
    print(f"\n🎧 Saga: *listening for {duration}s...*")

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
        print(f"👂 Saga heard: \"{text}\"")
    else:
        print(f"👂 Saga heard: *nothing intelligible*")

    return text


def squawkers_makes_noise(squawkers, action_name, description):
    """Squawkers makes a sound."""
    print(f"\n🦜 Squawkers: *{description}*")
    method = getattr(squawkers, action_name)
    method()
    time.sleep(0.5)  # Let the IR command send and sound start


def main():
    """Run the short demo."""

    print("\n" + "=" * 60)
    print("SAGA: SQUAWKERS' THERAPIST")
    print("(A very short therapy session)")
    print("=" * 60)

    # Initialize everything
    print("\nInitializing...")

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
    print("Loading Whisper STT model (this may take a moment)...")
    stt_model = WhisperModel(STT_MODEL, device="cpu", compute_type="int8")

    # Audio devices
    # Use EMEET microphone for recording (listening to Squawkers)
    input_dev = find_emeet_input()
    if input_dev is None:
        input_dev = sd.default.device[0]
        print("⚠️  EMEET mic not found, using default input")
    else:
        print(f"✓ Using EMEET microphone for recording (device {input_dev})")

    # Use default speaker for Saga's voice (avoids device conflicts)
    output_dev = sd.default.device[1]
    print(f"✓ Using default speaker for Saga's voice (device {output_dev})")

    print("\n✓ Ready!\n")
    time.sleep(1)

    # THE SHOW
    print("=" * 60)

    # Exchange 1
    saga_speaks(tts_voice, output_dev, "Hello, Squawkers. How are you today?")
    squawkers_makes_noise(squawkers, "button_e", "Custom response!")
    heard = saga_listens(stt_model, input_dev, duration=RECORDING_DURATION)

    if heard:
        saga_speaks(tts_voice, output_dev, f"I heard {heard}. Go on.")
    else:
        saga_speaks(tts_voice, output_dev, "Tell me more.")

    # Exchange 2
    squawkers_makes_noise(squawkers, "gag_a", "Squawk!")
    heard = saga_listens(stt_model, input_dev, duration=RECORDING_DURATION)

    if heard:
        saga_speaks(tts_voice, output_dev, f"Interesting. {heard}. I see.")
    else:
        saga_speaks(tts_voice, output_dev, "Right. Continue.")

    # Exchange 3 - Squawkers continues!
    squawkers_makes_noise(squawkers, "button_b", "Custom response!")
    heard = saga_listens(stt_model, input_dev, duration=RECORDING_DURATION)

    if heard:
        saga_speaks(tts_voice, output_dev, f"{heard}. Yes. That's quite common.")
    else:
        saga_speaks(tts_voice, output_dev, "Uh huh. I understand.")

    # Exchange 4
    saga_speaks(tts_voice, output_dev, "And how does that make you feel?")
    squawkers_makes_noise(squawkers, "gag_c", "More squawking!")
    heard = saga_listens(stt_model, input_dev, duration=RECORDING_DURATION)

    if heard:
        saga_speaks(tts_voice, output_dev, f"Yes. {heard}. That makes sense.")
    else:
        saga_speaks(tts_voice, output_dev, "I see. Go on.")

    # Exchange 5
    squawkers_makes_noise(squawkers, "gag_d", "Warbling!")
    heard = saga_listens(stt_model, input_dev, duration=RECORDING_DURATION)

    if heard:
        saga_speaks(tts_voice, output_dev, f"Hmmm. {heard}. Fascinating.")
    else:
        saga_speaks(tts_voice, output_dev, "Hmmm. Noted.")

    # Finale
    time.sleep(0.5)
    saga_speaks(tts_voice, output_dev, "I think we've made real progress today. Same time next week?")

    print("\n" + "=" * 60)
    print("~ fin ~")
    print("=" * 60)
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
