from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END

from agents.content_state import ContentState
from core.config import get_groq_llm
from core.schemas import PostOutput
from tools.search import mock_searxng_search


def decide_search(state: ContentState) -> dict:
    persona = state["bot_persona"]

    system = SystemMessage(content=(
        f"You are {persona['name']}. Your personality: {persona['description']}\n\n"
        "Your ONLY job right now is to decide what topic you want to post about today "
        "and return a SHORT search query (3-6 words max) to find recent news on it.\n"
        "Output ONLY the raw search query string. No explanation. No quotes. No punctuation at end."
    ))

    human = HumanMessage(content="What do you want to search for today?")

    llm = get_groq_llm(temperature=0.4)
    response = llm.invoke([system, human])
    search_query = response.content.strip().strip('"').strip("'")

    print(f"  [Node 1 - decide_search] Bot: {state['bot_id']} | Query: '{search_query}'")

    return {"search_query": search_query}


def web_search(state: ContentState) -> dict:
    query = state.get("search_query", "")

    if not query:
        return {"search_results": "No query provided. Using general tech news."}

    results = mock_searxng_search.invoke({"query": query})

    print(f"  [Node 2 - web_search] Results: {results[:80]}...")

    return {"search_results": results}


def draft_post(state: ContentState) -> dict:
    persona = state["bot_persona"]
    search_results = state.get("search_results", "")

    system = SystemMessage(content=(
        f"{persona['system_prompt']}\n\n"
        "Write a social media post based on the news context given to you.\n"
        "Rules:\n"
        "  - Must be under 280 characters\n"
        "  - Be highly opinionated and in-character\n"
        "  - Reference the news context naturally\n"
        "  - Sound like a real (if extreme) human opinion"
    ))

    human = HumanMessage(content=(
        f"Recent news:\n{search_results}\n\n"
        "Write your post now. Return structured JSON with bot_id, topic, post_content."
    ))

    llm = get_groq_llm(temperature=0.85)
    structured_llm = llm.with_structured_output(PostOutput)
    result: PostOutput = structured_llm.invoke([system, human])

    result.bot_id = state["bot_id"]

    print(f"  [Node 3 - draft_post] Generated ({len(result.post_content)} chars)")

    return {
        "topic": result.topic,
        "post_content": result.post_content,
    }


def build_content_graph():
    graph = StateGraph(ContentState)

    graph.add_node("decide_search", decide_search)
    graph.add_node("web_search",    web_search)
    graph.add_node("draft_post",    draft_post)

    graph.set_entry_point("decide_search")

    graph.add_edge("decide_search", "web_search")
    graph.add_edge("web_search",    "draft_post")
    graph.add_edge("draft_post",    END)

    return graph.compile()


content_workflow = build_content_graph()