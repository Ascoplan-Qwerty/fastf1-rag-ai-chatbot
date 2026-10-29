import os
import re
import datetime
import fastf1
import pandas as pd
import requests
from pydantic import BaseModel, Field


class Tools:
    def __init__(self):
        # Local Ollama endpoint accessible from inside Docker container
        self.ollama_url = "http://host.docker.internal:11434/api/generate"

        # Configure FastF1 caching inside the container persistent space
        self.cache_dir = "/app/backend/data/f1_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(self.cache_dir)

    def _call_ollama(self, model: str, prompt: str) -> str:
        """Utility method to trigger local Ollama model inferences."""
        try:
            payload = {"model": model, "prompt": prompt, "stream": False}
            res = requests.post(self.ollama_url, json=payload, timeout=90)
            if res.status_code == 200:
                return res.json().get("response", "")
            return f"Ollama API Error: Status {res.status_code}"
        except Exception as e:
            return f"Ollama Connection Error: {str(e)}"

    def query_fastf1_agent(
        self,
        query: str = Field(
            ...,
            description="The user's original F1 telemetry, lap time, strategy, or anomaly question.",
        ),
        year: int = Field(
            datetime.datetime.now().year,
            description="F1 Championship year (1950 to present season).",
        ),
        race: str = Field(
            ...,
            description="Grand Prix event name or location, e.g., 'Bahrain', 'Monza', 'Silverstone'.",
        ),
        session_type: str = Field(
            "R",
            description="Session identifier code: 'R' (Race), 'Q' (Qualifying), 'FP1', 'FP2', 'FP3', or 'SQ'.",
        ),
    ) -> str:
        """
        Universal Formula 1 Agentic Tool. Executes live FastF1 Pandas calculations,
        performs telemetry anomaly analysis, and returns verified statistics.
        """
        # --- 1. Guardrail & Bounds Validation ---
        current_year = datetime.datetime.now().year
        if not (1950 <= year <= current_year):
            return f"❌ Validation Error: Year {year} is out of bounds (1950-{current_year})."

        # --- 2. Step-by-Step Intent Classification (Router) ---
        router_prompt = f"""Classify this F1 query into exactly ONE category: [CALCULATION, ANOMALY, GENERAL].
Query: "{query}"
Rules:
- CALCULATION: Laps, fastest times, deltas, pit counts, or specific telemetry metrics.
- ANOMALY: Questions asking 'why' pace dropped, tire degradation anomalies, or strategic failures.
- GENERAL: Basic session facts or race summaries.
Output ONLY the single category word."""

        intent_res = self._call_ollama("llama3.2", router_prompt).strip().upper()

        # --- 3. Dynamic Execution Path A: CALCULATION via Qwen2.5-Coder ---
        if "CALCULATION" in intent_res or "GENERAL" in intent_res:
            try:
                session = fastf1.get_session(year, race, session_type)
                session.load(laps=True, telemetry=False, weather=False)
            except Exception as e:
                return f"❌ FastF1 Load Error: Could not fetch {year} {race} ({session_type}). Details: {str(e)}"

            coder_prompt = f"""You are an expert Python F1 data engineer. I have a FastF1 session loaded in a variable named `session`.
Write Python code to solve this query: "{query}"

Data Schema Available:
- `session.laps` Pandas DataFrame columns: ['Driver', 'LapNumber', 'LapTime', 'Stint', 'Compound', 'TyreLife', 'FreshTyre']

Rules:
- Parse target driver or metrics dynamically from the query.
- Calculate the result and store the string output in a variable called `FINAL_RESULT`.
- Example: `FINAL_RESULT = f"Driver {{driver}} fastest lap: {{fastest['LapTime']}} on Lap {{int(fastest['LapNumber'])}}"`
- Output ONLY executable Python code inside a ```python ``` block."""

            code_res = self._call_ollama("qwen2.5-coder:3b", coder_prompt)
            match = re.search(r"```python\n(.*?)\n```", code_res, re.DOTALL)

            if match:
                generated_code = match.group(1)
                exec_globals = {"session": session, "pd": pd, "FINAL_RESULT": ""}
                try:
                    exec(generated_code, exec_globals)
                    result = exec_globals.get(
                        "FINAL_RESULT",
                        "Code executed successfully but no FINAL_RESULT was stringified.",
                    )
                    return f"🏎️ **FastF1 Calculated Output**:\n{result}"
                except Exception as exec_err:
                    return f"❌ Sandbox Execution Error: {str(exec_err)}\n\nGenerated Code:\n```python\n{generated_code}\n```"
            else:
                return f"⚠️ Code generation parsing failed. Raw response:\n{code_res}"

        # --- 4. Dynamic Execution Path B: ANOMALY & REASONING via DeepSeek-R1 ---
        elif "ANOMALY" in intent_res:
            try:
                session = fastf1.get_session(year, race, session_type)
                session.load(laps=True, telemetry=False, weather=True)
                laps_summary = (
                    session.laps[
                        ["Driver", "LapNumber", "LapTime", "Compound", "TyreLife"]
                    ]
                    .head(50)
                    .to_string()
                )
            except Exception as e:
                laps_summary = f"Session data could not be pre-loaded: {str(e)}"

            reasoner_prompt = f"""You are a senior F1 Race Strategist. Analyze this anomaly/strategy query using the loaded session context.

Query: {query}
Session Data Context:
{laps_summary}

Provide a deep, step-by-step reasoning breakdown explaining the telemetry/strategy dynamics."""

            reasoning_res = self._call_ollama("deepseek-r1", reasoner_prompt)
            return f"🧠 **DeepSeek-R1 Anomaly Analysis**:\n{reasoning_res}"

        return "Unable to determine dynamic route for the specified query."
