from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
import kivent
from random import randint
from random import random
from math import radians
from kivy.graphics import *

import cymunk as cy
from math import *

import os

import ui_elements


class TestGame(Widget):
    def __init__(self, **kwargs):
        super(TestGame, self).__init__(**kwargs)
        Clock.schedule_once(self.init_game)
        self.asteroids = []
        self.maintools = self.ids['gamescreenmanager'].ids['main_screen'].ids['mainTools']
        self.maintools.setTool("draw")
        self.touches = {0:{"active":False , "pos":(0,0), "screenpos":(0,0)}}
        try: 
            self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
        except:
            print 'Python python no keyboard'

    def init_game(self, dt):
        try: 
            self._init_game(0)
        except e:
            print 'failed: rescheduling init'
            Clock.schedule_once(self.init_game)
    def _init_game(self, dt):
        self.setup_map()
        self.setup_states()
        self.set_state()
        
        
        self.draw_some_stuff()
        Clock.schedule_interval(self.update, 0)
        Clock.schedule_once(self.init_sprites)
    def init_sprites(self, dt):
        usprites = self.gameworld.systems['renderer'].uv_dict.keys()
        sprites = []
        print usprites
        for k in usprites:
          print k
          if k!='atlas_size' and k!='main_texture' :sprites.append(str(k))
        self.maintools.spriteSpinner.values = sprites
      

    def draw_some_stuff(self):
        size = Window.size
        for x in range(50):
            pos = (randint(size[0]/3, size[0]), randint(0, size[1]))
            self.create_circle(pos,y_vel=random()*-20, texture="sheep")
        self.create_box((size[0]/2.0,0), mass=0, width=size[0]*2, height=10, angle=0)
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

    def create_circle(self, pos, radius=6, mass=10, friction=1.0, elasticity=.5, angle = 0, x_vel=0,y_vel=0,angular_velocity=0, texture="sheep"):
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
            'physics_renderer': {'texture': texture, 'size': (radius*2 , radius*2)}, 
            'position': pos, 'rotate': 0}
        component_order = ['position', 'rotate', 
            'physics', 'physics_renderer']
        asteroidID = self.gameworld.init_entity(create_component_dict, component_order)
        self.asteroids.append(asteroidID)
        return asteroidID
      
    def create_box(self, pos, width=40, height=40, mass=10, friction=1.0, elasticity=.5, angle = 0, x_vel=0,y_vel=0,angular_velocity=0, texture="face_box"):
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
            'physics_renderer': {'texture': texture, 'size': (width , height)}, 
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
        #if touch.x < self.width*.1:
        #  #print "menu?"
        #  return
        space =self.gameworld.systems['physics'].space
        ctouch = self.touches[touch.id]
        pos = self.getWorldPosFromTouch(touch)
        spos = ctouch['pos']
        ctouch['newpos'] = pos
        ctouch['ownbody'].position = pos
        #print super(TestGame, self).on_touch_move(touch)
        #if (self.maintools.currentTool == "circle"):
        #  mass = 0 if self.maintools.staticOn else 3
        #  self.create_circle(pos, mass=mass)
        #if (self.maintools.currentTool == "box"):
        #  mass = 0 if self.maintools.staticOn else 3
        #  self.create_box(pos, mass=mass)
        #  print "There are: %i Asteroids" % len(self.asteroids)
        #print dir(touch)
        if (ctouch['tool'] == "camera"):
          super(TestGame, self).on_touch_move(touch)
        
        if ctouch['tool'] == "draw" and ctouch["active"]:
          mass = self.maintools.massSlider.value #0 if self.maintools.staticOn else 3
          xd = spos[0]-pos[0]
          yd = spos[1]-pos[1]
          dist= sqrt(xd**2+yd**2)
          if dist > 10:
            midx = (spos[0]+pos[0])/2.0
            midy = (spos[1]+pos[1])/2.0
            angle = atan2(yd,xd)
            print "angle = ",angle
            self.create_box((midx,midy), mass=mass, width=dist, height=10, angle=angle,texture=self.maintools.spriteSpinner.text)
            ctouch['pos'] = pos
            
        shape = ctouch['touching']
        if shape and shape.body.is_static and (ctouch['tool'] == 'drag'):
            shape.body.position=(shape.body.position.x+touch.dx,shape.body.position.y+touch.dy)
            space.reindex_shape(shape)
          
        
          
    def on_touch_up(self, touch):
        pos = self.getWorldPosFromTouch(touch)
        ctouch = self.touches[touch.id]
        spos = ctouch['pos']
        
        space =self.gameworld.systems['physics'].space
        position = cy.Vec2d(pos[0], pos[1])
        shape = space.point_query_first(position)
        
        if 'mousejoint' in ctouch and (ctouch['tool'] != "pin"):
          space.remove(ctouch['mousejoint'])
        
        
        if ctouch['onmenu']:return
        
        tshape = ctouch['touching']
        if tshape and shape:
          if ctouch['tool'] == 'c2p':
            b1 = ctouch['touching'].body#self.gameworld.entities[asteroidID]
            b2 = shape.body#self.gameworld.entities[self.asteroids[-1]]
            b2l = b2.world_to_local(position)
            print b2l
            #qj = cy.PivotJoint(b1, b2, pos)
            qj = cy.PinJoint(b1, b2, (0,0), (b2l['x'], b2l['y']))#, (b1.position.x,b1.position.y),(b2.position.x,b2.position.y))
            space.add(qj)
            
          if ctouch['tool'] == 'p2p':
            b1 = ctouch['touching'].body#self.gameworld.entities[asteroidID]
            b2 = shape.body#self.gameworld.entities[self.asteroids[-1]]
            b2l = b2.world_to_local(position)
            b1l = b1.world_to_local(cy.Vec2d(spos[0], spos[1]))
            print b2l
            #qj = cy.PivotJoint(b1, b2, pos)
            qj = cy.PinJoint(b1, b2, (b1l['x'], b1l['y']), (b2l['x'], b2l['y']))#, (b1.position.x,b1.position.y),(b2.position.x,b2.position.y))
            space.add(qj)
            
          if ctouch['tool'] == 'p2ps':
            b1 = ctouch['touching'].body#self.gameworld.entities[asteroidID]
            b2 = shape.body#self.gameworld.entities[self.asteroids[-1]]
            sposition = cy.Vec2d(spos[0], spos[1])
            b2l = b2.world_to_local(position)
            b1l = b1.world_to_local(sposition)
            dvec = cy.Vec2d(position.x-sposition.x,position.y-sposition.y)
            dist= sqrt(dvec.x**2+dvec.y**2)
            qj = cy.DampedSpring(b1, b2, (b1l['x'], b1l['y']), (b2l['x'], b2l['y']),dist,100,0.1)#, (b1.position.x,b1.position.y),(b2.position.x,b2.position.y))
            space.add(qj)
            
          if ctouch['tool'] == 'c2c':
            b1 = shape.body#self.gameworld.entities[asteroidID]
            b2 = ctouch['touching'].body#self.gameworld.entities[self.asteroids[-1]]
            qj = cy.PinJoint(b1, b2, (0,0), (0,0))#, (b1.position.x,b1.position.y),(b2.position.x,b2.position.y))
            #b2.physics.shapes[0].group=1
            #b1.physics.shapes[0].group=1
            space.add(qj)
        
        if (ctouch['tool'] == "draw" or ctouch['tool'] == "plank") and ctouch["active"]:
          mass = self.maintools.massSlider.value #0 if self.maintools.staticOn else 3
          xd = spos[0]-pos[0]
          yd = spos[1]-pos[1]
          midx = (spos[0]+pos[0])/2.0
          midy = (spos[1]+pos[1])/2.0
          angle = atan2(yd,xd)
          dist= sqrt(xd**2+yd**2)
          if dist<4:dist=8
          print "angle = ",angle
          self.create_box((midx,midy), mass=mass, width=dist, height=10, angle=angle, texture=self.maintools.spriteSpinner.text)
      
        if ctouch['tool'] == "circle" and ctouch["active"]:
          mass = self.maintools.massSlider.value #0 if self.maintools.staticOn else 3
          dist= sqrt((spos[0]-pos[0])**2+(spos[1]-pos[1])**2)
          if dist<4:dist=8
          print dist
          self.create_circle(spos, mass=mass, radius=dist, texture=self.maintools.spriteSpinner.text)
        if ctouch['tool'] == "box" and ctouch["active"]:
          mass = self.maintools.massSlider.value #0 if self.maintools.staticOn else 3
          spos = ctouch['pos']
          xd = max(5, abs(spos[0]-pos[0]))
          yd = max(5, abs(spos[1]-pos[1]))
          midx = (spos[0]+pos[0])/2.0
          midy = (spos[1]+pos[1])/2.0
          #angle = atan2(yd,xd)
          #dist= sqrt(xd**2+yd**2)
          #if dist<4:dist=8
          #print "angle = ",angle
          self.create_box((midx,midy), mass=mass, width=xd, height=yd, angle=0, texture=self.maintools.spriteSpinner.text)
        if ctouch['tool'] == "square" and ctouch["active"]:
          mass = self.maintools.massSlider.value #0 if self.maintools.staticOn else 3
          spos = ctouch['pos']
          xd = spos[0]-pos[0]
          yd = spos[1]-pos[1]
          angle = atan2(yd,xd)
          dist= sqrt(xd**2+yd**2)
          if dist<4:dist=8
          print "angle = ",angle
          self.create_box(spos, mass=mass, width=dist*2, height=dist*2, angle=angle, texture=self.maintools.spriteSpinner.text)
        self.touches[touch.id] = {"active":False , "newpos":pos, "screenpos":(touch.x,touch.y)}
    def on_touch_down(self, touch):
        print "TOUCHDOWN\n"
        #print os.listdir("./sprites")
        pos = self.getWorldPosFromTouch(touch)
        position = cy.Vec2d(pos[0], pos[1])
        space =self.gameworld.systems['physics'].space
        shape = space.point_query_first(position)
        #self.selectedShape = shape
        print "touched shape:", shape
        self.touches[touch.id] = {"active":False , "pos":pos,"newpos":pos, "screenpos":(touch.x,touch.y), "tool":self.maintools.currentTool, "onmenu":False, "touching":shape, "ownbody":cy.Body()}
        if self.maintools.on_touch_down(touch):#True:#touch.x < self.width*.1:
          self.touches[touch.id]["onmenu"] = True
          #sresult = super(TestGame, self).on_touch_down(touch)
          print "clicked in menu"
          return
        print self.maintools.currentTool
        self.touches[touch.id]['active'] =  True
        
        #if self.maintools.currentTool == 'draw':
        #  self.touches[touch.id].drawpoints={}
          
        if shape and self.maintools.currentTool == 'del':
          #print dir(shape)
          #print dir(shape.body)
          #self.gameworld.remove_entity(howdoigetIDfromshape?)
          space.remove(shape)
          if shape.body in space.bodies:
            space.remove(shape.body)
        
        if shape and not shape.body.is_static and (self.maintools.currentTool == 'drag' or self.maintools.currentTool == 'pin'):
          ctouch=self.touches[touch.id]
          body = ctouch['ownbody']
          body.position = pos
          ctouch['mousejoint'] = cy.PivotJoint(shape.body, body, position)
          space.add(ctouch['mousejoint'])
        
        #if (self.maintools.currentTool == "circle"):
        #  mass = 0 if self.maintools.staticOn else 3
        #  self.create_circle(pos, mass=mass)
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
          dvecx = (pos[0]-apos.x)*asteroid.physics.body.mass*0.02
          dvecy = (pos[1]-apos.y)*asteroid.physics.body.mass*0.02
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
