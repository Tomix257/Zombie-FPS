from ursina import *
from sun import SunLight
from movement import FirstPersonController

# SETTINGS
window.title = 'zombie game'
app = Ursina()

window.fullscreen = True
window.exit_button.disable()
window.cog_button.disable()

# MAP
ground = Entity(model='plane', collider='box', scale=64, texture='grass', texture_scale=(4,4))

wall_1=Entity(model="cube", collider="cube", position=(-9, 0, 0), scale=(8, 5, 1), rotation=(0,0,0),
    texture="brick", texture_scale=(5,5), color=color.rgb(255, 128, 0))
wall_2 = duplicate(wall_1, z=5)
wall_2=duplicate(wall_1, z=10)
wall_2=duplicate(wall_1, z=15)
wall_3=Entity(model="cube", collider="cube", position=(-15, 0, 10), scale=(1,5,20), rotation=(0,0,0),
    texture="brick", texture_scale=(5,5), color=color.rgb(255, 128, 0))


wall_4=Entity(model="cube", collider="cube", position=(9, 0, 0), scale=(8, 5, 1), rotation=(0,0,0),
    texture="brick", texture_scale=(5,5), color=color.rgb(255, 128, 0))
wall_5 = duplicate(wall_4, z=5)
wall_5=duplicate(wall_4, z=10)
wall_5=duplicate(wall_4, z=15)
wall_6=Entity(model="cube", collider="cube", position=(15, 0, 10), scale=(1,5,20), rotation=(0,0,0),
    texture="brick", texture_scale=(5,5), color=color.rgb(255, 128, 0))

wall_7=Entity(model="cube", collider="cube", position=(-5, 0, -20), scale=(20, 5, 1), rotation=(0,0,0),
    texture="brick", texture_scale=(5,5), color=color.rgb(255, 128, 0))

# PLAYER
player = FirstPersonController(model='cube',collider="cube", z=-10, color=color.light_gray, origin_y=-.5, speed=8)
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))

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
        from ursina.prefabs.ursfx import ursfx
        ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], wave = 'assets/sounds/gun.wav', )
        invoke(gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.25)
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 10
            mouse.hovered_entity.blink(color.red)

# HEALTHBAR
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
        hit_info = raycast(self.world_position + Vec3(0,1,0), self.forward, 30, ignore=(self,))
        if hit_info.entity == player:
            if dist > 2:
                self.position += self.forward * time.dt * 5
            if dist < 1.5:
                player.damage()

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value
        if value <= 0:
            destroy(self)
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1

# Enemy()
enemies = [Enemy(x=x*-0.5,z=x*-0.5) for x in range(10)]
    

# PAUSE
pause_handler = Entity(ignore_paused=True)
pause_text = Text('PAUSED', origin=(0,0), scale=2, enabled=False) # Make a Text saying "PAUSED" just to make it clear when it's paused.

def pause_handler_input(key):
    if key == 'p':
        application.paused = not application.paused # Pause/unpause the game.
        pause_text.enabled = application.paused     # Also toggle "PAUSED" graphic.

pause_handler.input = pause_handler_input   # Assign the input function to the pause handler.


# TEXT
Text('EARLY RELEASE!',color=color.yellow, origin=(4,2))
# Lighting + shadows
sun = SunLight(direction = (-0.7, -0.9, 0.5), resolution = 3072, player = player)
ambient = AmbientLight(color = Vec4(0.5, 0.55, 0.66, 0) * 1.5)

render.setShaderAuto()
# SKY
Sky(texture = "assets/textures/sky")

#EXIT
def input(key):
    if key == 'escape':
        quit()

app.run()