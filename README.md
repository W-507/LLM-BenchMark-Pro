# LLM-BenchMark-Pro

Advanced Multi-Model Evaluation & Cost Optimization Framework.

## 📌 Project Overview
In the rapidly evolving landscape of GenAI, choosing the right model is no longer about finding "the best" model, but the "most optimal" for a specific use case. **LLM-BenchMark-Pro** is a comprehensive, data-driven evaluation framework designed to benchmark Large Language Models (LLMs) across performance, cost, and accuracy dimensions. This project empowers developers and enterprises to move beyond "vibe-based" testing to a rigorous, metrics-driven selection process.

## 🚀 Why Use This Tool? (The Value Proposition)
Deciding between models like GPT-4o, Claude 3.5 Sonnet, and Llama 3.1 involves complex trade-offs. This tool solves the following problems:
*   **Cost vs. Performance Dilemma**: Is the extra cost of GPT-4o worth it for your specific prompt? Our **Efficiency Frontier** chart tells you instantly.
*   **Latency Sensitivity**: For real-time apps, milliseconds matter. We measure **Time-to-First-Token (TTFT)** and **Tokens Per Second (TPS)** with precision.
*   **Safety & Reliability**: How does the model handle malicious inputs? Our **Robustness Tests** (Prompt Injection, Context Stress) verify security.
*   **Subjective Quality**: "Better" is subjective. Our **Human-in-the-loop** system allows you to build a ground-truth dataset based on your team's specific criteria.

## 🛠 Features
* **Multi-Provider Integration**: OpenAI, Anthropic, Gemini support via LiteLLM.
* **Performance Metrics**: TTFT, Latency, TPS.
* **Economic Analysis**: Cost calculation.
* **Advanced Evaluation**:
    * **Efficiency Frontier**: Visual Cost vs. Quality tradeoffs.
    * **Robustness Testing**: Prompt injection and stress testing.
    * **Human-in-the-loop**: Integrated feedback system.
* **Reporting**: Auto-generated Excel and PDF reports.
* **Visualization**: Interactive Streamlit dashboard.
* **Production Ready**: Optimized multi-stage Docker build.

## Setup

1. **Clone the repository** (if not already done).
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up API Keys**:
   Copy `.env.example` to `.env` and add your keys:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.

## Usage

### Run Benchmark
#### Option 1: Real Benchmarking (Requires API Keys)
To run the standard benchmark using models like GPT-4o and Claude 3.5:
```bash
python main.py --config config/standard_test.yaml
```

#### Option 2: Demo Mode (No Keys Required)
To try the pipeline with simulated mock models (great for testing the UI):
```bash
python main.py --config config/demo_test.yaml
```

### Run Dashboard
To visualize the results and access reports:
```bash
streamlit run ui/app.py
```

## ❓ Troubleshooting
*   **RuntimeError: Event loop is closed**: This is a known issue on Windows with `asyncio`. It has been handled in `main.py`, but ensure you are running Python 3.10+.
*   **RAGAS Evaluation Failed**: If you see this, check your `.env` file. RAGAS requires OpenAI keys to function as a "Judge". In Demo Mode, this is skipped automatically.
*   **Import Errors**: Ensure you installed requirements: `pip install -r requirements.txt`.

## Configuration
Edit `config/standard_test.yaml` to change models, prompts, or parameters.

## Docker
Build and run with Docker:
```bash
docker build -t llm-benchmark-pro .
docker run --env-file .env llm-benchmark-pro
```
