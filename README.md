# Multi-Agent Debate App

Two AI agents debate opposite sides of a topic, then a third agent judges the winner — built to learn LangChain and LangGraph by implementing agentic orchestration from scratch.

## How it works

- **Pro** and **Con** debater chains argue opposite stances on a given topic, alternating turns.
- Each debater sees the **full transcript so far** (including its own prior turns) and is explicitly instructed not to repeat itself — forcing genuine argumentative progression instead of rephrased talking points.
- Turn-taking and stopping conditions are handled by a **LangGraph state graph**, not a manual loop — nodes for `pro`, `con`, and `judge`, with a conditional edge deciding whether to continue debating or move to judgment.
- The **judge** returns a structured, typed verdict (winner, reasoning, scores per side) via Pydantic + `with_structured_output`, instead of free-text output.

## Tech stack

- [LangChain](https://python.langchain.com/) — prompt templates, LCEL chains, structured output
- [LangGraph](https://langchain-ai.github.io/langgraph/) — state graph orchestration
- [Groq](https://console.groq.com/) — free-tier inference (`openai/gpt-oss-120b`)

## Setup

```bash
git clone <your-repo-url>
cd multi-agent-debater
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate on Windows
pip install langchain langchain-groq langgraph python-dotenv pydantic
```

Create a `.env` file with a free Groq API key ([console.groq.com](https://console.groq.com)):
GROQ_API_KEY=your_key_here


## Run

```bash
python main.py
```

You'll be prompted for a debate topic, then the Pro and Con agents will argue for a fixed number of rounds before the judge delivers a verdict.
