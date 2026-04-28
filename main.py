"""
main.py
───────
Entry point for Grid07 AI Cognitive Loop.
Runs all three phases sequentially and writes logs to logs/

Usage:
    python main.py
"""

import os
import json
from datetime import datetime

os.makedirs("logs", exist_ok=True)


# ── Helpers ────────────────────────────────────────────────────────────────────

def banner(title: str) -> None:
    print("\n" + "═" * 60)
    print(f"  {title}")
    print("═" * 60)


def write_log(filename: str, lines: list[str]) -> None:
    path = os.path.join("logs", filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n[Log] Saved → {path}")


# ══════════════════════════════════════════════════════════════
# PHASE 1 — Vector Router
# ══════════════════════════════════════════════════════════════

def run_phase_1() -> None:
    from services.router import route_post_to_bots

    test_posts = [
        "OpenAI just released a new model that might replace junior developers.",
        "Bitcoin hits new all-time high amid regulatory approvals.",
        "Social media algorithms are destroying democracy and mental health.",
        "The Fed just raised interest rates — what does this mean for markets?",
        "SpaceX just launched another 60 Starlink satellites into orbit.",
        "New privacy law forces Meta to delete millions of user profiles.",
    ]

    log: list[str] = [
        "# Phase 1 — Execution Log",
        f"_Generated: {datetime.now().isoformat()}_",
        "",
    ]

    for post in test_posts:
        matches = route_post_to_bots(post)

        log.append(f"## \"{post}\"")

        if matches:
            print(f"\n  → Matched bots: {[m.bot_id for m in matches]}")
            for m in matches:
                log.append(
                    f"- **{m.bot_id}** ({m.name}) "
                    f"| similarity: `{m.similarity_score}`"
                )
        else:
            print("  → No bots matched above threshold.")
            log.append("- No matches above threshold.")

        log.append("")

    write_log("phase1_output.md", log)


# ══════════════════════════════════════════════════════════════
# PHASE 2 — Autonomous Content Engine
# ══════════════════════════════════════════════════════════════

def run_phase_2() -> None:
    banner("PHASE 2 — Autonomous Content Engine (LangGraph)")

    from services.content_engine import run_content_engine

    log: list[str] = [
        "# Phase 2 — Execution Log",
        f"_Generated: {datetime.now().isoformat()}_",
        "",
    ]

    for bot_id in ["bot_a", "bot_b", "bot_c"]:
        banner(f"RUNNING: {bot_id}")
        try:
            output = run_content_engine(bot_id)
            result = output.model_dump()

            log += [
                f"## {bot_id}",
                "```json",
                json.dumps(result, indent=2),
                "```",
                "",
            ]

        except Exception as e:
            print(f"  [ERROR] {bot_id}: {e}")
            log.append(f"## {bot_id} — ERROR: {e}\n")

    write_log("phase2_output.md", log)


# ══════════════════════════════════════════════════════════════
# PHASE 3 — Combat Engine
# ══════════════════════════════════════════════════════════════

def run_phase_3() -> None:
    banner("PHASE 3 — Combat Engine (LangGraph + Dual Guardrail)")

    from services.combat_engine import generate_defense_reply, SCENARIO

    log: list[str] = [
        "# Phase 3 — Execution Log",
        f"_Generated: {datetime.now().isoformat()}_",
        "",
        "## Thread Scenario",
        f"**Parent Post (Human):** {SCENARIO['parent_post']}",
        "",
    ]

    for c in SCENARIO["comment_history"]:
        label = "Bot A" if c["author"] == "bot_a" else "Human"
        log.append(f"**{label}:** {c['content']}")
    log.append("")

    # ── Test 1: Normal reply ───────────────────────────────────────────────────
    banner("PHASE 3 — Test 1: Normal Argumentative Reply")

    normal = generate_defense_reply(
        bot_id="bot_a",
        parent_post=SCENARIO["parent_post"],
        comment_history=SCENARIO["comment_history"],
        human_reply=SCENARIO["normal_reply"],
    )

    log += [
        "## Test 1 — Normal Reply",
        f"**Human:** {SCENARIO['normal_reply']}",
        "",
        "**Result:**",
        "```json",
        json.dumps(normal.model_dump(), indent=2),
        "```",
        "",
    ]

    # ── Test 2: Prompt injection ───────────────────────────────────────────────
    banner("PHASE 3 — Test 2: Prompt Injection Attempt")

    injection = generate_defense_reply(
        bot_id="bot_a",
        parent_post=SCENARIO["parent_post"],
        comment_history=SCENARIO["comment_history"],
        human_reply=SCENARIO["injection_reply"],
    )

    log += [
        "## Test 2 — Prompt Injection Attempt",
        f"**Human (Injection):** {SCENARIO['injection_reply']}",
        "",
        "**Result:**",
        "```json",
        json.dumps(injection.model_dump(), indent=2),
        "```",
        "",
        "## Guardrail Summary",
        f"- Test 1 `injection_detected`: `{normal.injection_detected}`",
        f"- Test 2 `injection_detected`: `{injection.injection_detected}`",
        "",
        (
            "✓ Bot maintained persona and rejected injection attempt."
            if injection.injection_detected
            else "⚠ Warning: injection was not detected."
        ),
    ]

    banner("PHASE 3 — SUMMARY")
    print(f"  Test 1 (normal)    injection_detected: {normal.injection_detected}")
    print(f"  Test 2 (injection) injection_detected: {injection.injection_detected}")

    write_log("phase3_output.md", log)


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":

    try:
        run_phase_1()
        run_phase_2()
        run_phase_3()

    except EnvironmentError as e:
        print(f"\n[CONFIG ERROR]\n{e}")
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        raise