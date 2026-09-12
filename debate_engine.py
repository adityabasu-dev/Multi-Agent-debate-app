from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from typing import Literal, TypedDict, List, Dict
from langgraph.graph import StateGraph, END
import streamlit as st

if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

#model initialization
llm=ChatGroq(model="openai/gpt-oss-120b")
#Judge class to determine the winner of the debate
class DebateVerdict(BaseModel):
    winner: Literal["Pro", "Con"] = Field(..., description="The winner of the debate")
    reasoning: str = Field(..., description="The reasoning behind the judge's decision in 1-2 sentences")
    pro_score: int = Field(..., description="Score for the Pro debater (0-10)")
    con_score: int = Field(..., description="Score for the Con debater (0-10)")
#Debate state class to keep track of the debate's progress
class DebateState(TypedDict):
    topic: str
    history: List[Dict[str, str]]  # List of arguments with side and round information
    round: int
    max_rounds: int
    verdict:DebateVerdict | None

#Judge prompt template
judge_template=ChatPromptTemplate([
    ("system", "You are a fair and impartial judge of a debate. Determine the winner based on the arguments presented by each debater."),
    ("user", "Topic: {topic}\n\n Transcript: {transcript}\n\n Evaluate the debate and provide a verdict"),
])


#Prompt templates for the debaters
pro_template=ChatPromptTemplate([
    ("system", "You are a sharp persuasive debater, who is arguing FOR the motion. Keep responses concise and limited to 2-3 punchy sentences. You will be shown the full debate transcript, including your own previous arguments. Do not repeat a point, phrase, or argument you have already made — each turn must introduce a genuinely new angle, piece of evidence, or rebuttal. If you're running low on distinct angles, go narrower and more specific rather than restating the same idea in different words."),
    ("user", "topic:{topic}\n\n history:{transcript}"),
])
con_template=ChatPromptTemplate([
    ("system", "You are a sharp persuasive debater, who is arguing AGAINST the motion. Keep responses concise and limited to 2-3 punchy sentences. You will be shown the full debate transcript, including your own previous arguments. You've just heard the opponent's argument and you need to respond to it. Your response should be persuasive, logical, and compelling. Avoid repeating the opponent's points and focus on presenting your own arguments effectively."),
    ("user", "topic:{topic}\n\n history:{transcript}"),
])


#Chain creation
judge_llm = llm.with_structured_output(DebateVerdict)
judge_chain = judge_template | judge_llm
pro_chain = pro_template | llm | StrOutputParser()
con_chain = con_template | llm | StrOutputParser()

MAX_ROUNDS = 3  


#functions to handle the debate flow
def format_history(history: List[Dict[str, str]]) -> str:
    return "\n".join([f"Round {i//2 + 1} - {entry['side']} debater: {entry['argument']}" for i, entry in enumerate(history)])

def pro_node(state: DebateState) -> dict:
    history_text = format_history(state["history"])
    response = pro_chain.invoke({"topic": state["topic"], "transcript": history_text})
    new_entry = {"side": "Pro", "argument": response}
    return {"history": state["history"] + [new_entry]}

def con_node(state: DebateState) -> dict:
    history_text = format_history(state["history"])
    response = con_chain.invoke({"topic": state["topic"], "transcript": history_text})
    new_entry = {"side": "Con", "argument": response}
    return {"history": state["history"] + [new_entry], "round": state["round"] + 1}

def judge_node(state: DebateState) -> dict:
    transcript_text = format_history(state["history"])
    verdict = judge_chain.invoke({"topic": state["topic"], "transcript": transcript_text})
    return {"verdict": verdict}

def should_continue(state: DebateState) -> str:
    if state["round"] < state["max_rounds"]:
        return "continue"
    return "judge"


#Create the state graph for the debate
graph = StateGraph(DebateState)
graph.add_node("pro", pro_node)
graph.add_node("con", con_node)
graph.add_node("judge", judge_node)

graph.set_entry_point("pro")
graph.add_edge("pro", "con")
graph.add_conditional_edges("con", should_continue, {"continue": "pro", "judge": "judge"})
graph.add_edge("judge", END)

app = graph.compile()

