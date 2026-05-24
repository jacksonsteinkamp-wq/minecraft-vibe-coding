import os

def block_id(block):
    return block.split("[")[0] if "[" in block else block

ESCAPE_KEY = 256
python_path = r"C:\Python314\python.exe"
SCRIPT_DIR = os.path.dirname(os.path.dirname(__file__))

SHOVEL_BLOCKS = {
    "minecraft:dirt", "minecraft:gravel", "minecraft:sand",
    "minecraft:grass_block", "minecraft:coarse_dirt",
    "minecraft:rooted_dirt", "minecraft:mud", "minecraft:clay",
    "minecraft:soul_sand", "minecraft:soul_soil", "minecraft:snow_block", "minecraft:snow",
}

ORE_BLOCKS = {
    "minecraft:coal_ore", "minecraft:iron_ore", "minecraft:copper_ore",
    "minecraft:gold_ore", "minecraft:redstone_ore", "minecraft:lapis_ore",
    "minecraft:diamond_ore", "minecraft:emerald_ore",
    "minecraft:ancient_debris",
}

PICK_TIER = {
    "minecraft:wooden_pickaxe": 0,
    "minecraft:stone_pickaxe": 1,
    "minecraft:iron_pickaxe": 2,
    "minecraft:diamond_pickaxe": 3,
    "minecraft:netherite_pickaxe": 4,
}

SHOVEL_ITEMS = {
    "minecraft:wooden_shovel", "minecraft:stone_shovel",
    "minecraft:iron_shovel", "minecraft:diamond_shovel",
    "minecraft:netherite_shovel",
}

TOOL_ITEMS = PICK_TIER.keys() | SHOVEL_ITEMS | {
    "minecraft:wooden_sword", "minecraft:stone_sword",
    "minecraft:iron_sword", "minecraft:diamond_sword",
    "minecraft:netherite_sword",
    "minecraft:wooden_axe", "minecraft:stone_axe",
    "minecraft:iron_axe", "minecraft:diamond_axe",
    "minecraft:netherite_axe",
    "minecraft:wooden_hoe", "minecraft:stone_hoe",
    "minecraft:iron_hoe", "minecraft:diamond_hoe",
    "minecraft:netherite_hoe",
}

KEEP_IN_HOTBAR = TOOL_ITEMS | FOOD_ITEMS

FOOD_ITEMS = {
    "minecraft:apple", "minecraft:baked_potato", "minecraft:beef",
    "minecraft:bread", "minecraft:carrot", "minecraft:chicken",
    "minecraft:cooked_beef", "minecraft:cooked_chicken",
    "minecraft:cooked_cod", "minecraft:cooked_mutton",
    "minecraft:cooked_porkchop", "minecraft:cooked_rabbit",
    "minecraft:cooked_salmon", "minecraft:golden_carrot",
    "minecraft:mutton", "minecraft:porkchop", "minecraft:potato",
    "minecraft:pumpkin_pie", "minecraft:rabbit", "minecraft:salmon",
}

TRASH_ITEMS = {
    "minecraft:cobblestone", "minecraft:cobbled_deepslate",
    "minecraft:dirt", "minecraft:gravel",
    "minecraft:andesite", "minecraft:diorite", "minecraft:granite",
}

GRAVITY_BLOCKS = {"minecraft:gravel", "minecraft:sand", "minecraft:red_sand"}

MINERAL_ITEMS = ORE_BLOCKS | {
    "minecraft:raw_iron", "minecraft:raw_gold", "minecraft:raw_copper",
    "minecraft:diamond", "minecraft:emerald", "minecraft:lapis_lazuli",
    "minecraft:iron_ingot", "minecraft:gold_ingot", "minecraft:copper_ingot",
    "minecraft:netherite_ingot", "minecraft:netherite_scrap",
    "minecraft:redstone", "minecraft:coal", "minecraft:flint",
    "minecraft:amethyst_shard", "minecraft:quartz",
}

FOOD_THRESHOLD = 10
TRASH_INTERVAL = 60
MOVE_TIMEOUT = 10
JUMP_HOLD = 0.6
MOVE_HOLD = 0.45
MOVED_THRESHOLD = 0.35
STUCK_THRESHOLD = 0.2
GIVEUP_TIMEOUT = 120
