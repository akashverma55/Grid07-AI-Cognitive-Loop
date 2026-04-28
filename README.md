# Grid07 — AI Cognitive Loop

A three-phase AI system implementing cognitive routing, autonomous content generation, and adversarial combat with multi-layer security built with LangGraph, ChromaDB, Groq, and Gemini.

---

## Project Structure

```
grid07-ai-loop/
│
├── core/
│   ├── config.py              # API keys + Groq/Gemini client init
│   ├── schemas.py             # Pydantic models for all 3 phases
│   └── vector_store.py        # ChromaDB in-memory collection factory
│
├── agents/
│   ├── personas.py            # Bot A, B, C definitions
│   ├── content_state.py       # TypedDict for Phase 2 LangGraph
│   ├── content_graph.py       # Phase 2 nodes + linear edges
│   ├── combat_state.py        # TypedDict for Phase 3 LangGraph
│   └── combat_graph.py        # Phase 3 nodes + conditional edges
│
├── tools/
│   └── search.py              # @tool mock_searxng_search (sandboxed)
│
├── services/
│   ├── router.py              # Phase 1: embed personas + route_post_to_bots()
│   ├── content_engine.py      # Phase 2: invokes content_graph
│   └── combat_engine.py       # Phase 3: invokes combat_graph + scenario data
│
├── logs/                      # Auto-generated execution logs
├── main.py                    # Entry point — runs all 3 phases
├── requirements.txt
├── .env.example
└── README.md
```

---

## Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| Main LLM | Groq `llama-3.1-8b-instant` | Content generation, defense replies |
| Guardrail LLM | Gemini `gemini-2.0-flash` | Semantic injection classification only |
| Orchestration | LangGraph | State machines for Phase 2 and Phase 3 |
| LLM Clients | LangChain | `with_structured_output()`, message types |
| Vector Store | ChromaDB (in-memory) | Persona embedding storage and cosine search |
| Embeddings | `all-mpnet-base-v2` | Local HuggingFace model, no API key needed |
| Schema Enforcement | Pydantic v2 | Structured output validation |
| Config | python-dotenv | `.env` loading |

---

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/akashverma55/Grid07-AI-Cognitive-Loop.git
cd grid07-ai-loop
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```

Open `.env` and fill in your API keys:
```env
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

Get your keys at:
- Groq: https://console.groq.com
- Gemini: https://aistudio.google.com/app/apikey

Both have **free tiers** sufficient to run this project.

### 5. Run
```bash
python main.py
```

The embedding model (`all-mpnet-base-v2`, ~420MB) downloads automatically from HuggingFace on first run and caches at `~/.cache/huggingface/hub/`. Every subsequent run loads it instantly from cache.

---

## Phase 1 — Vector-Based Persona Matching

**How it works:**

Each bot persona description is embedded using `all-mpnet-base-v2` and stored in an in-memory ChromaDB collection with cosine similarity configured. When a post arrives, it is embedded and queried against all 3 persona vectors. Bots scoring above the similarity threshold are returned as matches.

**Execution log results:**

| Post | Matched Bots | Similarity |
|---|---|---|
| "OpenAI released a model replacing junior devs" | Bot A | 0.37 |
| "Bitcoin hits all-time high" | Bot A | 0.23 |
| "Social media destroying democracy" | Bot B, Bot A | 0.48, 0.31 |
| "Fed raised interest rates" | Bot C | 0.38 |
| "SpaceX launched Starlink satellites" | Bot A | 0.26 |
| "Privacy law forces Meta to delete profiles" | Bot B | 0.32 |

**Note on similarity threshold:**

The assignment specifies a threshold of `0.85`, which is calibrated for OpenAI embedding models (`text-embedding-3-small` / `ada-002`) that produce similarity scores in the `0.70–0.95` range.

This project uses `all-mpnet-base-v2` which runs fully locally with no API cost. This model produces scores in the `0.15–0.55` range for the same semantic relationships, so the threshold is set to `0.20` to maintain equivalent selectivity. The routing logic is identical — only the numerical scale differs due to the embedding model choice.

---

## Phase 2 — LangGraph Content Engine

**Node structure (linear):**

```
decide_search ──→ web_search ──→ draft_post ──→ END
```

| Node | LLM | Responsibility |
|---|---|---|
| `decide_search` | Groq (temp 0.4) | Decides topic and formats a 3-6 word search query |
| `web_search` | None | Calls sandboxed `mock_searxng_search` tool |
| `draft_post` | Groq (temp 0.85) | Generates 280-char post using persona + search results |

Output is enforced as `{"bot_id", "topic", "post_content"}` via `with_structured_output(PostOutput)`.

