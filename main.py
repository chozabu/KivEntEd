from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
import kivent
from random import randint
from math import radians
from kivy.graphics import *

import ui_elements


class TestGame(Widget):
    def __init__(self, **kwargs):
        super(TestGame, self).__init__(**kwargs)
        Clock.schedule_once(self.init_game)
        self.asteroids = []
        self.maintools = self.ids['gamescreenmanager'].ids['main_screen'].ids['mainTools']
        self.maintools.setTool("circle")

    def init_game(self, dt):
        self.setup_map()
        self.setup_states()
        self.set_state()
        self.draw_some_stuff()
        Clock.schedule_interval(self.update, 0)

    def draw_some_stuff(self):
        size = Window.size
        for x in range(50):
            pos = (randint(0, size[0]), randint(0, size[1]))
            self.create_asteroid(pos)

    def create_asteroid(self, pos, radius=20, mass=10, friction=1.0, elasticity=.5):
        x_vel = randint(-100, 100)
        y_vel = randint(-100, 100)
        angle = radians(randint(-360, 360))
        angular_velocity = radians(randint(-150, -150))
        shape_dict = {'inner_radius': 0, 'outer_radius': radius, 
            'mass': mass, 'offset': (0, 0)}
        col_shape = {'shape_type': 'circle', 'elasticity': elasticity, 
            'collision_type': 1, 'shape_info': shape_dict, 'friction': friction}
        col_shapes = [col_shape]
        physics_component = {'main_shape': 'circle', 
            'velocity': (x_vel, y_vel), 
            'position': pos, 'angle': angle, 
            'angular_velocity': angular_velocity, 
            'vel_limit': 1024, 
            'ang_vel_limit': radians(200), 
            'mass': mass, 'col_shapes': col_shapes}
        create_component_dict = {'physics': physics_component, 
            'physics_renderer': {'texture': 'circle', 'size': (radius*2 , radius*2)}, 
            'position': pos, 'rotate': 0}
        component_order = ['position', 'rotate', 
            'physics', 'physics_renderer']
        asteroidID = self.gameworld.init_entity(create_component_dict, component_order)
        self.asteroids.append(asteroidID)
        return asteroidID
      
    def create_box(self, pos, width=40, height=40, mass=10, friction=1.0, elasticity=.5):
        x_vel = randint(-100, 100)
        y_vel = randint(-100, 100)
        angle = radians(randint(-360, 360))
        angular_velocity = radians(randint(-150, -150))
        
        '''aview_dict = {'vertices': [(0., 0.), (0.0, width), 
            (height, width), (height, 0.0)],
            'offset': (height/2., -width/2.)}
        acol_shape_dict = {'shape_type': 'box', 'elasticity': .5, 
            'collision_type': 2, 'shape_info': box_dict, 'friction': 1.0}
        '''
        box_dict = {
            'width': width, 
            'height': height,
            'mass': mass}
        #shape_dict = {'inner_radius': 0, 'outer_radius': radius, 
        #    'mass': mass, 'offset': (0, 0)}
        col_shape = {'shape_type': 'box', 'elasticity': elasticity, 
            'collision_type': 1, 'shape_info': box_dict, 'friction': friction}
        col_shapes = [col_shape]
        physics_component = {'main_shape': 'box', 
            'velocity': (x_vel, y_vel), 
            'position': pos, 'angle': angle, 
            'angular_velocity': angular_velocity, 
            'vel_limit': 1024, 
            'ang_vel_limit': radians(200), 
            'mass': mass, 'col_shapes': col_shapes}
        create_component_dict = {'physics': physics_component, 
            'physics_renderer': {'texture': 'square', 'size': (width , height)}, 
            'position': pos, 'rotate': 0}
        component_order = ['position', 'rotate', 
            'physics', 'physics_renderer']
        asteroidID = self.gameworld.init_entity(create_component_dict, component_order)
        self.asteroids.append(asteroidID)
        return asteroidID

    def setup_map(self):
        gameworld = self.gameworld
        gameworld.currentmap = gameworld.systems['map']

    def on_touch_move(self, touch):
        if touch.x < min(self.width*.25, 300):
          print "menu?"
          return
        #print super(TestGame, self).on_touch_move(touch)
        pos = (touch.x, touch.y)
        if (self.maintools.currentTool == "circle"):
          self.create_asteroid(pos)
          print "There are: %i Asteroids" % len(self.asteroids)
        
        if (self.maintools.currentTool == "camera"):
          super(TestGame, self).on_touch_move(touch)
          
        if (self.maintools.currentTool == "vortex"):
          for aid in self.asteroids:
            asteroid = self.gameworld.entities[aid]
            apos = asteroid.position
            dvecx = (touch.x-apos.x)*asteroid.physics.body.mass*0.1
            dvecy = (touch.y-apos.y)*asteroid.physics.body.mass*0.1
            asteroid.physics.body.apply_impulse((dvecx,dvecy))
    def on_touch_down(self, touch):
        print self.maintools.currentTool
        if touch.x < min(self.width*.25, 300):
          super(TestGame, self).on_touch_down(touch)
          print "menu?"
          return
        pos = (touch.x, touch.y)
        if (self.maintools.currentTool == "circle"):
          self.create_asteroid(pos)
        if (self.maintools.currentTool == "box"):
          self.create_box(pos)
    def update(self, dt):
        self.gameworld.update(dt)
        systems = self.gameworld.systems
        print systems
        viewport = systems['gameview']
        print dir(viewport)
        print viewport.camera_pos

    def setup_states(self):
        self.gameworld.add_state(state_name='main', 
            systems_added=['renderer', 'physics_renderer'],
            systems_removed=[], systems_paused=[],
            systems_unpaused=['renderer', 'physics_renderer'],
            screenmanager_screen='main')

    def set_state(self):
        self.gameworld.state = 'main'


class YourAppNameApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1.)


if __name__ == '__main__':
    YourAppNameApp().run()
