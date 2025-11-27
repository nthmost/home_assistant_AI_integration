#!/usr/bin/env python3
"""
Demo script for testing LLM integration with Ollama on loki.local.

Tests connection to qwen2.5:7b for voice assistant responses.
"""

import argparse
import logging
import sys
import time

from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# LLM configuration
OLLAMA_BASE_URL = "http://loki.local:11434/v1"
DEFAULT_MODEL = "qwen2.5:7b"
DEFAULT_SYSTEM_PROMPT = """You are Saga, a helpful voice assistant for home automation.

Keep responses concise and natural for spoken conversation.
For home automation commands, be direct and confirmatory.
You have a warm, professional personality."""


class LLMClient:
    """OpenAI-compatible client for Ollama."""

    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = DEFAULT_MODEL):
        """
        Initialize LLM client.

        Args:
            base_url: Ollama API endpoint
            model: Model name to use
        """
        logger.info(f"🤖 Connecting to LLM: {model}")
        logger.info(f"   URL: {base_url}")

        self.client = OpenAI(
            base_url=base_url,
            api_key="ollama"  # Ollama doesn't need a real key
        )
        self.model = model

    def generate(
        self,
        prompt: str,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        max_tokens: int = 100,
        temperature: float = 0.7
    ) -> tuple[str, float]:
        """
        Generate a response from the LLM.

        Args:
            prompt: User input
            system_prompt: System instructions
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)

        Returns:
            Tuple of (response_text, generation_time_ms)
        """
        start = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )

            generation_time = (time.time() - start) * 1000  # Convert to ms

            response_text = response.choices[0].message.content.strip()

            return response_text, generation_time

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(
        description="Test LLM integration with Ollama",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic test
  python demo_llm.py

  # Custom prompt
  python demo_llm.py --prompt "What's the weather like?"

  # Different model
  python demo_llm.py --model mistral:7b

  # Multiple runs
  python demo_llm.py --runs 3
        """
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="Turn on the Office LED Lights",
        help="User prompt to send to LLM"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Model to use (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=100,
        help="Maximum tokens to generate (default: 100)"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Sampling temperature 0-1 (default: 0.7)"
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of test runs (default: 1)"
    )

    args = parser.parse_args()

    # Print banner
    print("\n" + "="*60)
    print("🤖 LLM INTEGRATION TEST")
    print("="*60)

    # Initialize LLM client
    try:
        llm = LLMClient(model=args.model)
    except Exception as e:
        logger.error(f"❌ Failed to initialize LLM client: {e}")
        logger.info("\n💡 Troubleshooting:")
        logger.info("   1. Check that Ollama is running on loki.local")
        logger.info("   2. Verify network connectivity: ping loki.local")
        logger.info("   3. Check model is available: ssh loki.local 'ollama list'")
        return 1

    # Run test generations
    logger.info(f"\n{'='*60}")
    logger.info(f"🎯 Running {args.runs} test(s)")
    logger.info(f"{'='*60}")
    logger.info(f"📝 Prompt: \"{args.prompt}\"")
    logger.info(f"⚙️  Model: {args.model}")
    logger.info(f"⚙️  Max tokens: {args.max_tokens}")
    logger.info(f"⚙️  Temperature: {args.temperature}")
    logger.info(f"{'='*60}\n")

    total_generation_time = 0
    successful_runs = 0

    for i in range(args.runs):
        if args.runs > 1:
            print(f"\n{'─'*60}")
            print(f"Test {i+1} of {args.runs}")
            print(f"{'─'*60}")

        try:
            # Generate response
            print("🧠 Generating response...", flush=True)
            response, generation_time = llm.generate(
                prompt=args.prompt,
                max_tokens=args.max_tokens,
                temperature=args.temperature
            )
            total_generation_time += generation_time
            successful_runs += 1

            # Display results
            print(f"\n{'─'*60}")
            print(f"⏱️  Generation time: {generation_time:.0f}ms")
            print(f"💬 Response:")
            print(f"   \"{response}\"")
            print(f"{'─'*60}")

            # Pause between runs
            if i < args.runs - 1:
                print("\n   ⏸️  Pausing 2 seconds before next test...")
                time.sleep(2)

        except KeyboardInterrupt:
            logger.info("\n\n⏹️  Stopped by user")
            break
        except Exception as e:
            logger.error(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return 1

    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"   Tests completed: {successful_runs}/{args.runs}")

    if successful_runs > 0:
        avg_generation = total_generation_time / successful_runs
        print(f"   Average generation time: {avg_generation:.0f}ms")
        print(f"   Target for voice assistant: ~600-850ms")

        if avg_generation < 600:
            print(f"   ✅ Under target! Excellent performance.")
        elif avg_generation < 1000:
            print(f"   ✅ Within acceptable range for voice assistant.")
        else:
            print(f"   ⚠️  Above target. Consider shorter max_tokens.")

    print(f"{'='*60}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
