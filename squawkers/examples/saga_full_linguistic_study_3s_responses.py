#!/usr/bin/env python3
"""
Saga: Complete Linguistic Analysis of Subject "Squawkers"

Dr. Saga conducts a comprehensive anthropological study of Subject Squawkers.
She believes he is a human from a remote culture and systematically tests
ALL available response buttons to document his language.

She will:
- Test Response Buttons (A-F)
- Test Gags responses (A-F)
- Analyze phonetic patterns
- Attempt to construct a grammar
- Provide comprehensive conclusions

This is going to be hilarious.
"""

import sys
import time
import numpy as np
import sounddevice as sd
from pathlib import Path
from collections import Counter

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


def test_response(squawkers, stt_model, input_dev, method_name, label, test_num, reset_after=False):
    """Test a response and record what we hear."""
    print(f"\n{'─' * 60}")
    print(f"TEST {test_num}: {label}")
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

    # Trigger parrot IMMEDIATELY (no delay - recording already started)
    method = getattr(squawkers, method_name)
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

    # If this triggers dance, reset afterwards
    if reset_after:
        time.sleep(1.0)
        squawkers.reset()
        print("🛑 Dance interrupted with RESET")

    return heard


def analyze_words(responses):
    """Analyze word frequency for 'phonetic patterns'."""
    all_words = []
    for text in responses.values():
        if text:
            # Simple word split
            words = text.lower().replace("!", "").replace("?", "").replace(".", "").split()
            all_words.extend(words)

    if not all_words:
        return None

    # Get most common words
    word_counts = Counter(all_words)
    return word_counts.most_common(5)


