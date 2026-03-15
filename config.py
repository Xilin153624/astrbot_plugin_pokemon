from enum import Enum

class Type(Enum):
    NORMAL = "普通"
    FIRE = "火"
    WATER = "水"
    GRASS = "草"
    FLYING = "飞行"
    ELECTRIC = "电"
    GROUND = "地面"
    MECHANICAL = "机械"
    DARK = "暗"
    LIGHT = "光"
    POISON = "毒"
# 属性克制矩阵
TYPE_CHART = {
    Type.FIRE: {
        Type.GRASS: 2.0,
        Type.WATER: 0.5,
        Type.FIRE: 0.5,
        Type.MECHANICAL: 0.5,
    },
    Type.WATER: {
        Type.FIRE: 2.0,
        Type.GRASS: 0.5,
        Type.ELECTRIC: 0.5,
        Type.GROUND: 2.0,
    },
    Type.GRASS: {
        Type.WATER: 2.0,
        Type.FIRE: 0.5,
        Type.FLYING: 0.5,
        Type.GROUND: 2.0,
    },
    Type.FLYING: {
        Type.GRASS: 2.0,
        Type.ELECTRIC: 0.5,
        Type.GROUND: 0.0,
    },
    Type.ELECTRIC: {
        Type.WATER: 2.0,
        Type.FLYING: 2.0,
        Type.GROUND: 0.0,
    },
    Type.GROUND: {
        Type.FIRE: 2.0,
        Type.ELECTRIC: 2.0,
        Type.FLYING: 0.0,
    },
    Type.MECHANICAL: {
        Type.FIRE: 0.5,
        Type.GROUND: 0.5,
        Type.ELECTRIC: 0.5,
        Type.WATER: 0.5,
    },
    Type.DARK: {
        Type.LIGHT: 2.0,
        Type.DARK: 0.5,
    },
    Type.LIGHT: {
        Type.DARK: 2.0,
        Type.LIGHT: 0.5,
    },
}

def get_type_multiplier(attack_type: Type, defend_types: list[Type]) -> float:
    multiplier = 1.0
    for def_type in defend_types:
        multiplier *= TYPE_CHART.get(attack_type, {}).get(def_type, 1.0)
    return multiplier