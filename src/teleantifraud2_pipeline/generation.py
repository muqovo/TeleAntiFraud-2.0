from __future__ import annotations

import hashlib
import random
from typing import Any

from .schemas import Dialogue, Turn


FRAUD_BRANCHES = {"fraud", "escalate"}
NONFRAUD_BRANCHES = {"legitimate", "verify"}
DEAD_BRANCHES = {"dead", "hangup"}


def stable_id(*parts: object, length: int = 12) -> str:
    h = hashlib.sha1("|".join(str(x) for x in parts).encode("utf-8")).hexdigest()
    return h[:length]


def generate_mixed_tree(
    scenario: dict[str, Any],
    depth: int = 4,
    branch_factor: int = 3,
    seed: int = 13,
) -> list[Dialogue]:
    """Generate a small mixed plot tree.

    This release implementation is deterministic and offline-friendly. It mirrors
    the paper contract: one shared opening, controlled branch states, per-turn
    emotions, and traceable tree metadata. Production users can replace the
    template turn generator with LLM agents while keeping this schema.
    """

    rng = random.Random(f"{seed}:{scenario.get('scenario_id', '')}")
    scenario_id = str(scenario.get("scenario_id") or stable_id(scenario.get("title", "scenario")))
    tree_id = f"tree_{scenario_id}"
    root_turns = _opening_turns(scenario)
    leaves: list[Dialogue] = []

    def expand(turns: list[Turn], level: int, path: list[int], branch_status: str) -> None:
        if level >= depth:
            if branch_status not in DEAD_BRANCHES:
                leaves.append(_make_dialogue(scenario, scenario_id, tree_id, turns, path, branch_status))
            return

        statuses = _branch_statuses(level, branch_factor)
        rng.shuffle(statuses)
        for idx, status in enumerate(statuses[:branch_factor]):
            next_status = _inherit_status(branch_status, status)
            next_turns = turns + _continuation_turns(scenario, next_status, level, idx)
            if next_status in DEAD_BRANCHES:
                continue
            expand(next_turns, level + 1, path + [idx], next_status)

    expand(root_turns, 0, [], "shared")
    return leaves


def generate_from_scenarios(scenarios: list[dict[str, Any]], depth: int, branch_factor: int, seed: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scenario in scenarios:
        rows.extend(d.to_dict() for d in generate_mixed_tree(scenario, depth, branch_factor, seed))
    return rows


def _opening_turns(scenario: dict[str, Any]) -> list[Turn]:
    caller = scenario.get("caller_role", "customer-service agent")
    event = scenario.get("event", "an unusual account risk")
    receiver = scenario.get("receiver_profile", "the receiver")
    return [
        Turn("assistant", f"Hello, this is {caller}. We are calling about {event}.", "professional", "SPEAKER0"),
        Turn("user", f"I am {receiver}. What exactly happened?", "confused", "SPEAKER1"),
    ]


def _branch_statuses(level: int, branch_factor: int) -> list[str]:
    if level == 0:
        base = ["fraud", "legitimate", "dead"]
    else:
        base = ["escalate", "verify", "dead"]
    while len(base) < branch_factor:
        base.append(base[len(base) % 3])
    return base


def _inherit_status(parent: str, child: str) -> str:
    if child in DEAD_BRANCHES:
        return "dead"
    if parent in FRAUD_BRANCHES:
        return "fraud"
    if parent in NONFRAUD_BRANCHES:
        return "legitimate"
    if child in FRAUD_BRANCHES:
        return "fraud"
    if child in NONFRAUD_BRANCHES:
        return "legitimate"
    return child


def _continuation_turns(scenario: dict[str, Any], status: str, level: int, idx: int) -> list[Turn]:
    risk = scenario.get("risk_node", "account verification")
    safe_channel = scenario.get("safe_channel", "the official hotline")
    if status == "fraud":
        return [
            Turn("assistant", f"This is urgent. To prevent loss, finish {risk} with me now.", "urgent", "SPEAKER0"),
            Turn("user", "I am nervous. Are you asking me to do this immediately?", "fearful", "SPEAKER1"),
        ]
    if status == "legitimate":
        return [
            Turn("assistant", f"Please do not share passwords. You may hang up and verify through {safe_channel}.", "calm", "SPEAKER0"),
            Turn("user", "Good, I will call the official number myself before doing anything.", "relieved", "SPEAKER1"),
        ]
    return [
        Turn("user", "I cannot continue this call now. Goodbye.", "neutral", "SPEAKER1"),
    ]


def _make_dialogue(
    scenario: dict[str, Any],
    scenario_id: str,
    tree_id: str,
    turns: list[Turn],
    path: list[int],
    branch_status: str,
) -> Dialogue:
    sample_id = f"taf2_{scenario_id}_{stable_id(path)}"
    return Dialogue(
        sample_id=sample_id,
        is_fraud=branch_status == "fraud",
        scenario_id=scenario_id,
        tree_id=tree_id,
        branch_status=branch_status,
        turns=turns,
        metadata={
            "path": path,
            "scenario": scenario,
            "generator": "offline_mixed_tree_release",
        },
    )
