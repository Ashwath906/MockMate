
from pathlib import Path

WEAK_TOPICS_FILE = Path("workspace/weak-topics.md")
WEAK_SCORE_THRESHOLD = 7


def record_weak_topics(scorecard):
    """Record weak areas without overwriting existing records."""

    WEAK_TOPICS_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not WEAK_TOPICS_FILE.exists():
        WEAK_TOPICS_FILE.write_text(
            "# MockMate Weak Topics\n\n"
            "This file tracks topics where the candidate needs improvement.\n\n"
            "## Weak Topics\n",
            encoding="utf-8"
        )

    if scorecard.score >= WEAK_SCORE_THRESHOLD:
        return "No weak areas detected. Score is satisfactory."

    content = WEAK_TOPICS_FILE.read_text(encoding="utf-8")

    new_topics = [
        gap for gap in scorecard.gaps
        if gap not in content
    ]

    if not new_topics:
        return "These weak topics are already recorded."

    with WEAK_TOPICS_FILE.open("a", encoding="utf-8") as file:
        file.write(f"\n- Score: {scorecard.score}/10\n")

        for topic in new_topics:
            file.write(f"- {topic}\n")

    return "Weak areas recorded successfully."


def read_weak_topics():
    """Read previously recorded weak topics."""

    if not WEAK_TOPICS_FILE.exists():
        return []

    content = WEAK_TOPICS_FILE.read_text(encoding="utf-8")

    topics = []

    for line in content.splitlines():
        line = line.strip()

        if line.startswith("- ") and not line.startswith("- Score:"):
            topics.append(line[2:])

    return topics


def reset_weak_topics():
    """Reset the weak-topic file. Call only after user approval."""

    WEAK_TOPICS_FILE.parent.mkdir(parents=True, exist_ok=True)

    WEAK_TOPICS_FILE.write_text(
        "# MockMate Weak Topics\n\n"
        "This file tracks topics where the candidate needs improvement.\n\n"
        "## Weak Topics\n",
        encoding="utf-8"
    )

    return "Weak topics reset successfully."
