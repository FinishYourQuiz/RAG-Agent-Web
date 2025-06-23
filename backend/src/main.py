# backend/main.py
from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from backend.src.graph import build_graph, ChatState
import uvicorn

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

rag_flow = build_graph()

@app.post("/upload")
async def upload(file: UploadFile):
    text = (await file.read()).decode()
    state = ChatState(document_text=text)
    rag_flow.invoke(state)                # pre-index
    return {"msg": "Doc indexed"}

@app.post("/chat")
async def chat(question: str = Form(...)):
    state = ChatState(question=question)
    rag_flow.invoke(state)
    return {"answer": state["answer"]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
