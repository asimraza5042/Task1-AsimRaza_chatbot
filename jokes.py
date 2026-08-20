"""Random joke provider. Uses pyjokes when installed, otherwise built-in jokes."""

import random

JOKES = [
    "A programmer's wife tells him: \"Buy a loaf of bread, and if they have "
    "eggs, get a dozen.\" He came home with twelve loaves.",
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "There are only 10 types of people in the world: those who understand "
    "binary and those who don't.",
    "I would tell you a UDP joke, but you might not get it.",
    "A SQL query walks into a bar, walks up to two tables, and asks: "
    "\"Can I join you?\"",
    "Why did the Python programmer refuse to work on the AI project? "
    "He didn't want to deal with indentation errors in the neural network.",
    "How many programmers does it take to change a light bulb? None — "
    "that's a hardware problem.",
    "Rule-based AI walks into a bar. The bartender says: \"We don't serve "
    "your type here.\" The bot replies: \"I don't have a rule for that yet.\"",
]


def get_joke():
    try:
        import pyjokes

        return pyjokes.get_joke(language="en", category="neutral")
    except ImportError:
        return random.choice(JOKES)


def joke_count():
    return len(JOKES)
