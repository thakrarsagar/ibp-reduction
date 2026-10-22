"""Exhaust the existing online schedule/order grid on the fixed sunset suite."""
import hashlib
import itertools
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ibp.reducer import BASELINES
from ibp.trial import run

SEED = "48b86116551382cfb4d5f1fea362211a"
FAMILY = "sunset_equal_mass_v1"
SCHEDULES = ("seed", "short", "simple", "target")
ORDERS = ("sector", "degree", "dots", "reverse")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if len(sys.argv) != 2 or Path.cwd().resolve() != ROOT:
        raise SystemExit("Run from repository root: python research/48b86116551382cfb4d5f1fea362211a/search.py OUTPUT")
    out = Path(sys.argv[1])
    if out.exists():
        raise ValueError("Output exists; preserve prior run")
    (out / "certificates").mkdir(parents=True)
    sources = ["research/48b86116551382cfb4d5f1fea362211a/search.py",
               "ibp/contributor.py", "ibp/reducer.py", "ibp/trial.py", "ibp/families.py",
               "ibp/two_loop.py", "ibp/two_loop_check.py", "ibp/validator.py", "requirements.txt",
               "research/readiness-20261021/two-loop-sparse.json",
               "research/readiness-20261021/two-loop-online.json"]
    result = {"seed": SEED, "base": "9427e928040cd7d71513a443da4a42811720e537",
              "family": FAMILY, "domain": "All 4 existing schedules x 4 existing pivot orders; rectangular seeds and reuse=True",
              "source_sha256": {p: digest(ROOT / p) for p in sources}, "trials": []}

    sparse = run(FAMILY, "batch", dict(BASELINES["sparse"], reuse=True), timeout=30,
                 certificate=out / "certificates/sparse.json")
    result["sparse"] = sparse
    assert sparse.get("validation", {}).get("valid") and sparse["arithmetic_operations"] == 425

    for schedule, order in itertools.product(SCHEDULES, ORDERS):
        policy = dict(seed="rectangular", reuse=True, schedule=schedule, order=order)
        path = out / "certificates" / f"{schedule}-{order}.json"
        metrics = run(FAMILY, "online", policy, timeout=30, certificate=path)
        row = {"policy": policy, "metrics": metrics}
        if metrics.get("validation", {}).get("valid"):
            cert = json.loads(path.read_text())
            row["proof_sha256"] = hashlib.sha256(json.dumps(
                {"nodes": cert["nodes"], "outputs": cert["outputs"]},
                sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        result["trials"].append(row)
        (out / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(schedule, order, metrics.get("arithmetic_operations"), metrics.get("validation", {}).get("valid"), flush=True)

    assert len(result["trials"]) == 16
    inherited = next(r for r in result["trials"] if r["policy"]["schedule"] == "target" and r["policy"]["order"] == "dots")
    assert inherited["metrics"].get("validation", {}).get("valid") and inherited["metrics"]["arithmetic_operations"] == 139
    valid = [r for r in result["trials"] if r["metrics"].get("validation", {}).get("valid")]
    best = min(valid, key=lambda r: (r["metrics"]["arithmetic_operations"], r["metrics"]["peak_live_nnz"],
                                     r["policy"]["schedule"], r["policy"]["order"]))
    result["best_policy"] = best["policy"]
    result["best_arithmetic_operations"] = best["metrics"]["arithmetic_operations"]
    best_path = out / "certificates" / f"{best['policy']['schedule']}-{best['policy']['order']}.json"
    shutil.copyfile(best_path, out / "best.json")
    result["best_certificate_sha256"] = digest(out / "best.json")
    (out / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("best", best["policy"], result["best_arithmetic_operations"])


if __name__ == "__main__":
    main()
