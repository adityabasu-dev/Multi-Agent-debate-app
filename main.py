from debate_engine import app, MAX_ROUNDS

topic = input("Enter the debate topic: ")
result = app.invoke({
    "topic": topic,
    "history": [],
    "round": 0,
    "max_rounds": MAX_ROUNDS,
    "verdict": None,
})
for entry in result["history"]:
    print(f"{entry['side']}: {entry['argument']}\n")
print("Winner:", result["verdict"].winner)
print("Reasoning:", result["verdict"].reasoning)
print(f"Pro: {result['verdict'].pro_score}/10, Con: {result['verdict'].con_score}/10")