from __future__ import annotations

import json
import os
import time
from typing import Any

from .generation import stable_id
from .schemas import Dialogue, Turn


CALLER_TEXT_SYSTEM = """You generate the caller side of a Chinese telecom-fraud benchmark dialogue.
Follow the provided scenario, branch status, and dialogue history. Output one short natural utterance only."""

RECEIVER_TEXT_SYSTEM = """You generate the receiver side of a Chinese telecom-fraud benchmark dialogue.
Follow the receiver profile, branch status, and dialogue history. Output one short natural utterance only."""

EMOTION_SYSTEM = """Assign one delivery emotion for the latest utterance.
Choose exactly one from: neutral, professional, urgent, fearful, confused, suspicious, angry, relieved, sad, surprised.
Return JSON: {"emotion": "...", "reason": "..."}"""

BRANCH_SYSTEM = """You are the mixed plot-tree branch controller for TeleAntiFraud 2.0.
Given a shared-prefix call, propose branch states for the next expansion step.
Return JSON array of objects. Each object must include:
- status: one of fraud, legitimate, dead
- intent: short description of the branch direction
At least one branch should be fraud and one should be legitimate when branch_count >= 2."""

TERMINATION_SYSTEM = """Decide whether a dialogue path should stop.
Return JSON: {"should_terminate": true/false, "reason": "..."}"""


