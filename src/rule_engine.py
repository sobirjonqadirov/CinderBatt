# CinderBatt - A lightweight Windows battery management app
# Copyright (C) 2026 Sobirjon Qadirov
# Licensed under GNU GPL v3 — see LICENSE for details

import json
import os
from rules import BlacklistRule, BaseRule
from config import BASE_DIR, RULES_STATE_PATH

class RuleEngine:
    def __init__(self):
        self.rules: list[BaseRule] = [
            BlacklistRule(),
        ]
        self._load_state()

    def _load_state(self):
        try:
            if not os.path.exists(RULES_STATE_PATH):
                return
            with open(RULES_STATE_PATH, "r") as f:
                state = json.load(f)
            for rule in self.rules:
                if rule.name in state:
                    rule.enabled = state[rule.name]
        except Exception as e:
            print(f"[engine] failed to load rule state: {e}")

    def save_state(self):
        try:
            state = {rule.name: rule.enabled for rule in self.rules}
            with open(RULES_STATE_PATH, "w") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"[engine] failed to save rule state: {e}")

    def apply_all(self):
        for rule in self.rules:
            if rule.enabled:
                rule.apply()

    def enforce_all(self):
        for rule in self.rules:
            if rule.enabled:
                rule.enforce()

    def revert_all(self):
        for rule in self.rules:
            if rule.enabled:
                rule.revert()

    def get_rules(self) -> list[BaseRule]:
        return self.rules

    def set_rule_enabled(self, name: str, enabled: bool):
        for rule in self.rules:
            if rule.name == name:
                rule.enabled = enabled
                self.save_state()
                return