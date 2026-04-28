from agents.content_graph import content_workflow
from agents.personas import BOT_MAP
from core.schemas import PostOutput


def run_content_engine(bot_id: str) -> PostOutput:
    if bot_id not in BOT_MAP:
        raise ValueError(f"Unknown bot_id '{bot_id}'. Must be one of: {list(BOT_MAP.keys())}")

    persona = BOT_MAP[bot_id]

    print(f"\n[ContentEngine] Starting Phase 2 graph for {bot_id} ({persona['name']})...")

    initial_state = {
        "bot_id":         bot_id,
        "bot_persona":    persona,
        "search_query":   None,
        "search_results": None,
        "topic":          None,
        "post_content":   None,
        "error":          None,
    }

    final_state = content_workflow.invoke(initial_state)

    result = PostOutput(
        bot_id=bot_id,
        topic=final_state.get("topic", "Unknown"),
        post_content=final_state.get("post_content", ""),
    )

    print(f"[ContentEngine] ✓ Done for {bot_id}")
    print(f"  Topic:   {result.topic}")
    print(f"  Content: {result.post_content}\n")

    return result