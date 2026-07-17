"""Streaming orchestrator — yields progress events for SSE"""
import os
import json
from typing import List, Optional, Generator
from .strategy_agent import plan_topics, plan_caption_strategy
from .data_agent import retrieve_facts
from .reporting_agent import write_caption


def stream_agentic_topics(text: str, filename: str, chunks: Optional[List[str]] = None) -> Generator[dict, None, list]:
    """
    Yields progress events during topic generation, returns final topics.
    """
    context = text[:4000]

    yield {"agent": "Strategy", "status": "running", "progress": 20, "message": "Menganalisis dokumen..."}
    strategies = plan_topics(context, filename)
    yield {"agent": "Strategy", "status": "done", "progress": 40, "message": "2 angle konten ditemukan"}

    enriched_topics = []
    for i, s in enumerate(strategies):
        pct = 40 + (i + 1) * 25
        yield {
            "agent": "Data",
            "status": "running",
            "progress": pct,
            "message": f"Mencari fakta untuk: {s.title[:50]}..."
        }
        data_ctx = retrieve_facts(s.query, chunks or [context], top_k=5)

        enriched_topics.append({
            "title": s.title,
            "angle": s.angle,
            "key_points": s.key_points,
            "facts": [
                {"statement": f.statement, "source_chunk": f.source_chunk}
                for f in data_ctx.facts
            ],
            "has_evidence": len(data_ctx.facts) > 0,
        })
        yield {
            "agent": "Data",
            "status": "done",
            "progress": pct,
            "message": f"{len(data_ctx.facts)} fakta ditemukan untuk topic {i+1}"
        }

    yield {"agent": "Complete", "status": "done", "progress": 100, "message": "Topics siap!", "final_result": {"topics": enriched_topics}}
    return {"topics": enriched_topics}


def stream_agentic_caption(
    text: str,
    filename: str,
    topic_title: str,
    topic_angle: str,
    topic_key_points: list,
    chunks: Optional[List[str]] = None,
    industry_hint: str = "",
) -> Generator[dict, None, dict]:
    """
    Yields progress events during caption generation, returns final CaptionOutput dict.
    """
    yield {"agent": "Data", "status": "running", "progress": 15, "message": "Mencari fakta relevan dari dokumen..."}

    data_ctx = retrieve_facts(
        f"{topic_title}: {topic_angle}",
        chunks or [text[:4000]],
        top_k=5
    )
    yield {"agent": "Data", "status": "done", "progress": 35, "message": f"{len(data_ctx.facts)} fakta ditemukan"}

    if not data_ctx.facts:
        from .schemas import DataContext
        data_ctx = DataContext(topic_title=topic_title, facts=[], raw_chunks=[text[:4000]])

    yield {"agent": "Strategy", "status": "running", "progress": 50, "message": "Menentukan strategi penulisan..."}

    facts_summary = "\n".join([
        f"[Chunk {f.source_chunk}] {f.statement}" for f in data_ctx.facts
    ])
    strategy = plan_caption_strategy(topic_title, topic_angle, facts_summary, industry_hint)
    yield {"agent": "Strategy", "status": "done", "progress": 65, "message": f"Persona: {strategy.persona[:40]}..."}

    yield {"agent": "Reporting", "status": "running", "progress": 75, "message": "Menulis caption..."}
    output = write_caption(strategy, data_ctx)
    yield {"agent": "Reporting", "status": "done", "progress": 90, "message": "Caption selesai, memverifikasi..."}

    result = {
        "caption": output.caption,
        "hashtags": output.hashtags,
        "verified_claims": output.verified_claims,
        "unverified_claims": output.unverified_claims,
    }

    yield {"agent": "Complete", "status": "done", "progress": 100, "message": "Selesai!"}
    return result
