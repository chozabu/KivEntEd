from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
import kivent
from random import randint
from random import random
from math import radians
from kivy.graphics import *

from kivy.atlas import Atlas

import json
import os
import cymunk as cy
from math import *

import os

import ui_elements


class TestGame(Widget):
    def __init__(self, **kwargs):
        super(TestGame, self).__init__(**kwargs)
        Clock.schedule_once(self.init_game)
        self.entIDs = []
        self.maintools = self.ids['gamescreenmanager'].ids['main_screen'].ids['mainTools']
        #self.maintools.setTool("draw")
        self.maintools.drawPressed(None)
        self.maintools.setRef(self)
        self.startID = -1
        self.finishID = -1
        self.touches = {0:{"active":False , "pos":(0,0), "screenpos":(0,0)}}
        self.atlas = Atlas('assets/myatlas.atlas')
        try:
            self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
        except:
            print 'Python python no keyboard'

    def init_game(self, dt):
        try:
            self._init_game(0)
        except:
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
        #self.gameworld.systems['renderer'].do_rotate = True
        #self.gameworld.systems['renderer'].on_do_rotate(None,None)
        usprites = self.gameworld.systems['renderer'].uv_dict.keys()
        sprites = []
        print usprites
        for k in usprites:
          print k
          if k!='atlas_size' and k!='main_texture' :sprites.append(str(k))
        self.maintools.spriteSpinner.values = sprites
        self.maintools.selectedMenu.texLabel.values = sprites
    def reindexEntID(self, entityID):
      self.reindexEnt(self.gameworld.entities[entityID])
    def reindexEnt(self, entity):
      space =self.gameworld.systems['physics'].space
      if entity and hasattr(entity, "physics"):
        for s in entity.physics.shapes:
              space.reindex_shape(s)

    def draw_some_stuff(self):
        size = Window.size
        for x in range(50):
            pos = (randint(size[0]/3, size[0]), randint(0, size[1]))
            self.create_circle(pos,y_vel=random()*-20, texture="sheep", radius=15)
        self.create_box((size[0]/2.0,0), mass=0, width=size[0]*2, height=10, angle=0)
    def _keyboard_closed(self):
        try:
          self._keyboard.unbind(on_key_down=self._on_keyboard_down)
          self._keyboard = None
        except:
          print "still no keyboard!"

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        space =self.gameworld.systems['physics'].space
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

    def create_decoration(self, pos=(0,0), width=40, height=40, angle = 0, texture="sheep"):
        create_component_dict = {
            'renderer': {'texture': texture, 'size': (width , height)},
            'position': pos, 'rotate': 0}
        component_order = ['position', 'rotate', 'renderer']
        entityID = self.gameworld.init_entity(create_component_dict, component_order)
        return entityID
    def create_circle(self, pos, radius=6, mass=10, friction=1.0, elasticity=.5, angle = 0, x_vel=0,y_vel=0,angular_velocity=0, texture="sheep",selectNow = True):
        shape_dict = {'inner_radius': 0, 'outer_radius': radius,
            'mass': mass, 'offset': (0, 0)}
        col_shape = {'shape_type': 'circle', 'elasticity': elasticity,
            'collision_type': 1, 'shape_info': shape_dict, 'friction': friction}
        col_shapes = [col_shape]
        physics_component = {'main_shape': 'circle',
            'velocity': (x_vel, y_vel),
            'position': pos, 'angle': angle,
            'angular_velocity': angular_velocity,
            'vel_limit': 2048,
            'ang_vel_limit': radians(2000),
            'mass': mass, 'col_shapes': col_shapes}
        create_component_dict = {'physics': physics_component,
            'physics_renderer': {'texture': texture, 'size': (radius*2 , radius*2)},
            'position': pos, 'rotate': 0}
        component_order = ['position', 'rotate',
            'physics', 'physics_renderer']
        entityID = self.gameworld.init_entity(create_component_dict, component_order)
        self.entIDs.append(entityID)
        if self.maintools.paused: (self.gameworld.systems['physics'].update(0.00001))
        if selectNow: self.maintools.setShape(self.gameworld.entities[entityID].physics.shapes[0])
        return entityID

    def create_box(self, pos, width=40, height=40, mass=10, friction=1.0, elasticity=.5, angle = 0, x_vel=0,y_vel=0,angular_velocity=0, texture="face_box",selectNow = True):
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
            'vel_limit': 2048,
            'ang_vel_limit': radians(2000),
            'mass': mass, 'col_shapes': col_shapes}
        create_component_dict = {'physics': physics_component,
            'physics_renderer': {'texture': texture, 'size': (width , height)},
            'position': pos, 'rotate': 0}
        component_order = ['position', 'rotate',
            'physics', 'physics_renderer']
        entityID = self.gameworld.init_entity(create_component_dict, component_order)
        #b1 = self.gameworld.entities[entityID]
        #b2 = self.gameworld.entities[self.entIDs[-1]]
        #qj = cy.PivotJoint(b1.physics.body, b2.physics.body, b2.physics.body.position)
        #print (b2.physics.shapes[0])
        #b2.physics.shapes[0].group=1
        #b1.physics.shapes[0].group=1
        #self.gameworld.systems['physics'].space.add(qj)
        #print (self.gameworld.systems['physics'].space)
        self.entIDs.append(entityID)
        if self.maintools.paused: (self.gameworld.systems['physics'].update(0.00001))
        if selectNow: self.maintools.setShape(self.gameworld.entities[entityID].physics.shapes[0])
        return entityID

    def setup_map(self):
        gameworld = self.gameworld
        gameworld.currentmap = gameworld.systems['map']

    def on_touch_move(self, touch):
        self.maintools.on_touch_move(touch)
        #if touch.x < self.width*.1:
        #  #print "menu?"
        #  return
        space =self.gameworld.systems['physics'].space
        ctouch = self.touches[touch.id]
        pos = self.getWorldPosFromTouch(touch)
        spos = ctouch['pos']
        ctouch['newpos'] = pos
        ctouch['ownbody'].position = pos


        position = cy.Vec2d(pos[0], pos[1])
        shape = space.point_query_first(position)
        ctouch['touchingnow'] = shape

        #print super(TestGame, self).on_touch_move(touch)
        #if (self.maintools.currentTool == "circle"):
        #  mass = 0 if self.maintools.staticOn else 3
        #  self.create_circle(pos, mass=mass)
        #if (self.maintools.currentTool == "box"):
        #  mass = 0 if self.maintools.staticOn else 3
        #  self.create_box(pos, mass=mass)
        #  print "There are: %i Asteroids" % len(self.entIDs)
        #print dir(touch)
        if ctouch['tool'] == "camera":
          super(TestGame, self).on_touch_move(touch)

        #a = self.gameworld.entities[ctouch['previewShape']]
        #print dir(self.gameworld.systems['renderer'])
        #self.gameworld.systems['renderer'].do_rotate = True
        if ctouch['tool'] == "box" and ctouch["active"]:
          xd = spos[0]-pos[0]
          yd = spos[1]-pos[1]
          midx = (spos[0]+pos[0])/2.0
          midy = (spos[1]+pos[1])/2.0
          prect = self.gameworld.entities[ctouch['previewShape']]
          prect.position.x = midx#(midx,midy)
          prect.position.y = midy#(midx,midy)
          prect.renderer.width = xd
          prect.renderer.height = yd
        if ctouch['tool'] == "circle" and ctouch["active"]:
          xd = spos[0]-pos[0]
          yd = spos[1]-pos[1]
          dist= sqrt(xd**2+yd**2)
          prect = self.gameworld.entities[ctouch['previewShape']]
          prect.position.x = spos[0]#(midx,midy)
          prect.position.y = spos[1]#(midx,midy)
          angle = atan2(yd,xd)
          prect.rotate.r = angle
          prect.renderer.width = dist*2
          prect.renderer.height = dist*2
        if ctouch['tool'] == "square" and ctouch["active"]:
          xd = spos[0]-pos[0]
          yd = spos[1]-pos[1]
          dist= sqrt(xd**2+yd**2)
          prect = self.gameworld.entities[ctouch['previewShape']]
          prect.position.x = spos[0]#(midx,midy)
          prect.position.y = spos[1]#(midx,midy)
          angle = atan2(yd,xd)
          prect.rotate.r = angle
          prect.renderer.width = dist*2
          prect.renderer.height = dist*2
        if ctouch['tool'] == "plank" and ctouch["active"]:
          xd = spos[0]-pos[0]
          yd = spos[1]-pos[1]
          dist= sqrt(xd**2+yd**2)
          midx = (spos[0]+pos[0])/2.0
          midy = (spos[1]+pos[1])/2.0
          angle = atan2(yd,xd)
          prect = self.gameworld.entities[ctouch['previewShape']]
          prect.position.x = midx#(midx,midy)
          prect.position.y = midy#(midx,midy)
          prect.rotate.r = angle
          prect.renderer.height = 10
          prect.renderer.width = dist
        if ctouch['tool'] == "draw" and ctouch["active"]:
          mass = self.maintools.massSlider.value #0 if self.maintools.staticOn else 3
          xd = spos[0]-pos[0]
          yd = spos[1]-pos[1]
          dist= sqrt(xd**2+yd**2)
          prect = self.gameworld.entities[ctouch['previewShape']]
          midx = (spos[0]+pos[0])/2.0
          midy = (spos[1]+pos[1])/2.0
          angle = atan2(yd,xd)
          prect.position.x = midx#(midx,midy)
          prect.position.y = midy#(midx,midy)
          prect.rotate.r = angle
          prect.renderer.height = 10
          prect.renderer.width = dist
          #prect.size = (10,dist)
          print dir(prect.renderer)
          if dist > 10:
            print "angle = ",angle
            self.create_box((midx,midy), mass=mass, width=dist, height=10, angle=angle,texture=self.maintools.spriteSpinner.text)
            ctouch['pos'] = pos

        shape = ctouch['touching']
        if shape and (shape.body.is_static or self.maintools.paused) and (ctouch['tool'] == 'drag'):
            shape.body.position=(shape.body.position.x+touch.dx,shape.body.position.y+touch.dy)
            self.reindexEntID(shape.body.data)
            if self.maintools.paused:
              (self.gameworld.systems['physics'].update(0.00000001))
              (self.gameworld.systems['physics_renderer'].update(0.00000001))
              (self.gameworld.systems['renderer'].update(0.00000001))
            #space.reindex_shape(shape)

    def shapeToDict(self, shape):
      sd = {'collision_type':shape.collision_type, 'elasticity':shape.elasticity, 'friction':shape.friction, 'group':shape.group}
      if hasattr(shape, "radius"):
        sd['radius'] = shape.radius
      else:
        sd['width'] = shape.width
        sd['height'] = shape.height
      return sd
    def entToDict(self, e):
      ed = {"orig_id": e.entity_id}
      #print dir(e)
      #print (e.entity_id)
      #'load_order', 'physics', 'physics_renderer', 'position', 'rotate'
      if hasattr(e, "load_order"):
        #print e.load_order
        ed["load_order"] = e.load_order
      if hasattr(e, "physics"):
        #print dir(e.physics)
        b = e.physics.body
        #for item in dir(b):
        #  print item, getattr(b, item)
        bd = {'velocity': (b.velocity.x, b.velocity.y),
          'position': (b.position.x,b.position.y),
          'angle': b.angle,
          'angular_velocity': b.angular_velocity,
          'vel_limit': b.velocity_limit,
          'ang_vel_limit': b.angular_velocity_limit,
          'mass': b.mass
          }
        #print (e.physics.shape_type)
        shapes = []
        for s in e.physics.shapes:
          #print s
          #print dir(s)
          shapes.append(self.shapeToDict(s))
        pd = {"shapes": shapes, "shape_type":e.physics.shape_type ,"body":bd }
        ed["physics"] = pd
      if hasattr(e, "physics_renderer"):
        #print dir(e.physics_renderer)
        prd = {"width":e.physics_renderer.width,"height":e.physics_renderer.height, "texture":e.physics_renderer.texture}
        ed["physics_renderer"] = prd
      if hasattr(e, "position"):
        #print dir(e.position)
        pd = {"x":e.position.x,"y":e.position.y}
        ed["position"] = pd
      if hasattr(e, "rotate"):
        rd = {"r":e.rotate.r}
        ed["rotate"] = rd
        #print dir(e.rotate.r)
      return ed
    def exportJointsToDicts(self):
      space =self.gameworld.systems['physics'].space
      jds = []
      for j in space.constraints:
        jtype = j.__class__.__name__
        print jtype
        print dir(j)
        anchor1 = j.anchor1
        #if None == j.a.data and j.a != space.static_body:
        #  anchor1 = {'x':j.a.position.x, 'y':j.a.position.y}

        anchor2 = j.anchor2
        if anchor2['x'] == 0 and anchor2['y'] == 0 and j.b.data is None:
          anchor2 = {'x':j.b.position.x, 'y':j.b.position.y}
        jd = {"type":jtype,"a":j.a.data, "b":j.b.data,
              "anchor1":anchor1,"anchor2":anchor2}
        if jtype == "DampedSpring":
          jd['rest_length'] = j.rest_length
          jd['stiffness'] = j.stiffness
          jd['damping'] = j.damping
        jds.append(jd)
      return jds
    def exportEntsToDicts(self):
      entsdict = []
      for eid in self.entIDs:
        e = self.gameworld.entities[eid]
        #print "\n"
        ed = self.entToDict(e)
        entsdict.append(ed)
      return entsdict
    def exportJSON(self, fileName="defaultlevel.json"):
      global dataDir
      entslist = self.exportEntsToDicts()
      jointslist = self.exportJointsToDicts()
      #print dir(space.constraints[0])
      space =self.gameworld.systems['physics'].space
      worlddict = {"ents":entslist,"jointslist":jointslist,"settings":{"gravity":(space.gravity.x,space.gravity.y)}}
      with open(dataDir+fileName, 'w') as fo:
        json.dump(worlddict, fo)
      print "dir=",dataDir
      print "done"
      return worlddict
    def loadJSON(self, fileName="defaultlevel.json"):
      with open(dataDir+fileName, 'r') as fo:
        entsdict = json.load(fo)
      print entsdict
      self.loadFromDict(entsdict)
      #print dir(space.constraints[0])
      #print (space.constraints[0].a)
    def loadFromDict(self, data):
      print "LOADING"
      #print data
      space =self.gameworld.systems['physics'].space
      if "settings" in data:
        g = data['settings']['gravity']
        space.gravity = (g[0],g[1])
      ents = data['ents']
      idConvDict = {}
      for e in ents:
        if "physics" in e:
          stype = e['physics']['shape_type']
          pr = e['physics_renderer']
          p = e['physics']
          body = p['body']
          shape = p['shapes'][0]
          bp = (body['position'][0],body['position'][1])
          mass = body['mass']
          texture = str(pr['texture'])
          if str(mass) == 'inf': mass = 0
          print e['orig_id']
          if stype == "circle":
            idConvDict[e['orig_id']] = self.create_circle(bp, radius=shape['radius'], mass=mass, friction=shape['friction'], elasticity=shape['elasticity'], angle = body['angle'], texture=texture, selectNow = False)
          elif stype == "box":
            idConvDict[e['orig_id']] = self.create_box(bp, width=shape['width'], height=shape['height'], mass=mass, friction=shape['friction'], elasticity=shape['elasticity'], angle = body['angle'], texture=texture, selectNow = False)
      if "jointslist" in data:
        jointslist = data['jointslist']
        for j in jointslist:
          if j['a'] in idConvDict:
            b1id = idConvDict[j['a']]
            b1 = self.gameworld.entities[b1id].physics.body
          else: b1 = cy.Body()
          if j['b'] in idConvDict:
            b2id = idConvDict[j['b']]
            b2 = self.gameworld.entities[b2id].physics.body
          else: b2 = cy.Body()
          b1l = j['anchor1']
          b2l = j['anchor2']
          if str(j['type']) == "PivotJoint":
            qj = cy.PivotJoint(b1, b2, (b1l['x'], b1l['y']), (b2l['x'], b2l['y']))#, (b1.position.x,b1.position.y),(b2.position.x,b2.position.y))
            space.add(qj)
          if str(j['type']) == "PinJoint":
            qj = cy.PinJoint(b1, b2, (b1l['x'], b1l['y']), (b2l['x'], b2l['y']))#, (b1.position.x,b1.position.y),(b2.position.x,b2.position.y))
            space.add(qj)
          if str(j['type']) == "DampedSpring":
            qj = cy.DampedSpring(b1, b2, (b1l['x'], b1l['y']), (b2l['x'], b2l['y']),j['rest_length'],j['stiffness'],j['damping'])#, (b1.position.x,b1.position.y),(b2.position.x,b2.position.y))
            space.add(qj)
          print j

    def on_touch_up(self, touch):
        self.maintools.on_touch_up(touch)
        if touch.id not in self.touches:
          print super(TestGame, self).on_touch_up(touch)
          print "touchdown not found, mousewheel?"
          return
        pos = self.getWorldPosFromTouch(touch)
        ctouch = self.touches[touch.id]
        spos = ctouch['pos']
        if 'previewShape' in ctouch:
          self.gameworld.remove_entity(ctouch['previewShape'])
        #  self.canvas.before.remove(ctouch['previewShape'])

        space =self.gameworld.systems['physics'].space
        position = cy.Vec2d(pos[0], pos[1])
        shape = space.point_query_first(position)
        ctouch['touchingnow'] = shape

        if 'mousejoint' in ctouch and (ctouch['tool'] != "pin"):
          space.remove(ctouch['mousejoint'])


        if ctouch['onmenu']:return

        tshape = ctouch['touching']
        if tshape and shape:
          if ctouch['tool'] == 'c2p':
            b1 = ctouch['touching'].body#self.gameworld.entities[entityID]
            b2 = shape.body#self.gameworld.entities[self.entIDs[-1]]
            b2l = b2.world_to_local(position)
            print b2l
            #qj = cy.PivotJoint(b1, b2, pos)
            qj = cy.PinJoint(b1, b2, (0,0), (b2l['x'], b2l['y']))#, (b1.position.x,b1.position.y),(b2.position.x,b2.position.y))
            space.add(qj)

          if ctouch['tool'] == 'p2p':
            b1 = ctouch['touching'].body#self.gameworld.entities[entityID]
            b2 = shape.body#self.gameworld.entities[self.entIDs[-1]]
            b2l = b2.world_to_local(position)
            b1l = b1.world_to_local(cy.Vec2d(spos[0], spos[1]))
            print b2l
            #qj = cy.PivotJoint(b1, b2, pos)
            qj = cy.PinJoint(b1, b2, (b1l['x'], b1l['y']), (b2l['x'], b2l['y']))#, (b1.position.x,b1.position.y),(b2.position.x,b2.position.y))
            space.add(qj)

          if ctouch['tool'] == 'p2ps':
            b1 = ctouch['touching'].body#self.gameworld.entities[entityID]
            b2 = shape.body#self.gameworld.entities[self.entIDs[-1]]
            sposition = cy.Vec2d(spos[0], spos[1])
            b2l = b2.world_to_local(position)
            b1l = b1.world_to_local(sposition)
            dvec = cy.Vec2d(position.x-sposition.x,position.y-sposition.y)
            dist= sqrt(dvec.x**2+dvec.y**2)
            qj = cy.DampedSpring(b1, b2, (b1l['x'], b1l['y']), (b2l['x'], b2l['y']),dist,100,0.1)#, (b1.position.x,b1.position.y),(b2.position.x,b2.position.y))
            space.add(qj)

          if ctouch['tool'] == 'c2c':
            b1 = shape.body#self.gameworld.entities[entityID]
            b2 = ctouch['touching'].body#self.gameworld.entities[self.entIDs[-1]]
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
          spos = ctouch['pos']
          xd = spos[0]-pos[0]
          yd = spos[1]-pos[1]
          angle = atan2(yd,xd)
          self.create_circle(spos, mass=mass, radius=dist, texture=self.maintools.spriteSpinner.text, angle=angle)
        if ctouch['tool'] == "start" and ctouch["active"]:
          if self.startID < 0:
            self.startID = self.create_circle(pos, mass=0, radius=30, texture="orb")
          else:
            ent = self.gameworld.entities[self.startID]
            ent.physics.body.position = pos
            self.reindexEnt(ent)
        if ctouch['tool'] == "end" and ctouch["active"]:
          if self.finishID < 0:
            self.finishID = self.create_circle(pos, mass=0, radius=30, texture="checksphere")
          else:
            ent = self.gameworld.entities[self.finishID]
            ent.physics.body.position = pos
            self.reindexEnt(ent)
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
        pos = self.getWorldPosFromTouch(touch)
        position = cy.Vec2d(pos[0], pos[1])
        space =self.gameworld.systems['physics'].space
        shape = space.point_query_first(position)
        #self.selectedShape = shape
        print "touched shape:", shape
        self.touches[touch.id] = {"active":False , "pos":pos,"newpos":pos, "screenpos":(touch.x,touch.y), "tool":self.maintools.currentTool, "onmenu":False, "touching":shape, "touchingnow":shape, "ownbody":cy.Body()}
        ctouch = self.touches[touch.id]
        if self.maintools.on_touch_down(touch):#True:#touch.x < self.width*.1:
          ctouch["onmenu"] = True
          #sresult = super(TestGame, self).on_touch_down(touch)
          print "clicked in menu"
          return
        print "not in menu"
        ct = self.maintools.currentTool
        print ct
        ctouch['active'] =  True

        if ct in ["draw", "square", "box", "circle", "plank"]:
          ctouch['previewShape'] = self.create_decoration(pos=(0,0), width=0,height=0,texture=self.maintools.spriteSpinner.text)
          #with self.canvas.before:
          #    ctouch['previewShape'] = Rectangle(
          #        texture=self.atlas[self.maintools.spriteSpinner.text],
          #        pos=(300,300),
          #        size=(300,300))'''

        self.maintools.setShape(shape)

        #if self.maintools.currentTool == 'draw':
        #  ctouch.drawpoints={}

        if shape and self.maintools.currentTool == 'del':
          #print dir(shape)
          #print dir(shape.body)
          self.delObj(shape.body.data)
          ctouch['touchingnow'] = None
          #self.gameworld.remove_entity(shape.body.data)
          #space.remove(shape)
          #if shape.body in space.bodies:
          #  space.remove(shape.body)

        if shape and not shape.body.is_static and (self.maintools.currentTool == 'drag' or self.maintools.currentTool == 'pin'):
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
    def delObj(self, objid):
          #todo check before removing these items
          self.gameworld.remove_entity(objid)
          if objid in self.entIDs: self.entIDs.remove(objid)
    def getWorldPosFromTouch(self,touch):

        viewport = self.gameworld.systems['gameview']
        return touch.x- viewport.camera_pos[0],touch.y- viewport.camera_pos[1]
    def update(self, dt):
      self.maintools.update(dt)
      if not self.maintools.paused:
        self.gameworld.update(dt)
        for t in self.touches:
          ctouch = self.touches[t]
          if ctouch['active']:
            if ctouch['tool'] == 'vortex':
              self.pull2point(ctouch['newpos'])
            elif ctouch['tool'] == 'del' and 'touchingnow' in ctouch:
              if ctouch['touchingnow']:
                self.delObj(ctouch['touchingnow'].body.data)
                ctouch['touchingnow'] = None
    def pull2point(self, pos):
      for aid in self.entIDs:
        entity = self.gameworld.entities[aid]
        if entity.physics.body.is_static == 0:
          apos = entity.position
          dvecx = (pos[0]-apos.x)*entity.physics.body.mass*0.02
          dvecy = (pos[1]-apos.y)*entity.physics.body.mass*0.02
          entity.physics.body.apply_impulse((dvecx,dvecy))
          #entity.physics.body.apply_force((dvecx,dvecy))
    def setup_states(self):
        self.gameworld.add_state(state_name='main',
            systems_added=['renderer', 'physics_renderer'],
            systems_removed=[], systems_paused=[],
            systems_unpaused=['renderer', 'physics_renderer'],
            screenmanager_screen='main')

    def set_state(self):
        self.gameworld.state = 'main'

dataDir = ""
class KivEntEd(App):
    def build(self):
        global dataDir
        Window.clearcolor = (0, 0, 0, 1.)
        dataDir = self.get_application_config_dir()
        if not os.path.exists(dataDir):
          os.makedirs(dataDir)
        print self.get_application_config_dir()
        print self.get_application_config()
    def get_application_config_dir(self,extra=""):
        return super(KivEntEd, self).get_application_config(
            '~/.%(appname)s/'+extra)
    def get_application_config(self):
        return self.get_application_config_dir("%(appname)s.ini")


if __name__ == '__main__':
    KivEntEd().run()
