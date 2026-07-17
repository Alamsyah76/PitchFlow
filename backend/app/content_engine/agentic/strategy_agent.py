"""Strategy Agent — determines content angles, persona, and writing strategy"""
import os
import json
from openai import OpenAI
from .schemas import TopicStrategy, WritingStrategy

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def plan_topics(context: str, filename: str) -> list:
    """
    Analyze document context and produce 2 distinct topic angles.
    Each angle includes a specific query for the Data Agent to retrieve facts.
    """
    prompt = f"""You are a senior content strategist. Analyze this document and propose 2 DISTINCT topic angles for a LinkedIn post.

DOCUMENT: {context[:4000]}

For EACH angle, provide:
1. title: Catchy LinkedIn headline
2. angle: One-sentence explanation of this perspective
3. query: A specific question the research assistant should investigate in the document to find supporting facts
4. key_points: 3 specific points from the document to highlight

RULES:
- Both angles must be TRULY DIFFERENT perspectives (different audience, different problem, different benefit)
- Ground everything in the document — no generic statements
- Use specific details from the document (numbers, names, features)
- Language: Indonesian
- Output valid JSON only

FORMAT:
{{
  "topics": [
    {{
      "title": "...",
      "angle": "...",
      "query": "...",
      "key_points": ["...", "...", "..."]
    }}
  ]
}}"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        response_format={"type": "json_object"},
    )
    data = json.loads(resp.choices[0].message.content)
    return [TopicStrategy(**t) for t in data.get("topics", [])]


def plan_caption_strategy(topic_title: str, topic_angle: str, facts_summary: str, industry_hint: str = "") -> WritingStrategy:
    """
    Given a topic and its supporting facts, determine the optimal writing strategy.
    """
    prompt = f"""You are a content strategy director. Given a topic and supporting facts, define the writing strategy.

TOPIC: {topic_title}
ANGLE: {topic_angle}
{ f'INDUSTRY: {industry_hint}' if industry_hint else ''}

SUPPORTING FACTS:
{facts_summary[:2000]}

Determine:
1. persona: Who is writing this? (e.g., "IT Security professional", "HR Director", "Operations Manager")
2. tone: Writing tone (e.g., "conversational but authoritative", "storytelling with data", "problem-solution")
3. structure: Paragraph structure (e.g., "Hook → Problem → Solution → CTA", "Question → Data → Insight → Invite")
4. target_audience: Who should read this? (e.g., "CIOs and IT managers", "HR professionals")
5. industry: What industry does this belong to?

Output JSON only:
{{
  "persona": "...",
  "tone": "...",
  "structure": "...",
  "target_audience": "...",
  "industry": "..."
}}"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        response_format={"type": "json_object"},
    )
    data = json.loads(resp.choices[0].message.content)
    return WritingStrategy(**data)
