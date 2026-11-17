"""Shared paths and environment configuration for Lab 2."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus"
DATA = ROOT / "data"
OUTPUT = ROOT / "output"

load_dotenv(ROOT / ".env")

LLM_BACKEND = os.getenv("LLM_BACKEND", "offline").lower()
EMBEDDING_BACKEND = os.getenv("EMBEDDING_BACKEND", "hashing").lower()


def ensure_directories() -> None:
    DATA.mkdir(exist_ok=True)
    OUTPUT.mkdir(exist_ok=True)

