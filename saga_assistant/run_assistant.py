#!/usr/bin/env python3
"""
Saga Voice Assistant - Main orchestration script.

Integrates wakeword detection, STT, LLM, and TTS into a complete voice assistant.
"""

import argparse
import logging
import sys
import time
from pathlib import Path
from enum import Enum

import numpy as np
import sounddevice as sd
from openwakeword.model import Model as WakewordModel
from faster_whisper import WhisperModel
from openai import OpenAI
from piper import PiperVoice

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuration
EMEET_DEVICE_NAME = "EMEET"
WAKEWORD_MODEL = "models/hey_saga_noisy.onnx"
WAKEWORD_THRESHOLD = 0.5
STT_MODEL = "base"
STT_DURATION = 5.0  # seconds
LLM_BASE_URL = "http://loki.local:11434/v1"
LLM_MODEL = "qwen2.5:7b"
TTS_VOICE = "en_GB-semaine-medium"
SAMPLE_RATE = 16000


class AssistantState(Enum):
    """Voice assistant state machine."""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"


class SagaAssistant:
    """Complete voice assistant orchestration."""

    def __init__(self):
        """Initialize all components."""
        self.state = AssistantState.IDLE
        self.emeet_input = None
        self.emeet_output = None

        logger.info("🚀 Initializing Saga Voice Assistant...")

        # Find audio devices
        self._find_audio_devices()

        # Initialize components
        self._init_wakeword()
        self._init_stt()
        self._init_llm()
        self._init_tts()

        logger.info("✅ All components initialized successfully!")

    def _find_audio_devices(self):
        """Find EMEET audio devices."""
        logger.info("🔍 Looking for EMEET audio devices...")

        devices = sd.query_devices()

        for idx, device in enumerate(devices):
            if EMEET_DEVICE_NAME.lower() in device['name'].lower():
                if device['max_input_channels'] > 0 and self.emeet_input is None:
                    self.emeet_input = idx
                    logger.info(f"   ✅ Input: Device {idx} - {device['name']}")

                if device['max_output_channels'] > 0 and self.emeet_output is None:
                    self.emeet_output = idx
                    logger.info(f"   ✅ Output: Device {idx} - {device['name']}")

        if self.emeet_input is None or self.emeet_output is None:
            raise RuntimeError("EMEET audio devices not found")

    def _init_wakeword(self):
        """Initialize wakeword detection."""
        logger.info("🎤 Loading wakeword model...")

        model_path = Path(__file__).parent / WAKEWORD_MODEL
        if not model_path.exists():
            raise FileNotFoundError(f"Wakeword model not found: {model_path}")

        self.wakeword = WakewordModel(
            wakeword_models=[str(model_path)],
            inference_framework="onnx"
        )

        logger.info(f"   ✅ Loaded: {WAKEWORD_MODEL}")

    def _init_stt(self):
        """Initialize speech-to-text."""
        logger.info("🗣️  Loading STT model...")

        self.stt = WhisperModel(
            STT_MODEL,
            device="cpu",
            compute_type="int8"
        )

        logger.info(f"   ✅ Loaded: faster-whisper {STT_MODEL}")

    def _init_llm(self):
        """Initialize LLM client."""
        logger.info("🤖 Connecting to LLM...")

        self.llm = OpenAI(
            base_url=LLM_BASE_URL,
            api_key="ollama"
        )

        self.system_prompt = """You are Saga, a helpful voice assistant for home automation.

Keep responses concise and natural for spoken conversation (1-2 sentences max).
For home automation commands, be direct and confirmatory.
You have a warm, professional personality."""

        logger.info(f"   ✅ Connected to {LLM_MODEL} on loki.local")

    def _init_tts(self):
        """Initialize text-to-speech."""
        logger.info("🔊 Loading TTS voice...")

        # Download voice if needed
        models_dir = Path.home() / ".local" / "share" / "piper" / "voices"
        model_file = models_dir / f"{TTS_VOICE}.onnx"
        config_file = models_dir / f"{TTS_VOICE}.onnx.json"

        if not (model_file.exists() and config_file.exists()):
            raise FileNotFoundError(f"TTS voice not found: {TTS_VOICE}")

        self.tts_voice = PiperVoice.load(str(model_file), config_path=str(config_file))

        logger.info(f"   ✅ Loaded: {TTS_VOICE}")

    def listen_for_wakeword(self) -> bool:
        """
        Listen for wakeword detection.

        Returns:
            True if wakeword detected
        """
        logger.info("👂 Listening for 'Hey Saga'...")

        chunk_duration = 1.28  # seconds (wakeword model requirement)
        chunk_samples = int(SAMPLE_RATE * chunk_duration)

        try:
            with sd.InputStream(
                device=self.emeet_input,
                channels=1,
                samplerate=SAMPLE_RATE,
                dtype='int16'
            ) as stream:
                while True:
                    # Read audio chunk
                    audio, _ = stream.read(chunk_samples)
                    audio = audio.flatten().astype(np.int16)

                    # Run wakeword detection
                    prediction = self.wakeword.predict(audio)

                    # Check if wakeword detected
                    for model_name, score in prediction.items():
                        if score >= WAKEWORD_THRESHOLD:
                            logger.info(f"✅ Wakeword detected! (score: {score:.3f})")
                            return True

        except KeyboardInterrupt:
            return False

    def record_command(self) -> np.ndarray:
        """
        Record voice command after wakeword.

        Returns:
            Audio data as numpy array
        """
        self.state = AssistantState.LISTENING
        logger.info(f"🎤 Recording command for {STT_DURATION}s...")

        audio = sd.rec(
            int(STT_DURATION * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype='int16',
            device=self.emeet_input
        )

        sd.wait()
        logger.info("   ⏹️  Recording complete")

        return audio.flatten()

    def transcribe(self, audio: np.ndarray) -> str:
        """
        Transcribe audio to text.

        Args:
            audio: Audio data

        Returns:
            Transcribed text
        """
        logger.info("🗣️  Transcribing...")

        # Convert int16 to float32
        audio_float = audio.astype(np.float32) / 32768.0

        segments, _ = self.stt.transcribe(
            audio_float,
            language="en",
            beam_size=1,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )

        text = " ".join(segment.text for segment in segments).strip()

        if text:
            logger.info(f"   📝 You said: \"{text}\"")
        else:
            logger.warning("   ⚠️  No speech detected")

        return text

    def generate_response(self, prompt: str) -> str:
        """
        Generate LLM response.

        Args:
            prompt: User input

        Returns:
            LLM response text
        """
        self.state = AssistantState.PROCESSING
        logger.info("🤖 Generating response...")

        try:
            response = self.llm.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )

            response_text = response.choices[0].message.content.strip()
            logger.info(f"   💬 Response: \"{response_text}\"")

            return response_text

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return "I'm sorry, I had trouble processing that request."

    def speak(self, text: str):
        """
        Speak text using TTS.

        Args:
            text: Text to speak
        """
        self.state = AssistantState.SPEAKING
        logger.info("🔊 Speaking...")

        # Synthesize audio
        audio_chunks = []
        for audio_chunk in self.tts_voice.synthesize(text):
            audio_chunks.append(audio_chunk.audio_int16_array)

        if audio_chunks:
            audio_array = np.concatenate(audio_chunks)

            # Play audio
            sd.play(
                audio_array,
                samplerate=self.tts_voice.config.sample_rate,
                device=self.emeet_output
            )
            sd.wait()

            logger.info("   ✅ Speech complete")

    def run(self):
        """Main assistant loop."""
        logger.info("\n" + "="*60)
        logger.info("🎙️  Saga Voice Assistant is ready!")
        logger.info("   Say 'Hey Saga' to activate")
        logger.info("   Press Ctrl+C to exit")
        logger.info("="*60 + "\n")

        try:
            while True:
                # Reset to idle
                self.state = AssistantState.IDLE

                # Wait for wakeword
                if not self.listen_for_wakeword():
                    break

                # Record command
                audio = self.record_command()

                # Transcribe
                text = self.transcribe(audio)

                if not text:
                    logger.warning("No command detected, returning to idle")
                    continue

                # Generate response
                response = self.generate_response(text)

                # Speak response
                self.speak(response)

                # Small pause before listening again
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("\n\n⏹️  Saga Voice Assistant stopped")
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
            return 1

        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Saga Voice Assistant - Complete voice pipeline"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in test mode (single interaction)"
    )

    args = parser.parse_args()

    try:
        assistant = SagaAssistant()
        return assistant.run()
    except Exception as e:
        logger.error(f"❌ Failed to start assistant: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
