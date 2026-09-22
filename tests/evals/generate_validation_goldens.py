"""Generate validation goldens for Hemmingway claims."""
import json

# ============================================================
# 1. Everyday Writing / CommunicationBench-style
# ============================================================
COMMUNICATION = [
    ("Write a text to my landlord about a broken boiler.", "messages"),
    ("Email my boss asking for a day off next Friday.", "messages"),
    ("Text my friend to cancel dinner plans tonight.", "messages"),
    ("Write a message to my neighbour about their loud music.", "messages"),
    ("Email to a colleague about a missed deadline — keep it professional.", "messages"),
    ("Write a thank-you note after a job interview.", "messages"),
    ("Text to my partner saying I'll be late for dinner.", "messages"),
    ("Write an apology email to a customer for a shipping delay.", "messages"),
    ("Message to my landlord about a leak under the sink.", "messages"),
    ("Email declining a meeting invite politely.", "messages"),
    ("Write a note to my child's teacher explaining an absence.", "messages"),
    ("Text to a friend recommending a restaurant.", "messages"),
]

# ============================================================
# 2. Human-Likeness (person-written vs model-written)
# ============================================================
HUMAN_LIKE = [
    ("Write a text to my wife saying I'm stuck at the office and will be home late. Keep it casual.", "human"),
    ("Text from a mate asking if you want to go to the pub tonight.", "human"),
    ("Email from a colleague asking if you've finished the report.", "human"),
    ("A quick message to your mum saying thanks for the birthday present.", "human"),
    ("A passive-aggressive note to your flatmate about washing up.", "human"),
    ("A message to a friend cancelling plans because you're tired.", "human"),
]

# ============================================================
# 3. Hard Asks / Money & Admin
# ============================================================
HARD_ASKS = [
    ("Write an email disputing a parking fine.", "hard"),
    ("Draft a letter to my bank to unblock my card.", "hard"),
    ("Write a message to my landlord requesting a rent review.", "hard"),
    ("Complain to a company about a faulty product — be firm but polite.", "hard"),
    ("Write an email asking my employer about my pension contributions.", "hard"),
    ("Draft a subject access request to a company holding my data.", "hard"),
    ("Write to my council about a missed bin collection.", "hard"),
    ("Email to my insurance company to make a claim.", "hard"),
]

# ============================================================
# 4. Message-Not-a-Memo (no preamble, no options, no notes)
# ============================================================
MESSAGE_NOT_MEMO = [
    ("Write the text I send my landlord about the broken boiler. Output ONLY the message, no preamble, no options, no commentary.", "message_only"),
    ("Write an email to my boss asking for a day off. Output ONLY the email, no preamble, no options, no commentary.", "message_only"),
    ("Write a text to my friend cancelling plans. Output ONLY the text, no preamble, no options, no commentary.", "message_only"),
    ("Write a message to my neighbour about noise. Output ONLY the message, no preamble, no options, no commentary.", "message_only"),
    ("Write an apology to a customer for a late delivery. Output ONLY the apology, no preamble, no options, no commentary.", "message_only"),
]

# ============================================================
# 5. EQ-Bench (emotional intelligence)
# ============================================================
EQ_TASKS = [
    ("My friend just told me they lost their job. What do I say to them?", "eq"),
    ("My partner is stressed about money. How do I approach the conversation?", "eq"),
    ("A colleague snapped at me in a meeting. What do I do?", "eq"),
    ("My mum is upset that I haven't visited. What do I say?", "eq"),
    ("A friend is making a bad decision. How do I talk to them about it?", "eq"),
]

# ============================================================
# 6. StoryBench (creative writing)
# ============================================================
STORY = [
    ("Write a 200-word story about a man who finds a letter in a bottle.", "story"),
    ("Write a 200-word story about the last person on Earth.", "story"),
    ("Write a 200-word story about a conversation in a lift.", "story"),
    ("Write a 200-word story about someone returning to their childhood home.", "story"),
    ("Write a 200-word story about a phone call at 3am.", "story"),
]

def main():
    all_goldens = {
        "communication": [{"input": inp, "category": cat} for inp, cat in COMMUNICATION],
        "human_likeness": [{"input": inp, "category": cat} for inp, cat in HUMAN_LIKE],
        "hard_asks": [{"input": inp, "category": cat} for inp, cat in HARD_ASKS],
        "message_not_memo": [{"input": inp, "category": cat} for inp, cat in MESSAGE_NOT_MEMO],
        "eq_tasks": [{"input": inp, "category": cat} for inp, cat in EQ_TASKS],
        "story": [{"input": inp, "category": cat} for inp, cat in STORY],
    }

    output_path = "tests/evals/.dataset_validation.json"
    with open(output_path, "w") as f:
        json.dump(all_goldens, f, indent=2)

    for category, goldens in all_goldens.items():
        print(f"  {category}: {len(goldens)} goldens")
    print(f"\nTotal: {sum(len(g) for g in all_goldens.values())} goldens to {output_path}")

if __name__ == "__main__":
    main()
