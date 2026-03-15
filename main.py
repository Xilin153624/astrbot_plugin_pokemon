from astrbot.api.star import Context, Star, register
from astrbot.api.event import filter, AstrMessageEvent

from .battle import Battle
from .data_manager import get_trainer, update_trainer, load_pokedex
from .models import Pokemon, Skill
from .config import Type

import random


@register(
    name="pokemon",
    author="你的名字",
    desc="精灵对战插件",
    version="2.0"
)
class PokemonPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.battles = {}
        self.waiting_players = []

        try:
            self.pokedex = load_pokedex()
        except Exception as e:
            print("图鉴加载失败:", e)
            self.pokedex = {}

    def get_user_id(self, event):
        return str(event.get_sender_id())

    def get_user_name(self, event):
        return event.get_sender_name()

    # ------------------------- 指令注册 -------------------------

    @filter.command("测试")
    async def cmd_test(self, event: AstrMessageEvent):
        yield event.plain_result("宝可梦插件运行正常")

    @filter.command("帮助")
    async def cmd_help(self, event: AstrMessageEvent):
        msg = (
            "精灵对战插件命令列表\n"
            "━━━━━━━━━━━━━━━━\n"
            "1. 我的精灵\n"
            "   - 查看自己的精灵队伍，当前出战（★）\n\n"
            "2. 选择初始 水or火or草\n"
            "   - 仅首次使用：1=水甲龟(水), 2=赤火猪(火), 3=仙人球(草)\n\n"
            "3. 捕捉\n"
            "   - 随机获得一只初始精灵（等级1）\n\n"
            "4. 选择 N\n"
            "   - 非战斗：设置第N只为首发（★）\n"
            "   - 战斗中：临时切换到第N只出战\n\n"
            "5. 技能 N\n"
            "   - 战斗中使用当前精灵的第N个技能（1~4）\n\n"
            "6. 挑战 QQ号\n"
            "   - 向指定玩家发起对战请求\n\n"
            "7. 接受 QQ号\n"
            "   - 接受某玩家的挑战请求\n\n"
            "8. 拒绝 QQ号\n"
            "   - 拒绝某玩家的挑战请求\n\n"
            "9. 换人 N\n"
            "   - 战斗中手动切换到第N只精灵\n\n"
            "10. 退出战斗\n"
            "    - 强制结束当前对战，恢复状态\n\n"
            "11. 放生 N\n"
            "    - 永久释放队伍第N只精灵（不能放生出战精灵）\n\n"
            "12. 图鉴\n"
            "    - 查看所有可获得的精灵列表\n\n"
            "13. 帮助\n"
            "    - 显示此帮助信息\n\n"
            " 战斗规则\n"
            "- 回合制，双方同时选择技能，同时计算伤害\n"
            "- 精灵倒下后必须手动换人才能继续\n"
            "- 战斗结束（胜负或平局）后所有精灵状态恢复（测试福利）\n"
            "- 首发精灵：用“选择 N”设定，战斗开始时自动出战"
        )
        yield event.plain_result(msg)

    @filter.command("图鉴")
    async def cmd_pokedex(self, event: AstrMessageEvent):
        if not self.pokedex:
            yield event.plain_result("图鉴为空")
            return
        msg = "图鉴：\n"
        for pid, data in self.pokedex.items():
            types = "/".join(data["types"])
            msg += f"{data['name']} ({types}) 编号:{pid}\n"
        yield event.plain_result(msg)

    @filter.command("我的精灵")
    async def cmd_my_pokemon(self, event: AstrMessageEvent):
        trainer = get_trainer(self.get_user_id(event), self.get_user_name(event))
        if not trainer.party:
            yield event.plain_result("你还没有精灵，请先选择初始精灵")
            return
        msg = f"{trainer.name} 的精灵：\n"
        for i, p in enumerate(trainer.party):
            status = "★" if i == trainer.active_pokemon_index else " "
            msg += f"{i+1}. [{status}] {p.name} Lv.{p.level} HP:{p.current_hp}/{p.max_hp}\n"
            for j, skill in enumerate(p.skills):
                msg += f"  技能{j+1}: {skill.name} PP:{skill.pp}/{skill.max_pp}\n"
        yield event.plain_result(msg)

    @filter.command("选择初始水")
    async def cmd_choose1(self, event: AstrMessageEvent):
        msg = await self._choose_starter(event, 0)
        yield event.plain_result(msg)

    @filter.command("选择初始火")
    async def cmd_choose2(self, event: AstrMessageEvent):
        msg = await self._choose_starter(event, 1)
        yield event.plain_result(msg)

    @filter.command("选择初始草")
    async def cmd_choose3(self, event: AstrMessageEvent):
        msg = await self._choose_starter(event, 2)
        yield event.plain_result(msg)

    async def _choose_starter(self, event, choice):
        trainer = get_trainer(self.get_user_id(event), self.get_user_name(event))
        if trainer.party:
            return "你已经拥有精灵"  # 返回字符串，不发消息
        starter_ids = ["001", "004", "007"]
        pid = starter_ids[choice]
        pokemon = await self._create_pokemon(trainer, pid, starter=True)
        return f"你选择了 {pokemon.name} 作为初始精灵！"

    async def _create_pokemon(self, trainer, pid, starter=False):
        base_data = self.pokedex[pid]
        pokemon = Pokemon(
            id=pid,
            name=base_data["name"],
            types=[Type(t) for t in base_data["types"]],
            base_hp=base_data["base_hp"],
            base_attack=base_data["base_attack"],
            base_defense=base_data["base_defense"],
            base_sp_attack=base_data["base_sp_attack"],
            base_sp_defense=base_data["base_sp_defense"],
            base_speed=base_data["base_speed"],
            level=1,
            skills=[Skill.from_dict(s) for s in base_data["skills"][:4]]
        )
        trainer.add_pokemon(pokemon)
        update_trainer(trainer)
        return pokemon  # 返回精灵对象，让调用者自己发消息
    @filter.command("捕捉")
    async def capture_pokemon(self, event: AstrMessageEvent):
        trainer = get_trainer(self.get_user_id(event), self.get_user_name(event))
        starter_ids = ["001", "004", "007"]
        pid = random.choice(starter_ids)
        pokemon = await self._create_pokemon(trainer, pid)  # 新调用，去掉event，获取返回值
        yield event.plain_result(f"捕捉成功：{pokemon.name}")  # 自己发送消息

    async def _create_pokemon(self, trainer, pid, starter=False):
        base_data = self.pokedex[pid]
        pokemon = Pokemon(
            id=pid,
            name=base_data["name"],
            types=[Type(t) for t in base_data["types"]],
            base_hp=base_data["base_hp"],
            base_attack=base_data["base_attack"],
            base_defense=base_data["base_defense"],
            base_sp_attack=base_data["base_sp_attack"],
            base_sp_defense=base_data["base_sp_defense"],
            base_speed=base_data["base_speed"],
            level=1,
            skills=[Skill.from_dict(s) for s in base_data["skills"][:4]]
        )
        trainer.add_pokemon(pokemon)
        update_trainer(trainer)
        return pokemon  # 返回精灵对象，让调用者自己发消息
    @filter.command("背包")
    async def cmd_bag(self, event: AstrMessageEvent):
        trainer = get_trainer(self.get_user_id(event), self.get_user_name(event))
        if not trainer.party:
            yield event.plain_result("你还没有精灵，请先选择初始精灵")
            return
        msg = f"{trainer.name} 的精灵：\n"
        for i, p in enumerate(trainer.party):
            status = "★" if i == trainer.active_pokemon_index else " "
            msg += f"{i+1}. [{status}] {p.name} Lv.{p.level} HP:{p.current_hp}/{p.max_hp}\n"
        yield event.plain_result(msg)

    # ------------------------- 对战命令 -------------------------

    @filter.command("挑战")
    async def challenge_player(self, event: AstrMessageEvent):
        parts = event.message_str.strip().split()
        if len(parts) != 2:
            yield event.plain_result("格式错误：请使用“挑战 QQ号”")
            return
        target_id = parts[1].strip()
        user_id = event.get_sender_id()
        user_name = event.get_sender_name()

        # 不能挑战自己
        if target_id == user_id:
            yield event.plain_result("不能挑战自己。")
            return

        # 检查自己是否已经在战斗中
        if self._find_battle_by_user(user_id):
            yield event.plain_result("你已经在战斗中了，无法发起新的挑战。")
            return

        # 检查自己是否有可战斗精灵
        trainer = get_trainer(user_id, user_name)
        if not trainer.can_battle():
            yield event.plain_result("你没有可战斗的精灵，无法发起挑战。")
            return

        # 检查是否已有相同请求
        for req in self.waiting_players:
            if req[0] == user_id and req[1] == target_id:
                yield event.plain_result("你已经向该玩家发起过挑战，请等待回应。")
                return
            if req[0] == target_id and req[1] == user_id:
                yield event.plain_result("对方已经向你发起挑战，请使用“接受”或“拒绝”回应。")
                return

        self.waiting_players.append((user_id, target_id))
        yield event.plain_result(f"你向 {target_id} 发起了对战挑战！对方可使用“接受 {user_id}”或“拒绝 {user_id}”回应。")

    @filter.command("接受")
    async def accept_battle(self, event: AstrMessageEvent):
        parts = event.message_str.strip().split()
        if len(parts) != 2:
            yield event.plain_result("格式错误：请使用“接受 QQ号”")
            return
        challenger_id = parts[1].strip()
        user_id = event.get_sender_id()
        user_name = event.get_sender_name()

        # 不能接受自己的挑战
        if challenger_id == user_id:
            yield event.plain_result("不能接受自己的挑战。")
            return

        # 检查自己是否已在战斗中
        if self._find_battle_by_user(user_id):
            yield event.plain_result("你已经在战斗中了，无法接受新的挑战。")
            return

        # 查找对应的挑战请求
        found = None
        for req in self.waiting_players:
            if req[0] == challenger_id and req[1] == user_id:
                found = req
                break
        if not found:
            yield event.plain_result(f"没有来自 {challenger_id} 的挑战请求。")
            return

        trainer1 = get_trainer(challenger_id)
        trainer2 = get_trainer(user_id, user_name)

        # 检查发起方是否已在战斗中（可能在他发起后进入了另一场战斗）
        if self._find_battle_by_user(challenger_id):
            self.waiting_players.remove(found)
            yield event.plain_result(f"发起方 {trainer1.name} 已经进入战斗，请求已取消。")
            return

        # 检查双方是否有可战斗精灵
        if not trainer1.can_battle():
            self.waiting_players.remove(found)
            yield event.plain_result(f"发起方 {trainer1.name} 没有可战斗的精灵，请求已取消。")
            return
        if not trainer2.can_battle():
            yield event.plain_result("你没有可战斗的精灵，无法接受挑战。")
            return

        battle = Battle(trainer1, trainer2)
        battle_key = f"{challenger_id}_{user_id}"
        self.battles[battle_key] = battle
        self.waiting_players.remove(found)

        yield event.plain_result(
            f"对战开始！{trainer1.name}({trainer1.user_id}) vs {trainer2.name}({trainer2.user_id})\n"
            f"{trainer1.name} 的 {trainer1.get_active_pokemon().name} 对阵 "
            f"{trainer2.name} 的 {trainer2.get_active_pokemon().name}\n"
            f"请双方使用“技能 N”选择技能。"
        )

    @filter.command("拒绝")
    async def reject_battle(self, event: AstrMessageEvent):
        parts = event.message_str.strip().split()
        if len(parts) != 2:
            yield event.plain_result("格式错误：请使用“拒绝 QQ号”")
            return
        challenger_id = parts[1].strip()
        user_id = event.get_sender_id()

        found = None
        for req in self.waiting_players:
            if req[0] == challenger_id and req[1] == user_id:
                found = req
                break
        if found:
            self.waiting_players.remove(found)
            yield event.plain_result(f"你已拒绝 {challenger_id} 的挑战请求。")
        else:
            yield event.plain_result("没有找到该挑战请求。")

    # ---------- 战斗操作 ----------
    @filter.command("技能")
    async def use_skill(self, event: AstrMessageEvent):
        parts = event.message_str.strip().split()
        if len(parts) != 2 or not parts[1].isdigit():
            yield event.plain_result("格式错误：请使用“技能 数字”")
            return

        skill_num = int(parts[1])
        if skill_num < 1 or skill_num > 4:
            yield event.plain_result("技能序号必须在 1-4 之间")
            return
        skill_index = skill_num - 1
        user_id = event.get_sender_id()

        battle = self._find_battle_by_user(user_id)
        if not battle:
            yield event.plain_result("你不在对战中。")
            return

        if battle.winner:
            yield event.plain_result("对战已结束，请开始新的对战。")
            return

        trainer = get_trainer(user_id)
        active = trainer.get_active_pokemon()
        if not active:
            yield event.plain_result("你没有出战的精灵。")
            return
        if active.is_fainted():
            yield event.plain_result(f"{active.name} 已经倒下了，请先用“选择 N”换一只精灵。")
            return
        skill = active.get_skill(skill_index)
        if not skill:
            yield event.plain_result("技能不存在。")
            return
        if skill.pp <= 0:
            yield event.plain_result(f"{skill.name} 的 PP 已耗尽，请选择其他技能。")
            return

        # 记录技能
        if battle.trainer1.user_id == user_id:
            battle.set_action(battle.trainer1, skill_index)
            if battle.is_ready():
                try:
                    result = battle.execute_turn()
                except Exception as e:
                    result = f"战斗执行异常：{str(e)}"
                yield event.plain_result(result)
                update_trainer(battle.trainer1)
                update_trainer(battle.trainer2)

                if battle.winner:
                    battle.restore_original_state()
                    update_trainer(battle.trainer1)
                    update_trainer(battle.trainer2)
                    yield event.plain_result(f"对战结束，胜者：{battle.winner.name}（测试模式，所有精灵状态已恢复）")
                    self._end_battle(battle)
                elif not battle.trainer1.can_battle() and not battle.trainer2.can_battle():
                    # 平局
                    battle.restore_original_state()
                    update_trainer(battle.trainer1)
                    update_trainer(battle.trainer2)
                    yield event.plain_result("对战结束，双方都无精灵，平局！（状态已恢复）")
                else:
                    yield event.plain_result("回合结束，请继续选择技能。")
            else:
                yield event.plain_result("指令已记录，等待对手选择技能。")
        elif battle.trainer2.user_id == user_id:
            battle.set_action(battle.trainer2, skill_index)
            if battle.is_ready():
                try:
                    result = battle.execute_turn()
                except Exception as e:
                    result = f"战斗执行异常：{str(e)}"
                yield event.plain_result(result)
                update_trainer(battle.trainer1)
                update_trainer(battle.trainer2)
                if battle.winner:
                    battle.restore_original_state()
                    update_trainer(battle.trainer1)
                    update_trainer(battle.trainer2)
                    yield event.plain_result(f"对战结束，胜者：{battle.winner.name}（测试模式，所有精灵状态已恢复）")
                    self._end_battle(battle)
                else:
                    yield event.plain_result("回合结束，请继续选择技能。")
            else:
                yield event.plain_result("指令已记录，等待对手选择技能。")
        else:
            yield event.plain_result("你不在对战中。")

    @filter.command("换人")
    async def switch_pokemon(self, event: AstrMessageEvent):
        parts = event.message_str.strip().split()
        if len(parts) != 2 or not parts[1].isdigit():
            yield event.plain_result("格式错误：请使用“换人 数字”")
            return
        index = int(parts[1]) - 1
        user_id = event.get_sender_id()

        battle = self._find_battle_by_user(user_id)
        if not battle:
            yield event.plain_result("你不在对战中。")
            return

        trainer = get_trainer(user_id)
        result = battle.switch_pokemon(trainer, index)
        yield event.plain_result(result)
        update_trainer(trainer)

    @filter.command("退出战斗")
    async def quit_battle(self, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        battle = self._find_battle_by_user(user_id)
        if not battle:
            yield event.plain_result("你不在对战中。")
            return

        # 恢复双方状态
        battle.restore_original_state()
        update_trainer(battle.trainer1)
        update_trainer(battle.trainer2)
        self._end_battle(battle)
        yield event.plain_result("你已退出战斗，双方精灵状态已恢复。")

    @filter.command("选择")
    async def select_pokemon(self, event: AstrMessageEvent):
        parts = event.message_str.strip().split()
        if len(parts) != 2 or not parts[1].isdigit():
            yield event.plain_result("格式错误：请使用“选择 数字”")
            return
        index = int(parts[1]) - 1
        user_id = event.get_sender_id()
        trainer = get_trainer(user_id)

        if index < 0 or index >= len(trainer.party):
            yield event.plain_result("索引超出队伍范围。")
            return

        battle = self._find_battle_by_user(user_id)
        if battle:
            # 战斗中：临时换人
            result = battle.switch_pokemon(trainer, index)
            yield event.plain_result(result)
            update_trainer(trainer)
        else:
            # 非战斗：设置首发
            if trainer.party[index].is_fainted():
                yield event.plain_result("该精灵已倒下，无法设为首发。")
                return
            trainer.first_pokemon_index = index
            trainer.active_pokemon_index = index
            update_trainer(trainer)
            yield event.plain_result(f"已将 {trainer.party[index].name} 设为首发精灵。")

    @filter.command("放生")
    async def release_pokemon(self, event: AstrMessageEvent):
        parts = event.message_str.strip().split()
        if len(parts) != 2 or not parts[1].isdigit():
            yield event.plain_result("格式错误：请使用“放生 数字”")
            return
        index = int(parts[1]) - 1
        user_id = event.get_sender_id()
        trainer = get_trainer(user_id)

        if index < 0 or index >= len(trainer.party):
            yield event.plain_result("索引超出队伍范围。")
            return

        # 战斗中禁止放生
        if self._find_battle_by_user(user_id):
            yield event.plain_result("战斗中不能放生精灵。")
            return

        # 不能放生当前出战的精灵
        if index == trainer.active_pokemon_index:
            yield event.plain_result("不能放生当前出战的精灵，请先切换到其他精灵。")
            return

        pokemon_name = trainer.party[index].name
        # 移除精灵
        del trainer.party[index]

        # 调整首发索引和当前出战索引
        if trainer.first_pokemon_index >= len(trainer.party):
            trainer.first_pokemon_index = 0 if trainer.party else None
        if trainer.active_pokemon_index >= len(trainer.party):
            trainer.active_pokemon_index = 0 if trainer.party else None

        update_trainer(trainer)
        yield event.plain_result(f"你放生了 {pokemon_name}。")
        if not trainer.party:
            yield event.plain_result("你的队伍已经没有精灵了，请及时捕捉或选择初始。")

    # ------------------------- 辅助方法 -------------------------

    def _find_battle(self, user_id):
        for battle in self.battles.values():
            if battle.trainer1.user_id == user_id or battle.trainer2.user_id == user_id:
                return battle
        return None
    def _find_battle_by_user(self, user_id):
        for battle in self.battles.values():
            if battle.trainer1.user_id == user_id or battle.trainer2.user_id == user_id:
                return battle
        return None
    def _end_battle(self, battle):
        for key, b in list(self.battles.items()):
            if b == battle:
                del self.battles[key]
                break