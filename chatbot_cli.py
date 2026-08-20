"""Terminal interface for the rule-based chatbot."""

import engine

LINE = "=" * 58
PROMPT = "\nYou:\t"


def say(message):
    print(f"{engine.BOT_NAME}:\t{message}")


def banner():
    print(f"\n{LINE}"
          f"\n\t{engine.BOT_NAME.upper()}  |  RULE-BASED CHAT ENGINE"
          f"\n\t{engine.rule_count()} rules loaded across "
          f"{len(engine.INTENTS)} intents"
          f"\n\tType 'help' for options, 'exit' to quit."
          f"\n{LINE}")


def main():
    banner()

    while True:
        try:
            clean_input = engine.sanitize(input(PROMPT))
        except (KeyboardInterrupt, EOFError):
            print()
            say("Session ended.\n")
            break

        if not clean_input:
            say("Nothing received. Type a message.")
            continue

        if engine.is_exit(clean_input):
            say("Goodbye. Thanks for chatting.\n")
            break

        result = engine.respond(clean_input)
        say(result["reply"])

        if result["path"] == "fallback":
            print("\t[ no rule matched ]")
        else:
            print(f"\t[ {result['path']} match -> {result['intent']} ]")


if __name__ == "__main__":
    main()
