# FastF1 Telemetry & AI Agentic Analytics for OpenWebUI

An edge-native Formula 1 telemetry and strategy analytics tool built for **OpenWebUI and Ollama**. It leverages the [FastF1](https://docs.fastf1.dev/) API to retrieve historical and session telemetry data, enabling interactive analysis through natural-language queries.

The tool combines **Python, Pandas, and locally hosted LLMs** to support telemetry processing, lap-time analysis, race strategy evaluation, anomaly detection, and interactive visualizations.

### Key Features

- **Telemetry ingestion:** Access Formula 1 session data through the FastF1 Python library.
- **Dynamic data analysis:** Use Python and Pandas to process telemetry and perform calculations.
- **AI-powered reasoning:** Use `qwen2.5-coder:3b` for code-oriented analysis and `deepseek-r1` for strategy reasoning, where supported by the tool implementation.
- **Natural-language interface:** Query telemetry and race strategy data directly through OpenWebUI.
- **Local inference:** Run supported models through Ollama without relying on hosted LLM APIs.
- **Interactive visualizations:** Render maps and other HTML-based outputs when supported by the tool and OpenWebUI configuration.

---

## Installation and Setup

### Prerequisites

Ensure you have the following installed and configured:

- Docker and a running OpenWebUI container
- Ollama with the required models available
- Python 3 and pip in the OpenWebUI container
- Network access to retrieve data from FastF1, when required

Pull the required models through Ollama if they are not already installed:

```bash
ollama pull qwen2.5-coder:3b
ollama pull deepseek-r1
```

> **Note:** The model names configured in your tool must match the models available in Ollama. Adjust the commands if your implementation uses different model tags.

### 1. Install Python Dependencies

Install the required packages inside the running OpenWebUI container to ensure they are available to the environment in which the tool executes.

First, identify your container name:

```bash
docker ps
```

Then install the dependencies, replacing `open-webui` if your container has a different name:

```bash
docker exec -u 0 -it open-webui \
  pip install --default-timeout=300 \
  fastf1 pandas pydantic requests \
  langchain-ollama chromadb
```

**Important:** Installing packages as root may be necessary for a quick setup, but it is not always the best long-term solution. For a persistent deployment, consider adding the dependencies to a custom OpenWebUI image so they survive container recreation.

The packages listed above assume they are required by the supplied tool. Remove any dependencies that the implementation does not actually use.

### 2. Import the Tool into OpenWebUI

1. Open the OpenWebUI interface.
2. Navigate to **Workspace → Tools**.
3. Select **+ Create Tool**.
4. Open `tools/fast_f1_rag.py` in your project.
5. Copy its complete contents into the tool editor.
6. Save the tool and resolve any reported syntax or dependency errors.


### 3. Configure Interactive HTML Rendering

If the tool generates HTML visualizations, maps, or other interactive artifacts:

1. Open **Settings → Interface**.
2. Locate the artifact or HTML-rendering options available in your OpenWebUI version.
3. Enable HTML/artifact rendering if the relevant options are available.
4. Enable iframe sandbox options only if the generated content requires them and you understand the associated security implications.

**Security note:** Allowing an iframe to use `allow-same-origin` can weaken sandbox isolation in certain configurations. Enable it only when necessary, and avoid rendering untrusted HTML or JavaScript.

OpenWebUI settings and labels may vary by version. Verify the available options in your installed release.

### 4. Enable Tools in Chat

1. Start a new chat in OpenWebUI.
2. Select a model that supports tool calling in your configuration.
3. Open the tools menu (typically represented by a wrench or tools icon).
4. Enable the FastF1 telemetry tool.
5. Submit a natural-language query to test the integration.

Example queries:

- "Compare the fastest laps of two drivers in a selected session."
- "Analyze the lap-time consistency of the top five drivers."
- "Identify unusual speed or braking patterns in a lap."
- "Compare tyre strategies and estimate their impact on race pace."

The actual queries supported depend on the functions implemented in the Python tool.

---

## Troubleshooting

| Problem | Suggested fix |
|---|---|
| `ModuleNotFoundError` | Install the missing package in the Python environment used by OpenWebUI. |
| Ollama model not found | Pull the model and verify that the configured model tag matches the installed tag. |
| FastF1 data retrieval fails | Check network connectivity, session identifiers, and FastF1 cache permissions. |
| Tool fails to save | Check Python syntax, imports, and the tool schema expected by your OpenWebUI version. |
| HTML visualization does not render | Check artifact support, browser restrictions, iframe settings, and the generated HTML. |
| Changes disappear after a restart | Add dependencies and configuration to a persistent image or deployment setup. |

## Notes and Limitations

- FastF1 data availability depends on the selected session and the data exposed by the library.
- Historical telemetry analysis and genuinely live telemetry are different capabilities. Do not assume live, real-time telemetry is available unless it is explicitly implemented and supported by the data source.
- AI-generated strategy assessments are estimates, not official team strategy outputs.
- Local inference reduces dependence on hosted LLM services, but FastF1 data retrieval may still require internet connectivity.
- Interactive map output requires the tool to generate compatible visualizations; enabling HTML rendering alone does not implement map functionality.

## Project Status

This README describes the intended architecture and setup. Verify each feature against the actual Python implementation before claiming that it is fully functional.

