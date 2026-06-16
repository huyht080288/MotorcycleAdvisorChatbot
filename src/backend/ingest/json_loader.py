from dataclasses import dataclass
import json
from pathlib import Path

from backend.paths import DATAREF_DIR


@dataclass
class KnowledgeEntry:
    id: str
    question: str
    answer: str
    tags: list[str]
    source_url: str
    source_file: str


def entry_to_document(entry: KnowledgeEntry) -> str:
    return f"{entry.question} {entry.answer}"


def load_dataref_file(path: Path) -> list[KnowledgeEntry]:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    entries: list[KnowledgeEntry] = []
    for item in data.get("entries", []):
        question = (item.get("question") or "").strip()
        answer = (item.get("answer") or "").strip()
        if not question or not answer:
            continue
        entries.append(
            KnowledgeEntry(
                id=item.get("id") or f"{path.stem}-{len(entries)}",
                question=question,
                answer=answer,
                tags=item.get("tags") or [],
                source_url=item.get("source_url") or "",
                source_file=path.name,
            )
        )
    return entries


def load_multiple_files(filenames: list[str]) -> list[KnowledgeEntry]:
    all_entries: list[KnowledgeEntry] = []
    seen_ids: set[str] = set()

    for name in filenames:
        path = DATAREF_DIR / name
        if not path.exists():
            raise FileNotFoundError(f"Không tìm thấy file: {name}")
        for entry in load_dataref_file(path):
            if entry.id in seen_ids:
                entry.id = f"{entry.id}-{entry.source_file}"
            seen_ids.add(entry.id)
            all_entries.append(entry)

    return all_entries


def list_dataref_files() -> list[str]:
    if not DATAREF_DIR.exists():
        return []
    return sorted(p.name for p in DATAREF_DIR.glob("*.json"))
