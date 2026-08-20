"""Rule engine for the chatbot. Shared by CLI and GUI interfaces."""

import re
from datetime import datetime

import jokes

BOT_NAME = "DecodeBot"

_session = {"greeting_count": 0}

EXIT_COMMANDS = {"exit", "quit", "bye", "goodbye", "see you"}
FALLBACK_REPLY = "I don't have a rule for that yet. Type 'help' to see what I know."

INTENTS = {
    "greeting": {
        "label": "Greeting",
        "keys": ["hello", "hi", "hey", "hii", "yo", "good morning", "good evening"],
        "reply": f"Hello. I'm {BOT_NAME}, a rule-based engine. "
                 f"Ask me something, or type 'help' for the full list.",
    },
    "identity": {
        "label": "Identity",
        "keys": ["who are you", "what are you", "your name", "name"],
        "reply": f"I'm {BOT_NAME}. There's no AI model behind me - every answer "
                 f"I give was written as an explicit rule by my developer.",
    },
    "wellbeing": {
        "label": "Status",
        "keys": ["how are you", "how r u", "how is it going", "whats up"],
        "reply": "Operating normally. I'm deterministic, so I behave the same "
                 "way every single run.",
    },
    "capability": {
        "label": "Capability",
        "keys": ["help", "what can you do", "commands", "options", "menu"],
        "reply": "I currently respond to: greetings, questions about me, my "
                 "status, the time, the date, jokes, AI basics, and thanks. "
                 "Type 'exit' to close the session.",
    },
    "time": {
        "label": "Clock",
        "keys": ["time", "what time is it", "current time"],
        "reply": lambda: f"It's {datetime.now().strftime('%I:%M %p')} right now.",
    },
    "date": {
        "label": "Calendar",
        "keys": ["date", "what is the date", "today", "day"],
        "reply": lambda: f"Today is {datetime.now().strftime('%A, %d %B %Y')}.",
    },
    "joke": {
        "label": "Humour",
        "keys": ["joke", "tell me a joke", "make me a joke", "make me laugh",
                 "funny", "another joke"],
        "reply": jokes.get_joke,
    },
    "ai_concept": {
        "label": "AI Basics",
        "keys": ["what is ai", "what is artificial intelligence",
                 "what is rule based ai", "what is machine learning",
                 "what is the ipo model"],
        "reply": "AI is software that mimics intelligent behaviour. This bot is "
                 "rule-based: every answer comes from a dictionary lookup, not a "
                 "model. Machine learning lets systems learn from data; rule-based "
                 "systems use explicit if-else logic. The IPO model is Input -> "
                 "Process -> Output.",
    },
    "gratitude": {
        "label": "Gratitude",
        "keys": ["thanks", "thank you", "thx", "appreciate it"],
        "reply": "You're welcome.",
    },
}

RULES = {}
for _name, _intent in INTENTS.items():
    for _key in _intent["keys"]:
        RULES[_key] = (_name, _intent["reply"])


def sanitize(raw_text):
    lowered = raw_text.lower().strip()
    stripped = re.sub(r"[^\w\s']", " ", lowered)
    return re.sub(r"\s+", " ", stripped).strip()


def is_exit(clean_text):
    return clean_text in EXIT_COMMANDS


def respond(clean_text):
    hit = RULES.get(clean_text)
    if hit:
        name, reply = hit
        return _build_result(name, reply, "exact", clean_text)

    # Longest keyword wins so "what time is it" beats "hey" in "hey, what time is it".
    padded = f" {clean_text} "
    best_key = None
    for key in RULES:
        if f" {key} " in padded:
            if best_key is None or len(key) > len(best_key):
                best_key = key

    if best_key:
        name, reply = RULES[best_key]
        return _build_result(name, reply, "keyword", best_key)

    return {
        "reply": FALLBACK_REPLY,
        "intent": None,
        "path": "fallback",
        "matched": None,
    }


def _build_result(name, reply, path, matched):
    if name == "greeting":
        _session["greeting_count"] += 1
        if _session["greeting_count"] > 1:
            text = (f"Welcome back. You've greeted me {_session['greeting_count']} "
                    f"times this session. What can I help with?")
            return {
                "reply": text,
                "intent": name,
                "path": path,
                "matched": matched,
            }

    return {
        "reply": reply() if callable(reply) else reply,
        "intent": name,
        "path": path,
        "matched": matched,
    }


def rule_count():
    return len(RULES)


def intent_rows():
    return [(n, i["label"], len(i["keys"])) for n, i in INTENTS.items()]
