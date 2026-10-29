# FastF1 Telemetry and AI Agentic Analytics Tool for OpenWebUI

An edge-native Formula 1 telemetry and strategy analytics tool designed for OpenWebUI and Ollama. It ingests live and historical session data via the fastf1 API, executes dynamic Python and Pandas logic on the fly using qwen2.5-coder:3b, performs strategy and anomaly reasoning with deepseek-r1, and routes natural language queries across local LLMs.

---

## Installation and Setup

### 1. Install Dependencies in OpenWebUI Container
To prevent missing module errors when creating or saving tools, execute pip install inside your running OpenWebUI container:

```bash
docker exec -u 0 -it open-webui pip install --default-timeout=300 fastf1 pandas pydantic requests langchain-ollama chromadb