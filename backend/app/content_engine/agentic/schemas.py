"""Agentic RAG — data models for agent I/O"""
from typing import List, Optional

class TopicStrategy:
    """Output from Strategy Agent — a single topic angle"""
    def __init__(self, title: str, angle: str, query: str, key_points: List[str]):
        self.title = title
        self.angle = angle
        self.query = query       # specific query for Data Agent to retrieve
        self.key_points = key_points

class Fact:
    """A single verified fact from document"""
    def __init__(self, statement: str, source_chunk: int, context: str = ""):
        self.statement = statement
        self.source_chunk = source_chunk
        self.context = context

class DataContext:
    """Output from Data Agent — facts organized by topic"""
    def __init__(self, topic_title: str, facts: List[Fact], raw_chunks: List[str] = None):
        self.topic_title = topic_title
        self.facts = facts
        self.raw_chunks = raw_chunks or []

class WritingStrategy:
    """Output from Strategy Agent for caption writing"""
    def __init__(self, persona: str, tone: str, structure: str, target_audience: str, industry: str):
        self.persona = persona
        self.tone = tone
        self.structure = structure
        self.target_audience = target_audience
        self.industry = industry

class CaptionOutput:
    """Final output from Reporting Agent"""
    def __init__(self, caption: str, hashtags: List[str], verified_claims: List[dict], unverified_claims: List[str]):
        self.caption = caption
        self.hashtags = hashtags
        self.verified_claims = verified_claims      # [{claim, source_chunk}]
        self.unverified_claims = unverified_claims  # claims that couldn't be verified
