import json
from pathlib import Path
from typing import Dict, Optional
from .models import Trainer

# 全局变量，存储数据目录路径
_DATA_DIR: Optional[Path] = None
TRAINERS_FILE: Optional[Path] = None
POKEDEX_FILE: Optional[Path] = None

def init_data_dir(data_dir: Path):
    """由插件在初始化时调用，设置数据目录路径"""
    global _DATA_DIR, TRAINERS_FILE, POKEDEX_FILE
    _DATA_DIR = data_dir
    TRAINERS_FILE = data_dir / "trainers.json"
    POKEDEX_FILE = data_dir / "pokedex.json"
    _DATA_DIR.mkdir(parents=True, exist_ok=True)

def ensure_data_dir():
    """确保数据目录存在"""
    if _DATA_DIR:
        _DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_pokedex() -> dict:
    """加载精灵图鉴，如果不存在则创建默认图鉴"""
    if POKEDEX_FILE is None:
        raise RuntimeError("data_manager 未初始化，请先调用 init_data_dir")
    if not POKEDEX_FILE.exists():
        # 默认图鉴数据（请保留您原有的默认数据）
        default_pokedex = {
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
                    {"name": "缩壳", "type": "水", "power": 0, "pp": 40, "max_pp": 40, "accuracy": 100},
                    {"name": "咬住", "type": "暗", "power": 60, "pp": 25, "max_pp": 25, "accuracy": 100}
                ]
            },
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
            }
        }
        with open(POKEDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_pokedex, f, ensure_ascii=False, indent=2)
        return default_pokedex
    else:
        with open(POKEDEX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

def load_trainers() -> Dict[str, Trainer]:
    if TRAINERS_FILE is None:
        raise RuntimeError("data_manager 未初始化，请先调用 init_data_dir")
    if not TRAINERS_FILE.exists():
        return {}
    with open(TRAINERS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    trainers = {}
    for uid, trainer_data in data.items():
        trainers[uid] = Trainer.from_dict(trainer_data)
    return trainers

def save_trainers(trainers: Dict[str, Trainer]):
    if TRAINERS_FILE is None:
        raise RuntimeError("data_manager 未初始化，请先调用 init_data_dir")
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