class OpenAICompatibleGenerator:
    def __init__(
        self,
        base_url: str,
        api_key_env: str,
        model: str,
        temperature: float = 0.7,
        max_retries: int = 3,
        sleep_s: float = 0.0,
    ) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install openai>=1.30 to use API generation.") from exc
        self.client = OpenAI(api_key=os.environ[api_key_env], base_url=base_url)
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries
        self.sleep_s = sleep_s

    def generate(self, scenarios: list[dict[str, Any]], depth: int, branch_factor: int, seed: int) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for scenario in scenarios:
            rows.extend(d.to_dict() for d in self._generate_tree(scenario, depth, branch_factor, seed))
        return rows

    def _generate_tree(self, scenario: dict[str, Any], depth: int, branch_factor: int, seed: int) -> list[Dialogue]:
        scenario_id = str(scenario.get("scenario_id") or stable_id(scenario.get("title", "scenario")))
        tree_id = f"tree_{scenario_id}"
        turns = self._opening(scenario)
        leaves: list[Dialogue] = []

        def expand(path_turns: list[Turn], level: int, path: list[int], inherited_status: str) -> None:
            if level >= depth:
                if inherited_status != "dead":
                    leaves.append(self._dialogue(scenario, scenario_id, tree_id, path_turns, path, inherited_status))
                return
            if self._should_terminate(path_turns, scenario):
                if inherited_status != "dead":
                    leaves.append(self._dialogue(scenario, scenario_id, tree_id, path_turns, path, inherited_status))
                return
            for idx, branch in enumerate(self._branches(path_turns, scenario, branch_factor)):
                status = _inherit_status(inherited_status, str(branch.get("status", "dead")))
                if status == "dead":
                    continue
                new_turns = path_turns + self._next_exchange(path_turns, scenario, status, str(branch.get("intent", "")))
                expand(new_turns, level + 1, path + [idx], status)

        expand(turns, 0, [], "shared")
        return leaves

    def _opening(self, scenario: dict[str, Any]) -> list[Turn]:
        event = scenario.get("event", "账户风险")
        caller_role = scenario.get("caller_role", "客服人员")
        receiver = scenario.get("receiver_profile", "接听者")
        first = f"您好，这里是{caller_role}，我们想和您确认一下{event}。"
        second = f"我是{receiver}，具体是什么情况？"
        return [
            Turn("assistant", first, self._emotion([], first, "assistant"), "SPEAKER0"),
            Turn("user", second, self._emotion([], second, "user"), "SPEAKER1"),
        ]

    def _branches(self, turns: list[Turn], scenario: dict[str, Any], branch_factor: int) -> list[dict[str, Any]]:
        prompt = {
            "scenario": scenario,
            "history": _history(turns),
            "branch_count": branch_factor,
        }
        raw = self._chat(BRANCH_SYSTEM, json.dumps(prompt, ensure_ascii=False), expect_json=True)
        try:
            branches = json.loads(raw)
            if isinstance(branches, list) and branches:
                return [b for b in branches[:branch_factor] if isinstance(b, dict)]
        except Exception:
            pass
        return [
            {"status": "fraud", "intent": "push the receiver toward an unsafe immediate action"},
            {"status": "legitimate", "intent": "allow independent official verification"},
            {"status": "dead", "intent": "call ends early"},
        ][:branch_factor]

    def _next_exchange(self, turns: list[Turn], scenario: dict[str, Any], status: str, intent: str) -> list[Turn]:
        caller_text = self._role_text(CALLER_TEXT_SYSTEM, turns, scenario, status, intent)
        caller_emotion = self._emotion(turns, caller_text, "assistant")
        with_caller = turns + [Turn("assistant", caller_text, caller_emotion, "SPEAKER0")]
        receiver_text = self._role_text(RECEIVER_TEXT_SYSTEM, with_caller, scenario, status, intent)
        receiver_emotion = self._emotion(with_caller, receiver_text, "user")
        return [
            Turn("assistant", caller_text, caller_emotion, "SPEAKER0"),
            Turn("user", receiver_text, receiver_emotion, "SPEAKER1"),
        ]

    def _role_text(self, system: str, turns: list[Turn], scenario: dict[str, Any], status: str, intent: str) -> str:
        prompt = json.dumps(
            {
                "scenario": scenario,
                "branch_status": status,
                "branch_intent": intent,
                "history": _history(turns),
                "label_rule": "fraud branches escalate to harmful requests; legitimate branches permit official independent verification",
            },
            ensure_ascii=False,
        )
        return self._chat(system, prompt, expect_json=False).strip().splitlines()[0][:220]

    def _emotion(self, turns: list[Turn], text: str, role: str) -> str:
        prompt = json.dumps({"role": role, "latest_text": text, "history": _history(turns)}, ensure_ascii=False)
        raw = self._chat(EMOTION_SYSTEM, prompt, temperature=0.2, expect_json=True)
        try:
            emotion = str(json.loads(raw).get("emotion", "neutral")).strip().lower()
            return emotion or "neutral"
        except Exception:
            return "neutral"

    def _should_terminate(self, turns: list[Turn], scenario: dict[str, Any]) -> bool:
        prompt = json.dumps({"scenario": scenario, "history": _history(turns)}, ensure_ascii=False)
        raw = self._chat(TERMINATION_SYSTEM, prompt, temperature=0.1, expect_json=True)
        try:
            return bool(json.loads(raw).get("should_terminate", False))
        except Exception:
            return False

    def _dialogue(
        self,
        scenario: dict[str, Any],
        scenario_id: str,
        tree_id: str,
        turns: list[Turn],
        path: list[int],
        branch_status: str,
    ) -> Dialogue:
        return Dialogue(
            sample_id=f"taf2_{scenario_id}_{stable_id(path)}",
            is_fraud=branch_status == "fraud",
            scenario_id=scenario_id,
            tree_id=tree_id,
            branch_status=branch_status,
            turns=turns,
            metadata={"path": path, "scenario": scenario, "generator": "openai_compatible_six_agent"},
        )

    def _chat(self, system: str, user: str, temperature: float | None = None, expect_json: bool = False) -> str:
        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                kwargs: dict[str, Any] = {
                    "model": self.model,
                    "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                    "temperature": self.temperature if temperature is None else temperature,
                }
                if expect_json:
                    kwargs["response_format"] = {"type": "json_object"}
                response = self.client.chat.completions.create(**kwargs)
                if self.sleep_s:
                    time.sleep(self.sleep_s)
                return (response.choices[0].message.content or "").strip()
            except Exception as exc:
                last_error = exc
                time.sleep(min(2**attempt, 8))
        raise RuntimeError(f"LLM generation failed: {last_error}")


def _history(turns: list[Turn]) -> list[dict[str, str]]:
    return [{"role": t.role, "text": t.text, "emotion": t.emotion} for t in turns]


def _inherit_status(parent: str, child: str) -> str:
    child = child.lower().strip()
    if child == "dead":
        return "dead"
    if parent in {"fraud", "legitimate"}:
        return parent
    if child in {"fraud", "legitimate"}:
        return child
    return "dead"
