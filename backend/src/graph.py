from __future__ import annotations
from typing import Dict
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from langchain_aws import ChatBedrock, BedrockEmbeddings          # AWS Bedrock
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from typing import Optional
 
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env", override=True) 

def split_and_embed(state: dict) -> dict:
    # 1. Split the text into overlapping chunks
    text = state["document_text"]
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=80)
    chunks = splitter.split_text(text)
    # 2. Create embeddings via AWS Bedrock
    embedder = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0")

    vectordb = FAISS.from_texts(texts=chunks, embedding=embedder)
    state["vectordb"] = vectordb
    return state

def retrieve(state: dict) -> dict:
    # 3. Fetch the top-k nearest chunks for the question
    vectordb: FAISS = state["vectordb"]
    docs = vectordb.similarity_search(state["question"], k=4)
    state["context"] = "\n\n".join(d.page_content for d in docs)
    return state

def generate(state: dict) -> dict:
    # 4. Call the LLM with context + question
    llm = ChatBedrock(
        model="anthropic.claude-3-sonnet-v1",
        streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()],
    )
    prompt = f"""You are a helpful assistant.
    Use ONLY the context to answer.
    Context:
    {state['context']}

    Question: {state['question']}
    """
    state["answer"] = llm.invoke(prompt)
    return state


# ---------- 3. Build graph ----------
def build_graph(entry_point: str) -> CompiledStateGraph:
    g = StateGraph(dict)
    g.add_node("index", split_and_embed)
    g.add_node("retrieve", retrieve)
    g.add_node("generate", generate)
    g.set_entry_point(entry_point)
    if entry_point == "index":
        g.add_edge("index", END)
    else:
        # we assume vectordb is already in state
        g.add_edge("retrieve", "generate")
        g.add_edge("generate", END)
    return g.compile()
