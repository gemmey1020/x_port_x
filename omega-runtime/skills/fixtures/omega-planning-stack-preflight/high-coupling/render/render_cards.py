from render_shell import SHELL_TEMPLATE


def build_card_slots() -> list[str]:
    return [f"{SHELL_TEMPLATE['hero']}-skill-card", "proof-lock-card"]
