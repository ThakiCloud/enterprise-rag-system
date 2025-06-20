# Enterprise RAG System

A comprehensive Retrieval-Augmented Generation (RAG) system designed for enterprise environments, supporting multiple LLM providers and advanced document processing capabilities.

## 🚀 Features

- **Multi-LLM Support**: OpenAI, Anthropic (Claude), Google (Gemini), Ollama, vLLM, LM Studio
- **Advanced Document Processing**: PDF, DOCX, TXT, and URL content ingestion
- **Hybrid Search**: Combines vector similarity and BM25 for optimal retrieval
- **Reasoning Capabilities**: Chain-of-thought reasoning for complex queries
- **Session Management**: Persistent conversation history
- **🧠 Intelligent Memory System**: Agno-powered user memory for personalized conversations
- **Context-Aware Responses**: Remember user preferences and conversation history
- **Enterprise Ready**: Docker, Kubernetes, and Terraform support
- **Modern UI**: AGUIApp-based interface with real-time streaming

## 📋 Prerequisites

- Python 3.11+
- Docker and Docker Compose (for containerized deployment)
- OpenAI API key (or other LLM provider keys)

## 🛠️ Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd enterprise-rag-system
```

### 2. Configure Environment

```bash
cp config.env.example config.env
# Edit config.env with your API keys and preferences
```

### 3. Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# UI
cd ../ui
pip install -r requirements.txt
```

### 4. Run the System

#### Option A: Using Python Scripts
```bash
# Terminal 1: Start Backend
python run_backend.py

# Terminal 2: Start UI (AGUIApp)
python run_ui.py
```

#### Option B: Using Docker Compose
```bash
docker-compose -f infrastructure/docker-compose.yml up --build
```

#### Option C: Direct AGUIApp Execution
```bash
cd ui
python main.py
```

### 5. Access the Application

- **UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## ⚙️ Configuration

### Model Providers

Set `MODEL_PROVIDER` in your environment:

```bash
# OpenAI (default)
MODEL_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# Anthropic Claude
MODEL_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Google Gemini
MODEL_PROVIDER=google
GOOGLE_API_KEY=your-google-key-here

# Ollama (local)
MODEL_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434

# LM Studio (local)
MODEL_PROVIDER=lm-studio
LM_STUDIO_BASE_URL=http://localhost:1234/v1

# vLLM or custom OpenAI-compatible
MODEL_PROVIDER=vllm
CUSTOM_API_BASE_URL=http://localhost:8000/v1
CUSTOM_MODEL_NAME=your-model-name
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │   Backend API   │
│   (AGUIApp)     │◄──►│   (FastAPI)     │
└─────────────────┘    └─────────────────┘
                                │
                       ┌────────┴────────┐
                       │                 │
                ┌──────▼──────┐   ┌─────▼─────┐
                │   Agents    │   │ Knowledge │
                │   System    │   │   Base    │
                └─────────────┘   └───────────┘
                       │                 │
                ┌──────▼──────┐   ┌─────▼─────┐
                │    LLM      │   │ Vector DB │
                │ Providers   │   │(LanceDB)  │
                └─────────────┘   └───────────┘
```

## 📁 Project Structure

```
enterprise-rag-system/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── agents/         # AI agents and factories
│   │   ├── api/           # API routes
│   │   ├── core/          # Configuration and dependencies
│   │   ├── knowledge/     # Document processing
│   │   └── schemas/       # Pydantic models
│   ├── requirements.txt
│   └── Dockerfile
├── ui/                     # AGUIApp frontend
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   └── Dockerfile
├── infrastructure/         # Simple deployment
│   └── docker-compose.yml
├── tests/                 # Test suites
└── docs/                  # Documentation
```

## 🧪 Testing & Code Quality

### 로컬 테스트
```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Run tests
pytest tests/

# Basic syntax check
pip install flake8
flake8 backend/app --select=E9,F63,F7,F82
```

### CI/CD 프로세스
- **자동 실행**: 모든 커밋/PR에서 기본 문법 검사 & 테스트 자동 실행
- **수동 배포**: GitHub Actions에서 명시적으로 빌드/배포 요청
- **상세 가이드**: [CI/CD 가이드](docs/cicd-guide.md) 참고

## 🚢 Deployment

### Quick Start

```bash
# Set required environment variable
export OPENAI_API_KEY="your-api-key-here"

# One-command deployment
./deploy.sh
```

### Manual Docker Compose

```bash
# Set environment variable
export OPENAI_API_KEY="your-api-key-here"

# Build and run
cd infrastructure
docker-compose up -d
```

## 📊 Monitoring

- **Health Check**: `/health/` endpoint
- **Metrics**: Prometheus-compatible metrics (planned)
- **Logs**: Structured logging with correlation IDs

## 🧠 Memory System

This RAG system features an intelligent memory system powered by Agno that enables personalized, context-aware conversations.

### Key Features

- **User-Specific Memory**: Each user/session maintains separate memory storage
- **Automatic Memory Creation**: Conversations are automatically processed to extract relevant memories
- **Semantic Memory Search**: Find relevant memories based on query context
- **Memory Management**: Add, update, delete, and search memories via API
- **Cross-Session Persistence**: Memories persist across multiple conversation sessions

### API Endpoints

#### Query with Memory
```bash
POST /api/query/stream/
{
  "question": "안녕하세요, 저는 개발자입니다",
  "session_id": "user123",
  "user_id": "user123",
  "use_memory": true
}
```

#### Memory Management
```bash
# Get memories for a session
GET /api/sessions/{session_id}/memories?limit=10

# Search memories
POST /api/sessions/{session_id}/search-memories
{
  "query": "개발자",
  "limit": 5
}

# Add memory manually
POST /api/sessions/{session_id}/memories
{
  "action": "add",
  "memory_content": "사용자는 Python 개발자입니다",
  "topics": ["개발", "Python"]
}

# Clear all memories
POST /api/sessions/{session_id}/memories
{
  "action": "clear"
}
```

### Memory Configuration

The memory system uses SQLite by default for storage:

```bash
# Memory database location
MEMORY_DB_PATH=tmp/session_memories.db

# Enable/disable memory for queries
USE_MEMORY_DEFAULT=true
```

### How It Works

1. **Automatic Memory Creation**: When users interact with the system, conversations are analyzed and key information is extracted as memories
2. **Context Injection**: Relevant memories are automatically retrieved and injected into the conversation context
3. **Semantic Search**: The system uses AI models to find the most relevant memories for each query
4. **Personalized Responses**: Agents use memory context to provide more personalized and contextually appropriate responses

## 🔧 Development

### Adding New LLM Providers

1. Update `backend/app/core/config.py` with new provider settings
2. Modify `backend/app/agents/factory.py` to handle the new provider
3. Add corresponding model class imports

### Extending Document Types

1. Add new knowledge class in `backend/app/knowledge/manager.py`
2. Update file type detection logic
3. Test with sample documents

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: GitHub Issues
- **Documentation**: `/docs` directory
- **API Reference**: http://localhost:8000/docs (when running)

## 🗺️ Roadmap

- [ ] Streaming responses
- [ ] Multi-modal document support (images, audio)
- [ ] Advanced analytics dashboard
- [ ] Plugin system for custom tools
- [ ] Multi-tenant support
- [ ] Enhanced security features