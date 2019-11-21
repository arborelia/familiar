import random

LEVELS = [
    'House',
    'Trump Castle',
    'Milk Sea',
    'Fairy Forest',
    'Star Hill',
    'Ice-Fire Mountain'
]

FACES = [
    'a HERO', 'a NINJA', 'a ROBOT', 'an ALIEN', 'a FIGHTER', 'a MONSTER', 'a GHOST', 'a ?'
]
BODIES = [
    'in ARMOR', 'with WINGS', 'JET', 'CYBORG', 'BOAT', 'BUGGY', 'TANK', 'with a ? body'
]
WEAPONS = [
    'PARASOL', 'BOOMERANG', 'SHURIKEN', 'BALL', 'PENCIL', 'CRYSTAL', 'FLOWER', 'MELODY'
]


def cocoron_char():
    face = random.choice(FACES)
    body = random.choice(BODIES)
    weapon = random.choice(WEAPONS)

    return f"{face} {body}, whose weapon is a {weapon}"


def cocoron_rando():
    levels = LEVELS[:]
    random.shuffle(levels)
    level_order = ', '.join(levels)
    char = cocoron_char()
    response = [
        f"Your level order is: {level_order}",
        f"Your starting character is {char}.",
        "Say !cchar to get another character."
    ]
    return response


if __name__ == '__main__':
    print(cocoron_rando())