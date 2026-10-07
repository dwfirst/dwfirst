"""
counter.py - token counting for IRIS window.

Uses llama tokenizer. Does NOT load model itself - receives it from outside.
"""
import os
import sys

X = "X:" + os.sep
MODULES = os.path.join(X, "01_core", "modules")
if MODULES not in sys.path:
    sys.path.insert(0, MODULES)


# Approximate overhead per message in chat format (role prefix, separators).
# Gemma 4 chat template adds <start_of_turn>role\n ... <end_of_turn>\n per message.
# Roughly 4-6 tokens overhead per message.
MSG_OVERHEAD = 5


def count_text(llama, text):
    """Count tokens in a single text string."""
    if not text:
        return 0
    return len(llama.tokenize(text.encode("utf-8")))


def count_message(llama, msg):
    """Count tokens in one chat message including format overhead."""
    return count_text(llama, msg.get("content", "")) + MSG_OVERHEAD


def count_window(llama, messages):
    """Count total tokens in a list of chat messages."""
    total = 0
    for m in messages:
        total += count_message(llama, m)
    return total


def fits(llama, messages, budget):
    """Check if messages fit into token budget."""
    return count_window(llama, messages) <= budget


def trim_to_budget(llama, messages, budget, keep_last=4):
    """
    Drop oldest messages until it fits budget.
    Always keeps last keep_last messages.
    Returns (kept_messages, dropped_messages).
    """
    if count_window(llama, messages) <= budget:
        return list(messages), []

    kept = list(messages)
    dropped = []
    while len(kept) > keep_last and count_window(llama, kept) > budget:
        dropped.append(kept.pop(0))
    return kept, dropped


if __name__ == "__main__":
    print("counter.py - module. Needs llama object to work.")