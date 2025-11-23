# Saga Memory Architecture

## Design Principles

1. **User-driven** - Memory is explicit, triggered by power phrases
2. **Simple storage** - SQLite with JSON columns for flexibility
3. **LLM-friendly** - Easy to inject relevant context into prompts
4. **Single-user first** - But designed for multi-user expansion
5. **Privacy-focused** - User can clear memory with confirmation

## Memory Types

### 1. User Preferences
**Trigger phrases:**
- "I prefer [X]"
- "I have a preference for [X]"
- "In general I like [X]"
- "My default [X] is [Y]"

**Examples:**
- "In general I like the color pink for my colored lights"
  → `{"category": "lights", "preference": "color", "value": "pink", "scope": "default"}`
- "I prefer the temperature at 72 degrees"
  → `{"category": "climate", "preference": "temperature", "value": 72, "scope": "default"}`

**Storage:** Preferences table with category, key, value, scope

### 2. Facts to Remember
**Trigger phrases:**
- "Remember that [X]"
- "For future reference, [X]"
- "Keep in mind that [X]"

**Examples:**
- "Remember that my meeting room is the office"
  → `{"type": "room_mapping", "fact": "meeting room = office"}`
- "Remember that I walk the dog at 6pm"
  → `{"type": "routine", "fact": "dog walk at 6pm"}`

**Storage:** Facts table with type, content, timestamp, relevance_tags

### 3. Active Context (Session Memory)
**Not explicitly triggered** - Automatically maintained during session

**Contains:**
- Current conversation history (last N exchanges)
- Active timers/reminders
- Ongoing tasks

**Storage:** In-memory during session, optionally persisted to DB

### 4. Conversation History (Optional, Future)
**For analytics/learning** - Not initially used for context

**Storage:** Conversation log table (for later analysis)

## Database Schema

### SQLite Tables

```sql
-- User preferences (what user likes/prefers)
CREATE TABLE preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT DEFAULT 'default',  -- For future multi-user
    category TEXT NOT NULL,          -- 'lights', 'climate', 'routines', etc.
    preference_key TEXT NOT NULL,    -- 'color', 'temperature', etc.
    preference_value TEXT NOT NULL,  -- JSON-encoded value
    scope TEXT DEFAULT 'default',    -- 'default', 'specific', 'always'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, category, preference_key)
);

-- Facts to remember (context about user/home)
CREATE TABLE facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT DEFAULT 'default',
    fact_type TEXT NOT NULL,         -- 'room_mapping', 'routine', 'person', etc.
    content TEXT NOT NULL,           -- Natural language fact
    structured_data TEXT,            -- Optional JSON for structured facts
    relevance_tags TEXT,             -- Comma-separated tags for retrieval
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP,
    access_count INTEGER DEFAULT 0
);

-- Conversation history (optional, for future learning)
CREATE TABLE conversation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT DEFAULT 'default',
    session_id TEXT NOT NULL,
    turn_number INTEGER NOT NULL,
    user_utterance TEXT,
    saga_response TEXT,
    intent_detected TEXT,            -- What Saga understood
    memory_created BOOLEAN DEFAULT 0, -- Did this create a memory?
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Session state (active context)
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT DEFAULT 'default',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context_summary TEXT,            -- JSON: current conversation context
    active_tasks TEXT                -- JSON: timers, reminders, etc.
);
```

## Power Phrase Detection

### Pattern Matching (Initial Implementation)

```python
# In intent_parser.py
MEMORY_PATTERNS = {
    "preference": [
        r"(?:in general |generally )?I (?:prefer|like|want) (.+)",
        r"(?:my|the) default (\w+) (?:is|should be) (.+)",
        r"I have a preference for (.+)",
    ],
    "remember": [
        r"remember that (.+)",
        r"for future reference,? (.+)",
        r"keep in mind that (.+)",
        r"don't forget (?:that )?(.+)",
    ],
    "forget": [
        r"forget (?:about )?(.+)",
        r"clear (?:my )?memory",
        r"reset (?:your )?memory",
    ]
}
```

### LLM-Assisted Extraction (Future Enhancement)

For complex preferences, use LLM to extract structured data:
```python
prompt = f"""
User said: "{user_utterance}"

Extract any preferences or facts to remember.
Return JSON: {{"category": "...", "preference": "...", "value": "..."}}
If nothing to remember, return null.
"""
```

## Context Injection Strategy

### Relevant Memory Retrieval

When forming Saga's response, inject relevant memories:

