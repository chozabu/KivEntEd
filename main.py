from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
import kivent
from random import randint
from math import radians
from kivy.graphics import *

import cymunk as cy
from math import *

import ui_elements


class TestGame(Widget):
    def __init__(self, **kwargs):
        super(TestGame, self).__init__(**kwargs)
        Clock.schedule_once(self.init_game)
        self.asteroids = []
        self.maintools = self.ids['gamescreenmanager'].ids['main_screen'].ids['mainTools']
        self.maintools.setTool("circle")
        self.touches = {0:{"active":False , "pos":(0,0), "screenpos":(0,0)}}
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

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
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        space =self.gameworld.systems['physics'].space
        '''if keycode[1] == 'w':
            self.player1.center_y += 10
        elif keycode[1] == 's':
            self.player1.center_y -= 10
        elif keycode[1] == 'up':
            self.player2.center_y += 10
        el'''
        if keycode[1] == 'up':
            space.gravity = space.gravity.x,space.gravity.y+10
        if keycode[1] == 'down':
            space.gravity = space.gravity.x,space.gravity.y-10
        if keycode[1] == 'left':
            space.gravity = space.gravity.x-10 ,space.gravity.y
        if keycode[1] == 'right':
            space.gravity = space.gravity.x+10 ,space.gravity.y
            print space.gravity
        return True

    def create_asteroid(self, pos, radius=6, mass=10, friction=1.0, elasticity=.5, angle = radians(randint(-360, 360))):
        x_vel = 0#randint(-100, 100)
        y_vel = 0#randint(-100, 100)
        angular_velocity = 0#radians(randint(-150, -150))
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
      
    def create_box(self, pos, width=40, height=40, mass=10, friction=1.0, elasticity=.5, angle = radians(randint(-360, 360))):
        x_vel = 0#randint(-100, 100)
        y_vel = 0#randint(-100, 100)
        
        angular_velocity = 0#radians(randint(-150, -150))
        
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
        #b1 = self.gameworld.entities[asteroidID]
        #b2 = self.gameworld.entities[self.asteroids[-1]]
        #qj = cy.PivotJoint(b1.physics.body, b2.physics.body, b2.physics.body.position)
        #print (b2.physics.shapes[0])
        #b2.physics.shapes[0].group=1
        #b1.physics.shapes[0].group=1
        #self.gameworld.systems['physics'].space.add(qj)
        #print (self.gameworld.systems['physics'].space)
        self.asteroids.append(asteroidID)
        return asteroidID

    def setup_map(self):
        gameworld = self.gameworld
        gameworld.currentmap = gameworld.systems['map']

    def on_touch_move(self, touch):
        if touch.x < self.width*.1:
          print "menu?"
          return
        ctouch = self.touches[touch.id]
        pos = self.getWorldPosFromTouch(touch)
        ctouch['newpos'] = pos
        ctouch['ownbody'].position = pos
        #print super(TestGame, self).on_touch_move(touch)
        #if (self.maintools.currentTool == "circle"):
        #  mass = 0 if self.maintools.staticOn else 3
        #  self.create_asteroid(pos, mass=mass)
        #if (self.maintools.currentTool == "box"):
        #  mass = 0 if self.maintools.staticOn else 3
        #  self.create_box(pos, mass=mass)
        #  print "There are: %i Asteroids" % len(self.asteroids)
        
        if (self.maintools.currentTool == "camera"):
          super(TestGame, self).on_touch_move(touch)
          
        
          
    def on_touch_up(self, touch):
        pos = self.getWorldPosFromTouch(touch)
        ctouch = self.touches[touch.id]
        spos = ctouch['pos']
        
        space =self.gameworld.systems['physics'].space
        if 'mousejoint' in ctouch:
          space.remove(ctouch['mousejoint'])
          
        
        if ctouch['onmenu']:return
        
        if self.maintools.currentTool == "draw" and ctouch["active"]:
          mass = 0 if self.maintools.staticOn else 3
          xd = spos[0]-pos[0]
          yd = spos[1]-pos[1]
          midx = (spos[0]+pos[0])/2.0
          midy = (spos[1]+pos[1])/2.0
          angle = atan2(yd,xd)
          dist= sqrt(xd**2+yd**2)
          if dist<4:dist=8
          print "angle = ",angle
          self.create_box((midx,midy), mass=mass, width=dist, height=10, angle=angle)
      
        if self.maintools.currentTool == "circle" and ctouch["active"]:
          mass = 0 if self.maintools.staticOn else 3
          dist= sqrt((spos[0]-pos[0])**2+(spos[1]-pos[1])**2)
          if dist<4:dist=8
          print dist
          self.create_asteroid(spos, mass=mass, radius=dist)
        if self.maintools.currentTool == "box" and ctouch["active"]:
          mass = 0 if self.maintools.staticOn else 3
          spos = ctouch['pos']
          xd = spos[0]-pos[0]
          yd = spos[1]-pos[1]
          angle = atan2(yd,xd)
          dist= sqrt(xd**2+yd**2)
          if dist<4:dist=8
          print "angle = ",angle
          self.create_box(spos, mass=mass, width=dist*2, height=dist*2, angle=angle)
        self.touches[touch.id] = {"active":False , "newpos":pos, "screenpos":(touch.x,touch.y)}
    def on_touch_down(self, touch):
        pos = self.getWorldPosFromTouch(touch)
        position = cy.Vec2d(pos[0], pos[1])
        space =self.gameworld.systems['physics'].space
        shape = space.point_query_first(position)
        #self.selectedShape = shape
        print "touched shape:", shape
        self.touches[touch.id] = {"active":False , "pos":pos,"newpos":pos, "screenpos":(touch.x,touch.y), "tool":self.maintools.currentTool, "onmenu":False, "touching":shape, "ownbody":cy.Body()}
        if touch.x < self.width*.1:
          self.touches[touch.id]["onmenu"] = True
          super(TestGame, self).on_touch_down(touch)
          print "menu?"
          return
        print self.maintools.currentTool
        self.touches[touch.id]['active'] =  True
        
        #if self.maintools.currentTool == 'draw':
        #  self.touches[touch.id].drawpoints={}
          
        if shape and self.maintools.currentTool == 'del':
          space.remove(shape)
          if shape.body in space.bodies:
            space.remove(shape.body)
        
        if shape and not shape.body.is_static and self.maintools.currentTool == 'drag':
          ctouch=self.touches[touch.id]
          body = ctouch['ownbody']
          body.position = pos
          ctouch['mousejoint'] = cy.PivotJoint(shape.body, body, position)
          space.add(ctouch['mousejoint'])
        
        #if (self.maintools.currentTool == "circle"):
        #  mass = 0 if self.maintools.staticOn else 3
        #  self.create_asteroid(pos, mass=mass)
        #if (self.maintools.currentTool == "box"):
        #  mass = 0 if self.maintools.staticOn else 3
        #  self.create_box(pos, mass=mass)
    def getWorldPosFromTouch(self,touch):
    
        viewport = self.gameworld.systems['gameview']
        return (touch.x- viewport.camera_pos[0],touch.y- viewport.camera_pos[1])
    def update(self, dt):
      if not self.maintools.paused:
        self.gameworld.update(dt)
        for t in self.touches:
          ctouch = self.touches[t]
          if ctouch['active']:
            if ctouch['tool'] == 'vortex':
              self.pull2point(ctouch['newpos'])
    def pull2point(self, pos):
      for aid in self.asteroids:
        asteroid = self.gameworld.entities[aid]
        if asteroid.physics.body.is_static == 0:
          apos = asteroid.position
          dvecx = (pos[0]-apos.x)*asteroid.physics.body.mass*0.1
          dvecy = (pos[1]-apos.y)*asteroid.physics.body.mass*0.1
          asteroid.physics.body.apply_impulse((dvecx,dvecy))
          #asteroid.physics.body.apply_force((dvecx,dvecy))
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
