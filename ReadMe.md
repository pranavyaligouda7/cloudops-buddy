```markdown
# 🚀 CloudOps Buddy – Your DevOps AI Assistant

**CloudOps Buddy** is an intelligent CLI and API tool that helps DevOps engineers generate cloud CLI commands, diagnose errors, and explain infrastructure concepts using large language models (LLMs). It supports multiple LLM providers: **Gemini**, **Groq**, **OpenAI**, and **local Ollama** models.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Multi‑Provider Support** | Switch between Gemini, Groq, OpenAI, or local Ollama models. |
| **Command Generation** | Convert natural language requests into precise CLI commands (AWS, kubectl, Terraform, Docker, etc.). |
| **Error Diagnosis** | Paste cloud error logs and receive root cause analysis + fix suggestions. |
| **Step‑by‑Step Procedures** | Get sequential installation/setup steps with descriptions. |
| **Concept Explanations** | Ask "explain kubernetes" and get structured answers with key features and components. |
| **Safe Execution** | Dry‑run by default; execute with confirmation; command whitelist and dangerous pattern blocking. |
| **CLI & REST API** | Use interactively via CLI or integrate programmatically via FastAPI. |
| **Offline Support** | Run with local Ollama models (fully offline). |
| **Containerized** | Ready to deploy with Docker and Docker Compose. |

---

## 📦 Quick Start (Local)

### 1. Prerequisites
- Python 3.12+
- pip
- (Optional) Docker Desktop

### 2. Install from Source

```bash
git clone https://github.com/yourusername/cloudops-buddy.git
cd cloudops-buddy
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -e .
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Gemini (optional)
gemini_api_key=your_gemini_key
gemini_model=gemini-2.5-flash

# Groq (optional)
groq_api_key=your_groq_key
groq_model=llama-3.3-70b-versatile

# OpenAI / Ollama (local)
openai_api_key=dummy
openai_base_url=http://localhost:11434/v1   # For Ollama
openai_model=qwen3:0.6b

# Security
CLOUDOPS_BUDDY_DRY_RUN=true
CLOUDOPS_BUDDY_ALLOWED_COMMANDS=aws,az,kubectl,terraform,docker,ping,curl
```

### 4. Run Locally (CLI)

```bash
# Interactive mode
cloudops-buddy

# Single query with Groq
cloudops-buddy --provider groq "list all S3 buckets"

# Execute the generated command (with confirmation)
cloudops-buddy --execute "install Jenkins on Ubuntu"
```

---

## 🐳 Run with Docker

### Option A – Agent Only (using host Ollama)

```bash
docker run -d -p 8000:8000 \
  -e gemini_api_key=dummy \
  -e groq_api_key=dummy \
  -e openai_api_key=dummy \
  -e openai_base_url=http://host.docker.internal:11434/v1 \
  -e openai_model=qwen3:0.6b \
  --name cloudops-buddy \
  cloudops-buddy
```

### Option B – Full Stack (Agent + Ollama) using Docker Compose

```bash
docker compose up -d
```

This starts:
- **Ollama** on `http://localhost:11434`
- **CloudOps Buddy API** on `http://localhost:8000`

---

## 📡 REST API Usage

### Health Check
```bash
curl http://localhost:8000/health
```
```json
{"status":"ok"}
```

### Chat Endpoint
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"list all S3 buckets"}'
```
```json
{
  "response": "💡 Lists all S3 buckets...\n\n```bash\naws s3 ls\n```"
}
```

### Request Body Schema
```json
{
  "query": "your question here",
  "provider": "openai",   // optional, default: openai
  "execute": false        // optional, default: false
}
```

---

## 🧠 Supported LLM Providers

| Provider | Environment Variable | Notes |
|----------|----------------------|-------|
| **Gemini** | `gemini_api_key` | Google Gemini API (requires key) |
| **Groq** | `groq_api_key` | Fast, free tier available |
| **OpenAI** | `openai_api_key`, `openai_base_url` | Works with OpenAI, Azure, and Ollama |
| **Ollama (local)** | `openai_base_url=http://localhost:11434/v1` | Offline, self‑hosted |

---

## 🔧 Configuration Reference

| Environment Variable | Description | Default |
|----------------------|-------------|---------|
| `gemini_api_key` | Google Gemini API key | (required if using Gemini) |
| `groq_api_key` | Groq API key | (required if using Groq) |
| `openai_api_key` | OpenAI API key (or dummy for Ollama) | `dummy` |
| `openai_base_url` | OpenAI‑compatible endpoint | `https://api.openai.com/v1` |
| `openai_model` | Model name | `gpt-4o-mini` |
| `CLOUDOPS_BUDDY_DRY_RUN` | Dry‑run mode (`true`/`false`) | `true` |
| `CLOUDOPS_BUDDY_ALLOWED_COMMANDS` | Comma‑separated allowed commands | `aws,az,kubectl,terraform,docker,ping,curl` |
| `CLOUDOPS_BUDDY_COMMAND_TIMEOUT` | Command execution timeout (seconds) | `30` |

---

## 🛡️ Security & Safety

- **Command Whitelist** – Only allowed commands can be executed.
- **Dangerous Pattern Blocking** – Prevents `rm -rf`, `delete`, `terminate`, etc.
- **Dry‑Run by Default** – Commands are not executed unless `--execute` is used.
- **User Confirmation** – Every execution prompts for confirmation.
- **Environment Variables** – Sensitive data stored in `.env`, never hardcoded.

---

## 🏗️ Project Structure

```
cloud-buddy/
├── src/
│   ├── agent/
│   │   ├── core.py              # Agent logic
│   │   ├── llm_client.py        # Gemini client
│   │   ├── llm_client_groq.py   # Groq client
│   │   └── llm_client_openai.py # OpenAI/Ollama client
│   ├── cli/
│   │   └── main.py              # CLI entry point
│   ├── config/
│   │   └── settings.py          # Pydantic settings
│   ├── tools/
│   │   └── executor.py          # Secure command execution
│   └── api.py                   # FastAPI wrapper
├── tests/
│   └── test_executor.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Deployment on AWS Free Tier

1. Launch an **EC2 t4g.small** instance (Ubuntu 24.04).
2. Install Docker and Docker Compose.
3. Clone the repository.
4. Run `docker compose up -d`.
5. Configure Security Group to allow inbound on port 8000 (and 11434 if needed).
6. (Optional) Set up auto‑stop to save costs.

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run a specific test
pytest tests/test_executor.py -v
```

---

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/amazing-feature`.
3. Commit your changes: `git commit -m 'Add amazing feature'`.
4. Push to the branch: `git push origin feature/amazing-feature`.
5. Open a Pull Request.

---

## 📄 License

MIT License – see the [LICENSE](LICENSE) file for details.

---

## 🙋 Support

- **Issues**: [GitHub Issues](https://github.com/pranavyaligouda7/cloudops-buddy/issues)
- **Discussions**: [GitHub Discussions](https://github.com/pranavyaligouda7/cloudops-buddy/discussions)

---

## ✍️ Authors

- Pranav Yaligouda – [@pranavyaligouda7](https://github.com/pranavyaligouda7)

---

## ⭐ Acknowledgments

- [Ollama](https://ollama.com) – Local LLM runtime.
- [Groq](https://groq.com) – Fast inference API.
- [FastAPI](https://fastapi.tiangolo.com) – Web framework.
- [Click](https://click.palletsprojects.com) – CLI framework.
```