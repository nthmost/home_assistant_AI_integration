# Squawkers McCaw IR Commands Reference

Based on the official Squawkers McCaw manual and known working commands.

## Confirmed Working Commands

These commands have been tested and work:

- **DANCE** - Makes Squawkers dance (most reliable, works in any mode)
- **RESET** - Stops current action and returns to hangout mode

## Remote Control Buttons (A-F)

According to the manual, these buttons trigger preset behaviors:

### Response Mode Buttons:
- **Button A**: Be startled with a squawk!
- **Button B**: Laugh
- **Button C**: Laugh hilariously
- **Button D**: Warble
- **Button E**: Say "Whatever!!"
- **Button F**: Play along with the remote

### Command Mode Buttons:
Same A-F buttons, but used for custom voice command/response pairs when programmed.

### Gags Mode Buttons:
Same A-F buttons, but different behaviors (manual doesn't specify exact behaviors).

## Remote Control Functions

### Mode Switches:
- **Content Selector**: Parrot Talk / Custom Speech
- **Remote Switch**: Response / Command / Gags

### Special Buttons:
- **DANCE**: Triggers dance behavior
- **RESET**: Stops current mode, returns to hangout
- **REPEAT**: In repeat mode, makes Squawkers repeat what you say
- **Custom Record**: Records custom vocabulary

## IR Command Naming Convention

When learning commands in Home Assistant, you might use names like:

- `DANCE` - Dance button
- `RESET` - Reset button
- `RESPONSE_A` through `RESPONSE_F` - Response mode buttons
- `COMMAND_A` through `COMMAND_F` - Command mode buttons
- `GAGS_A` through `GAGS_F` - Gags mode buttons
- `REPEAT` - Repeat button
- `CUSTOM_RECORD` - Custom record button

## Using Commands with Squawkers Class

```python
from squawkers import Squawkers
from saga_assistant.ha_client import HomeAssistantClient

client = HomeAssistantClient()
squawkers = Squawkers(client)

# Confirmed working
squawkers.dance()
squawkers.reset()

# If you've learned other commands
squawkers.command("RESPONSE_A")  # Startled squawk
squawkers.command("RESPONSE_B")  # Laugh
squawkers.command("RESPONSE_C")  # Laugh hilariously
squawkers.command("RESPONSE_D")  # Warble
squawkers.command("RESPONSE_E")  # "Whatever!!"
squawkers.command("RESPONSE_F")  # Play along

# Custom repeats for unreliable commands
squawkers.command("RESPONSE_A", num_repeats=5)
```

## Voice Commands

Squawkers responds to these voice commands (requires microphone, not IR):

- "Peek-a-boo!" - Plays peek-a-boo game
- "Wanna dance?" - Enters dance mode
- "Polly!" - Enters repeat mode

**Note**: Voice commands use the built-in microphone, not the IR remote. These cannot be triggered via Home Assistant IR control.

## Sensors

Squawkers has these sensors (not controllable via IR):

- **Light Sensor** (forehead) - Wave hand to make him blink
- **Back Sensor** - Pet back for coos and movement
- **Head Sensor** - Pet head firmly to relax or exit modes
- **Beak Sensor** - Pet beak for coos or kisses
- **Tongue Switch** - Place cracker on tongue for feeding behavior

## Play Modes

### Hangout Mode (Default)
- Relaxing, making occasional sounds
- Responds to sensors
- Ready for interaction

### Dance Mode
- Triggered by "Wanna dance?" voice or DANCE button
- Dances to music beat or own beat
- Exits after 8 seconds of inactivity or RESET button

### Repeat Mode
- Triggered by "Polly!" voice command
- Repeats what you say in silly voice
- Exits after 1 minute inactivity or RESET button

## Programming Custom Commands

You can program buttons A-F with custom voice commands and responses:

1. Set Remote to "Command" mode
2. Press and hold button (A-F)
3. Squawkers squawks when ready
4. Speak command phrase (up to 25 seconds)
5. Speak it again when prompted
6. Squawkers repeats it back

Then program the response:

1. Set Remote to "Response" mode
2. Press and hold same button
3. Squawkers squawks when ready
4. Speak response phrase (up to 3 seconds)
5. Squawkers repeats it back

Now when Squawkers hears the command, he'll say the response!

**Note**: Custom programmed commands are stored in Squawkers' memory, not in Home Assistant. The IR buttons just trigger them.

## Discovering Your Learned Commands

To see what IR commands you've learned in Home Assistant:

1. Open Home Assistant web interface
2. Go to: Developer Tools > Services
3. Select service: `remote.send_command`
4. Select entity: `remote.office_lights`
5. Set device: `squawkers`
6. The command dropdown shows all learned commands

Or run: `python squawkers/list_commands.py`

## Reference

- Original manual: `squawkers/MANUAL.txt`
- GitHub project: https://github.com/playfultechnology/SquawkersMcGraw
- IR timing codes: `squawkers/broadlink_squawkers.py`
