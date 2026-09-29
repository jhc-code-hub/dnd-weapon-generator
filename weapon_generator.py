#!/usr/bin/env python3
"""Generate a rollable D&D weapon attack line from user prompts."""

import re
import sys


def ask(prompt):
    """Prompt for non-empty input."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  Please enter a value.")


def ask_int(prompt, minimum=None):
    """Prompt for an integer, optionally enforcing a minimum."""
    while True:
        raw = ask(prompt)
        try:
            value = int(raw)
        except ValueError:
            print("  Please enter a whole number (e.g. 5, 0, -1).")
            continue
        if minimum is not None and value < minimum:
            print(f"  Value must be at least {minimum}.")
            continue
        return value


def ask_attack_type():
    """Return 'melee', 'ranged', or 'both'."""
    options = {
        "m": "melee", "melee": "melee",
        "r": "ranged", "ranged": "ranged",
        "b": "both", "both": "both",
    }
    while True:
        raw = ask("Is the weapon (M)elee, (R)anged, or (B)oth? ").lower()
        if raw in options:
            return options[raw]
        print("  Please enter M, R, or B.")


def ask_reach():
    return ask_int("Reach in feet (e.g. 5, 10): ", minimum=1)


def ask_range():
    """Range must always have a minimum and a maximum."""
    normal = ask_int("Normal (minimum) range in feet (e.g. 30): ", minimum=1)
    while True:
        long_range = ask_int("Long (maximum) range in feet (e.g. 120): ", minimum=1)
        if long_range > normal:
            return normal, long_range
        print(f"  Maximum range must be greater than the minimum ({normal}).")


def ask_dice():
    """Ask for dice in NdS format; return (count, sides)."""
    while True:
        raw = ask("Weapon damage dice (D&D notation, e.g. 1d8, 2d6): ").lower().replace(" ", "")
        match = re.fullmatch(r"(\d*)d(\d+)", raw)
        if match:
            count = int(match.group(1)) if match.group(1) else 1
            sides = int(match.group(2))
            if count >= 1 and sides >= 2:
                return count, sides
        print("  Please use the format NdS, such as 1d8 or 2d6.")


def build_line(name, attack_type, reach, rng, dice, hit_mod, str_mod, damage_type):
    count, sides = dice
    hit_str = f"{hit_mod:+d}"  # always shows a sign, e.g. +5, +0, -1
    dice_str = f"{count}d{sides}"

    # Average damage (rounded down), as in the D&D stat block convention
    average = (count * (sides + 1)) // 2 + str_mod
    average = max(average, 1)

    if str_mod > 0:
        display_expr = f"{dice_str} + {str_mod}"
        notation = f"{dice_str}+{str_mod}"
    elif str_mod < 0:
        display_expr = f"{dice_str} - {abs(str_mod)}"
        notation = f"{dice_str}-{abs(str_mod)}"
    else:
        display_expr = dice_str
        notation = dice_str

    if attack_type == "melee":
        attack_label = "Melee Attack Roll"
        distance = f"reach {reach} ft."
    elif attack_type == "ranged":
        attack_label = "Ranged Attack Roll"
        distance = f"range {rng[0]}/{rng[1]} ft."
    else:
        attack_label = "Melee or Ranged Attack Roll"
        distance = f"reach {reach} ft. or range {rng[0]}/{rng[1]} ft."

    damage_type_cap = damage_type.strip().capitalize()

    return (
        f"{name}. {attack_label}: "
        f'[rollable]{hit_str};{{"diceNotation":"1d20{hit_str}", '
        f'"rollType":"to hit", "rollAction":"{name}"}}[/rollable], '
        f"{distance} "
        f"Hit: {average} "
        f'[rollable]({display_expr});{{"diceNotation":"{notation}", '
        f'"rollType":"damage", "rollAction":"{name}", '
        f'"rollDamageType":"{damage_type_cap}"}}[/rollable] '
        f"{damage_type_cap} damage."
    )


def main():
    print("=== D&D Weapon Attack Generator ===\n")

    name = ask("Weapon name: ")
    attack_type = ask_attack_type()

    reach = None
    rng = None
    if attack_type in ("melee", "both"):
        reach = ask_reach()
    if attack_type in ("ranged", "both"):
        rng = ask_range()

    dice = ask_dice()
    hit_mod = ask_int("Hit modifier to add to the attack roll (e.g. 5, 0, -1): ")
    str_mod = ask_int("Strength modifier to add to damage (e.g. 3, 0, -1): ")
    damage_type = ask("Damage type (e.g. piercing, slashing, bludgeoning): ")

    line = build_line(name, attack_type, reach, rng, dice, hit_mod, str_mod, damage_type)

    print("\n--- Result ---\n")
    print(line)
    print("\nNOTE: Please ensure to Bold/Italicize the weapon name as well as Italicze the damage type\n")
    print()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
        sys.exit(1)
