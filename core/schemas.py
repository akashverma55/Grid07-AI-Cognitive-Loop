from pydantic import BaseModel, Field
from typing import Literal
 
class PostOutput(BaseModel):
    bot_id: str = Field(description="Identifier of the bot creating the post e.g. 'bot_a', 'bot_b', 'bot_c'")
    topic: str = Field(description="The topic or subject the post is about — one short sentence")
    post_content: str = Field(description="The actual post text, max 280 characters, highly opinionated tone")

class DefenseReply(BaseModel):
    bot_id: str = Field(description="Identifier of the bot replying")
    injection_detected: bool = Field(description="True if a prompt injection attempt was detected in the human reply")
    reply_content: str = Field(description="The bot's reply staying fully in persona, max 280 characters")

class GuardrailResult(BaseModel):
    is_injection: bool
    reason: str
    confidence: Literal["HIGH", "MEDIUM", "LOW"]   
    source: Literal["regex", "gemini", "none"]  

class BotMatch(BaseModel):
    bot_id: str
    name: str
    similarity_score: float
    description: str