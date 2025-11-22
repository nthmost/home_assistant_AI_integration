"""
Setup script for Home Assistant AI Integration project
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="home-assistant-ai-integration",
    version="0.1.0",
    description="Home Assistant integration with AI voice assistant (Saga) and various automations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="nthmost",
    python_requires=">=3.13",
    packages=find_packages(exclude=["tests", "docs", "scripts"]),
    install_requires=[
        "homeassistant-api>=5.0.2",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "streamlit>=1.41.1",
        "pyaudio",
        "sounddevice",
        "openwakeword",
        "onnxruntime",
        "faster-whisper",
        "piper-tts",
        "openai",
        "torch",
        "torchaudio",
        "silero-vad",
        "scipy",
        "webrtcvad",
    ],
    extras_require={
        "dev": [
            "pytest>=8.3.4",
            "pytest-mock",
            "pytest-cov",
        ],
    },
    entry_points={
        "console_scripts": [
            "saga-assistant=saga_assistant.run_assistant:main",
            "test-squawkers=squawkers.test_squawkers:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Home Automation",
        "Programming Language :: Python :: 3.13",
    ],
)
