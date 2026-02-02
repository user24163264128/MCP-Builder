"""Content selection for reasoning."""

from ..ingestion.models import RepositorySnapshot


def select_content(snapshot: RepositorySnapshot, max_length: int = 10000) -> str:
    """Select and concatenate high-priority content for reasoning.

    Args:
        snapshot: Repository snapshot
        max_length: Maximum content length

    Returns:
        Concatenated content string
    """
    content_parts = []
    total_length = 0

    for file in snapshot.files:
        if total_length + len(file.content) > max_length:
            remaining = max_length - total_length
            content_parts.append(file.content[:remaining])
            break
        content_parts.append(file.content)
        total_length += len(file.content)

    return "\n\n".join(content_parts)