from dataclasses import dataclass
from pathlib import Path
from typing import Any 

@dataclass
class Chunk:
    id: str
    text: str
    metadata: dict[str, Any]

def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    
    parts = text.split("---", 2)

    if len(parts) < 3:
        return {}, text
    
    raw_metadata = parts[1]
    body = parts[2].strip()

    metadata: dict[str, Any] = {}

    for line in raw_metadata.splitlines():
        if ":" not in line:
            continue
    key, value = line.split(":", 1)
    key = key.strip()
    value = value.strip()

    if key == "year":
        metadata[key] = int(value)
    else:
        metadata[key] = value

    
    return metadata, body

def split_markdown_section(text: str) -> list[tuple[str, str]]:
    lines = text.splitlines()

    sections: list[tuple[str, str]] = []
    current_title = "Introduction"
    current_lines: list[str] = []

    for line in lines:
        if line.startswith("#"):
            if current_lines:
                sections.append((current_title, "\n".join(current_lines).strip()))
                current_lines = []
            
            current_title = line.lstrip("#").strip()
        else:
            current_lines.append(line)
    
    if current_lines:
        sections.append((current_title, "\n".join(current_lines).strip()))

    return [(title, body)
            for title, body in sections
            if body.strip()
    ]

def split_by_words(text: str, chunk_size: int, overlap: int) -> list[str]:
    words = text.split()

    if not words:
        return []
    
    chunks: list[str] = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))

        if end >= len(words):
            break

        start = end - overlap

    return chunks

def load_and_chunk_markdown_files(
        raw_dir: Path, 
        chunk_size: int,
        overlap: int
) -> list[Chunk]:
    all_chunks: list[Chunk] = []

    
    for path in sorted(raw_dir.glob("*.md")):
        raw_text = path.read_text(encoding="utf-8")
        base_metadata, body = parse_frontmatter(raw_text)

        doc_id = str(base_metadata.get("doc_id", path.stem))
        title = str(base_metadata.get("title", path.stem))

        sections = split_markdown_section(body)

        chunk_number = 0

        for section_title, section_body in sections:
            text_with_context = (
                f"Document title: {title}\n"
                f"Section: {section_title}\n\n"
                f"{section_body}"
            )

            parts = split_by_words(
                text=text_with_context,
                chunk_size=chunk_size,
                overlap=overlap
            )

            for part in parts:
                chunk_id = f"{doc_id}_chunk_{chunk_number:03d}"
                chunk_number += 1

                metadata = {
                    **base_metadata,
                    "source_file": path.name,
                    "section": section_title,
                    "chunk_index": chunk_number - 1,
                }

                all_chunks.append(
                    Chunk(
                        id=chunk_id,
                        text=part,
                        metadata=metadata
                    )
                )

        return all_chunks