def main():
    """Run the complete anthropological study."""

    print("\n" + "=" * 70)
    print("COMPLETE LINGUISTIC ANALYSIS: SUBJECT 'SQUAWKERS'")
    print("Principal Investigator: Dr. Saga")
    print("Study: Comprehensive Documentation of Remote Culture Language")
    print("=" * 70)

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
    print("\n" + "=" * 70)
    print("SESSION START - COMPREHENSIVE STUDY")
    print("=" * 70)

    saga_speaks(tts_voice, output_dev, "Recording now. Subject Squawkers, comprehensive linguistic analysis, session one.")
    time.sleep(0.5)

    saga_speaks(tts_voice, output_dev, "I have obtained access to the subject's complete communication interface.")
    time.sleep(0.5)

    saga_speaks(tts_voice, output_dev, "I will systematically elicit all available responses to fully document the language system.")
    time.sleep(1)

    # Store all responses
    all_responses = {}
    test_num = 1

    # PHASE 1: Response Buttons
    print("\n" + "=" * 70)
    print("PHASE 1: RESPONSE SET ALPHA (Buttons A-F)")
    print("=" * 70)

    saga_speaks(tts_voice, output_dev, "Beginning phase one. Response set alpha.")

    button_responses = {}

    # Varied responses to avoid monotony
    button_comments = [
        "Fascinating.",
        "Interesting variation.",
        "Noted.",
        "Remarkable.",
        "Most intriguing."
    ]

    for idx, letter in enumerate(['a', 'b', 'd', 'e', 'f']):  # Skip C for now
        heard = test_response(squawkers, stt_model, input_dev,
                            f'button_{letter}',
                            f'Response Button {letter.upper()}',
                            test_num)
        button_responses[f'button_{letter}'] = heard
        all_responses[f'button_{letter}'] = heard
        saga_speaks(tts_voice, output_dev, button_comments[idx])
        test_num += 1

        if test_num == 3:  # After button B, acknowledge skipping C
            print(f"\n{'─' * 60}")
            print(f"NOTE: Button C")
            print(f"{'─' * 60}")
            print(f"⚠️  SKIPPED FOR NOW - Will revisit if more data needed")
            saga_speaks(tts_voice, output_dev, "Skipping button C temporarily.")
            test_num += 1

    time.sleep(0.5)
    saga_speaks(tts_voice, output_dev, "Phase one complete. Proceeding to phase two.")

    # PHASE 2: Gags
    print("\n" + "=" * 70)
    print("PHASE 2: RESPONSE SET BETA (Gags A-F)")
    print("=" * 70)

    saga_speaks(tts_voice, output_dev, "Beginning phase two. Response set beta.")

    gag_responses = {}

    # Varied responses for gags
    gag_comments = [
        "Curious.",
        "Quite distinct.",
        "I see.",
        "Notable phonetic shift.",
        "Interesting.",
        "Significant variation."
    ]

    for idx, letter in enumerate(['a', 'b', 'c', 'd', 'e', 'f']):
        # Gag F triggers dance, handle specially
        if letter == 'f':
            heard = test_response(squawkers, stt_model, input_dev,
                                f'gag_{letter}',
                                f'Gag Response {letter.upper()}',
                                test_num,
                                reset_after=False)  # Don't auto-reset
            gag_responses[f'gag_{letter}'] = heard
            all_responses[f'gag_{letter}'] = heard
            # Saga interrupts the dance
            saga_speaks(tts_voice, output_dev, "Thank you. That's enough for now.")
            squawkers.reset()
            print("🛑 Dance interrupted with RESET")
        else:
            heard = test_response(squawkers, stt_model, input_dev,
                                f'gag_{letter}',
                                f'Gag Response {letter.upper()}',
                                test_num,
                                reset_after=False)
            gag_responses[f'gag_{letter}'] = heard
            all_responses[f'gag_{letter}'] = heard
            saga_speaks(tts_voice, output_dev, gag_comments[idx])

        test_num += 1

    time.sleep(0.5)
    saga_speaks(tts_voice, output_dev, "Phase two complete. Beginning analysis.")

    # ANALYSIS
    print("\n" + "=" * 70)
    print("COMPREHENSIVE ANALYSIS")
    print("=" * 70)

    time.sleep(1)
    saga_speaks(tts_voice, output_dev, "Comprehensive analysis follows.")
    time.sleep(0.5)

    # Count intelligible responses
    intelligible_count = sum(1 for v in all_responses.values() if v)
    total_count = len(all_responses)

    print(f"\n📊 STATISTICAL ANALYSIS:")
    print(f"   Total stimuli tested: {total_count}")
    print(f"   Intelligible responses: {intelligible_count}")
    print(f"   Success rate: {intelligible_count/total_count*100:.1f}%")

    saga_speaks(tts_voice, output_dev,
               f"The subject produced intelligible vocalisations in {intelligible_count} of {total_count} trials.")
    time.sleep(0.5)

    if intelligible_count > 8:
        saga_speaks(tts_voice, output_dev,
                   "This indicates a highly developed linguistic capacity.")
    elif intelligible_count > 4:
        saga_speaks(tts_voice, output_dev,
                   "This suggests moderate linguistic competence with possible dialectal variation.")
    else:
        saga_speaks(tts_voice, output_dev,
                   "The subject's language appears highly divergent or context-dependent.")

    # Word frequency analysis
    time.sleep(0.5)
    saga_speaks(tts_voice, output_dev, "Analyzing phonetic patterns.")

    word_freq = analyze_words(all_responses)

    if word_freq and len(word_freq) > 0:
        print(f"\n📝 PHONETIC PATTERN ANALYSIS:")
        print(f"   Most frequent lexemes:")
        for word, count in word_freq:
            print(f"     - '{word}': {count} occurrences")

        most_common = word_freq[0][0]
        saga_speaks(tts_voice, output_dev,
                   f"The most frequently occurring lexeme is '{most_common}'. This may indicate a core grammatical element.")
    else:
        saga_speaks(tts_voice, output_dev,
                   "Insufficient data for phonetic pattern analysis.")

    # Grammar construction attempt
    time.sleep(0.5)
    saga_speaks(tts_voice, output_dev, "Attempting grammatical construction.")

    # Find responses with multiple words
    multi_word = [(k, v) for k, v in all_responses.items() if v and len(v.split()) > 2]

    if len(multi_word) > 2:
        print(f"\n📖 GRAMMATICAL ANALYSIS:")
        print(f"   Complex utterances identified: {len(multi_word)}")
        for key, utterance in multi_word[:3]:
            print(f"     - {key}: \"{utterance}\"")

        saga_speaks(tts_voice, output_dev,
                   f"The subject produced {len(multi_word)} multi-word utterances, suggesting syntactic structure.")
    else:
        print(f"\n📖 GRAMMATICAL ANALYSIS:")
        print(f"   Limited multi-word utterances detected")
        saga_speaks(tts_voice, output_dev,
                   "Grammatical structure remains unclear. Further study required.")

    # Conclusions
    time.sleep(1)
    print("\n" + "=" * 70)
    print("CONCLUSIONS")
    print("=" * 70)

    saga_speaks(tts_voice, output_dev, "Preliminary conclusions.")
    time.sleep(0.5)

    if intelligible_count > 6:
        saga_speaks(tts_voice, output_dev,
                   "Subject Squawkers demonstrates a complex linguistic system with distinct response patterns.")
        time.sleep(0.5)
        saga_speaks(tts_voice, output_dev,
                   "I recommend longitudinal study to document contextual usage and pragmatic function.")
    else:
        saga_speaks(tts_voice, output_dev,
                   "The subject's communication system is highly specialized or culturally specific.")
        time.sleep(0.5)
        saga_speaks(tts_voice, output_dev,
                   "I recommend immersive fieldwork to establish cultural context.")

    # ADDITIONAL DATA COLLECTION - Button C
    time.sleep(1)
    print("\n" + "=" * 70)
    print("ADDITIONAL DATA COLLECTION")
    print("=" * 70)

    if intelligible_count < 8:
        saga_speaks(tts_voice, output_dev, "Data set insufficient for confident analysis.")
        time.sleep(0.5)
        saga_speaks(tts_voice, output_dev, "I must collect the previously omitted data point.")
        time.sleep(0.5)
        saga_speaks(tts_voice, output_dev, "Testing button C despite potential external effects.")

        heard = test_response(squawkers, stt_model, input_dev,
                            'button_c',
                            'Response Button C',
                            test_num)
        button_responses['button_c'] = heard
        all_responses['button_c'] = heard
        saga_speaks(tts_voice, output_dev, "Data point acquired.")

        # Recalculate statistics
        intelligible_count = sum(1 for v in all_responses.values() if v)
        total_count = len(all_responses)

        print(f"\n📊 UPDATED STATISTICS:")
        print(f"   Total stimuli tested: {total_count}")
        print(f"   Intelligible responses: {intelligible_count}")
        print(f"   Success rate: {intelligible_count/total_count*100:.1f}%")
    else:
        saga_speaks(tts_voice, output_dev, "Data set sufficient. Button C remains omitted.")

    time.sleep(0.5)
    saga_speaks(tts_voice, output_dev, "End recording. Report to follow.")

    # FINAL SUMMARY
    print("\n" + "=" * 70)
    print("SESSION COMPLETE - FIELD NOTES SUMMARY")
    print("=" * 70)

    print("\n📋 RESPONSE SET ALPHA (Buttons):")
    for key, heard in button_responses.items():
        label = key.replace('button_', 'Button ').upper()
        if heard:
            print(f"  {label}: \"{heard}\"")
        else:
            print(f"  {label}: [unintelligible]")

    print("\n📋 RESPONSE SET BETA (Gags):")
    for key, heard in gag_responses.items():
        label = key.replace('gag_', 'Gag ').upper()
        if heard:
            print(f"  {label}: \"{heard}\"")
        else:
            print(f"  {label}: [unintelligible]")

    print(f"\n📊 SUMMARY STATISTICS:")
    print(f"  Total responses documented: {total_count}")
    print(f"  Intelligible utterances: {intelligible_count}")
    print(f"  Analysis confidence: {'High' if intelligible_count > 8 else 'Moderate' if intelligible_count > 4 else 'Low'}")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Study interrupted!")
        print("Partial data may be analyzed separately.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
