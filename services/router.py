from sentence_transformers import SentenceTransformer
from core.config import EMBEDDING_MODEL, SIMILARITY_THRESHOLD
from core.vector_store import get_vector_store
from core.schemas import BotMatch
from agents.personas import ALL_BOTS

print(f"[Router] Loading embedding model: {EMBEDDING_MODEL}")
embedder = SentenceTransformer(EMBEDDING_MODEL)
print(f"[Router] Embedding model loaded.")

collection = get_vector_store("bot_personas")


def _initialize_persona_store() -> None:
    if collection.count() > 0:
        return

    print("[Router] Embedding and storing bot personas in ChromaDB...")

    for bot in ALL_BOTS:
        embedding = embedder.encode(bot["description"]).tolist()
        collection.add(
            ids=[bot["id"]],
            embeddings=[embedding],
            documents=[bot["description"]],
            metadatas=[{"name": bot["name"], "bot_id": bot["id"]}],
        )
        print(f"  Stored: {bot['id']} ({bot['name']})")

    print(f"[Router] collection.count() personas stored.\n")


_initialize_persona_store()


def route_post_to_bots(
    post_content: str,
    threshold: float = None,
) -> list[BotMatch]:
    if threshold is None:
        threshold = SIMILARITY_THRESHOLD

    if not post_content or not post_content.strip():
        print("[Router] Empty post — returning no matches.")
        return []

    post_embedding = embedder.encode(post_content.strip()).tolist()

    results = collection.query(
        query_embeddings=[post_embedding],
        n_results=len(ALL_BOTS),
        include=["metadatas", "documents", "distances"],
    )

    matched_bots: list[BotMatch] = []

    ids       = results["ids"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]
    documents = results["documents"][0]

    for i, (bot_id, distance, metadata) in enumerate(zip(ids, distances, metadatas)):
        # ChromaDB cosine: similarity = 1 - distance
        similarity = round(1.0 - distance, 4)

        print(
            f"  [Router] {bot_id} ({metadata['name']}) "
            f"| similarity: {similarity} | threshold: {threshold} "
            f"| {'✓ MATCHED' if similarity >= threshold else '✗ skipped'}"
        )

        if similarity >= threshold:
            matched_bots.append(BotMatch(
                bot_id=bot_id,
                name=metadata["name"],
                similarity_score=similarity,
                description=documents[i],
            ))

    matched_bots.sort(key=lambda x: x.similarity_score, reverse=True)

    print(f"\n[Router] Matched {len(matched_bots)}/{len(ALL_BOTS)} bots for this post.")
    return matched_bots