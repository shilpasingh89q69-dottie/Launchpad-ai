"""
ai_engine.py
------------
Orchestration layer for all interactions with the Google Gemini API.

Responsible for:
  - Configuring the Gemini client
  - Building a strict, structured system prompt
  - Forcing JSON-only responses
  - Parsing / validating the model's output
  - Raising clean, catchable exceptions for app.py to handle
"""

import os
import json
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-3.5-flash"

# Keys that MUST be present in a valid AI response
REQUIRED_KEYS = [
    "viability_score",
    "innovation_score",
    "swot",
    "market_insights",
    "growth_strategy",
]

REQUIRED_SWOT_KEYS = ["strengths", "weaknesses", "opportunities", "threats"]


class AIEngineError(Exception):
    """Raised whenever the AI engine cannot produce a usable analysis."""
    pass


def _configure_client():
    """Configures the genai client using the API key from environment vars."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise AIEngineError(
            "GEMINI_API_KEY is missing or not set. Please add a valid key to your .env file."
        )
    genai.configure(api_key=api_key)


def _build_prompt(name: str, description: str, audience: str, business_model: str) -> str:
    """Builds the structured system + user prompt that forces strict JSON output."""
    return f"""
You are a senior startup analyst and venture capital advisor AI embedded inside a
product called "LaunchPad AI". Analyze the startup idea below and return your
analysis as STRICT JSON ONLY.

RULES (follow exactly):
1. Respond with ONLY a single valid JSON object. No markdown, no code fences, no
   commentary, no preamble, no trailing text of any kind.
2. The JSON object MUST contain exactly these top-level keys:
   - "viability_score": integer from 0 to 100 (overall business viability)
   - "innovation_score": integer from 0 to 100 (novelty / differentiation)
   - "swot": an object with exactly four keys, each an array of 3-5 short strings:
        "strengths", "weaknesses", "opportunities", "threats"
   - "market_insights": a string (3-5 sentences) analyzing the target market
   - "growth_strategy": a string (3-5 sentences) with concrete, actionable growth
     recommendations
3. Do not wrap the JSON in ```json or any other formatting.
4. Be honest and critical, not overly optimistic. Base scores on real business
   reasoning.

STARTUP DETAILS:
- Name: {name}
- Description: {description}
- Target Audience: {audience}
- Business Model: {business_model}

Return the JSON object now.
"""


def _extract_json(raw_text: str) -> dict:
    """Attempts to safely parse JSON out of the model's raw text response."""
    cleaned = raw_text.strip()

    # Strip markdown code fences if the model added them despite instructions
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    # Fallback: extract the substring between the first "{" and the last "}"
    if not cleaned.startswith("{"):
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            cleaned = cleaned[start:end + 1]

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse AI response as JSON: %s\nRaw: %s", e, raw_text)
        raise AIEngineError("The AI response could not be parsed as valid JSON.")


def _validate_payload(data: dict) -> dict:
    """Ensures the parsed JSON has the required shape before returning it."""
    missing = [k for k in REQUIRED_KEYS if k not in data]
    if missing:
        raise AIEngineError(f"AI response is missing required keys: {missing}")

    swot = data.get("swot")
    if not isinstance(swot, dict):
        raise AIEngineError("AI response 'swot' field must be an object.")

    missing_swot = [k for k in REQUIRED_SWOT_KEYS if k not in swot]
    if missing_swot:
        raise AIEngineError(f"AI response 'swot' object is missing keys: {missing_swot}")

    # Clamp scores defensively in case the model returns out-of-range values
    for score_key in ("viability_score", "innovation_score"):
        try:
            data[score_key] = max(0, min(100, int(data[score_key])))
        except (ValueError, TypeError):
            raise AIEngineError(f"AI response field '{score_key}' must be numeric.")

    return data


def generate_startup_analysis(name: str, description: str, audience: str, business_model: str) -> dict:
    """
    Main entry point used by app.py.

    Returns a validated dict matching the required schema, or raises
    AIEngineError with a human-readable message on any failure.
    """
    _configure_client()

    prompt = _build_prompt(name, description, audience, business_model)

    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config={
                "temperature": 0.7,
                "response_mime_type": "application/json",
            },
        )
        response = model.generate_content(prompt)
    except Exception as e:
        logger.exception("Gemini API call failed")
        raise AIEngineError(f"Gemini API request failed: {e}")

    if not response or not getattr(response, "text", None):
        raise AIEngineError("Gemini returned an empty response.")

    parsed = _extract_json(response.text)
    validated = _validate_payload(parsed)
    return validated
