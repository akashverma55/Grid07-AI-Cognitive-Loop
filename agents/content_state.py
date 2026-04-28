from typing import TypedDict, Optional


class ContentState(TypedDict):
    bot_id: str
    bot_persona: dict
    search_query: Optional[str]
    search_results: Optional[str]
    topic: Optional[str]
    post_content: Optional[str]
    error: Optional[str]