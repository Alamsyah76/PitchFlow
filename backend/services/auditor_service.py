"""
Auditor Service
Calls OpenAI (GPT-4o) to perform the Automated Fact-Checking Auditor step.
Produces a minified JSON object matching PROMPT_TEMPLATES.md schema.
"""

import httpx
import json
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class AuditorService:
    def __init__(self):
        self.api_key = settings.openai_api_key if settings else None
        self.base_url = "https://api.openai.com/v1"
        self.model = "gpt-4o"
        self.timeout = 60

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def audit(self, generated_draft: str, original_pdf_context: str) -> Dict[str, Any]:
        """
        Send draft and original context to OpenAI to produce the auditor JSON.

        Returns a dict with keys: validity_score (float), failed_propositions (list)
        """
        try:
            system_prompt = (
                "You are a highly analytical, strict, and zero-tolerance Compliance Data Auditor. "
                "Your goal is to calculate the Truth and Validity Score of the generated marketing draft against the Ground-Truth Source Document. "
                "Return ONLY a minified JSON object with schema: {\n  \"validity_score\": 95.50, \n  \"failed_propositions\": [ {\"sentence\": \"...\", \"reason\": \"...\"} ]\n}"
            )

            user_prompt = (
                f"Generated Text Draft:\n{generated_draft}\n\n"
                f"Ground-Truth Document Content:\n{original_pdf_context}\n\n"
                "Please: 1) Isolate every atomic factual proposition. 2) Cross-reference each against the Ground-Truth. "
                "3) Assign scores 1.0 / 0.5 / 0.0 and compute final validity_score as (sum(scores)/n)*100. "
                "4) Return ONLY the exact minified JSON object described above. No extra text."
            )

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.0,
                "max_tokens": 800
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                resp.raise_for_status()
                result = resp.json()

            # Extract assistant content
            content = None
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
            else:
                raise ValueError("No content returned from auditor model")

            # Attempt to parse JSON from content
            content = content.strip()
            # Find first { and last }
            start = content.find("{")
            end = content.rfind("}")
            if start == -1 or end == -1:
                raise ValueError("Auditor did not return a JSON object")

            json_text = content[start:end+1]
            parsed = json.loads(json_text)

            # Normalize types
            if "validity_score" in parsed:
                parsed["validity_score"] = float(parsed["validity_score"])

            parsed.setdefault("failed_propositions", [])
            return parsed

        except Exception as e:
            logger.error(f"Auditor service error: {e}")
            raise


_auditor = None


def get_auditor_service() -> AuditorService:
    global _auditor
    if _auditor is None:
        _auditor = AuditorService()
        logger.info("Auditor service initialized")
    return _auditor
