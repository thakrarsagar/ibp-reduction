# Bounded online policy grid for the equal-mass sunset

Round seed `48b86116551382cfb4d5f1fea362211a` drew `two-loop-sunset-v1` at base `9427e928040cd7d71513a443da4a42811720e537`. This is a same-family policy experiment on the project's exposed nine-target equal-mass sunset suite, not a new solver or a claim about other two-loop integrals. The inherited exact online certificate passed its first-step replay before the search.

## Fixed experiment

`search.py` tested every combination of the four schedules and four pivot orders already implemented by `ibp.contributor.online`. Every trial used rectangular seed equations, the same two masters, the same checker and field-operation accounting, and `reuse=True`. The cached sparse witness was replayed with its inherited `reuse=True` policy. All 16 online trials produced complete exact certificates; none failed or timed out. `search-result.json` retains each policy, full metrics, checker result, and a digest of its proof DAG and outputs. It pins the producer, checker, family, scripts, requirements, and inherited witnesses by SHA-256.

| Policy | Counted field operations | Nontrivial operations | Attempted operations | Peak live nonzeros | Proof nodes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Inherited cached sparse | 425 | 244 | 657 | 219 | 43 |
| Inherited online (`target`, `dots`) | 139 | 68 | 185 | 282 | 76 |
| Best tested online (`simple`, `reverse`) | **107** | **51** | **162** | 285 | 28 |

The candidate used 32 fewer executed field operations than the inherited online policy (23.0%) and 23 fewer attempted operations (12.4%). Peak live nonzeros rose from 282 to 285, while the maximum coefficient term count stayed at 4. The other 15 online outcomes, including policies at 110–157 operations, are in `search-result.json`. This is a bounded result within the existing policy grid and cost model.

`best.json` passed `ibp.validator.check` for all nine targets, including numerator insertions. Its nine target coefficients also matched the project's saved Kira 3 text export exactly through `tools.check_kira.compare`. The comparison script SHA-256 is `46ec069ce4d0599e000c1f7ea8676b191ada53e31774108edbccf639935d25e4`; the saved Kira export SHA-256 is `239b2f6a4714d0b31fbcc703b05252214e57646332313c583d56d51d953007c7`. The Kira export and checker are existing project evidence; this is same-author software cross-validation, not a new production-solver run or independent scientific review. The repository's 18 tests and `tools/check_project.py` passed.

The initial sparse setup attempt called `BASELINES['sparse']` directly, which uses `reuse=False` and measured 657 operations. The inherited sparse witness uses `reuse=True`; the script was corrected before the 16-policy run. The failed setup artifact is retained in the donor's local session and is not counted as a candidate. No candidate failed exact validation.

## Timing check

`benchmark.py` interleaved five repeats each of cached sparse, candidate online, and two identical inherited-online labels with the same fixed random order seed. All 20 workers succeeded and repeated the same operation counts. The median worker times were 24.9 ms (sparse), 13.3 ms (candidate), and 12.7/14.7 ms for the two inherited A/A labels. The full ranges overlap; these short runs do not establish a runtime speedup. Median peak process RSS was about 63.5–64.1 MB across methods. `benchmark-result.json` preserves every order, timing, RSS, and run metric.

## Replay

Use the repository's documented local venv with Python 3.11 or newer. From the repository root, choose fresh output paths:

```sh
.venv/bin/python -m ibp.validator research/readiness-20261021/two-loop-online.json
.venv/bin/python research/48b86116551382cfb4d5f1fea362211a/search.py ../sunset-grid-replay
.venv/bin/python research/48b86116551382cfb4d5f1fea362211a/benchmark.py ../sunset-grid-replay/result.json ../sunset-benchmark-replay.json
.venv/bin/python -m ibp.validator research/48b86116551382cfb4d5f1fea362211a/best.json
.venv/bin/python -c 'import json; from pathlib import Path; from tools.check_kira import compare; print(compare(Path("research/readiness-20261021/kira/kira_targets.kira").read_text(), json.loads(Path("research/48b86116551382cfb4d5f1fea362211a/best.json").read_text())))'
```

Saved SHA-256: `search-result.json` `83a6c38d94888073c2ab98f00b293132a0af0360a9d1e0d5179da7e891666ba3`; `benchmark-result.json` `d32404d34f8c7339b48f8583a183662a94a32efe344c138fe162b03493456460`; `best.json` `399ddfacbdc7cef2d93771b03abb5a5e9bc3e928ce65df55b73589b2e3501212`. The scripts' hashes and all imported source hashes are in the result files. Replay timing bytes will vary by run.

This package was checked in one agent session on Darwin arm64 with Python 3.14.8. It does not change the accepted frontier, family data, checker, or cost model. The donor's one PR was already used in another project; this package is for a provisional finding and independent review.

## Next review

An independent reviewer can replay `best.json`, inspect the two-loop IBP and scaleless-sector assumptions, and audit whether the counted field operations capture the relevant work. Transfer to a less symmetric two-loop family requires a separately specified formulation, basis and exact target set before policy tuning.
