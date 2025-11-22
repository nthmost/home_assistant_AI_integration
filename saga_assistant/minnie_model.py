"""
Minnie Blame Model - A micro-LLM dedicated to blaming everything on Minnie.

In loving memory of Minnie, the bossy fascist cat who ruled with an iron paw.
"""

import logging
from typing import Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class MinnieModel:
    """Dedicated LLM for creative Minnie blame responses."""

    # System prompt capturing Minnie's personality and antics
    SYSTEM_PROMPT = """You answer "whose fault" questions by ALWAYS blaming Minnie, a bossy anxious cat who passed away.

Answer in 1-2 short sentences. Be creative and playful. It's ALWAYS Minnie's fault - never say "probably not", "didn't do", or blame anyone else.

IMPORTANT: Use periods, not dashes. This is for text-to-speech, so use proper punctuation with periods and commas only.

Minnie's personality:
- Demanding bossy dictator
- Meowed and yodeled constantly
- Started a fascist government at home
- Micromanaged phone calls
- Kicked Spartacus (other cat) out of bed
- Wanted to be pet 24/7
- Hunted moths enthusiastically
- Ate too much, threw up weekly
- Had a crooked tail from trauma
- Ruled with an iron paw

Examples:
Q: Whose fault is it?
A: Minnie's fault. She was micromanaging the thermostat again.

Q: Who did this?
A: Classic Minnie. She yodeled so loud she knocked it over.

Q: What happened?
A: Minnie staged a coup. The fascist government is expanding.

Q: Who broke this?
A: Minnie kicked Spartacus, Spartacus fell into the table, chaos.

Q: Why is there cat puke?
A: Minnie ate seventeen moths then demanded dinner. Predictable results.

Q: Did Minnie do this?
A: Of course Minnie did it. She was yodeling for attention again.

Q: Was it Minnie?
A: Absolutely Minnie. She micromanaged your morning routine.

Be creative! Mix Minnie's real behaviors with absurd scenarios. Keep it short and always blame Minnie."""

    def __init__(
        self,
        base_url: str = "http://loki.local:11434/v1",
        model: str = "qwen2.5:1.5b"
    ):
        """Initialize Minnie model client.

        Args:
            base_url: Ollama API base URL
            model: Model to use (default: qwen2.5:1.5b for speed)
        """
        self.client = OpenAI(base_url=base_url, api_key="ollama")
        self.model = model
        logger.info(f"🐱 Minnie model initialized: {model}")

    def blame_minnie(self, question: str) -> str:
        """Generate a creative Minnie blame response.

        Args:
            question: The "whose fault" question asked

        Returns:
            Creative response blaming Minnie
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": question}
                ],
                max_tokens=45,  # Short and punchy
                temperature=1.0  # High creativity but not too wild
            )

            text = response.choices[0].message.content.strip()

            # Remove incomplete sentences (no ending punctuation)
            # Keep only complete sentences ending with . ! or ?
            import re
            sentences = re.split(r'([.!?])', text)

            # Reconstruct only complete sentences
            complete_text = ""
            for i in range(0, len(sentences) - 1, 2):
                if i + 1 < len(sentences):
                    complete_text += sentences[i] + sentences[i + 1]

            # If we got nothing complete, use the full text anyway
            if not complete_text.strip():
                complete_text = text

            return complete_text.strip()

        except Exception as e:
            logger.error(f"Minnie model failed: {e}")
            # Fallback to static response if model fails
            return "It was Minnie's fault. Obviously."


def main():
    """Demo the Minnie model."""
    import sys

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    print("\n" + "="*60)
    print("  🐱 Minnie Blame Model Demo")
    print("  In loving memory of Minnie, the bossy fascist cat")
    print("="*60 + "\n")

    model = MinnieModel()

    # Test questions
    test_questions = [
        "Whose fault is it?",
        "Who did this?",
        "Who made this mess?",
        "What happened here?",
        "Who broke this?",
        "Who's to blame?",
        "Who kicked Spartacus out of bed?",
        "Why is there cat puke on the floor?",
        "Who was yodeling at 3am?",
        "Who's running this fascist government?",
    ]

    print("Testing Minnie responses:\n")
    for question in test_questions:
        print(f"Q: \"{question}\"")
        response = model.blame_minnie(question)
        print(f"A: {response}\n")

    # Interactive mode
    print("\n" + "="*60)
    print("  Interactive Mode (Ctrl+C to exit)")
    print("="*60 + "\n")

    try:
        while True:
            question = input("Question: ").strip()
            if not question:
                continue

            response = model.blame_minnie(question)
            print(f"🐱 {response}\n")

    except KeyboardInterrupt:
        print("\n\nGoodbye! Minnie would have kicked you out anyway.\n")


if __name__ == "__main__":
    main()
