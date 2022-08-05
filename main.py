from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader

# SETTINGS
window.title = 'new zombie game'
app = Ursina()

window.fullscreen = True
window.exit_button.enabled = False
window.cog_button.enabled = False
# MENU

# GRAPHICS
Entity.default_shader = lit_with_shadows_shader

# MAP
ground = Entity(model='plane', collider='box', scale=128, texture='grass', texture_scale=(4,4))

wall_1=Entity(model="cube", collider="box", position=(-8, 0, 0), scale=(8, 5, 1), rotation=(0,0,0),
    texture="brick", texture_scale=(5,5), color=color.rgb(255, 128, 0))
wall_2 = duplicate(wall_1, z=5)
wall_3=duplicate(wall_1, z=10)
wall_4=Entity(model="cube", collider="box", position=(-15, 0, 10), scale=(1,5,20), rotation=(0,0,0),
    texture="brick", texture_scale=(5,5), color=color.rgb(255, 128, 0))

# PLAYER
player = FirstPersonController(model='cube',collider="cube", z=-10, color=color.light_gray, origin_y=-.5, speed=8)
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))

# GUN
gun = Entity(model='assets/models/Beretta.obj', parent=camera, position=Vec3(0.7,-1,1.5), scale=(0.2), origin_z=-5, on_cooldown=False)
gun.muzzle_flash = Entity(parent=gun, z=15, world_scale=1,position=Vec3(0.7,2,9.9), model='quad', color=color.yellow, enabled=False)

shootables_parent = Entity()
mouse.traverse_target = shootables_parent

for i in range(26):
    Entity(model='cube', origin_y=-.15, scale=2, texture='brick', texture_scale=(1,2),
        x=random.uniform(-8,8),
        z=random.uniform(-8,8) + 18,
        collider='box',
        scale_y = random.uniform(2,3),
        color=color.hsv(0, 0, random.uniform(.9, 1))
        )

def update():
    if held_keys['left mouse']:
        shoot()

def shoot():
    if not gun.on_cooldown:
        # print('shoot')
        gun.on_cooldown = True
        gun.muzzle_flash.enabled=True
        from ursina.prefabs.ursfx import ursfx
        ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], wave = 'assets/sounds/gun.wav', )
        invoke(gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.30)
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
enemies = [Enemy(x=x*2) for x in range(16)]

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

# SUN
sun = DirectionalLight()
sun.look_at(Vec3(1,-1,-1))
Sky()

#EXIT
def input(key):
    if key == 'escape':
        quit()

app.run()