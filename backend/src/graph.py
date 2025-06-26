from __future__ import annotations
from typing import Dict
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from typing import Optional
from langchain_aws import ChatBedrock, BedrockEmbeddings          # AWS Bedrock
from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchResults   # Web search
import re

from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env.local", override=True) 
 
# ---------- Indexing for Document RAG (called only at upload) ----------
def index_document(text: str) -> FAISS:
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=80)
    chunks = splitter.split_text(text)
    embedder = BedrockEmbeddings(
        model_id="amazon.titan-embed-text-v1"
    )
    return FAISS.from_texts(texts=chunks, embedding=embedder)

# ---------- Document RAG nodes (for chat) ----------
def retrieve_doc(state: dict) -> dict:
    vectordb: FAISS = state["vectordb"]
    if vectordb is None:
        raise ValueError("No document indexed. Call /upload first.")
    docs = vectordb.similarity_search(state["question"], k=4)
    state["context"] = "\n".join(d.page_content for d in docs)
    return state

def generate_doc(state: dict) -> dict:
    llm = ChatBedrock(
        model="amazon.titan-text-lite-v1",
        streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()],
    )
    prompt = f"""You are a helpful assistant.
    Use ONLY the context to answer.
    Context:
    {state['context']}

    Question: {state['question']}
    """
    state["answer"] = llm.invoke(prompt).content
    return state

# ---------- Web Search + Chat nodes ----------
def parse_duckduckgo(raw: str):
    pattern = re.compile(
        r"""snippet:\s*(?P<snippet>.*?)(?=,\s*title:)   # grab everything up to the next ", title:"
         ,\s*title:\s*(?P<title>.*?)(?=,\s*link:)       # then grab title up to ", link:"
         ,\s*link:\s*(?P<link>\S+)(?=(?:,\s*snippet:|$)) # grab link up to next ", snippet:" or end
        """,
        re.IGNORECASE | re.DOTALL | re.VERBOSE,
    )
    return [
        {"snippet": m.group("snippet").strip(),
         "title":   m.group("title").strip(),
         "link":    m.group("link").strip()}
        for m in pattern.finditer(raw)
    ]
    
def web_search(state: dict) -> dict:
    search = DuckDuckGoSearchResults()
    result = search.run(state["question"])
    prased_results = parse_duckduckgo(result)
    state["web_results"] = prased_results
    return state


def generate_web(state: dict) -> dict:
    llm = ChatBedrock(
        model="amazon.titan-text-lite-v1",
        streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()],
    )  
    citations_block = "\n".join(
        f"[{i+1}] {res['title']} - {res['link']}" for i, res in enumerate(state.get("web_results", []))
    )    

    prompt = f"""
    You are an expert assistant with access to web search results.  

    Use the following search results for context:
    {citations_block}

    Question: {state['question']}
 
    """
    answer_body = llm.invoke(prompt).content  
    markdown_output = f"""{answer_body} \n Sources:\n
    {citations_block}
    """
    state["answer"] = markdown_output
    return state


# ---------- General Chat node ----------
def generate_general(state: dict) -> dict:
    llm = ChatBedrock(
        model="amazon.titan-text-lite-v1",
        streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()],
    ) 
    state["answer"] = llm.invoke(state["question"]).content
    return state

# ---------- Graph builders ----------
def build_doc_graph() -> CompiledStateGraph:
    g = StateGraph(dict)
    g.add_node("retrieve_doc", retrieve_doc)
    g.add_node("generate_doc", generate_doc)
    g.set_entry_point("retrieve_doc")
    g.add_edge("retrieve_doc", "generate_doc")
    g.add_edge("generate_doc", END)
    return g.compile()

def build_web_graph() -> CompiledStateGraph:
    g = StateGraph(dict)
    g.add_node("web_search", web_search)
    g.add_node("generate_web", generate_web)
    g.set_entry_point("web_search")
    g.add_edge("web_search", "generate_web")
    g.add_edge("generate_web", END)
    return g.compile()


def build_general_graph() -> CompiledStateGraph:
    g = StateGraph(dict)
    g.add_node("generate_general", generate_general)
    g.set_entry_point("generate_general")
    g.add_edge("generate_general", END)
    return g.compile()