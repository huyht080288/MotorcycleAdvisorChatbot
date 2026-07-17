"""CLI làm sạch answer trong một hoặc nhiều file DataRef JSON."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from tools.dataref_cleaner import clean_answer


def clean_file(path: Path, dry_run: bool = False) -> dict[str, int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.get("entries", [])
    changed = 0

    for entry in entries:
        old_answer = entry.get("answer", "")
        new_answer = clean_answer(old_answer, entry.get("id", ""))
        if new_answer != old_answer:
            entry["answer"] = new_answer
            changed += 1

    if changed and not dry_run:
        data["answers_cleaned_at"] = datetime.now(timezone.utc).isoformat()
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    return {"entries": len(entries), "changed": changed}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Loại boilerplate website khỏi answer trong DataRef JSON"
    )
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    for path in args.files:
        result = clean_file(path, dry_run=args.dry_run)
        action = "would_change" if args.dry_run else "changed"
        print(f"{path}: entries={result['entries']} {action}={result['changed']}")


if __name__ == "__main__":
    main()
