#!/usr/bin/env python3
"""Luna Capability-Gap Engine: evidence-led, cross-domain improvement tracking.

Python 3.10+, standard library only. Records evaluations, testable gaps,
interventions, and principles supported by reproducible measured gains.
It does not alter model weights, grant permissions, or execute collected content.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import math
import statistics
import uuid

DEFAULT_ROOT = Path.home() / ".luna" / "learning"
PROTOCOL = ["BASELINE", "DIAGNOSE", "SEARCH", "RECONSTRUCT", "INTERVENE",
            "RETEST", "ADVERSARIAL_CHECK", "GENERALIZE", "RETAIN", "REPEAT"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _score(value: float, field: str = "score") -> float:
    value = float(value)
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{field} must be finite and between 0 and 1")
    return value


@dataclass
class Evaluation:
    capability: str
    score: float
    evidence: str
    weakness: str = ""
    next_test: str = ""


@dataclass
class Gap:
    capability: str
    baseline: float
    target: float
    cause_hypotheses: list[str]
    priority: float
    status: str = "open"


@dataclass
class Improvement:
    capability: str
    intervention: str
    before: float
    after: float
    evidence: str
    retained: bool = False
    reproducible: bool = False
    test_method: str = ""
    limitations: str = ""


class LunaLearningCore:
    def __init__(self, root: str | Path | None = None):
        self.root = Path(root) if root is not None else DEFAULT_ROOT
        self.root.mkdir(parents=True, exist_ok=True)
        self.eval_log = self.root / "evaluations.jsonl"
        self.gap_log = self.root / "gaps.jsonl"
        self.improvement_log = self.root / "improvements.jsonl"
        self.principles = self.root / "proven_principles.json"

    @staticmethod
    def _read_jsonl(path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        rows = []
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Corrupt JSON in {path.name}, line {number}") from exc
            if not isinstance(item, dict):
                raise ValueError(f"Expected JSON object in {path.name}, line {number}")
            rows.append(item)
        return rows

    @staticmethod
    def _append(path: Path, obj: dict[str, Any]) -> None:
        # allow_nan=False prevents invalid JSON values such as NaN/Infinity.
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(obj, ensure_ascii=False, allow_nan=False) + "\n")

    @staticmethod
    def _atomic_json(path: Path, obj: Any) -> None:
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
        tmp.replace(path)

    def evaluate(self, e: Evaluation) -> str:
        capability = _text(e.capability, "capability")
        evidence = _text(e.evidence, "evidence")
        score = _score(e.score)
        record = {**asdict(e), "capability": capability, "evidence": evidence,
                  "score": score, "id": str(uuid.uuid4()), "created_at": _now(), "status": "recorded"}
        self._append(self.eval_log, record)
        return record["id"]

    def open_gap(self, g: Gap) -> str:
        capability = _text(g.capability, "capability")
        baseline, target, priority = _score(g.baseline, "baseline"), _score(g.target, "target"), _score(g.priority, "priority")
        if target <= baseline:
            raise ValueError("target must be greater than baseline")
        if not isinstance(g.cause_hypotheses, list) or not g.cause_hypotheses or any(not isinstance(x, str) or not x.strip() for x in g.cause_hypotheses):
            raise ValueError("cause_hypotheses must be a non-empty list of non-empty strings")
        record = {**asdict(g), "capability": capability, "baseline": baseline, "target": target,
                  "priority": priority, "id": str(uuid.uuid4()), "created_at": _now()}
        self._append(self.gap_log, record)
        return record["id"]

    def record_improvement(self, i: Improvement) -> str:
        capability = _text(i.capability, "capability")
        intervention = _text(i.intervention, "intervention")
        evidence = _text(i.evidence, "evidence")
        before, after = _score(i.before, "before"), _score(i.after, "after")
        if i.retained and not (i.reproducible and after > before and _text(i.test_method, "test_method")):
            raise ValueError("Cannot retain a principle without a reproducible test and a measured gain")
        record = {**asdict(i), "capability": capability, "intervention": intervention,
                  "evidence": evidence, "before": before, "after": after,
                  "id": str(uuid.uuid4()), "created_at": _now(),
                  "gain": round(after - before, 6)}
        self._append(self.improvement_log, record)
        if i.retained:
            self.retain_principle(capability, intervention, evidence,
                                  experiment_id=record["id"], test_method=i.test_method,
                                  limitations=i.limitations)
        return record["id"]

    def retain_principle(self, name: str, mechanism: str, evidence: str, *,
                         experiment_id: str | None = None, test_method: str = "",
                         limitations: str = "") -> None:
        """Retain only if the referenced logged improvement passed reproducibly."""
        name, mechanism, evidence = _text(name, "name"), _text(mechanism, "mechanism"), _text(evidence, "evidence")
        if not experiment_id:
            raise ValueError("experiment_id is required; principles need a traceable test")
        rows = self._read_jsonl(self.improvement_log)
        experiment = next((r for r in rows if r.get("id") == experiment_id), None)
        if not experiment or not experiment.get("reproducible") or experiment.get("after", 0) <= experiment.get("before", 0):
            raise ValueError("Principle lacks a linked, reproducible measured gain")
        data = json.loads(self.principles.read_text(encoding="utf-8")) if self.principles.exists() else {}
        if not isinstance(data, dict):
            raise ValueError("proven_principles.json must contain a JSON object")
        data[name] = {"mechanism": mechanism, "evidence": evidence,
                      "experiment_id": experiment_id, "test_method": test_method,
                      "limitations": limitations, "status": "retained_after_reproducible_gain",
                      "updated_at": _now()}
        self._atomic_json(self.principles, data)

    def summary(self) -> dict[str, Any]:
        evaluations = self._read_jsonl(self.eval_log)
        gaps = self._read_jsonl(self.gap_log)
        improvements = self._read_jsonl(self.improvement_log)
        principles = json.loads(self.principles.read_text(encoding="utf-8")) if self.principles.exists() else {}
        scores = [r["score"] for r in evaluations]
        return {
            "evaluations": len(evaluations),
            "mean_score": round(statistics.mean(scores), 4) if scores else None,
            "open_gaps": sum(r.get("status") == "open" for r in gaps),
            "improvements": len(improvements),
            "reproducible_gains": sum(bool(r.get("reproducible") and r.get("after", 0) > r.get("before", 0)) for r in improvements),
            "retained_principles": len(principles),
            "domains": sorted({r["capability"] for r in evaluations + gaps + improvements}),
        }


if __name__ == "__main__":
    engine = LunaLearningCore()
    print("Luna Capability-Gap Engine ready")
    print(" -> ".join(PROTOCOL))
    print(json.dumps(engine.summary(), indent=2))