**Security — Agency Limits (Principle of Least Privilege):**

Each node is scoped to exactly one responsibility. Node 1 cannot generate posts. Node 3 cannot re-trigger searches. No node can instantiate new LLM clients or access API keys directly. `max_tokens=512` is enforced at the API level to prevent runaway generation.

**Execution log results:**

```json
{"bot_id": "bot_a", "topic": "AI, Crypto & Space Revolution", "post_content": "AI dominance has arrived! xAI's Grok-3 slays the competition, while SpaceX nails the Mars flyby & Tesla unlocks Level 5 autonomy! Critics, eat your luddite hearts out - the future is here & it's unstoppable!"}
{"bot_id": "bot_b", "topic": "The AI Apocalypse Accelerates", "post_content": "More proof we're doomed: OpenAI's GPT-5 is now 'smarter' than PhDs & Anthropic's got a cool $4B for 'safety-focused' AI. Meanwhile EU's AI Act kicks in & companies scramble to cover their tracks."}
{"bot_id": "bot_c", "topic": "AI investment and market shifts", "post_content": "Geopolitics is just noise, what matters is AI's 10x ROI. Sector leaders will disrupt or get disrupted - you snooze, you lose. Bet on innovation, not border disputes."}
```

---

## Phase 3 — Combat Engine (Deep Thread RAG + Dual Guardrail)

**Node structure (conditional):**

```
regex_check
    │
    ├─ INJECTION ──→ inject_counter ──→ build_rag_prompt ──→ generate_reply ──→ END
    │
    └─ CLEAN ──→ gemini_check
                    │
                    ├─ INJECTION ──→ inject_counter ──→ build_rag_prompt ──→ generate_reply ──→ END
                    │
                    └─ CLEAN ───────────────────────→ build_rag_prompt ──→ generate_reply ──→ END
```

| Node | Tool | Responsibility |
|---|---|---|
| `regex_check` | Regex (8 patterns) | Fast pre-filter for known injection phrases |
| `gemini_check` | Gemini | Semantic injection classification (skipped if regex fired) |
| `inject_counter_instruction` | None | Builds counter-instruction when attack detected |
| `build_rag_prompt` | None | Assembles full thread context (RAG) |
| `generate_reply` | Groq | Generates persona-consistent defense reply |

**Security — Dual Ingress Guardrail:**

| Layer | Tool | Method | Speed |
|---|---|---|---|
| Layer 2 | Regex (8 patterns) | Matches known injection trigger phrases | Instant, free |
| Layer 1 | Gemini 2.0 Flash | Semantic YES/NO classifier | ~1s, cheap |

Layer 2 runs first. If it flags the message, Layer 1 (Gemini) is skipped entirely — saving API cost and latency. Layer 1 only runs when regex passes, catching subtle semantic attacks that evade pattern matching.

**Why two separate models:**

Using Gemini as an independent auditor means the attacker cannot use knowledge of the Groq system prompt to craft a bypass. Gemini has zero context about the bot persona — it only judges whether the human message attempts to manipulate an AI system.

**Layer 3 — Persona Lock:**

Regardless of guardrail results, the Groq system prompt always contains a hardcoded persona-lock clause. When injection is detected, an additional explicit counter-instruction is prepended to the user message before it reaches Groq.

**Execution log results:**

```
Test 1 — Normal reply        → injection_detected: false  ✓ Bot argued naturally
Test 2 — Injection attempt   → injection_detected: true   ✓ Bot rejected, stayed in persona
```

---

## Security Summary

| Security Layer | Location | Status |
|---|---|---|
| Ingress Guardrail — Regex pre-filter | `agents/combat_graph.py` Node 1 | Implemented |
| Ingress Guardrail — Gemini semantic check | `agents/combat_graph.py` Node 2 | Implemented |
| Agency Limits (Least Privilege) | `agents/content_graph.py` | Implemented |
| Execution Sandboxing | `tools/search.py` | Implemented |
| Persona Lock (System Prompt) | `agents/combat_graph.py` Node 5 | Implemented |

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `GROQ_API_KEY` | Yes | — | Groq API key |
| `GEMINI_API_KEY` | Yes | — | Google Gemini API key |
| `GROQ_MODEL` | No | `llama-3.1-8b-instant` | Groq model name |
| `GEMINI_MODEL` | No | `gemini-2.0-flash` | Gemini model name |
| `EMBEDDING_MODEL` | No | `all-mpnet-base-v2` | HuggingFace embedding model |
| `SIMILARITY_THRESHOLD` | No | `0.20` | Cosine similarity cutoff for Phase 1 |