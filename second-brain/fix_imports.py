"""Fix relative imports to absolute imports"""
import re
from pathlib import Path

files_to_fix = [
    "ingestion/deduplication.py",
    "ingestion/quality_gate.py",
    "ingestion/watcher.py",
    "storage/vector_store.py",
    "storage/knowledge_graph.py",
    "query/cli.py",
    "query/search.py",
]

replacements = {
    r"from \.\.shared\.": "from shared.",
    r"from \.\.storage\.": "from storage.",
    r"from \.\.ingestion\.": "from ingestion.",
    r"from \.\.query\.": "from query.",
    r"from \.": "from ingestion.",  # Single dot imports within ingestion/
}

for file_path in files_to_fix:
    path = Path(file_path)
    if not path.exists():
        print(f"Skipping {file_path} - not found")
        continue

    content = path.read_text()
    original = content

    for pattern, replacement in replacements.items():
        content = re.sub(pattern, replacement, content)

    if content != original:
        path.write_text(content)
        print(f"✓ Fixed {file_path}")
    else:
        print(f"- No changes needed for {file_path}")

print("\n✅ Import fixes complete!")