```python
def get_relevant_context(user_utterance, intent):
    """Retrieve memories relevant to current interaction."""

    context = {
        "preferences": [],
        "facts": [],
        "session_context": get_active_session()
    }

    # 1. Get preferences for this category
    if intent.category:
        prefs = db.query(
            "SELECT * FROM preferences WHERE category = ? OR category = 'global'",
            (intent.category,)
        )
        context["preferences"] = prefs

    # 2. Get relevant facts (keyword matching for now)
    keywords = extract_keywords(user_utterance)
    facts = db.query(
        "SELECT * FROM facts WHERE relevance_tags LIKE ?",
        (f"%{keyword}%",)  # Simple keyword matching
    )
    context["facts"] = facts[:5]  # Limit to 5 most relevant

    return context
```

### LLM Prompt Structure

```python
system_prompt = f"""
You are Saga, a helpful voice assistant.

REMEMBERED PREFERENCES:
{format_preferences(context["preferences"])}

RELEVANT FACTS:
{format_facts(context["facts"])}

SESSION CONTEXT:
{context["session_context"]}

Use this information to provide personalized responses.
"""
```

## Context Window Management

### For loki.local (qwen2.5:7b)

**Context window:** 32K tokens (~24K words)

**Allocation strategy:**
- System prompt: ~500 tokens
- Preferences: ~200 tokens (top 10 relevant)
- Facts: ~300 tokens (top 5 relevant)
- Session history: ~2000 tokens (last 5-10 exchanges)
- User utterance: ~100 tokens
- **Total input:** ~3100 tokens
- **Available for response:** ~28K tokens (plenty!)

**We're nowhere near the limit** - can be generous with context

### Memory Pruning (Future)

If context gets large:
1. Summarize old conversation history
2. Score facts by relevance + recency
3. Keep only top-N most relevant items

## User Commands

### Memory Management Commands

```python
MEMORY_COMMANDS = {
    "show_preferences": ["what do you know about my preferences", "what are my preferences"],
    "show_facts": ["what do you remember about me", "what facts do you know"],
    "clear_memory": ["clear your memory", "forget everything", "reset memory"],
    "forget_specific": ["forget that [X]", "remove that preference"],
}
```

### Clear Memory Flow (with confirmation)

```
User: "Clear your memory"
Saga: "This will delete all your preferences and facts. Are you sure?"
User: "Yes" / "Confirm"
Saga: "Memory cleared. Starting fresh."

User: "No" / "Cancel"
Saga: "Memory preserved."
```

## Multi-User Readiness

### Current: Single User
- `user_id = 'default'` in all tables
- No authentication needed

### Future: Multi-User
- Voice biometrics to identify user
- OR: Explicit user selection ("This is Alice")
- Each user gets own preferences/facts
- Shared facts table for household context

**Database already supports this** with `user_id` column

## Implementation Phases

### Phase 1: Basic Preferences (MVP)
- [x] Define power phrases
- [ ] Implement pattern detection
- [ ] Create SQLite schema
- [ ] Basic preference storage
- [ ] Inject preferences into LLM context
- [ ] Test with "I prefer pink lights"

### Phase 2: Facts & Context
- [ ] Implement "remember that" detection
- [ ] Store facts with relevance tagging
- [ ] Keyword-based fact retrieval
- [ ] Session context management

### Phase 3: Memory Management
- [ ] "Show preferences" command
- [ ] "Clear memory" with confirmation
- [ ] "Forget that" for specific items
- [ ] Memory statistics/debugging

### Phase 4: Advanced (Future)
- [ ] LLM-assisted memory classification
- [ ] Semantic similarity for fact retrieval (vector DB)
- [ ] Conversation summarization
- [ ] Multi-user support
- [ ] Privacy controls (memory expiration)

## File Structure

```
saga_assistant/
├── memory/
│   ├── __init__.py
│   ├── database.py          # SQLite connection & schema
│   ├── preferences.py       # Preference storage/retrieval
│   ├── facts.py             # Fact storage/retrieval
│   ├── session.py           # Session context management
│   └── context_builder.py   # Build LLM context from memory
├── intent_parser.py         # Add memory patterns
└── run_assistant.py         # Integrate memory system
```

## Example Usage

```python
from saga_assistant.memory import MemoryManager

memory = MemoryManager()

# User says: "In general I like pink for my colored lights"
if detected_preference:
    memory.save_preference(
        category="lights",
        key="default_color",
        value="pink"
    )

# Later: User says: "Turn on the bedroom lights"
context = memory.get_relevant_context(
    utterance="Turn on the bedroom lights",
    category="lights"
)
# Returns: {"preferences": [{"key": "default_color", "value": "pink"}], ...}

# LLM gets context, uses pink as default color
```

## Open Questions

1. **Keyword extraction** - Simple split or use LLM/NLP library?
2. **Fact relevance scoring** - TF-IDF? Simple keyword count? LLM?
3. **Session timeout** - How long before session context is cleared?
4. **Memory limits** - Max preferences per category? Max facts total?

Let's start with Phase 1 and iterate!
