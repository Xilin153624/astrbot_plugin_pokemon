import random
from typing import Optional
from .models import Trainer, Pokemon, Skill
from .config import get_type_multiplier

class Battle:
    def __init__(self, trainer1: Trainer, trainer2: Trainer):
        self.trainer1 = trainer1
        self.trainer2 = trainer2
        self.turn = 0
        self.ready1 = False
        self.ready2 = False
        self.action1 = None  # 技能索引
        self.action2 = None
        self.winner = None
        self._initial_index1 = trainer1.active_pokemon_index
        self._initial_index2 = trainer2.active_pokemon_index
        # 保存战斗前的状态
        self._saved_states = {
            trainer1.user_id: [p.save_state() for p in trainer1.party],
            trainer2.user_id: [p.save_state() for p in trainer2.party]
        }

    def is_ready(self) -> bool:
        return self.ready1 and self.ready2

    def set_action(self, trainer: Trainer, skill_index: int):
        if trainer == self.trainer1:
            self.action1 = skill_index
            self.ready1 = True
        elif trainer == self.trainer2:
            self.action2 = skill_index
            self.ready2 = True

    def execute_turn(self) -> str:
        """同时计算伤害，返回战斗日志"""
        if not self.is_ready():
            return "双方尚未准备好"

        # 检查双方是否还有可战斗精灵（若一方已无精灵，战斗应已结束）
        if not self.trainer1.can_battle():
            self.winner = self.trainer2
            return f"{self.trainer1.name} 没有可战斗的精灵了！"
        if not self.trainer2.can_battle():
            self.winner = self.trainer1
            return f"{self.trainer2.name} 没有可战斗的精灵了！"

        p1 = self.trainer1.get_active_pokemon()
        p2 = self.trainer2.get_active_pokemon()
        if not p1 or not p2:
            self.winner = self.trainer1 if p2 is None else self.trainer2
            return "有一方没有出战的精灵，战斗结束。"

        # 获取技能
        skill1 = p1.get_skill(self.action1)
        skill2 = p2.get_skill(self.action2)

        # 检查技能有效性（包括PP）
        logs = []
        valid1 = True
        valid2 = True
        if not skill1:
            logs.append(f"{self.trainer1.name} 的 {p1.name} 技能不存在！")
            valid1 = False
        elif skill1.pp <= 0:
            logs.append(f"{self.trainer1.name} 的 {p1.name} 的 {skill1.name} 没有PP了！")
            valid1 = False

        if not skill2:
            logs.append(f"{self.trainer2.name} 的 {p2.name} 技能不存在！")
            valid2 = False
        elif skill2.pp <= 0:
            logs.append(f"{self.trainer2.name} 的 {p2.name} 的 {skill2.name} 没有PP了！")
            valid2 = False

        # 消耗PP（如果有效）
        if valid1:
            skill1.use()
        if valid2:
            skill2.use()

        # 计算伤害（双方同时）
        damage1 = 0
        damage2 = 0
        if valid1:
            damage1 = self._calculate_damage(p1, p2, skill1)
        if valid2:
            damage2 = self._calculate_damage(p2, p1, skill2)

        # 应用伤害
        p1.take_damage(damage2)
        p2.take_damage(damage1)

        # 生成日志
        if valid1:
            logs.append(f"{self.trainer1.name} 的 {p1.name} 使用了 {skill1.name}，造成 {damage1} 点伤害！")
        if valid2:
            logs.append(f"{self.trainer2.name} 的 {p2.name} 使用了 {skill2.name}，造成 {damage2} 点伤害！")

        # 检查倒下
        if p1.is_fainted():
            logs.append(f"{self.trainer1.name} 的 {p1.name} 倒下了！")
        if p2.is_fainted():
            logs.append(f"{self.trainer2.name} 的 {p2.name} 倒下了！")

        # 检查战斗是否结束（双方都无精灵时平局）
        if not self.trainer1.can_battle() and not self.trainer2.can_battle():
            self.winner = None  # 平局
        elif not self.trainer1.can_battle():
            self.winner = self.trainer2
        elif not self.trainer2.can_battle():
            self.winner = self.trainer1

        # 重置回合状态（但注意，如果一方精灵倒下，下一回合需要玩家先换人，所以ready状态重置为False）
        self.ready1 = False
        self.ready2 = False
        self.action1 = None
        self.action2 = None
        self.turn += 1

        return "\n".join(logs)

    def _calculate_damage(self, attacker: Pokemon, defender: Pokemon, skill: Skill) -> int:
        if skill.power == 0:
            return 0  # 变化技能暂不实现
        random_factor = random.randint(85, 100) / 100.0
        attack = attacker.attack
        defense = defender.defense
        type_mult = get_type_multiplier(skill.type, defender.types)
        level = attacker.level
        base_damage = int((((2 * level / 5 + 2) * skill.power * attack / defense) / 50) + 2)
        damage = int(base_damage * random_factor * type_mult)
        return max(1, damage)

    def switch_pokemon(self, trainer: Trainer, index: int) -> str:
        """手动切换精灵"""
        if trainer.switch_pokemon(index):
            return f"{trainer.name} 换出了 {trainer.get_active_pokemon().name}！"
        else:
            return "切换失败，请确认索引有效且精灵未倒下。"

    def restore_original_state(self):
        for i, p in enumerate(self.trainer1.party):
            p.restore_state(self._saved_states[self.trainer1.user_id][i])
        for i, p in enumerate(self.trainer2.party):
            p.restore_state(self._saved_states[self.trainer2.user_id][i])
        self.trainer1.active_pokemon_index = self._initial_index1
        self.trainer2.active_pokemon_index = self._initial_index2