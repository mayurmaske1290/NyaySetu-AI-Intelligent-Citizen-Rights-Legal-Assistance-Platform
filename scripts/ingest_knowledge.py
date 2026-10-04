"""Re-ingest demo markdown into a JSON dump. Replace this with pgvector upsert when DATABASE_URL is set."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1] / "knowledge_base" / "legal_sources"
out = Path(__file__).resolve().parents[1] / "knowledge_base" / "chunks" / "ingested.json"
items = []
for p in sorted(root.glob("*.md")):
    items.append({"id": p.stem, "title": p.stem, "content": p.read_text(encoding="utf-8"), "is_demo": True})
out.write_text(json.dumps(items, indent=2), encoding="utf-8")
print(f"Wrote {len(items)} demo files to {out}")
