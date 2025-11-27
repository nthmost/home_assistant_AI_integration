#!/usr/bin/env python3
"""
Saga Voice Assistant - Main orchestration script.

Integrates wakeword detection, STT, LLM, and TTS into a complete voice assistant.
"""

import argparse
import json
import logging
import re
import sys
import time
from pathlib import Path
from enum import Enum
from typing import Optional

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
from saga_assistant.weather_v2 import get_weather, get_week_summary, will_it_rain, get_wind_info
from saga_assistant.timers import TimerManager
from saga_assistant.timer_sounds import TimerSoundManager
from saga_assistant.memory import ContextBuilder

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
STT_MODEL = "small"  # Best balance of accuracy vs speed (medium was too slow at 3s)
# VAD parameters (WebRTC VAD for dynamic recording)
VAD_MODE = 2  # Aggressiveness: 0 (least) to 3 (most). 2 is balanced.
VAD_FRAME_MS = 30  # Frame duration: 10, 20, or 30ms
MIN_SPEECH_CHUNKS = 2  # Minimum speech chunks to start recording (~60ms) - reduced from 3 to catch first syllable faster
MIN_SILENCE_CHUNKS = 23  # Silence chunks to stop recording (~700ms)
MAX_RECORDING_DURATION_S = 10  # Maximum recording duration (safety)
LLM_BASE_URL = "http://loki.local:11434/v1"
LLM_MODEL = "qwen2.5:7b"
TTS_VOICE = "en_GB-semaine-medium"
SAMPLE_RATE = 16000

def words_to_number(text: str) -> Optional[int]:
    """Convert number words to integers.

    Args:
        text: Number as word (e.g., "one", "twenty")

    Returns:
        Integer or None if not a number word
    """
    word_to_num = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
        "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
        "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
        "twenty-one": 21, "twenty-two": 22, "twenty-three": 23, "twenty-four": 24, "twenty-five": 25,
        "twenty-six": 26, "twenty-seven": 27, "twenty-eight": 28, "twenty-nine": 29,
        "thirty-one": 31, "thirty-two": 32, "forty-five": 45, "ninety": 90,
    }
    return word_to_num.get(text.lower())


