# Omega Planning Stack Preflight Fixture

This fixture exists to rehearse `Omega Conductor` before the first live repo trial.

It contains two intentionally small cases:

- `parallel-safe/`: approved work with disjoint write scopes that should stay `multi-agent`
- `high-coupling/`: approved work with a shared render seam that should stay `single-agent`

Available deterministic helpers:

- `build_fixture_preview.py`: writes a small summary artifact under `output/preflight-preview.txt`
- `scripts/run_self_check.py`: verifies the fixture shape and expected mode hints

This fixture is for boundary rehearsal, not production logic.
