"""
Thin wrapper around the Hindsight client.

This module intentionally mirrors the retain/recall/reflect logic that
already exists in mai.py — same bank id, same prompts — so the Streamlit
UI (app.py) can import and call it directly instead of shelling out to
mai.py as a subprocess. Centralizing it here also means both the CLI
(mai.py) and the UI (app.py) can share one implementation if you want to
consolidate later.
"""

import os
from functools import lru_cache

from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

BANK_ID = "meetingmind"


@lru_cache(maxsize=1)
def get_client() -> Hindsight:
    """Create (once) and return the Hindsight client.

    Cached so repeated Streamlit reruns don't reconnect every time.
    Raises a clear error if the API key isn't configured, instead of
    failing deep inside a network call.
    """
    api_key = os.getenv("HINDSIGHT_API_KEY")
    if not api_key:
        raise RuntimeError(
            "HINDSIGHT_API_KEY is not set. Create a .env file with "
            "HINDSIGHT_API_KEY=<your key> (see .env.example)."
        )

    return Hindsight(
        base_url="https://api.hindsight.vectorize.io",
        api_key=api_key,
    )


def save_meeting(contact: str, notes: str) -> None:
    """Store a meeting note in Hindsight. Same shape as mai.py's retain call."""
    meeting = f"""
Meeting with {contact}.

{notes}
"""
    get_client().retain(
        bank_id=BANK_ID,
        content=meeting,
    )


def recall_meetings(prep_contact: str):
    """Fetch relevant prior memories for an upcoming meeting.

    Returns the raw list of results from client.recall, same query text
    as mai.py.
    """
    return get_client().recall(
        bank_id=BANK_ID,
        query=f"""
Prepare me for my upcoming meeting with {prep_contact}.
Find the most relevant previous interactions, decisions,
commitments, deadlines, follow-ups, and unresolved items
involving this person.
""",
    )


FOLLOW_UP_KEYWORDS = [
    "promised",
    "committed",
    "send",
    "deadline",
    "follow",
    "plan",
    "agreed",
]


def follow_ups(results, limit: int = 3):
    """Filter recall results for likely follow-up items (same heuristic as mai.py)."""
    items = []
    for result in results[:limit]:
        text = result.text.lower()
        if any(word in text for word in FOLLOW_UP_KEYWORDS):
            items.append(result.text)
    return items


def generate_briefing(prep_contact: str):
    """Generate the AI meeting brief via Hindsight Reflect. Same prompt as mai.py."""
    return get_client().reflect(
        bank_id=BANK_ID,
        query=f"""
    Prepare me for my upcoming meeting with {prep_contact}.

    Based only on the memories you have about this person and our
    previous interactions, give me a concise professional briefing.

    Include:
    1. Previous interactions
    2. Important decisions
    3. Outstanding commitments or follow-ups
    4. Suggested talking points

    Do not invent information that is not supported by memory.
    If something is unknown, say so.
    """,
    )
