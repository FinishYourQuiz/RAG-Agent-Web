# backend/src/graph.py
from __future__ import annotations
import os, pathlib, tempfile
from typing import Dict, List

from langgraph.graph import StateGraph, END
from langchain_aws import BedrockChat, BedrockEmbeddings          # AWS Bedrock
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# ---------- 1. State definition ----------
class ChatState(Dict):
    """Holds {history, question, sources, answer}."""

# ---------- 2. Nodes ----------
def split_and_embed(state: ChatState) -> ChatState:
    text = state["document_text"]
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=80)
    chunks = splitter.split_text(text)

    embedder = BedrockEmbeddings(model_id="amazon.titan-embed-image-v1")
    vectordb = FAISS.from_texts(texts=chunks, embedding=embedder)
    state["vectordb"] = vectordb
    return state


def retrieve(state: ChatState) -> ChatState:
    vectordb: FAISS = state["vectordb"]
    docs = vectordb.similarity_search(state["question"], k=4)
    state["context"] = "\n".join(d.page_content for d in docs)
    return state


def generate(state: ChatState) -> ChatState:
    llm = BedrockChat(
        model_id="anthropic.claude-3-sonnet-v1",  # swap for your Bedrock model
        streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()],
    )
    prompt = f"""You are a helpful assistant.
    Use ONLY the context to answer.
    Context:
    {state['context']}
    Question: {state['question']}
    """
    answer = llm.invoke(prompt)
    state["answer"] = answer
    return state


# ---------- 3. Build graph ----------
def build_graph() -> StateGraph:
    g = StateGraph(ChatState)
    g.add_node("index", split_and_embed)
    g.add_node("retrieve", retrieve)
    g.add_node("generate", generate)

    # simple linear flow
    g.set_entry_point("index")
    g.add_edge("index", "retrieve")
    g.add_edge("retrieve", "generate")
    g.add_edge("generate", END)

    return g.compile()
