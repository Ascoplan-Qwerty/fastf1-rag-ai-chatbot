# FastF1 Telemetry and AI Agentic Analytics Tool for OpenWebUI

An edge-native Formula 1 telemetry and strategy analytics tool designed for OpenWebUI and Ollama. It ingests live and historical session data via the fastf1 API, executes dynamic Python and Pandas logic on the fly using qwen2.5-coder:3b, performs strategy and anomaly reasoning with deepseek-r1, and routes natural language queries across local LLMs.

---

## Installation and Setup

### 1. Install Dependencies in OpenWebUI Container
To prevent missing module errors when creating or saving tools, execute pip install inside your running OpenWebUI container:

```bash
docker exec -u 0 -it open-webui pip install --default-timeout=300 fastf1 pandas pydantic requests langchain-ollama chromadb

### 2. Import Tool into OpenWebUI

1. Open **OpenWebUI** → **Workspace** → **Tools** → **+ Create Tool**.

2. Copy and paste the contents of `tools/adsb_telemetry_tool.py`.

3. Click **Save**.



### 3. Enable Artifact Rendering (For Interactive Map Output)

1. Go to **Settings** → **Interface** → **Artifacts**.

2. Toggle **ON** `Artifacts / HTML Rendering`.

3. Toggle **ON** `iframe Sandbox Allow Same Origin`.



### 4. Enable Tools in Chat

Toggle **ON** the Wrench/Tools icon in the chat input controls before submitting spatial queries.

