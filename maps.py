import arcade

BOT = -1000
TOP = 1000
LEFT = -1000
RIGHT = 1000

def create_walls():
    scale = 0.5
    wall_list = arcade.SpriteList(use_spatial_hash=True)
    pos = []

    # Create bottom wall
    for x in range(LEFT, RIGHT, int(128 * scale)):
        pos.append([x, BOT])
        pos.append([x, TOP])
    for y in range(BOT, TOP, int(128 * scale)):
        pos.append([LEFT, y])
        pos.append([RIGHT, y])

    for p in pos:
        sprite = arcade.Sprite(':resources:images/tiles/stoneCenter.png', scale)
        sprite.position = p
        wall_list.append(sprite)

    return wall_list
