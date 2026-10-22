"""Interleave five repeated sunset timings with an online A/A control."""
import hashlib
import json
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ibp.reducer import BASELINES
from ibp.trial import run

SEED = "48b86116551382cfb4d5f1fea362211a"
FAMILY = "sunset_equal_mass_v1"


def main():
    if len(sys.argv) != 3 or Path.cwd().resolve() != ROOT:
        raise SystemExit("Run from repository root: python research/48b86116551382cfb4d5f1fea362211a/benchmark.py SEARCH_RESULT OUTPUT")
    source, output = map(Path, sys.argv[1:])
    if output.exists():
        raise ValueError("Output exists; preserve prior run")
    search = json.loads(source.read_text())
    inherited = json.loads((ROOT / "research/readiness-20261021/two-loop-online.json").read_text())["policy"]
    methods = {"cached-sparse": ("batch", dict(BASELINES["sparse"], reuse=True)),
               "inherited-online-a": ("online", inherited),
               "candidate-online": ("online", search["best_policy"]),
               "inherited-online-b": ("online", inherited)}
    rng = random.Random(int(SEED, 16))
    result = {"seed": SEED, "base": search["base"], "family": FAMILY, "repeats": 5,
              "source_sha256": {"search-result": hashlib.sha256(source.read_bytes()).hexdigest(),
                                "research/48b86116551382cfb4d5f1fea362211a/benchmark.py": hashlib.sha256((ROOT / "research/48b86116551382cfb4d5f1fea362211a/benchmark.py").read_bytes()).hexdigest(),
                                "ibp/trial.py": hashlib.sha256((ROOT / "ibp/trial.py").read_bytes()).hexdigest()},
              "methods": methods, "runs": []}
    for rep in range(5):
        order = list(methods)
        rng.shuffle(order)
        for name in order:
            engine, policy = methods[name]
            metrics = run(FAMILY, engine, policy, timeout=30)
            result["runs"].append({"repeat": rep, "method": name, "metrics": metrics})
            output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
            print(rep, name, metrics.get("arithmetic_operations"), metrics.get("worker_seconds"), flush=True)
    assert len(result["runs"]) == 20 and all(r["metrics"].get("success") for r in result["runs"])
    assert all(r["metrics"]["arithmetic_operations"] == (107 if r["method"] == "candidate-online" else 425 if r["method"] == "cached-sparse" else 139) for r in result["runs"])
    result["summary"] = {}
    for name in methods:
        rows = [r["metrics"] for r in result["runs"] if r["method"] == name]
        result["summary"][name] = {field: {"median": statistics.median(r[field] for r in rows),
                                            "range": [min(r[field] for r in rows), max(r[field] for r in rows)]}
                                   for field in ("worker_seconds", "cpu_seconds", "subprocess_seconds", "peak_rss_bytes")}
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("complete")


if __name__ == "__main__":
    main()
