"""Orchestrator — wires Strategy, Data, and Reporting Agents into a pipeline"""
import os
import json
from typing import List, Optional
from .schemas import TopicStrategy, DataContext, WritingStrategy, CaptionOutput
from .strategy_agent import plan_topics, plan_caption_strategy
from .data_agent import retrieve_facts
from .reporting_agent import write_caption


def agentic_generate_topics(text: str, filename: str, chunks: Optional[List[str]] = None) -> list:
    """
    2-Phase topic generation:
    1. Strategy Agent → 2 topic angles with specific queries
    2. Data Agent → for each angle, retrieve supporting facts

    Returns enriched topics ready for frontend.
    """
    # Phase 1: Strategy Agent plans 2 angles
    context = text[:4000]
    strategies = plan_topics(context, filename)

    enriched_topics = []
    for s in strategies:
        # Phase 2: Data Agent retrieves facts for this angle
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

    return enriched_topics


def agentic_generate_caption(
    text: str,
    filename: str,
    topic_title: str,
    topic_angle: str,
    topic_key_points: list,
    chunks: Optional[List[str]] = None,
    industry_hint: str = "",
) -> CaptionOutput:
    """
    3-Phase caption generation:
    1. Data Agent → retrieve facts for this topic
    2. Strategy Agent → determine writing strategy from facts
    3. Reporting Agent → write caption + self-verify
    """
    # Phase 1: Data Agent retrieves facts
    data_ctx = retrieve_facts(
        f"{topic_title}: {topic_angle}",
        chunks or [text[:4000]],
        top_k=5
    )

    if not data_ctx.facts:
        # Fallback: use text directly
        data_ctx = DataContext(
            topic_title=topic_title,
            facts=[],
            raw_chunks=[text[:4000]]
        )

    # Phase 2: Strategy Agent plans writing approach
    facts_summary = "\n".join([
        f"[Chunk {f.source_chunk}] {f.statement}" for f in data_ctx.facts
    ])
    strategy = plan_caption_strategy(
        topic_title, topic_angle, facts_summary, industry_hint
    )

    # Phase 3: Reporting Agent writes + verifies
    output = write_caption(strategy, data_ctx)

    return output
