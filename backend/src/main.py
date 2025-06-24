# backend/main.py
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from graph import build_graph 
import uvicorn

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # tighten in prod!
    allow_methods=["*"],
)

# build two separate flows
index_flow = build_graph(entry_point="index")
chat_flow  = build_graph(entry_point="retrieve")

@app.post("/upload")
async def upload(file: UploadFile):
    global _vectordb
    text = (await file.read()).decode()
    print(f"\n================\ntest: {text[:10]} \n================\n")  # Add this line
    state = {"document_text": text}
    index_flow.invoke(state)           # runs split_and_embed
    _vectordb = state["vectordb"]      # stash it
    return {"status": "indexed"}

@app.post("/chat")
async def chat(question: str = Form(...)):
    if _vectordb is None:
        raise HTTPException(400, detail="No document indexed yet.")
    state = {"question": question, "vectordb": _vectordb}
    chat_flow.invoke(state)            # runs retrieve → generate
    return {"answer": state["answer"]}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

