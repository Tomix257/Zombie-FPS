from ursina import *
from sun import SunLight
from player import Player
from main_menu import MainMenu


# SETTINGS
window.title = 'zombie game'
app = Ursina()

window.fullscreen = True
window.exit_button.disable()
window.cog_button.disable()

# MAP
ground = Entity(model='plane', collider='box', scale=64, texture='grass', texture_scale=(4,4),ignore=True)

wall_1=Entity(model="cube", collider="cube", position=(-9, 0, 0), scale=(8, 5, 1), rotation=(0,0,0),
    texture="brick", texture_scale=(5,5), color=color.rgb(255, 128, 0),ignore=True)
wall_2 = duplicate(wall_1, z=5)
wall_2=duplicate(wall_1, z=10)
wall_2=duplicate(wall_1, z=15)
wall_3=Entity(model="cube", collider="cube", position=(-15, 0, 10), scale=(1,5,20), rotation=(0,0,0),
    texture="brick", texture_scale=(5,5), color=color.rgb(255, 128, 0),ignore=True)
wall_4=Entity(model="cube", collider="cube", position=(9, 0, 0), scale=(8, 5, 1), rotation=(0,0,0),
    texture="brick", texture_scale=(5,5), color=color.rgb(255, 128, 0),ignore=True)
wall_5 = duplicate(wall_4, z=5)
wall_5=duplicate(wall_4, z=10)
wall_5=duplicate(wall_4, z=15)
wall_6=Entity(model="cube", collider="cube", position=(15, 0, 10), scale=(1,5,20), rotation=(0,0,0),
    texture="brick", texture_scale=(5,5), color=color.rgb(255, 128, 0),ignore=True)
wall_7=Entity(model="cube", collider="cube", position=(-5, 0, -20), scale=(20, 5, 1), rotation=(0,0,0),
    texture="brick", texture_scale=(5,5), color=color.rgb(255, 128, 0),ignore=True)
wall_8=Entity(model="cube", collider="cube", position=(5, 0, 20), scale=(20, 5, 1), rotation=(0,0,0),
    texture="brick", texture_scale=(5,5), color=color.rgb(255, 128, 0),ignore=True)

# PLAYER
player = Player(collider="box", z=-18, color=color.light_gray)
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))

player.disable()
main_menu = MainMenu(player)
# GUN
gun = Entity(model='assets/models/Beretta.obj', parent=camera, position=Vec3(0.7,-1,1.5), scale=(0.2), origin_z=-5, on_cooldown=False)
gun.muzzle_flash = Entity(parent=gun, z=15, world_scale=0.8,position=Vec3(0.7,2,9.9), model='quad', color=color.yellow, enabled=False)

shootables_parent = Entity()
mouse.traverse_target = shootables_parent

def update():
    if held_keys['left mouse']:
        shoot()

def shoot():
    if not gun.on_cooldown:
        gun.on_cooldown = True
        gun.muzzle_flash.enabled=True
        shooting =Audio('assets/sounds/gun.wav',loop = False)
        invoke(gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.25)
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 10
            mouse.hovered_entity.blink(color.red)

# ENEMY
from ursina.prefabs.health_bar import HealthBar

class Enemy(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=shootables_parent, model='cube', scale_y=2, origin_y=-.5, color=color.green, collider='box', **kwargs)
        self.health_bar = Entity(parent=self, y=1.2, model='cube', color=color.red, world_scale=(1.5,.1,.1))
        self.max_hp = 100
        self.hp = self.max_hp

    def update(self):
        dist = distance_xz(player.position, self.position)
        if dist > 40:
            return

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)

        self.look_at_2d(player.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0,1,0), self.forward, 50, ignore=(self,))
        if hit_info.entity == player:
            if dist > 2:
                self.position += self.forward * time.dt * 5
            if dist < 2:
                player.damage()

    @property

    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value
        if value <= 0:
            destroy(self)
            player.shot_enemy()
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1

# Enemy()
enemies = [Enemy(x=random.randint(-3,10),z=random.randint(-3,10)) for x in range(12)]

# PAUSE
pause_handler = Entity(ignore_paused=True)
pause_text = Text('PAUSED', origin=(0,0), scale=2, enabled=False) # Make a Text saying "PAUSED" just to make it clear when it's paused.

def pause_handler_input(key):
    if key == 'p':
        application.paused = not application.paused # Pause/unpause the game.
        pause_text.enabled = application.paused     # Also toggle "PAUSED" graphic.

pause_handler.input = pause_handler_input   # Assign the input function to the pause handler.

# Lighting + shadows
sun = SunLight(direction = (-0.7, -0.9, 0.5), resolution = 3072, player = player)
ambient = AmbientLight(color = Vec4(0.5, 0.55, 0.66, 0) * 1.5)

render.setShaderAuto()

# SKY

Sky(texture = "assets/textures/sky")

# RESUME MENU
def input(key):
    if main_menu.main_menu.enabled == False:
        if key == "escape":
            main_menu.pause_menu.enabled = not main_menu.pause_menu.enabled
            mouse.locked = not mouse.locked  

app.run()