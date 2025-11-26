#!/usr/bin/env python3
"""
Demo: Saga Memory System

Test the memory system with preference saving and retrieval.
"""

from saga_assistant.intent_parser import IntentParser

def main():
    print("\n" + "=" * 60)
    print("SAGA MEMORY SYSTEM - PHASE 1 TEST")
    print("=" * 60)

    # Create parser (no HA client needed for this test)
    parser = IntentParser(ha_client=None)

    # Test 1: Save a preference
    print("\n[TEST 1] User: 'I prefer pink lights'")
    intent = parser.parse("I prefer pink lights")
    print(f"Parsed intent: {intent}")

    result = parser.execute(intent)
    print(f"Result: {result}")

    # Test 2: Save another preference
    print("\n[TEST 2] User: 'In general I like the color blue for my bedroom'")
    intent = parser.parse("In general I like the color blue for my bedroom")
    print(f"Parsed intent: {intent}")

    result = parser.execute(intent)
    print(f"Result: {result}")

    # Test 3: Show preferences
    print("\n[TEST 3] User: 'What are my preferences?'")
    intent = parser.parse("What are my preferences?")
    print(f"Parsed intent: {intent}")

    result = parser.execute(intent)
    print(f"Result: {result}")

    # Test 4: Show memory stats
    print("\n[TEST 4] User: 'What do you remember about me?'")
    intent = parser.parse("What do you remember about me?")
    print(f"Parsed intent: {intent}")

    result = parser.execute(intent)
    print(f"Result: {result}")

    # Test 5: Context builder
    print("\n[TEST 5] Build LLM context")
    from saga_assistant.memory import ContextBuilder

    builder = ContextBuilder(parser.memory_db)
    context = builder.build_context()

    print(f"Context: {context}")
    print(f"\nContext summary: {context['context_summary']}")

    # Test 6: Format for system prompt
    print("\n[TEST 6] Format context for system prompt")
    base_prompt = "You are Saga, a helpful voice assistant."
    enhanced_prompt = builder.format_for_system_prompt(base_prompt)

    print(f"Enhanced prompt:\n{enhanced_prompt}")

    print("\n" + "=" * 60)
    print("TESTS COMPLETE")
    print("=" * 60)
    print("\nMemory database location: ~/.saga_assistant/memory.db")
    print("Check with: sqlite3 ~/.saga_assistant/memory.db 'SELECT * FROM preferences;'")
    print()

if __name__ == "__main__":
    main()
