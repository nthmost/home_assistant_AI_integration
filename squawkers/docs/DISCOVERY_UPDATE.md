# Automated Command Discovery - Update

## What's New

**Automated command discovery is now working!** 🎉

You can now automatically discover all your learned IR commands from Home Assistant.

## The Discovery Script

```bash
pipenv run python squawkers/discover_commands.py
```

This script:
1. SSHs to your Home Assistant server
2. Reads `/config/.storage/broadlink_remote_*_codes`
3. Extracts all commands for the 'squawkers' device
4. Displays them organized by category
5. Shows usage examples with your actual command names

## What We Discovered

You have **32 IR commands** (not the 26 I originally expected!):

### Categories
- **Universal**: DANCE, RESET (2 commands)
- **Plain Buttons**: Button A-F (6 commands)
- **Commands**: Command A-F (6 commands)
- **Gags**: Gags A-F (6 commands)
- **Record Command**: Record Command A-F (6 commands)
- **Record Response**: Record Response A-F (6 commands)

### What Changed

**Before:** I guessed you had "Response Button A", "Command Button C", etc.

**After Discovery:** Your actual naming is:
- `Command A` (not "Command Button A")
- `Button B` (plain, not "Response Button B")
- `Gags A` through `Gags F`
- `Record Command A` through `Record Command F` (new!)
- `Record Response A` through `Record Response F` (new!)

## Updated Files

1. **`discover_commands.py`** ⭐ NEW - Automated discovery script
2. **`squawkers_full.py`** - Updated with all 32 commands
3. **`MY_COMMANDS.md`** - Updated with discovered commands

## Updated SquawkersFull Class

Now has **32 convenience methods** matching your 32 commands:

```python
from squawkers.squawkers_full import SquawkersFull

squawkers = SquawkersFull(client)

# Universal (2)
squawkers.dance()
squawkers.reset()

# Plain Buttons (6)
squawkers.button_a() through squawkers.button_f()

# Commands (6)
squawkers.command_a() through squawkers.command_f()

# Gags (6)
squawkers.gag_a() through squawkers.gag_f()

# Record Commands (6) - NEW!
squawkers.record_command_a() through squawkers.record_command_f()

# Record Responses (6) - NEW!
squawkers.record_response_a() through squawkers.record_response_f()
```

## How Discovery Works

### Technical Details

1. **SSH Connection**: Connects to `homeassistant.local` as root
2. **File Location**: `/config/.storage/broadlink_remote_MACADDRESS_codes`
3. **Format**: JSON with structure:
   ```json
   {
     "data": {
       "squawkers": {
         "DANCE": "base64_ir_code...",
         "Button A": "base64_ir_code...",
         ...
       }
     }
   }
   ```
4. **Extraction**: Parses JSON, finds 'squawkers' key, lists command names
5. **Categorization**: Groups by naming pattern

### Requirements

- SSH access to Home Assistant (✓ you have this)
- SSH keys configured (✓ working)
- Broadlink integration active (✓ confirmed)

## Running Discovery

### Basic Discovery
```bash
pipenv run python squawkers/discover_commands.py
```

Output:
- All commands organized by category
- Behaviors (from manual) where known
- Usage examples with your actual command names
- Total command count

### Alternative: Check Full Class
```bash
pipenv run python squawkers/squawkers_full.py
```

Shows all 32 convenience methods available.

## Benefits of Automated Discovery

**Before:**
- Manual guessing of command names
- Might miss commands
- Had to check HA UI manually

**After:**
- Automatically finds all commands
- Correct names guaranteed
- Can re-run anytime you learn new codes
- Generates accurate usage examples

## Re-Discovery

If you learn new commands in the future:

```bash
pipenv run python squawkers/discover_commands.py
```

This will show your updated command list automatically!

## Integration

The discovery output format is designed to be:
- Human-readable (for you)
- Machine-parseable (for scripts)
- Copy-paste friendly (usage examples)

You could even auto-generate code from it!

## Next Steps

1. ✅ **Discovery working** - Automated via SSH
2. ✅ **All 32 commands mapped** - In SquawkersFull
3. ✅ **Documentation updated** - MY_COMMANDS.md
4. 🎯 **Test behaviors** - Try each command type
5. 🚀 **Integrate with Saga** - Voice control ready

## Quick Reference

```bash
# Discover all commands
pipenv run python squawkers/discover_commands.py

# See convenience methods
pipenv run python squawkers/squawkers_full.py

# Test basic functionality
pipenv run python squawkers/try_squawkers.py

# Read your commands
cat squawkers/MY_COMMANDS.md
```

---

**Bottom line:** You can now automatically discover your IR commands, and the convenience class has all 32 methods ready to use!
