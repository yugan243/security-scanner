<p align="center">
  <h1 align="center">🛡️ Vigil</h1>
  <p align="center">
    <strong>AI-Powered Security Scanner for Codebases</strong>
  </p>
  <p align="center">
    <a href="https://pypi.org/project/vigil-scanner/"><img src="https://img.shields.io/pypi/v/vigil-scanner?style=flat-square&color=blue" alt="PyPI"></a>
    <a href="https://pypi.org/project/vigil-scanner/"><img src="https://img.shields.io/pypi/pyversions/vigil-scanner?style=flat-square" alt="Python"></a>
    <a href="https://github.com/yugan243/security-scanner/blob/main/LICENSE"><img src="https://img.shields.io/github/license/yugan243/security-scanner?style=flat-square" alt="License"></a>
  </p>
</p>

---

Vigil is a multi-agent AI security scanner that combines **static analysis** (Semgrep) with **LLM verification** to find real vulnerabilities in your code — and filter out the noise.

> **The Problem:** Traditional static analysis tools generate hundreds of warnings. 80% are false positives. Developers stop reading them.
>
> **The Solution:** Vigil uses an AI verifier agent to analyze each finding with Chain-of-Thought reasoning, filtering out false alarms and keeping only real threats.

## ✨ Key Features

- **AI-Verified Findings** — LLM analyzes each vulnerability with a 4-step security framework
- **86% Accuracy** — Benchmarked on 100 real-world code samples with near-zero missed threats
- **Multi-Provider LLM Support** — Groq (free), Google Gemini, OpenAI, or local Ollama
- **GitHub URL Scanning** — Point it at any public repo and scan instantly
- **CISO Executive Summary** — AI-generated security report for stakeholders
- **Interactive Setup** — First-run wizard configures everything for you
- **Docker Ready** — Run anywhere with a single container

## 🚀 Quick Start

### Install

```bash
pip install vigil-scanner
```

### Scan a Repository

```bash
# Scan a remote GitHub repo
vigil scan https://github.com/username/repo

# Scan a local project
vigil scan ./my-project
```

On first run, Vigil will ask you to choose an LLM provider:

```
🛡️ Welcome to Vigil!

Available LLM Providers:

  1. Groq  —  Free cloud API (recommended)
  2. Google Gemini  —  Free tier available
  3. Ollama / LMStudio  —  Local & free
  4. OpenAI  —  Paid (GPT-4o)

Select provider (number): 1
Enter your Groq API key: gsk_xxxxx
 Configuration saved!
```

### Reconfigure Anytime

```bash
vigil init
```

## 🐳 Docker

```bash
# Build
docker build -t vigil .

# Scan with cloud LLM
docker run -e LLM_PROVIDER=groq -e GROQ_API_KEY=your_key \
  vigil scan https://github.com/username/repo

# Scan with local Ollama (using docker compose)
docker compose up -d
docker compose exec ollama ollama pull llama3
docker compose run vigil scan https://github.com/username/repo
```

## 🏗️ Architecture

Vigil uses a **LangGraph multi-agent pipeline** with three specialized nodes:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Scanner    │────►│   Verifier   │────►│   Reporter   │
│  (Semgrep)   │     │  (LLM + CoT) │     │  (LLM)       │
│              │     │              │     │              │
│ Static       │     │ AI verifies  │     │ Generates    │
│ analysis     │     │ each finding │     │ executive    │
│ rules        │     │ with Chain-  │     │ summary &    │
│              │     │ of-Thought   │     │ fix advice   │
└──────────────┘     └──────────────┘     └──────────────┘
     Finds              Filters              Reports
   candidates        false positives      to the team
```

### Verification Strategy

The Verifier agent uses:

- **Chain-of-Thought (CoT) reasoning** — 4-step analysis framework (data flow → defenses → CWE mapping → verdict)
- **Few-Shot examples** — Calibrated with real vulnerability patterns
- **Batch processing** — 10 findings per LLM call for token efficiency
- **Confidence thresholds** — Low-confidence dismissals are overridden (security-first)

## 📊 Benchmark Results

Tested on 100 real-world code samples from the [Code Vulnerability Labeled Dataset](https://huggingface.co/datasets/lemon42-ai/Code_Vulnerability_Labeled_Dataset):

| Metric | Score |
|---|---|
| **Accuracy** | 86% |
| **False Negative Rate** | 2% |
| **False Positive Rate** | ~14% |
| **Missed Threats** | 1 out of 100 |

## ⚙️ Configuration

Vigil supports configuration through environment variables or the `~/.vigil/.env` file:

| Variable | Description | Default |
|---|---|---|
| `LLM_PROVIDER` | `groq`, `google`, `openai`, `ollama` | `ollama` |
| `GROQ_API_KEY` | Groq API key | — |
| `GOOGLE_API_KEY` | Google Gemini API key | — |
| `OPENAI_API_KEY` | OpenAI API key | — |
| `OLLAMA_BASE_URL` | Ollama endpoint URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Model name for Ollama | `llama3` |

## 🛠️ Development

```bash
# Clone the repo
git clone https://github.com/yugan243/security-scanner.git
cd security-scanner

# Install dependencies
poetry install

# Run locally
poetry run vigil scan ./my-project

# Run benchmarks
poetry run python -m tests.benchmark
```

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  Built by Yugan Nimsara ❤️ with a little help of Antigravity using <a href="https://github.com/langchain-ai/langgraph">LangGraph</a> · <a href="https://semgrep.dev">Semgrep</a> · <a href="https://groq.com">Groq</a>
</p>
