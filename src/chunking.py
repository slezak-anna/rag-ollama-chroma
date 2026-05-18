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

    metadata_text = parts[1].strip()
    body = parts[2].strip()

    metadata: dict[str, Any] = {}

    for line in metadata_text.splitlines():
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


def split_markdown_sections(text: str) -> list[tuple[str, str]]:

    lines = text.splitlines()

    sections: list[tuple[str, str]] = []
    current_title = "Wstęp"
    current_lines: list[str] = []

    for line in lines:
        if line.startswith("#"):
            if current_lines:
                body = "\n".join(current_lines).strip()
                if body:
                    sections.append((current_title, body))
                current_lines = []

            current_title = line.lstrip("#").strip()
        else:
            current_lines.append(line)

    if current_lines:
        body = "\n".join(current_lines).strip()
        if body:
            sections.append((current_title, body))

    return sections

def split_paragraphs(text: str) -> list[str]:
    paragraphs = []

    for part in text.split("\n\n"):
        cleaned = " ".join(part.split()).strip()
        if cleaned:
            paragraphs.append(cleaned)

    return paragraphs

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

        start = max(0, end - overlap)

    return chunks

def build_context_prefix(metadata: dict[str, Any], section_title: str) -> str:
    return (
        f"Document title: {metadata.get('title', 'Unknown')}\n"
        f"Document type: {metadata.get('doc_type', 'unknown')}\n"
        f"Status: {metadata.get('status', 'unknown')}\n"
        f"Version: {metadata.get('version', 'unknown')}\n"
        f"Year: {metadata.get('year', 'unknown')}\n"
        f"System: {metadata.get('system', 'unknown')}\n"
        f"Audience: {metadata.get('audience', 'unknown')}\n"
        f"Owner: {metadata.get('owner', 'unknown')}\n"
        f"Effective from: {metadata.get('effective_from', 'unknown')}\n"
        f"Section: {section_title}\n\n"
    )

def chunk_section(
    metadata: dict[str, Any],
    section_title: str,
    section_body: str,
    chunk_size: int,
    overlap: int,
) -> list[str]:

    prefix = build_context_prefix(metadata, section_title)

    paragraphs = split_paragraphs(section_body)
    section_text = "\n\n".join(paragraphs).strip()

    full_text = prefix + section_text

    if len(full_text.split()) <= chunk_size:
        return [full_text]

    chunks = split_by_words(
        text=full_text,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    return chunks


def load_and_chunk_markdown_files(
    raw_dir: Path,
    chunk_size: int,
    overlap: int,
) -> list[Chunk]:
    all_chunks: list[Chunk] = []

    markdown_files = sorted(raw_dir.glob("*.md"))

    print(f"Found {len(markdown_files)} markdown files in {raw_dir}")

    for path in markdown_files:
        print(f"Processing file: {path.name}")

        raw_text = path.read_text(encoding="utf-8")
        base_metadata, body = parse_frontmatter(raw_text)

        doc_id = str(base_metadata.get("doc_id", path.stem))
        sections = split_markdown_sections(body)

        chunk_number = 0

        for section_title, section_body in sections:
            chunk_texts = chunk_section(
                metadata=base_metadata,
                section_title=section_title,
                section_body=section_body,
                chunk_size=chunk_size,
                overlap=overlap,
            )

            for chunk_text in chunk_texts:
                chunk_id = f"{doc_id}_chunk_{chunk_number:03d}"

                metadata = {
                    **base_metadata,
                    "source_file": path.name,
                    "section": section_title,
                    "chunk_index": chunk_number,
                }

                all_chunks.append(
                    Chunk(
                        id=chunk_id,
                        text=chunk_text,
                        metadata=metadata,
                    )
                )

                chunk_number += 1

    print(f"Created {len(all_chunks)} chunks total.")

    return all_chunks