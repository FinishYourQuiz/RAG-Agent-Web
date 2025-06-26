# backend/main.py
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from graph import (
    index_document,
    build_doc_graph,
    build_web_graph,
    build_general_graph,
) 
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # tighten in prod!
    allow_methods=["*"],
)

# build two separate flows
# Compile flows once
doc_flow = build_doc_graph()
web_flow = build_web_graph()
general_flow = build_general_graph()

vectordb_global = None

@app.post("/upload")
async def upload(file: UploadFile):
    global vectordb_global
    text = (await file.read()).decode()
    vectordb_global = index_document(text)
    return {"msg": "Document successfully indexed."}

@app.post("/chat")
async def chat(
    question: str = Form(...),
    mode: str = Form("doc")  # 'doc', 'web', or 'general'
):
    state = {}
    state["vectordb"] = None  # Reset vector DB for each chat
    state["web_context"] = None  # Reset web context for each chat  
    state["answer"] = {}
    state["question"] = question 
    
    if mode == "doc":
        if vectordb_global is None:
            raise HTTPException(status_code=400, detail="No document indexed. Upload first.")
        state["vectordb"] = vectordb_global
        doc_flow.invoke(state)

    elif mode == "web":
        web_flow.invoke(state)

    elif mode == "general":
        general_flow.invoke(state)

    else:
        raise HTTPException(status_code=400, detail="Invalid mode. Use 'doc', 'web', or 'general'.")
 
    return {"answer": state["answer"]}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

