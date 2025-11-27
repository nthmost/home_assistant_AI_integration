# Parking Voice Commands for Saga

## Quick Reference

These voice commands now work with Saga!

### Save Parking Location

Say "Hey Saga" then:
- "I parked on the north side of Anza between 7th and 8th ave"
- "My car is on Valencia between 18th and 19th"
- "I parked on Mission near 24th street"

### Check Where You Parked

Say "Hey Saga" then:
- "Where did I park?"
- "Where's my car?"
- "Where am I parked?"

### Check Street Sweeping

Say "Hey Saga" then:
- "When do I need to move my car?"
- "Is there street sweeping?"
- "When is street sweeping?"
- "When is street cleaning?"

## Example Conversation

```
You: "Hey Saga"
Saga: *beep*

You: "I parked on the north side of Anza between 7th and 8th ave"
Saga: "Got it. You're parked on Anza St. I'll remind you about street sweeping."

---

You: "Hey Saga"
Saga: *beep*

You: "Where did I park?"
Saga: "Parked on Anza St 07th Ave - 08th Ave (North side).
       Next sweeping: Friday, November 28 8am-10am"

---

You: "Hey Saga"
Saga: *beep*

You: "When do I need to move my car?"
Saga: "Street sweeping is Friday, November 28 from 8 AM to 10 AM."
```

## How It Works

```
Wakeword Detection → Speech-to-Text → Intent Parser → Parking Manager → TTS Response
```

1. **Wakeword**: "Hey Saga" activates the assistant
2. **STT**: Your command is transcribed using faster-whisper
3. **Intent Parser**: Detects parking intent and extracts location
4. **Parking Manager**:
   - Parses natural language location
   - Looks up street sweeping from local SF database
   - Saves/retrieves parking state
5. **Response**: Saga speaks the answer via TTS

## Technical Details

- **100% Offline**: Works without internet (after initial data download)
- **Local Database**: 37,878 SF street sweeping records cached
- **Natural Language**: Fuzzy street name matching, handles variations
- **Persistent State**: Parking saved to `~/.saga_assistant/parking_state.json`
- **Fast**: Lookup from local cache is <1ms

## Testing

### Text-based Testing
```bash
# Test just the parking intents (no voice)
pipenv run python saga_assistant/demo_parking_voice.py
```

### Full Voice Testing
```bash
# Test with wakeword + voice I/O
pipenv run python saga_assistant/run_assistant.py
```

Then say:
1. "Hey Saga"
2. Wait for beep
3. "I parked on Valencia between 18th and 19th"
4. Listen for response

## Supported Location Formats

- **With cross streets**: "north side of Anza between 7th and 8th"
- **Simple cross streets**: "Valencia between 18th and 19th"
- **Near**: "Mission near 24th street"
- **Address** (future): "1234 Valencia Street"

## Troubleshooting

**"I couldn't find that street"**
- Check the street name spelling
- Try with the street type: "Valencia Street" or "Valencia St"
- SF has: St, Ave, Blvd, Dr, Way, Ln

**"No street sweeping found"**
- Some blocks don't have regular sweeping
- Database might not have that specific block
- Try nearby blocks

**Wrong block detected**
- Be specific: "between 7th and 8th" not just "on 7th"
- Use "north/south/east/west side" to specify which side

## Files Modified

- `run_assistant.py` - Main loop integration
- `intent_parser.py` - Parking intent patterns and handlers
- `parking.py` - Location parsing, schedule lookup, state management

---

**Ready to try it?** Just say "Hey Saga, I parked on..." and Saga will remember!
