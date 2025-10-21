# Claude Code Guidelines for this Project

## Python Code Standards

### Exception Handling
- **Avoid long try-except blocks** - keep them focused and minimal
- **Never use generic `Exception`** - always catch specific exception types
- Use multiple specific exception handlers rather than one broad catch-all

### Logging Standards
- **Build logging into scripts from the start** - it's not optional
- Follow proper log levels:
  - `INFO` - Key milestones, workflow progress, successful operations
  - `DEBUG` - Detailed diagnostic information, data dumps, trace info
  - `WARNING` - Something unexpected but recoverable happened
  - `ERROR` - Operation failed but application continues
  - `CRITICAL` - System-level failure

- **More logging is better than less**, but must be tunable
- Enable log level filtering so we can turn off the firehose when needed
- **Use colors, formatting, and emojis** to enhance log readability
  - Make logs human-friendly AND machine-parseable
  - This is a log-heavy project where logs will be consumed by other agents
  - Clear, well-formatted logs are critical for debugging complex orchestrations

### Log Consumption Pattern
- Logs will frequently be read and analyzed by other AI agents
- Lack of visibility into system state makes complex systems hard to debug
- Design logs with both human operators and automated analysis in mind

### File Naming Conventions
- **Never use `test_*.py` for demo/trial scripts** - this prefix is reserved for unit tests
- Use descriptive names like `demo_*.py`, `try_*.py`, `run_*.py`, or `example_*.py` for experimental scripts
- Keep `test_*.py` exclusively for proper unit tests in the `tests/` directory

### Code Organization
- **All imports at top of file, never in functions**
- Keep imports organized: stdlib, third-party, local modules
- Avoid lazy imports unless there's a strong performance reason

### Display Mode vs Headless Mode
- **ASCII displays: completely suppress logging when display is active**
- When running with interactive displays (curses, rich panels, etc.), logs interfere with the display
- **Simple rule: display mode = no logs, headless mode = normal logs**
- This ensures clean visual output without log noise
- Use `--display` flag pattern for scripts that offer visual modes

### Streamlit Development
- **`st.rerun()` calls are almost never necessary** - Streamlit's run model handles reruns automatically
- Every widget interaction triggers a natural rerun of the entire script
- Fetch fresh state at the top of the script - it runs on every interaction
- Let Streamlit's reactive model work for you - don't fight it with manual reruns
- Pattern: Fetch state → Render UI → Handle interactions → (Streamlit reruns automatically)

## Collaboration Style

### Decision Making
- **When asked "should we X?" - DO NOT implement X immediately**
- Wait for confirmation and discussion first
- Offer multiple solution options when available (within reason)
- Present trade-offs clearly

---

**Last Updated:** October 2025
