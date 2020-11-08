"""
Sprite Explosion

Simple program to show how to make explosions with a series of bitmaps.

Artwork from http://kenney.nl
Explosion graphics from http://www.explosiongenerator.com/

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_explosion_bitmapped
"""
import random
import arcade
import os
import PIL
from arcade.draw_commands import Texture
from arcade.experimental.lights import Light, LightLayer

import maps
import player

SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_COIN = 0.2
SPRITE_SCALING_LASER = 0.8
COIN_COUNT = 100

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Sprite Explosion Example"

BULLET_SPEED = 5
PLAYER_SPEED = 4

EXPLOSION_TEXTURE_COUNT = 60


class Explosion(arcade.Sprite):
    """ This class creates an explosion animation """

    def __init__(self, texture_list):
        super().__init__()

        # Start at the first frame
        self.current_texture = 0
        self.textures = texture_list

    def update(self):

        # Update to the next frame of the animation. If we are at the end
        # of our frames, then delete this sprite.
        self.current_texture += 1
        if self.current_texture < len(self.textures):
            self.set_texture(self.current_texture)
        else:
            self.remove_from_sprite_lists()


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=False)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Variables that will hold sprite lists
        self.player_list = None
        self.coin_list = None
        self.bullet_list = None
        self.explosions_list = None
        self.wall_list = None

        # Set up the player info
        self.player = None
        self.score = 0

        self.can_move = True

        self.light_layer = None
        self.player_light = None
        self.player_radius = 200

        # Pre-load the animation frames. We don't do this in the __init__
        # of the explosion sprite because it
        # takes too long and would cause the game to pause.
        self.explosion_texture_list = []

        columns = 16
        count = 60
        sprite_width = 256
        sprite_height = 256
        file_name = ":resources:images/spritesheets/explosion.png"

        # Load the explosions from a sprite sheet
        self.explosion_texture_list = arcade.load_spritesheet(file_name, sprite_width, sprite_height, columns, count)

        # Load sounds. Sounds from kenney.nl
        self.gun_sound = arcade.sound.load_sound(":resources:sounds/laser2.wav")
        self.hit_sound = arcade.sound.load_sound(":resources:sounds/explosion2.wav")

        self.a_down = False
        self.d_down = False
        self.s_down = False
        self.w_down = False

        self.VIEW_LEFT = 0 - (SCREEN_WIDTH / 2)
        self.VIEW_BOT = 0 - (SCREEN_HEIGHT / 2)

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.explosions_list = arcade.SpriteList()
        self.wall_list = maps.create_walls()

        # Set up the player
        self.score = 0

        # Image from kenney.nl
        self.player = player.PlayerCharacter()
        self.player.center_x = 0
        self.player.center_y = 0
        self.player_list.append(self.player)
        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.wall_list)

        # Create the coins
        for coin_index in range(COIN_COUNT):

            # Create the coin instance
            # Coin image from kenney.nl
            coin = arcade.Sprite(":resources:images/items/coinGold.png", SPRITE_SCALING_COIN)

            # Position the coin
            coin.center_x = random.randrange(SCREEN_WIDTH)
            coin.center_y = random.randrange(150, SCREEN_HEIGHT)

            # Add the coin to the lists
            self.coin_list.append(coin)

        # Set the background color
        #arcade.set_background_color(arcade.color.CELESTIAL_BLUE)

        # Lighting
        self.light_layer = LightLayer(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.light_layer.set_background_color(arcade.color.CELESTIAL_BLUE)

        # Player lighting
        self.player_light = Light(0, 0, self.player_radius, arcade.csscolor.WHITE, 'soft')
        self.light_layer.add(self.player_light)

    def on_key_press(self, key, modifiers):
        if not self.can_move:
            return

        if key == arcade.key.A:
            self.a_down = True
            self.player.change_x = -PLAYER_SPEED
        elif key == arcade.key.D:
            self.d_down = True
            self.player.change_x = PLAYER_SPEED
        elif key == arcade.key.S:
            self.s_down = True
            self.player.change_y = -PLAYER_SPEED
        elif key == arcade.key.W:
            self.w_down = True
            self.player.change_y = PLAYER_SPEED

    def on_key_release(self, key, modifiers):
        if key == arcade.key.A:
            self.a_down = False
            if not self.d_down:
                self.player.change_x = 0
        elif key == arcade.key.D:
            self.d_down = False
            if not self.a_down:
                self.player.change_x = 0
        elif key == arcade.key.S:
            self.s_down = False
            if not self.w_down:
                self.player.change_y = 0
        elif key == arcade.key.W:
            self.w_down = False
            if not self.s_down:
                self.player.change_y = 0

    def disable_movement(self):
        self.player.change_x = 0
        self.player.change_y = 0
        self.can_move = False

    def enable_movement(self):
        self.can_move = True

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        with self.light_layer:
            self.coin_list.draw()
            self.bullet_list.draw()
            self.player_list.draw()
        self.light_layer.draw(ambient_color=(0, 0, 0))

        self.explosions_list.draw()
        self.wall_list.draw()

        # Render the text
        arcade.draw_text(f"Score: {self.score}", 10, 20, arcade.color.WHITE, 14)

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Called whenever the mouse button is clicked.
        """
        self.shoot()

    def on_update(self, delta_time):
        """ Movement and game logic """

        self.physics_engine.update()
        self.player_list.update_animation()

        # Call update on bullet sprites
        self.bullet_list.update()
        self.explosions_list.update()

        arcade.set_viewport(
            self.VIEW_LEFT + self.player.center_x,
            self.VIEW_LEFT + self.player.center_x + SCREEN_WIDTH,
            self.VIEW_BOT + self.player.center_y,
            self.VIEW_BOT + self.player.center_y + SCREEN_HEIGHT,
        )

        self.player_light.position = self.player.position

        # Loop through each bullet
        for bullet in self.bullet_list:

            # Check this bullet to see if it hit a coin
            hit_list = arcade.check_for_collision_with_list(bullet, self.coin_list)

            # If it did...
            if len(hit_list) > 0:

                # Make an explosion
                explosion = Explosion(self.explosion_texture_list)

                # Move it to the location of the coin
                explosion.center_x = hit_list[0].center_x
                explosion.center_y = hit_list[0].center_y

                # Call update() because it sets which image we start on
                explosion.update()

                # Add to a list of sprites that are explosions
                self.explosions_list.append(explosion)

                # Get rid of the bullet
                bullet.remove_from_sprite_lists()

            # For every coin we hit, add to the score and remove the coin
            for coin in hit_list:
                coin.remove_from_sprite_lists()
                self.score += 1

                # Hit Sound
                arcade.sound.play_sound(self.hit_sound)

            # If the bullet flies off-screen, remove it.
            if bullet.bottom > SCREEN_HEIGHT:
                bullet.remove_from_sprite_lists()


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
