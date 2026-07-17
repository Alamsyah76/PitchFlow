"""Reporting Agent — writes grounded caption, verifies claims, generates hashtags"""
import os
import json
import re
from openai import OpenAI
from .schemas import CaptionOutput, WritingStrategy, DataContext

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

AVOID = ["pernahkah anda", "apakah anda", "tahukah anda", "seiring dengan", "era baru", "lanskap",
         "mari kita", "mari diskusikan", "game changer", "revolution", "transformasi",
         "era digital", "future of", "dunia semakin", "tidak bisa dipungkiri",
         "yang perlu anda ketahui", "yang menarik adalah", "perlu diingat",
         "kita semua tahu", "sudah bukan rahasia", "tren yang berkembang",
         "selain itu", "sementara itu", "di sisi lain",
         "tidak hanya", "tetapi juga", "hal ini", "dengan demikian",
         "pada akhirnya", "oleh karena itu", "tak hanya",
         "merupakan salah satu", "salah satu", "dengan semakin"]


def write_caption(strategy: WritingStrategy, data: DataContext) -> CaptionOutput:
    """
    Write LinkedIn caption using strategy + verified data.
    Then self-verify each claim against source chunks.
    """
    facts_text = "\n".join([
        f"[Chunk {f.source_chunk}] {f.statement}" for f in data.facts
    ])
    chunks_text = "\n\n---\n\n".join(
        [f"CHUNK {i}:\n{c[:300]}" for i, c in enumerate(data.raw_chunks)]
    ) if data.raw_chunks else ""

    prompt = f"""You are a senior LinkedIn content writer. Write a professional LinkedIn post.

WRITING STRATEGY:
- Persona: {strategy.persona}
- Tone: {strategy.tone}
- Structure: {strategy.structure}
- Target Audience: {strategy.target_audience}
- Industry: {strategy.industry}

VERIFIED FACTS (use ONLY these — do not invent facts):
{facts_text}

RAW CHUNKS (for context only):
{chunks_text[:3000]}

REQUIREMENTS:
1. Write 3 paragraphs following the specified structure
2. Every claim MUST come from the VERIFIED FACTS above — no invented data
3. Natural, conversational tone — not salesy, not robotic
4. AVOID these phrases: {', '.join(AVOID[:15])}
5. End with a question or invitation to engage (not a sales pitch)
6. Language: Indonesian

Output JSON:
{{
  "caption": "Full post text...",
  "hashtags": ["#Hashtag1", "#Hashtag2", "#Hashtag3", "#Hashtag4", "#Hashtag5"]
}}

Hashtags: max 5, relevant to the content, mix of broad and specific, Indonesian/English.
"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        response_format={"type": "json_object"},
    )
    result = json.loads(resp.choices[0].message.content)

    caption = result.get("caption", "")
    hashtags_raw = result.get("hashtags", [])

    # Clean hashtags
    hashtags = [t for t in hashtags_raw if len(t) >= 3]
    hashtags = hashtags[:5]

    # VERIFICATION: check each claim against source chunks
    verified_claims, unverified_claims = _verify_claims(caption, data)

    return CaptionOutput(
        caption=_post_process(caption),
        hashtags=hashtags,
        verified_claims=verified_claims,
        unverified_claims=unverified_claims
    )


def _verify_claims(caption: str, data: DataContext) -> tuple:
    """
    Self-verification: extract claims from caption and check against source chunks.
    Returns (verified_claims, unverified_claims).
    """
    prompt = f"""You are a fact-checker. Given a LinkedIn caption and the source document chunks:

CAPTION:
{caption}

SOURCE CHUNKS:
{chr(10).join([f"Chunk {f.source_chunk}: {f.statement}" for f in data.facts])}

TASK: For each factual claim in the caption:
1. List the claim
2. Check if it's supported by a source chunk
3. Mark as VERIFIED or UNVERIFIED

Output JSON:
{{
  "verifications": [
    {{"claim": "...", "status": "VERIFIED", "source_chunk": 0}},
    {{"claim": "...", "status": "UNVERIFIED", "source_chunk": null}}
  ]
}}

Only check factual claims — not opinions, questions, or engagement hooks.
"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        response_format={"type": "json_object"},
    )
    result = json.loads(resp.choices[0].message.content)

    verified = []
    unverified = []
    for v in result.get("verifications", []):
        item = {"claim": v.get("claim", ""), "source_chunk": v.get("source_chunk")}
        if v.get("status") == "VERIFIED":
            verified.append(item)
        else:
            unverified.append(item["claim"])

    return verified, unverified


def _post_process(caption: str) -> str:
    """Clean up common AI-ish patterns"""
    result = caption
    for phrase in AVOID:
        # Case-insensitive replacement
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        result = pattern.sub("", result)
    # Clean up double spaces
    result = re.sub(r'  +', ' ', result)
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result.strip()