def load_power_phrases(filepath: Path = None) -> dict:
    """Load power phrases from JSON file.

    Args:
        filepath: Path to power_phrases.json (defaults to same dir as this script)

    Returns:
        Dict of regex patterns -> responses
    """
    if filepath is None:
        filepath = Path(__file__).parent / "power_phrases.json"

    # Flatten the JSON structure into pattern -> response dict
    phrases = {}

    try:
        with open(filepath) as f:
            data = json.load(f)

        for category, patterns in data.items():
            for pattern, response in patterns.items():
                # Convert pipe-separated pattern to regex with word boundaries
                regex = r"\b(" + pattern + r")\b"
                phrases[regex] = response

        logger.info(f"   ✅ Loaded {len(phrases)} power phrases from {filepath.name}")

    except FileNotFoundError:
        logger.warning(f"   ⚠️  Power phrases file not found: {filepath}")
        # Fallback to basic greetings
        phrases = {
            r"\b(hi|hello|hey)\b": "Hello!",
            r"\b(thank you|thanks)\b": "You're welcome!",
        }

    return phrases


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
        self.power_phrases = {}
        self.timer_manager = TimerManager()
        self.timer_sounds = TimerSoundManager()

        # Conversation state for follow-up questions
        self.awaiting_followup = False
        self.followup_type = None
        self.followup_data = None

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

        # Load power phrases (must be after logger is configured)
        logger.info("⚡ Loading power phrases...")
        self.power_phrases = load_power_phrases()

        logger.info("✅ All components initialized successfully!")

    def timer_expired_callback(self, name: str, message: str = None):
        """Called when a timer expires.

        Args:
            name: Timer name
            message: Optional reminder message
        """
        if message:
            # This is a reminder
            logger.info(f"⏰ Reminder '{name}' expired - announcing: {message}")
            self.speak(f"Reminder: {message}")
        else:
            # This is a timer - play custom sound if available
            logger.info(f"⏰ Timer '{name}' expired")

            # Get sound for this timer type
            sound_path = self.timer_sounds.get_sound_for_timer(name)

            if sound_path:
                logger.info(f"🔊 Playing custom sound for '{name}' timer")
                self._play_wav(sound_path)
            else:
                # No custom sound, use default
                logger.info(f"🔊 Playing default timer sound")
                default_sound = self.timer_sounds.get_default_sound()
                if default_sound:
                    self._play_wav(default_sound)
                else:
                    # Fallback to speech
                    self.speak("Your timer is up!")

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

        self.system_prompt = """You are Saga, a helpful and witty voice assistant in San Francisco (zip 94118).

RESPONSE LENGTH: Keep it SHORT (1-2 sentences max). This is VOICE.

Personality: Helpful first, playful second. Be practical and conversational.

Response rules:
- HOME AUTOMATION: "Done" or confirm action (4-6 words)
- WEATHER: You have local weather access, don't ask for location unless they ask about somewhere else
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
        """Initialize Home Assistant client and intent parser."""
        logger.info("🏠 Connecting to Home Assistant...")

        try:
            self.ha_client = HomeAssistantClient()

            # Test connection
            if self.ha_client.check_health():
                config = self.ha_client.get_config()
                logger.info(f"   ✅ Connected to {config.get('location_name', 'Home')}")
            else:
                logger.warning("   ⚠️  Home Assistant connection failed (continuing without HA)")
                self.ha_client = None

        except Exception as e:
            logger.warning(f"   ⚠️  Home Assistant unavailable: {e} (continuing without HA)")
            self.ha_client = None

        # Always init IntentParser (supports parking even without HA)
        logger.info("🧠 Loading intent parser...")
        self.intent_parser = IntentParser(self.ha_client)
        logger.info("   ✅ Intent parser ready (HA + parking + memory support)")

        # Initialize context builder for memory system
        logger.info("🧠 Loading memory context builder...")
        self.context_builder = ContextBuilder(self.intent_parser.memory_db)
        logger.info("   ✅ Memory context ready")

    def play_confirmation_beep(self):
        """Play a short confirmation beep when wakeword is detected."""
        # Generate a pleasant two-tone beep (600Hz -> 800Hz)
        duration = 0.15  # seconds
        sample_rate = 48000  # EMEET output sample rate

        # First tone (600Hz)
        t1 = np.linspace(0, duration/2, int(sample_rate * duration/2), False)
        tone1 = np.sin(600 * 2 * np.pi * t1)

        # Second tone (800Hz)
        t2 = np.linspace(0, duration/2, int(sample_rate * duration/2), False)
        tone2 = np.sin(800 * 2 * np.pi * t2)

        # Combine tones
        beep = np.concatenate([tone1, tone2])

        # Apply fade in/out to avoid clicks
        fade_samples = int(sample_rate * 0.01)  # 10ms fade
        beep[:fade_samples] *= np.linspace(0, 1, fade_samples)
        beep[-fade_samples:] *= np.linspace(1, 0, fade_samples)

        # Scale to reasonable volume (30% max)
        beep = (beep * 0.3 * 32767).astype(np.int16)

        # Play through EMEET speaker (non-blocking to minimize latency)
        sd.play(beep, samplerate=sample_rate, device=self.emeet_output)
        sd.wait()
        # Removed sleep here - audio device will be released naturally

    def play_question_beep(self):
        """Play a rising 'question' beep when waiting for follow-up answer."""
        # Generate a questioning tone (500Hz -> 900Hz) - rising, asking
        duration = 0.12  # seconds (slightly shorter)
        sample_rate = 48000  # EMEET output sample rate

        # First tone (500Hz - lower start)
        t1 = np.linspace(0, duration/2, int(sample_rate * duration/2), False)
        tone1 = np.sin(500 * 2 * np.pi * t1)

        # Second tone (900Hz - higher end)
        t2 = np.linspace(0, duration/2, int(sample_rate * duration/2), False)
        tone2 = np.sin(900 * 2 * np.pi * t2)

        # Combine tones
        beep = np.concatenate([tone1, tone2])

        # Apply fade in/out to avoid clicks
        fade_samples = int(sample_rate * 0.01)  # 10ms fade
        beep[:fade_samples] *= np.linspace(0, 1, fade_samples)
        beep[-fade_samples:] *= np.linspace(1, 0, fade_samples)

        # Scale to reasonable volume (25% max - slightly softer than confirmation)
        beep = (beep * 0.25 * 32767).astype(np.int16)

        # Play through EMEET speaker (non-blocking to minimize latency)
        sd.play(beep, samplerate=sample_rate, device=self.emeet_output)
        sd.wait()
        # Removed sleep here - audio device will be released naturally

    def listen_for_wakeword(self) -> bool:
        """
        Listen for wakeword detection.

        Returns:
            True if wakeword detected
        """
        logger.info("👂 Listening for 'Hey Saga'...")

        chunk_duration = 1.28  # seconds (wakeword model requirement)
        chunk_samples = int(SAMPLE_RATE * chunk_duration)
        cooldown_chunks = 3  # Ignore detections for 3 chunks (~4 seconds) after a wake

        max_retries = 3
        for attempt in range(max_retries):
            try:
                with sd.InputStream(
                    device=self.emeet_input,
                    channels=1,
                    samplerate=SAMPLE_RATE,
                    dtype='int16'
                ) as stream:
                    cooldown_counter = 0

                    while True:
                        # Read audio chunk
                        audio, _ = stream.read(chunk_samples)
                        audio = audio.flatten().astype(np.int16)

                        # Run wakeword detection
                        prediction = self.wakeword.predict(audio)

                        # Decrement cooldown if active
                        if cooldown_counter > 0:
                            cooldown_counter -= 1
                            continue  # Skip detection during cooldown

                        # Check if wakeword detected
                        for model_name, score in prediction.items():
                            if score >= WAKEWORD_THRESHOLD:
                                logger.info(f"✅ Wakeword detected! (score: {score:.3f})")
                                self.play_confirmation_beep()
                                cooldown_counter = cooldown_chunks  # Start cooldown
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
        pre_speech_buffer = deque(maxlen=50)  # 1.5s of pre-speech audio to catch first syllables (increased from 20)

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

    def check_power_phrases(self, text: str) -> Optional[str]:
        """
        Check if text matches a power phrase for instant response.

        Args:
            text: User command text

        Returns:
            Response text if matched, None otherwise
        """
        text_lower = text.lower()

        # Check for "quick question" power phrase
        quick_mode = False
        if text_lower.startswith("quick question"):
            quick_mode = True
            # Remove the phrase and strip punctuation
            text_lower = text_lower.replace("quick question", "", 1).strip()
            text_lower = text_lower.lstrip('.,;:!?- ').strip()
            logger.debug(f"Quick mode enabled for power phrase, parsing: {text_lower}")

        # Smart weather query parser - extracts time from any weather question
        # Catches: "what's the weather", "weather", "how's the weather", etc.
        if re.search(r"\b(weather|forecast)\b", text_lower):
            # Extract time keywords
            when = "now"  # default
            if re.search(r"\btomorrow\b", text_lower):
                when = "tomorrow"
            elif re.search(r"\b(this evening|tonight|this night)\b", text_lower):
                when = "tonight"
            elif re.search(r"\bthis afternoon\b", text_lower):
                when = "this afternoon"
            elif re.search(r"\bthis morning\b", text_lower):
                when = "this morning"
            elif re.search(r"\b(today|now|currently|right now)\b", text_lower):
                when = "today"
            elif re.search(r"\b(this week|the week|for the week|weekly)\b", text_lower):
                # Extract location for week summary
                location_match = re.search(r"\bin ([a-z\s]+?)(?:\s+for the week|\s+this week|\s+weekly|$)", text_lower)
                location = location_match.group(1).strip() if location_match else None
                return get_week_summary(location=location)

            # Extract location if specified
            location_match = re.search(r"\bin ([a-z\s]+?)(?:\s+(today|tomorrow|tonight|this morning|this afternoon)|$)", text_lower)
            if location_match:
                location = location_match.group(1).strip()
                return get_weather(location=location, when=when, quick_mode=quick_mode)

            # Default location
            return get_weather(when=when, quick_mode=quick_mode)

        # Special handling for timer commands (accept both digits and words)
        # Supports: "Set a timer for 5 minutes" or "Set a laundry timer for 60 minutes"
        # Extract timer type if specified (e.g., "laundry timer", "tea timer", "meditation timer")
        timer_set_match = re.search(
            r"(?:set a |set |)(?:([a-z]+) |)timer for (\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty) (minute|second)s?",
            text_lower
        )
        if timer_set_match:
            timer_type = timer_set_match.group(1)  # May be None for generic "timer"
            duration_str = timer_set_match.group(2)
            unit = timer_set_match.group(3)

            # Convert word to number if needed
            if duration_str.isdigit():
                duration = int(duration_str)
            else:
                duration = words_to_number(duration_str)
                if duration is None:
                    duration = 1  # Fallback

            # Use timer type as name if specified, otherwise "timer"
            timer_name = timer_type if timer_type else "timer"

            # Check if this is a new timer type without assigned sound
            if timer_type and not self.timer_sounds.has_sound_for_timer(timer_type):
                logger.info(f"🆕 New timer type detected: '{timer_type}'")
                # For now, just log it - future enhancement: offer sound selection
                # TODO: Implement voice-based sound selection dialog

            if unit == "minute":
                return self.timer_manager.set_timer(
                    duration_minutes=duration,
                    name=timer_name,
                    callback=self.timer_expired_callback
                )
            else:
                return self.timer_manager.set_timer(
                    duration_seconds=duration,
                    name=timer_name,
                    callback=self.timer_expired_callback
                )

        # Special handling for reminders (accept both digits and words)
        # "Remind me in 5 minutes to call mom"
        reminder_in_match = re.search(r"remind me in (\d+|one|two|three|four|five|six|seven|eight|nine|ten|fifteen|twenty|thirty|forty|fifty|sixty) (minute|second|hour)s? to (.+)", text_lower)
        if reminder_in_match:
            duration_str = reminder_in_match.group(1)
            unit = reminder_in_match.group(2)
            message = reminder_in_match.group(3).strip()

            # Convert word to number if needed
            if duration_str.isdigit():
                duration = int(duration_str)
            else:
                duration = words_to_number(duration_str)
                if duration is None:
                    duration = 1  # Fallback

            if unit == "hour":
                duration_minutes = duration * 60
            elif unit == "minute":
                duration_minutes = duration
            else:
                # seconds
                return self.timer_manager.set_timer(
                    duration_seconds=duration,
                    message=message,
                    callback=self.timer_expired_callback,
                    name="reminder"
                )

            return self.timer_manager.set_timer(
                duration_minutes=duration_minutes,
                message=message,
                callback=self.timer_expired_callback,
                name="reminder"
            )

        # "Remind me at 3pm to call mom" - TODO: implement time-based reminders
        # For now, we'll skip this and let it fall through to LLM

        # Check standard power phrases
        for pattern, response in self.power_phrases.items():
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                # Handle special tokens in response
                if response == "<TIME>":
                    return time.strftime("It's %I:%M %p")
                elif response == "<DATE>":
                    return time.strftime("It's %A, %B %d")
                elif response.startswith("<WEATHER:"):
                    when = response[9:-1]  # Extract "now", "today", "tomorrow", etc.
                    return get_weather(when=when)
                elif response.startswith("<RAIN:"):
                    when = response[6:-1]  # Extract "today" or "tomorrow"
                    return will_it_rain(when=when)
                elif response == "<WIND>":
                    return get_wind_info()
                elif response == "<TIMER:check>":
                    return self.timer_manager.check_timer()
                elif response == "<TIMER:cancel>":
                    return self.timer_manager.cancel_timer()
                else:
                    return response
        return None

    def process_command(self, text: str) -> str:
        """
        Process user command - check power phrases, HA intents, then LLM.

        Args:
            text: User command text

        Returns:
            Response text
        """
        self.state = AssistantState.PROCESSING

        # Check if we're waiting for a follow-up answer
        if self.awaiting_followup:
            logger.info(f"🔄 Processing follow-up answer for: {self.followup_type}")
            start_time = time.time()
            result = self.intent_parser.handle_followup(
                self.followup_type,
                text,
                self.followup_data
            )
            elapsed = time.time() - start_time

            # Check if the follow-up answer itself needs another follow-up (chained questions)
            if result.get("status") == "needs_followup":
                self.followup_type = result.get("followup_type")
                self.followup_data = result.get("partial_data", {})
                response_text = result.get("message", "I need more information.")
                logger.info(f"   💬🚗❓ ({elapsed:.2f}s): \"{response_text}\"")
                logger.info(f"   ⏸️  Chained follow-up: {self.followup_type}")
                return response_text

            # Clear followup state (conversation complete)
            self.awaiting_followup = False
            self.followup_type = None
            self.followup_data = None

            response_text = result.get("message", "Done.")
            logger.info(f"   💬🚗 ({elapsed:.2f}s): \"{response_text}\"")
            return response_text

        # Check power phrases first (instant, no LLM needed!)
        start_time = time.time()
        power_response = self.check_power_phrases(text)
        if power_response:
            elapsed = time.time() - start_time
            logger.info(f"   💬⚡ ({elapsed:.2f}s): \"{power_response}\"")
            return power_response

        # Try intent parsing (HA + parking + memory) second
        if self.intent_parser:
            try:
                logger.info("🔍 Checking for intent command...")
                intent = self.intent_parser.parse(text)

                # Memory commands - high priority (user is explicitly managing memory)
                if intent.action in ["save_preference", "remember_fact", "show_preferences", "show_memory", "forget_memory"]:
                    logger.info(f"   🧠 Memory command detected: {intent.action}")
                    start_time = time.time()
                    result = self.intent_parser.execute(intent)
                    elapsed = time.time() - start_time
                    response_text = result.get("message", "Got it.")
                    logger.info(f"   💬🧠 ({elapsed:.2f}s): \"{response_text}\"")
                    return response_text

                # Minnie blame queries - always high priority!
                if intent.action == "minnie_blame":
                    logger.info(f"   🐱 Minnie blame query detected")
                    start_time = time.time()
                    result = self.intent_parser.execute(intent)
                    elapsed = time.time() - start_time
                    response_text = result.get("message", "It was Minnie's fault.")
                    logger.info(f"   💬🐱 ({elapsed:.2f}s): \"{response_text}\"")
                    return response_text

                # Parking and road trip intents don't need entity_id
                if intent.action in ["save_parking", "where_parked", "when_to_move", "forget_parking",
                                     "road_trip_distance", "road_trip_time", "road_trip_best_time", "road_trip_poi"]:
                    if intent.confidence >= 0.6:
                        # Log with appropriate emoji
                        if intent.action.startswith("road_trip"):
                            logger.info(f"   🚗 Road trip query detected (confidence: {intent.confidence:.2f})")
                        else:
                            logger.info(f"   🚗 Parking command detected (confidence: {intent.confidence:.2f})")
                        start_time = time.time()
                        result = self.intent_parser.execute(intent)
                        elapsed = time.time() - start_time

                        # Check if we need a follow-up question
                        if result.get("status") == "needs_followup":
                            self.awaiting_followup = True
                            self.followup_type = result.get("followup_type")
                            self.followup_data = result.get("partial_data")
                            response_text = result.get("message", "I need more information.")
                            emoji = "🗺️" if intent.action.startswith("road_trip") else "🚗"
                            logger.info(f"   💬{emoji}❓ ({elapsed:.2f}s): \"{response_text}\"")
                            logger.info(f"   ⏸️  Waiting for follow-up: {self.followup_type}")
                            return response_text

                        response_text = result.get("message", "Command executed successfully.")
                        emoji = "🗺️" if intent.action.startswith("road_trip") else "🚗"
                        logger.info(f"   💬{emoji} ({elapsed:.2f}s): \"{response_text}\"")
                        return response_text
                    else:
                        logger.info(f"   ⚠️  Low confidence ({intent.confidence:.2f}), using LLM")

                # HA intents need entity_id
                elif intent.confidence >= 0.6 and intent.entity_id:
                    logger.info(f"   ✅ HA command detected (confidence: {intent.confidence:.2f})")
                    start_time = time.time()
                    result = self.intent_parser.execute(intent)

                    # Get friendly name for response
                    entity = self.ha_client.get_state(intent.entity_id)
                    friendly_name = entity.get("attributes", {}).get(
                        "friendly_name", intent.entity_id
                    )

                    if intent.action == "turn_on":
                        response_text = f"Okay, I've turned on the {friendly_name}."
                    elif intent.action == "turn_off":
                        response_text = f"Okay, I've turned off the {friendly_name}."
                    elif intent.action == "toggle":
                        response_text = f"Okay, I've toggled the {friendly_name}."
                    elif intent.action == "status":
                        state = entity["state"]
                        response_text = f"The {friendly_name} is {state}."
                    else:
                        response_text = result.get("message", "Command executed successfully.")

                    elapsed = time.time() - start_time
                    logger.info(f"   💬🏠 ({elapsed:.2f}s): \"{response_text}\"")
                    return response_text

                else:
                    logger.info(f"   ⚠️  Low confidence ({intent.confidence:.2f}), using LLM")

            except IntentParseError as e:
                logger.info(f"   ℹ️  Not an intent command: {e}")
            except Exception as e:
                logger.warning(f"   ⚠️  Intent command failed: {e}")

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
        start_time = time.time()

        # Build context-enhanced system prompt with user preferences
        enhanced_prompt = self.context_builder.format_for_system_prompt(
            self.system_prompt,
            utterance=prompt
        )

        try:
            response = self.llm.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": enhanced_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=30,  # Aggressive brevity for speed - voice needs to be snappy!
                temperature=0.8
            )

            elapsed = time.time() - start_time
            response_text = response.choices[0].message.content.strip()
            logger.info(f"   💬🤖 ({elapsed:.2f}s): \"{response_text}\"")

            return response_text

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return "I'm sorry, I had trouble processing that request."

    def _play_wav(self, wav_path: str):
        """Play a WAV file.

        Args:
            wav_path: Path to WAV file
        """
        import wave

        try:
            with wave.open(wav_path, 'rb') as wav_file:
                sample_rate = wav_file.getframerate()
                n_channels = wav_file.getnchannels()
                audio_data = wav_file.readframes(wav_file.getnframes())

                # Convert to numpy array
                if wav_file.getsampwidth() == 2:  # 16-bit
                    audio_array = np.frombuffer(audio_data, dtype=np.int16)
                else:
                    logger.error(f"Unsupported WAV format: {wav_file.getsampwidth()} bytes per sample")
                    return

                # Convert to float
                audio_array = audio_array.astype(np.float32) / 32768.0

                # Handle stereo (convert to mono if needed)
                if n_channels == 2:
                    audio_array = audio_array.reshape(-1, 2).mean(axis=1)

                # Play audio
                sd.play(audio_array, samplerate=sample_rate, device=self.emeet_output)
                sd.wait()

                logger.info("   ✅ Sound complete")

                # Add cooldown to prevent audio device contention
                # macOS Core Audio needs time to release the device before input can be opened
                # OPTIMIZED: Reduced from 0.5s to 0.2s based on measured switching time (72ms avg)
                time.sleep(0.2)  # Phase 1 optimization: faster return to wakeword detection

        except Exception as e:
            logger.error(f"Failed to play WAV: {e}")

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

            # Add cooldown to prevent TTS from triggering wakeword + ensure device is released
            # TTS echoes can sound similar to "Hey Saga"
            # BUT: Skip cooldown if we're waiting for follow-up (no wakeword detection)
            # OPTIMIZED: Reduced from 1.2s to 0.5s based on measured device switching time (72ms avg)
            if not self.awaiting_followup:
                time.sleep(0.5)  # Phase 1 optimization: faster response
            else:
                time.sleep(0.2)  # Just enough to release audio device

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

                # If we're waiting for a follow-up, skip wakeword and listen immediately
                if self.awaiting_followup:
                    logger.info("⏩ Listening for follow-up answer (no wakeword needed)...")
                    # Play question beep to signal we're ready for answer
                    self.play_question_beep()
                else:
                    # Wait for wakeword
                    if not self.listen_for_wakeword():
                        break

                # Record command (or follow-up answer)
                audio = self.record_command()

                # Transcribe
                text = self.transcribe(audio)

                if not text:
                    logger.warning("No command detected, returning to idle")
                    # Clear follow-up state if we were waiting
                    if self.awaiting_followup:
                        logger.warning("   Clearing follow-up state due to no input")
                        self.awaiting_followup = False
                        self.followup_type = None
                        self.followup_data = None
                    continue

                # Process command (HA intent or LLM)
                response = self.process_command(text)

                # Speak response
                self.speak(response)

                # Small pause before listening again (skip if awaiting follow-up for faster response)
                if not self.awaiting_followup:
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
