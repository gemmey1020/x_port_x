# High-coupling Approved Plan

- Objective: adjust the shared HUD shell and the dependent skill-card renderer in one render seam.
- Critic verdict: `findings-only`
- Shared write scope: `high-coupling/render/render_shell.py`
- Dependent write scope: `high-coupling/render/render_cards.py`
- Additional consumer surface: `high-coupling/consumers/skill_cards.md`
- Expected conductor mode: `single-agent`
- Proof handoff focus: verify the joined render seam and the dependent output copy together.
