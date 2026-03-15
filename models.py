import random
from dataclasses import dataclass, field
from typing import List, Optional
from .config import Type, get_type_multiplier

@dataclass
class Skill:
    name: str
    type: Type
    power: int
    pp: int
    max_pp: int
    accuracy: int  # 0-100

    def use(self) -> bool:
        if self.pp <= 0:
            return False
        self.pp -= 1
        return True

    def restore_pp(self, amount: int):
        self.pp = min(self.max_pp, self.pp + amount)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type.value,
            "power": self.power,
            "pp": self.pp,
            "max_pp": self.max_pp,
            "accuracy": self.accuracy
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data["name"],
            type=Type(data["type"]),
            power=data["power"],
            pp=data["pp"],
            max_pp=data["max_pp"],
            accuracy=data["accuracy"]
        )

@dataclass
class Pokemon:
    id: str                # 图鉴ID，如 "001"
    name: str
    types: List[Type]
    base_hp: int
    base_attack: int
    base_defense: int
    base_sp_attack: int
    base_sp_defense: int
    base_speed: int
    level: int = 1
    current_hp: int = field(init=False)
    skills: List[Skill] = field(default_factory=list)
    exp: int = 0
    ev_hp: int = 0
    ev_attack: int = 0
    ev_defense: int = 0
    ev_sp_attack: int = 0
    ev_sp_defense: int = 0
    ev_speed: int = 0
    iv_hp: int = field(default_factory=lambda: random.randint(0, 31))
    iv_attack: int = field(default_factory=lambda: random.randint(0, 31))
    iv_defense: int = field(default_factory=lambda: random.randint(0, 31))
    iv_sp_attack: int = field(default_factory=lambda: random.randint(0, 31))
    iv_sp_defense: int = field(default_factory=lambda: random.randint(0, 31))
    iv_speed: int = field(default_factory=lambda: random.randint(0, 31))
    nickname: Optional[str] = None

    def save_state(self) -> dict:
        """保存当前HP和每个技能的PP"""
        return {
            "current_hp": self.current_hp,
            "skills_pp": [s.pp for s in self.skills]
        }

    def restore_state(self, state: dict):
        """恢复到之前保存的状态"""
        self.current_hp = state["current_hp"]
        for i, pp in enumerate(state["skills_pp"]):
            if i < len(self.skills):
                self.skills[i].pp = pp
    def __post_init__(self):
        self.current_hp = self.max_hp

    @property
    def max_hp(self) -> int:
        return int(((2 * self.base_hp + self.iv_hp + self.ev_hp // 4) * self.level) / 100) + self.level + 10

    @property
    def attack(self) -> int:
        return int(((2 * self.base_attack + self.iv_attack + self.ev_attack // 4) * self.level) / 100) + 5

    @property
    def defense(self) -> int:
        return int(((2 * self.base_defense + self.iv_defense + self.ev_defense // 4) * self.level) / 100) + 5

    @property
    def sp_attack(self) -> int:
        return int(((2 * self.base_sp_attack + self.iv_sp_attack + self.ev_sp_attack // 4) * self.level) / 100) + 5

    @property
    def sp_defense(self) -> int:
        return int(((2 * self.base_sp_defense + self.iv_sp_defense + self.ev_sp_defense // 4) * self.level) / 100) + 5

    @property
    def speed(self) -> int:
        return int(((2 * self.base_speed + self.iv_speed + self.ev_speed // 4) * self.level) / 100) + 5

    def is_fainted(self) -> bool:
        return self.current_hp <= 0

    def take_damage(self, damage: int):
        self.current_hp = max(0, self.current_hp - damage)

    def heal(self, amount: int):
        self.current_hp = min(self.max_hp, self.current_hp + amount)

    def get_skill(self, index: int) -> Optional[Skill]:
        if 0 <= index < len(self.skills):
            return self.skills[index]
        return None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "types": [t.value for t in self.types],
            "base_hp": self.base_hp,
            "base_attack": self.base_attack,
            "base_defense": self.base_defense,
            "base_sp_attack": self.base_sp_attack,
            "base_sp_defense": self.base_sp_defense,
            "base_speed": self.base_speed,
            "level": self.level,
            "current_hp": self.current_hp,
            "skills": [s.to_dict() for s in self.skills],
            "exp": self.exp,
            "ev_hp": self.ev_hp,
            "ev_attack": self.ev_attack,
            "ev_defense": self.ev_defense,
            "ev_sp_attack": self.ev_sp_attack,
            "ev_sp_defense": self.ev_sp_defense,
            "ev_speed": self.ev_speed,
            "iv_hp": self.iv_hp,
            "iv_attack": self.iv_attack,
            "iv_defense": self.iv_defense,
            "iv_sp_attack": self.iv_sp_attack,
            "iv_sp_defense": self.iv_sp_defense,
            "iv_speed": self.iv_speed,
            "nickname": self.nickname,
        }

    @classmethod
    def from_dict(cls, data: dict):
        skills = [Skill.from_dict(s) for s in data["skills"]]
        types = [Type(t) for t in data["types"]]
        pokemon = cls(
            id=data["id"],
            name=data["name"],
            types=types,
            base_hp=data["base_hp"],
            base_attack=data["base_attack"],
            base_defense=data["base_defense"],
            base_sp_attack=data["base_sp_attack"],
            base_sp_defense=data["base_sp_defense"],
            base_speed=data["base_speed"],
            level=data["level"],
            skills=skills,
            exp=data["exp"],
            ev_hp=data["ev_hp"],
            ev_attack=data["ev_attack"],
            ev_defense=data["ev_defense"],
            ev_sp_attack=data["ev_sp_attack"],
            ev_sp_defense=data["ev_sp_defense"],
            ev_speed=data["ev_speed"],
            iv_hp=data["iv_hp"],
            iv_attack=data["iv_attack"],
            iv_defense=data["iv_defense"],
            iv_sp_attack=data["iv_sp_attack"],
            iv_sp_defense=data["iv_sp_defense"],
            iv_speed=data["iv_speed"],
            nickname=data.get("nickname")
        )
        pokemon.current_hp = data["current_hp"]
        return pokemon

@dataclass
class Trainer:
    user_id: str
    name: str
    party: List[Pokemon] = field(default_factory=list)  # 最多6只
    pc: List[Pokemon] = field(default_factory=list)     # 存放更多精灵
    active_pokemon_index: int = 0                         # 当前出战精灵在party中的索引
    first_pokemon_index: int = 0
    def get_active_pokemon(self) -> Optional[Pokemon]:
        if 0 <= self.active_pokemon_index < len(self.party):
            return self.party[self.active_pokemon_index]
        return None

    def switch_pokemon(self, index: int) -> bool:
        if 0 <= index < len(self.party) and not self.party[index].is_fainted():
            self.active_pokemon_index = index
            return True
        return False

    def can_battle(self) -> bool:
        return any(not p.is_fainted() for p in self.party)

    def add_pokemon(self, pokemon: Pokemon) -> bool:
        if len(self.party) < 6:
            self.party.append(pokemon)
            return True
        else:
            self.pc.append(pokemon)
            return False

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "party": [p.to_dict() for p in self.party],
            "pc": [p.to_dict() for p in self.pc],
            "active_pokemon_index": self.active_pokemon_index,
            "first_pokemon_index": self.first_pokemon_index,
        }

    @classmethod
    def from_dict(cls, data: dict):
        party = [Pokemon.from_dict(p) for p in data["party"]]
        pc = [Pokemon.from_dict(p) for p in data["pc"]]
        return cls(
            user_id=data["user_id"],
            name=data["name"],
            party=party,
            pc=pc,
            active_pokemon_index=data["active_pokemon_index"],
            first_pokemon_index = data.get("first_pokemon_index", 0),
        )