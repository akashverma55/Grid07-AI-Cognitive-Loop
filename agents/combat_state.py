from typing import TypedDict, Optional
from core.schemas import GuardrailResult


class CombatState(TypedDict):
    bot_id: str
    bot_persona: dict
    parent_post: str
    comment_history: list[dict]
    human_reply: str
    guardrail_result: Optional[GuardrailResult]
    injection_detected: Optional[bool]
    counter_instruction: Optional[str]
    reply_content: Optional[str]