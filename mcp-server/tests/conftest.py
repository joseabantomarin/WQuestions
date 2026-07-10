import os

# Isolate the test process from any real persistence log. Importing server.py
# builds a module-level WQSession from WQUESTIONS_LOG (default
# ~/.wquestions/universe.jsonl); pin it off so tests never read or write a real
# universe. Persistence tests pass WQSession(log_path=<tmp>) explicitly and are
# unaffected by this env var.
os.environ["WQUESTIONS_LOG"] = "off"
