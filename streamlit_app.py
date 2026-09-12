import streamlit as st
from debate_engine import app, MAX_ROUNDS

st.title("Multi-Agent Debate Simulator")

topic = st.text_input("Enter the debate topic:")
if st.button("Start Debate") and topic:
    initial_state = {
        "topic": topic,
        "history": [],
        "round": 0,
        "max_rounds": MAX_ROUNDS,
        "verdict": None,
    }

    debate_stream = app.stream(initial_state)

    while True:
        with st.spinner("Debater is thinking..."):
            try:
                step = next(debate_stream)
            except StopIteration:
                break

        node_name, node_output = list(step.items())[0]
        if node_name in ("pro", "con"):
            latest_entry = node_output["history"][-1]
            role = "user" if latest_entry["side"] == "Pro" else "assistant"
            with st.chat_message(role):
                st.write(f"**{latest_entry['side']}**: {latest_entry['argument']}")

        elif node_name == "judge":
            verdict = node_output["verdict"]
            st.write("Winner:", verdict.winner)
            st.write("Reasoning:", verdict.reasoning)
            st.write(f"Pro: {verdict.pro_score}/10, Con: {verdict.con_score}/10")