"""
TTS Formatting Utilities

Format LLM output for text-to-speech by stripping markdown and other
formatting that sounds bad when spoken.

This is the "View" layer in MVC - LLMs can use any formatting they want
for conversation logic, but we clean it before speaking.
"""

import re


def format_for_tts(text):
    """
    Format LLM output for text-to-speech.
    Strips markdown and formatting that sounds bad when spoken.

    This allows LLMs to communicate naturally with formatting (useful for
    API interactions, logging, etc.) while ensuring voice output is clean.

    Args:
        text: Raw LLM output, possibly containing markdown

    Returns:
        Cleaned text suitable for TTS

    Example:
        >>> format_for_tts("**Important:** First, do this. Second, do that.")
        'Important: First, do this. Second, do that.'
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
