# Project 1 — Rule-Based AI Chatbot

DecodeLabs Industrial Training Kit · Batch 2026

A conversational agent whose every reply comes from an explicit rule written in
advance. No model, no training data, no API call. The point of the project is
control flow and traceability, not machine learning.

## Files

| File | Purpose |
|---|---|
| `engine.py` | The rule engine. All logic lives here — no printing, no widgets. |
| `jokes.py` | Joke library. Random jokes via `get_joke()`; uses `pyjokes` when installed. |
| `chatbot_cli.py` | Terminal interface. This is the deliverable the brief specifies. |
| `chatbot_gui.py` | Desktop interface built with Tkinter. |
| `requirements.txt` | Optional dependency list (`pyjokes` for extra jokes). |
| `README.md` | This file. |

Both interfaces import the same engine, so they behave identically. Change a
rule in `engine.py` and it changes in both.

## Running it

Requires Python 3.8+. Tkinter ships with Python on Windows and macOS.

```bash
pip install -r requirements.txt   # optional — adds pyjokes for more jokes
python chatbot_cli.py             # terminal version
python chatbot_gui.py             # desktop version
```

On Linux, if the GUI reports a missing module:
`sudo apt install python3-tk`

## How it works

Each turn follows the IPO model from the brief:

**Input** — read raw text and sanitize it. `sanitize()` lowercases, strips
whitespace, removes punctuation and collapses double spaces, so
`"  What TIME is it??  "` and `"what time is it"` are treated as the same
thing.

**Process** — match the cleaned text against `RULES`, a flat dictionary of
phrase → reply built once at import time. Matching runs in three passes:

1. **Exact** — the whole sentence is a key. One dictionary lookup, O(1).
2. **Keyword** — a trigger phrase appears inside the sentence. The *longest*
   match wins, so `"hey, what time is it"` answers with the clock rather than
   a greeting, even though `hey` appears first.
3. **Fallback** — nothing matched, so return a fixed safe reply. The bot never
   guesses and never crashes.

**Output** — print or draw the reply, along with which rule produced it.

## Why a dictionary and not if-elif

An if-elif ladder is O(n): Python evaluates every branch in order until one is
true, so the 40th rule costs 40 comparisons. A dictionary is O(1) — one hash
lookup, the same cost whether there are 8 rules or 8,000. `dict.get(key,
default)` also performs the lookup and the fallback in a single operation.

## Requirements checklist

| Brief requirement | Where it is implemented |
|---|---|
| Continuous input loop | `while True` in `chatbot_cli.py → main()` |
| Sanitization (case, whitespace) | `engine.sanitize()` |
| Knowledge base, 5+ intents | `engine.INTENTS` — 9 intents, 40+ trigger phrases |
| Joke library | `jokes.py` — random jokes with pyjokes fallback |
| Nested conditions | Repeat greetings get a different reply via session state |
| Default fallback response | `engine.FALLBACK_REPLY` |
| Clean exit command | `engine.EXIT_COMMANDS` → `break` |

## The GUI

The brief describes a rule-based system as a "white box" — input, logic,
output, nothing hidden. The interface is built around that idea. The right
panel lists the loaded knowledge base and highlights whichever intent just
fired, and the trace card underneath reports the last input, the rule that
matched it, and which of the three passes found it. Colour encodes the path:
green for exact, amber for keyword, grey for fallback.

Other details: replies appear after a short delay with a typing indicator,
messages re-flow when the window is resized, Enter sends, the quick chips
below the conversation send common phrases, and typing `exit` closes the
session and disables the input rather than killing the window.

## Extending it

- Add an intent to `engine.INTENTS`; both interfaces pick it up automatically.
- Give a reply a function instead of a string when the answer must be live —
  see how `time`, `date`, and `joke` are written.
- Track the last few turns to give context-aware replies (a second `hello`
  could get a different answer from the first).

## Known limits — worth being honest about

Exact and keyword matching cannot handle typos or unseen phrasings. `"helo"`
fails. `"I would like my money returned"` fails unless someone wrote that rule.
Covering every phrasing by hand is an infinite task, which is exactly the
problem semantic search and embeddings solve in Project 2.
