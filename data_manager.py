import json
import os
from typing import Dict, Optional
from .models import Trainer, Pokemon, Skill
from .config import Type

# 数据根目录：AstrBot的data文件夹下
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "pokemon")
TRAINERS_FILE = os.path.join(DATA_DIR, "trainers.json")
POKEDEX_FILE = os.path.join(DATA_DIR, "pokedex.json")

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_pokedex() -> dict:
    """加载精灵图鉴，如果不存在则创建默认图鉴（包含三个初始精灵家族）"""
    ensure_data_dir()
    if not os.path.exists(POKEDEX_FILE):
        # 创建默认图鉴
        default_pokedex = {
            # 水甲龟家族（水）
            "001": {
                "name": "水甲龟",
                "types": ["水"],
                "base_hp": 44,
                "base_attack": 48,
                "base_defense": 65,
                "base_sp_attack": 50,
                "base_sp_defense": 64,
                "base_speed": 43,
                "skills": [
                    {"name": "撞击", "type": "普通", "power": 40, "pp": 35, "max_pp": 35, "accuracy": 100},
                    {"name": "水枪", "type": "水", "power": 40, "pp": 25, "max_pp": 25, "accuracy": 100},
                    {"name": "缩壳", "type": "水", "power": 0, "pp": 40, "max_pp": 40, "accuracy": 100},  # 变化技能，提高防御
                    {"name": "咬住", "type": "暗", "power": 60, "pp": 25, "max_pp": 25, "accuracy": 100}
                ]
            },
            "002": {
                "name": "沼甲龟",
                "types": ["水", "地面"],
                "base_hp": 59,
                "base_attack": 63,
                "base_defense": 80,
                "base_sp_attack": 65,
                "base_sp_defense": 80,
                "base_speed": 58,
                "skills": [
                    {"name": "水之波动", "type": "水", "power": 60, "pp": 20, "max_pp": 20, "accuracy": 100},
                    {"name": "泥巴射击", "type": "地面", "power": 55, "pp": 15, "max_pp": 15, "accuracy": 95},
                    {"name": "高速旋转", "type": "普通", "power": 50, "pp": 40, "max_pp": 40, "accuracy": 100},
                    {"name": "守住", "type": "普通", "power": 0, "pp": 10, "max_pp": 10, "accuracy": 100}
                ]
            },
            "003": {
                "name": "海玄龟",
                "types": ["水", "地面"],
                "base_hp": 79,
                "base_attack": 83,
                "base_defense": 100,
                "base_sp_attack": 85,
                "base_sp_defense": 105,
                "base_speed": 78,
                "skills": [
                    {"name": "水炮", "type": "水", "power": 110, "pp": 5, "max_pp": 5, "accuracy": 80},
                    {"name": "地震", "type": "地面", "power": 100, "pp": 10, "max_pp": 10, "accuracy": 100},
                    {"name": "岩崩", "type": "地面", "power": 75, "pp": 10, "max_pp": 10, "accuracy": 90},
                    {"name": "睡觉", "type": "普通", "power": 0, "pp": 10, "max_pp": 10, "accuracy": 100}
                ]
            },
            # 赤火猪家族（火）
            "004": {
                "name": "赤火猪",
                "types": ["火"],
                "base_hp": 45,
                "base_attack": 60,
                "base_defense": 40,
                "base_sp_attack": 70,
                "base_sp_defense": 50,
                "base_speed": 65,
                "skills": [
                    {"name": "撞击", "type": "普通", "power": 40, "pp": 35, "max_pp": 35, "accuracy": 100},
                    {"name": "火花", "type": "火", "power": 40, "pp": 25, "max_pp": 25, "accuracy": 100},
                    {"name": "叫声", "type": "普通", "power": 0, "pp": 40, "max_pp": 40, "accuracy": 100},
                    {"name": "烟幕", "type": "火", "power": 0, "pp": 20, "max_pp": 20, "accuracy": 100}
                ]
            },
            "005": {
                "name": "炎火猪",
                "types": ["火", "地面"],
                "base_hp": 65,
                "base_attack": 80,
                "base_defense": 60,
                "base_sp_attack": 90,
                "base_sp_defense": 70,
                "base_speed": 80,
                "skills": [
                    {"name": "火焰拳", "type": "火", "power": 75, "pp": 15, "max_pp": 15, "accuracy": 100},
                    {"name": "泥巴炸弹", "type": "地面", "power": 65, "pp": 20, "max_pp": 20, "accuracy": 85},
                    {"name": "猛撞", "type": "普通", "power": 90, "pp": 20, "max_pp": 20, "accuracy": 85},
                    {"name": "吼叫", "type": "普通", "power": 0, "pp": 20, "max_pp": 20, "accuracy": 100}
                ]
            },
            "006": {
                "name": "炽火野猪",
                "types": ["火", "地面"],
                "base_hp": 85,
                "base_attack": 100,
                "base_defense": 80,
                "base_sp_attack": 110,
                "base_sp_defense": 90,
                "base_speed": 100,
                "skills": [
                    {"name": "喷火", "type": "火", "power": 150, "pp": 5, "max_pp": 5, "accuracy": 90},
                    {"name": "大地之力", "type": "地面", "power": 90, "pp": 10, "max_pp": 10, "accuracy": 100},
                    {"name": "蛮力", "type": "格斗", "power": 120, "pp": 5, "max_pp": 5, "accuracy": 100},
                    {"name": "健美", "type": "格斗", "power": 0, "pp": 20, "max_pp": 20, "accuracy": 100}
                ]
            },
            # 仙人球家族（草）
            "007": {
                "name": "仙人球",
                "types": ["草"],
                "base_hp": 35,
                "base_attack": 45,
                "base_defense": 50,
                "base_sp_attack": 70,
                "base_sp_defense": 55,
                "base_speed": 30,
                "skills": [
                    {"name": "撞击", "type": "普通", "power": 40, "pp": 35, "max_pp": 35, "accuracy": 100},
                    {"name": "吸取", "type": "草", "power": 20, "pp": 25, "max_pp": 25, "accuracy": 100},
                    {"name": "生长", "type": "普通", "power": 0, "pp": 40, "max_pp": 40, "accuracy": 100},
                    {"name": "毒针", "type": "毒", "power": 15, "pp": 35, "max_pp": 35, "accuracy": 100}
                ]
            },
            "008": {
                "name": "仙人掌",
                "types": ["草", "地面"],
                "base_hp": 55,
                "base_attack": 65,
                "base_defense": 70,
                "base_sp_attack": 90,
                "base_sp_defense": 75,
                "base_speed": 50,
                "skills": [
                    {"name": "飞叶快刀", "type": "草", "power": 55, "pp": 25, "max_pp": 25, "accuracy": 95},
                    {"name": "扎根", "type": "草", "power": 0, "pp": 20, "max_pp": 20, "accuracy": 100},
                    {"name": "撒菱", "type": "地面", "power": 0, "pp": 20, "max_pp": 20, "accuracy": 100},
                    {"name": "叩打", "type": "普通", "power": 80, "pp": 20, "max_pp": 20, "accuracy": 75}
                ]
            },
            "009": {
                "name": "巨型仙人掌",
                "types": ["草", "地面"],
                "base_hp": 75,
                "base_attack": 85,
                "base_defense": 90,
                "base_sp_attack": 115,
                "base_sp_defense": 95,
                "base_speed": 70,
                "skills": [
                    {"name": "阳光烈焰", "type": "草", "power": 120, "pp": 10, "max_pp": 10, "accuracy": 100},
                    {"name": "沙暴", "type": "地面", "power": 0, "pp": 10, "max_pp": 10, "accuracy": 100},
                    {"name": "尖刺臂", "type": "草", "power": 100, "pp": 10, "max_pp": 10, "accuracy": 85},
                    {"name": "剑舞", "type": "普通", "power": 0, "pp": 20, "max_pp": 20, "accuracy": 100}
                ]
            }
        }
        with open(POKEDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_pokedex, f, ensure_ascii=False, indent=2)
        return default_pokedex
    else:
        with open(POKEDEX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

def load_trainers() -> Dict[str, Trainer]:
    ensure_data_dir()
    if not os.path.exists(TRAINERS_FILE):
        return {}
    with open(TRAINERS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    trainers = {}
    for uid, trainer_data in data.items():
        trainers[uid] = Trainer.from_dict(trainer_data)
    return trainers

def save_trainers(trainers: Dict[str, Trainer]):
    ensure_data_dir()
    data = {uid: t.to_dict() for uid, t in trainers.items()}
    with open(TRAINERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_trainer(user_id: str, user_name: str = "未知训练家") -> Trainer:
    trainers = load_trainers()
    if user_id not in trainers:
        trainers[user_id] = Trainer(user_id, user_name)
        save_trainers(trainers)
    return trainers[user_id]

def update_trainer(trainer: Trainer):
    trainers = load_trainers()
    trainers[trainer.user_id] = trainer
    save_trainers(trainers)