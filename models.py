from enum import IntEnum
from dataclasses import dataclass

class PlayerFaction(IntEnum):
    UNDECIDED = 0
    NAVI = 1
    CORP = 2

class TerritoryFaction(IntEnum):
    NAVI = 1
    CORP = 2

class BooleanFlag(IntEnum):
    NO = 0
    YES = 1

class UnlockState(IntEnum):
    LOCKED = 0
    UNLOCKED = 2  # Note: Skips 1 as per game design

@dataclass
class SaveGameData:
    # Metagame
    navi_cost_reduction: int = 0
    corp_cost_reduction: int = 0
    player_faction: PlayerFaction = PlayerFaction.UNDECIDED

    # Player EPs
    eps: int = 0
    new_eps: int = 0
    new_psp_eps: int = 0
    eps_modifier: int = 0

    # Territory
    faction: TerritoryFaction = TerritoryFaction.NAVI
    home_base: BooleanFlag = BooleanFlag.NO
    base_units: int = 0
    secondary_base: BooleanFlag = BooleanFlag.NO
    defense_flags: BooleanFlag = BooleanFlag.YES
    active: BooleanFlag = BooleanFlag.NO
    activated_once: BooleanFlag = BooleanFlag.NO

    # Free Units
    troops: int = 0
    ground: int = 0
    air: int = 0

    # Possessions
    nb_in_stack: int = 0
    nb_in_clip: int = 0

    # Base Info
    side: int = 4
    pawn: int = 2
    is_female: BooleanFlag = BooleanFlag.NO
    face: int = 3
    entity_scanning_enabled: BooleanFlag = BooleanFlag.YES
    total_ep: int = 0

    # Time Info
    game_time: int = 0
    played_time: int = 0
    env_time: int = 0

    # XP Info
    current_xp: int = 0
    current_level: int = 0

    # Options
    rumble_enabled: BooleanFlag = BooleanFlag.NO
    first_person_mode: BooleanFlag = BooleanFlag.NO

    # Pandorapedia
    known_status: UnlockState = UnlockState.LOCKED

    # Pin Status
    pin_unlocked: BooleanFlag = BooleanFlag.NO

    # Achievement
    achievement_counter: int = 0

    # Skill Status
    skill_locked: UnlockState = UnlockState.LOCKED

    # Recovery
    recovery_bits: int = 0