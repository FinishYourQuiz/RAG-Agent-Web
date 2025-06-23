# RAG Agent with React, LangGraph & AWS

## Table of Contents

- [RAG Agent with React, LangGraph \& AWS](#rag-agent-with-react-langgraph--aws)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Architecture](#architecture)
  - [Tech Stack](#tech-stack)
  - [Prerequisites](#prerequisites)
  - [Getting Started](#getting-started)
    - [Clone Repository](#clone-repository)
    - [Backend Setup](#backend-setup)
    - [Frontend Setup](#frontend-setup)
  - [Configuration](#configuration)
  - [Running Locally](#running-locally)
  - [Deployment](#deployment)
  - [Environment Variables](#environment-variables)
  - [Next Steps](#next-steps)
  - [Contributing](#contributing)
  - [License](#license)

## Overview

This project demonstrates a simple Retrieval-Augmented Generation (RAG) agent with:

* **React** frontend for file upload and chat UI
* **LangGraph** backend flow: split → embed → retrieve → generate
* **AWS Bedrock** for LLM and embedding services
* **FAISS** for vector indexing
* **FastAPI** to expose HTTP endpoints
* **Infrastructure** deployable to AWS ECS, Lambda, or Amplify

## Architecture

```
[User Browser] <--HTTP--> [React Frontend]
                            |
                            |-- POST /upload --> [FastAPI + LangGraph]
                            |                    |-- split & embed → FAISS
                            |                    |-- similarity_search
                            |                    |-- invoke AWS Bedrock LLM
                            |
                            |-- POST /chat ---> [FastAPI + LangGraph]

Infrastructure:
- Containerized backend on ECS Fargate or Lambda
- Static React site on S3 + CloudFront via Amplify
- (Optional) Aurora PostgreSQL + pgvector or OpenSearch Serverless for vector store
```

## Tech Stack

* **Frontend:** React (Vite, TypeScript)
* **Backend:** Python, FastAPI, LangGraph, LangChain
* **Vector Store:** FAISS
* **LLM & Embeddings:** AWS BedrockChat & BedrockEmbeddings
* **Deployment:** AWS ECS / Lambda / Amplify

## Prerequisites

* Node.js >= 16
* Python 3.8+
* AWS account with Bedrock access
* AWS CLI configured (`aws configure`)

## Getting Started

### Clone Repository

```bash
git clone https://github.com/your-username/rag-app.git
cd rag-app
```

### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

## Configuration

Rename `.env.example` to `.env` in both `frontend` and `backend` and fill in:

```ini
# backend/.env
AWS_REGION=us-east-1
AWS_PROFILE=default
BEDROCK_ASSUME_ROLE_ARN=arn:aws:iam::123456789012:role/YourBedrockRole

# frontend/.env
VITE_API=http://localhost:8000
```

## Running Locally

1. **Start Backend**

   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Frontend**

   ```bash
   cd frontend
   npm run dev
   ```

3. Visit [http://localhost:5173](http://localhost:5173) in your browser. Upload a text file, then ask questions.

## Deployment

1. **Containerize Backend**

   ```bash
   docker build -t rag-api:latest -f backend/Dockerfile .
   aws ecr create-repository --repository-name rag-api
   aws ecr get-login-password | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com
   docker tag rag-api:latest <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/rag-api:latest
   docker push <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/rag-api:latest
   ```
2. **Deploy to ECS Fargate** or **Lambda + API Gateway** (see AWS docs).
3. **Host Frontend** via Amplify:

   ```bash
   cd frontend
   amplify init
   amplify add hosting
   amplify publish
   ```

## Environment Variables

See [Configuration](#configuration) section for all required environment variables.

## Next Steps

* **Streaming**: Convert `/chat` to SSE for real-time tokens.
* **Multi-Doc RAG**: Add metadata and per-doc citations.
* **Auth**: Integrate Cognito for secure endpoints.
* **Vector Persistence**: Swap FAISS for Aurora PostgreSQL + pgvector.
* **Monitoring**: Ship logs & metrics to CloudWatch.

## Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/xyz`)
3. Commit your changes
4. Push to your branch
5. Open a Pull Request

## License

MIT © Your Name
