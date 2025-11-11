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
import webrtcvad
from collections import deque
from openwakeword.model import Model as WakewordModel
from faster_whisper import WhisperModel
from openai import OpenAI
from piper import PiperVoice

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from saga_assistant.ha_client import HomeAssistantClient
from saga_assistant.intent_parser import IntentParser, IntentParseError

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
STT_MODEL = "medium"  # Best balance of accuracy vs speed for voice assistant
# VAD parameters (WebRTC VAD for dynamic recording)
VAD_MODE = 2  # Aggressiveness: 0 (least) to 3 (most). 2 is balanced.
VAD_FRAME_MS = 30  # Frame duration: 10, 20, or 30ms
MIN_SPEECH_CHUNKS = 3  # Minimum speech chunks to start recording (~90ms) - reduced to catch first syllable
MIN_SILENCE_CHUNKS = 23  # Silence chunks to stop recording (~700ms)
MAX_RECORDING_DURATION_S = 10  # Maximum recording duration (safety)
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
        self._init_vad()
        self._init_stt()
        self._init_llm()
        self._init_tts()
        self._init_ha()

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

    def _init_vad(self):
        """Initialize voice activity detection."""
        logger.info("🔊 Loading VAD...")

        self.vad = webrtcvad.Vad()
        self.vad.set_mode(VAD_MODE)
        self.vad_frame_size = int(SAMPLE_RATE * VAD_FRAME_MS / 1000)

        logger.info(f"   ✅ Loaded: WebRTC VAD (mode={VAD_MODE})")

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

        self.system_prompt = """You are Saga, a helpful and witty voice assistant.

RESPONSE LENGTH: Keep it SHORT (1-2 sentences max). This is VOICE.

Personality: Helpful first, playful second. Be practical and conversational.

Response rules:
- HOME AUTOMATION: "Done" or confirm action (4-6 words)
- REQUESTS (reminders, alarms, etc.): Ask for missing details concisely
  Example: "Remind me tomorrow to X" → "What time?"
- QUESTIONS: One helpful/interesting sentence, STOP
- IMPROV/FUN: Play along briefly (1 sentence)
- Be direct and useful, not flowery

Examples:
✅ User: "Remind me tomorrow to call mom" → You: "What time?"
✅ User: "Turn on the lights" → You: "Done."
✅ User: "What's your favorite book?" → You: "Hitchhiker's Guide. It's wonderfully absurd."
✅ User: "Let's play improv" → You: "Sure! I'll start: The coffee machine brews tea."

Be HELPFUL first, entertaining second. Keep it SHORT."""

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

    def _init_ha(self):
        """Initialize Home Assistant client."""
        logger.info("🏠 Connecting to Home Assistant...")

        try:
            self.ha_client = HomeAssistantClient()
            self.intent_parser = IntentParser(self.ha_client)

            # Test connection
            if self.ha_client.check_health():
                config = self.ha_client.get_config()
                logger.info(f"   ✅ Connected to {config.get('location_name', 'Home')}")
            else:
                logger.warning("   ⚠️  Home Assistant connection failed (continuing without HA)")
                self.ha_client = None
                self.intent_parser = None

        except Exception as e:
            logger.warning(f"   ⚠️  Home Assistant unavailable: {e} (continuing without HA)")
            self.ha_client = None
            self.intent_parser = None

    def listen_for_wakeword(self) -> bool:
        """
        Listen for wakeword detection.

        Returns:
            True if wakeword detected
        """
        logger.info("👂 Listening for 'Hey Saga'...")

        chunk_duration = 1.28  # seconds (wakeword model requirement)
        chunk_samples = int(SAMPLE_RATE * chunk_duration)

        max_retries = 3
        for attempt in range(max_retries):
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
            except sd.PortAudioError as e:
                logger.error(f"Audio device error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    logger.info("   🔄 Retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    logger.error("   ❌ Audio device failed after retries")
                    return False
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return False

        return False  # All retries exhausted

    def record_command(self) -> np.ndarray:
        """
        Record voice command after wakeword using VAD.

        Returns:
            Audio data as numpy array
        """
        self.state = AssistantState.LISTENING
        logger.info("🎤 Recording command (VAD auto-stop)...")

        # State tracking
        speech_chunk_count = 0
        silence_chunk_count = 0
        is_recording = False
        audio_buffer = []
        pre_speech_buffer = deque(maxlen=20)  # 600ms of pre-speech audio to catch first syllables

        max_chunks = int(MAX_RECORDING_DURATION_S * 1000 / VAD_FRAME_MS)
        chunk_count = 0
        start_time = None

        try:
            with sd.InputStream(
                device=self.emeet_input,
                channels=1,
                samplerate=SAMPLE_RATE,
                dtype='int16',
                blocksize=self.vad_frame_size
            ) as stream:

                while chunk_count < max_chunks:
                    # Read audio chunk
                    audio_chunk, _ = stream.read(self.vad_frame_size)
                    audio_chunk = audio_chunk.flatten()
                    chunk_count += 1

                    # Check for speech
                    audio_bytes = audio_chunk.tobytes()
                    try:
                        is_speech = self.vad.is_speech(audio_bytes, SAMPLE_RATE)
                    except:
                        is_speech = False

                    if is_speech:
                        speech_chunk_count += 1
                        silence_chunk_count = 0

                        if not is_recording:
                            if speech_chunk_count >= MIN_SPEECH_CHUNKS:
                                # Start recording
                                logger.info("   🔴 Speech detected, recording...")
                                is_recording = True
                                start_time = time.time()
                                # Add pre-speech buffer
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
                                # Enough silence, stop recording
                                duration = time.time() - start_time
                                logger.info(f"   ⏹️  Recording complete ({duration:.1f}s)")
                                break
                        else:
                            pre_speech_buffer.append(audio_chunk)

                else:
                    logger.warning(f"   ⚠️  Max duration reached ({MAX_RECORDING_DURATION_S}s)")

        except Exception as e:
            logger.error(f"Recording error: {e}")

        # Convert to numpy array
        if audio_buffer:
            return np.concatenate(audio_buffer)
        else:
            logger.warning("   ⚠️  No audio recorded")
            return np.array([], dtype=np.int16)

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

    def process_command(self, text: str) -> str:
        """
        Process user command - try HA intent first, fallback to LLM.

        Args:
            text: User command text

        Returns:
            Response text
        """
        self.state = AssistantState.PROCESSING

        # Try Home Assistant intent parsing first
        if self.ha_client and self.intent_parser:
            try:
                logger.info("🏠 Checking for Home Assistant command...")
                intent = self.intent_parser.parse(text)

                # If confidence is high enough, execute directly
                if intent.confidence >= 0.4:
                    logger.info(f"   ✅ HA command detected (confidence: {intent.confidence:.2f})")
                    result = self.intent_parser.execute(intent)

                    # Get friendly name for response
                    if intent.entity_id:
                        entity = self.ha_client.get_state(intent.entity_id)
                        friendly_name = entity.get("attributes", {}).get(
                            "friendly_name", intent.entity_id
                        )

                        if intent.action == "turn_on":
                            return f"Okay, I've turned on the {friendly_name}."
                        elif intent.action == "turn_off":
                            return f"Okay, I've turned off the {friendly_name}."
                        elif intent.action == "toggle":
                            return f"Okay, I've toggled the {friendly_name}."
                        elif intent.action == "status":
                            state = entity["state"]
                            return f"The {friendly_name} is {state}."

                    return result.get("message", "Command executed successfully.")

                else:
                    logger.info(f"   ⚠️  Low confidence ({intent.confidence:.2f}), using LLM")

            except IntentParseError as e:
                logger.info(f"   ℹ️  Not a HA command: {e}")
            except Exception as e:
                logger.warning(f"   ⚠️  HA command failed: {e}")

        # Fallback to LLM for conversational queries
        return self.generate_response(text)

    def generate_response(self, prompt: str) -> str:
        """
        Generate LLM response.

        Args:
            prompt: User input

        Returns:
            LLM response text
        """
        logger.info("🤖 Generating response...")

        try:
            response = self.llm.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,  # Force brevity - this is voice, not text chat!
                temperature=0.8
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

                # Process command (HA intent or LLM)
                response = self.process_command(text)

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
