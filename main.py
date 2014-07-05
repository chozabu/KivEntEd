from random import randint
from random import random
from math import radians
import json
import os
import cymunk as cy
from math import *
import os

#import cProfile

import serialisation
from objscripts import ObjScripts

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
import kivent
from kivy.graphics import *
from kivy.atlas import Atlas


from kivy.utils import platform
from os.path import dirname, join, exists, sep, expanduser, isfile

import ui_elements

#http://stackoverflow.com/a/1620686/445831
'''import sys
import traceback

class TracePrints(object):
  def __init__(self):
    self.stdout = sys.stdout
  def write(self, s):
    self.stdout.write("Writing %r\n" % s)
    traceback.print_stack(file=self.stdout)

sys.stdout = TracePrints()'''


class TestGame(Widget):
	def __init__(self, **kwargs):
		self.dataDir = ""
		super(TestGame, self).__init__(**kwargs)
		Clock.schedule_once(self.init_game)
		self.entIDs = []
		self.mainTools = self.ids['gamescreenmanager'].ids['main_screen'].ids['mainTools']
		self.mainTools.setRef(self)
		self.mainTools.setTool("draw")
		self.startID = -1
		self.finishID = -1
		self.selectedShapeID = None
		self.space = None
		self.serials = None
		self.scripty = None
		self.todelete = []
		self.jointEnts = {}
		self.selectedListIndex = 0
		self.lastlist = None
		self.touches = {0: {"active": False, "pos": (0, 0), "screenpos": (0, 0)}}
		self.atlas = Atlas('assets/myatlas.atlas')
		try:
			self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
			self._keyboard.bind(on_key_down=self._on_keyboard_down)
		except:
			print 'Python python no keyboard'


	def init_game(self, dt):
		try:
			self._init_game(0)
		except KeyError:
			print 'failed: rescheduling init'
			Clock.schedule_once(self.init_game)


	def _init_game(self, dt):
		self.setup_map()
		self.setup_states()
		self.set_state()

		self.space = self.gameworld.systems['physics'].space
		#self.space.add_collision_handler(1, 0, begin = self.pull2_first)
		self.serials = serialisation.Serials(self)
		self.scripty = ObjScripts(self)

		noload = True
		fileNamePath = self.dataDir+"settings.jso"
		if os.path.exists(self.dataDir+"settings.jso"):
			print "settings.jso found, loading last level"
			if os.path.isfile(fileNamePath):
				with open(fileNamePath) as fo:
					settingsDict = json.load(fo)
					self.serials.loadJSON(settingsDict['lastSave'])
					self.mainTools.nameBox.text = settingsDict['lastSave'][0:-5]
					noload = False

		if noload:
			self.draw_some_stuff()
			print "level not loaded - making some stuff"

		Clock.schedule_interval(self.update, 0)
		Clock.schedule_once(self.init_sprites)

	def init_sprites(self, dt):
		#self.gameworld.systems['renderer'].do_rotate = True
		#self.gameworld.systems['renderer'].on_do_rotate(None,None)
		usprites = self.gameworld.systems['renderer'].uv_dict.keys()
		sprites = []
		for k in usprites:
			if k != 'atlas_size' and k != 'main_texture': sprites.append(str(k))
		self.mainTools.sprite_list = sprites

	def reindexEntID(self, entityID):
		self.reindexEnt(self.gameworld.entities[entityID])

	def reindexEnt(self, entity):
		space = self.space
		if entity and hasattr(entity, "physics"):
			for s in entity.physics.shapes:
				space.reindex_shape(s)

	def draw_some_stuff(self):
		size = Window.size
		for x in range(50):
			pos = (randint(size[0] / 3, size[0]), randint(0, size[1]))
			self.create_circle(pos, y_vel=random() * -20, texture="sheep", radius=15, selectNow=False)
		self.create_box((size[0] / 2.0, 0), mass=0, width=size[0] * 2, height=10, angle=0, selectNow=False)
		self.create_circle((size[0] / 2.0,size[1] / 2.0), y_vel=random() * -20, texture="magicball", radius=150, mass=0, selectNow=False, collision_type=1, color=(1,1,1,0.4))

	def _keyboard_closed(self):
		try:
			self._keyboard.unbind(on_key_down=self._on_keyboard_down)
			self._keyboard = None
		except:
			print "still no keyboard!"

	def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
		space = self.space
		if keycode[1] == 'up':
			space.gravity = space.gravity.x, space.gravity.y + 10
		if keycode[1] == 'down':
			space.gravity = space.gravity.x, space.gravity.y - 10
		if keycode[1] == 'left':
			space.gravity = space.gravity.x - 10, space.gravity.y
		if keycode[1] == 'right':
			space.gravity = space.gravity.x + 10, space.gravity.y
		return True

	def setGrav(self, g):
		self.space.gravity = (g[0], g[1])
		self.mainTools.gravxSlider.value = g[0]
		self.mainTools.gravySlider.value = g[1]
	def create_decoration(self, pos=(0, 0), width=40, height=40, angle=0, texture="sheep", color=(1,1,1,1)):
		create_component_dict = {
			'renderer': {'texture': texture, 'size': (width, height)},
			'position': pos, 'rotate': 0 ,'color':color}
		component_order = ['color', 'position', 'rotate', 'renderer']
		entityID = self.gameworld.init_entity(create_component_dict, component_order)
		return entityID

	def create_circle(self, pos, radius=6., mass=10., friction=1.0, elasticity=.5, angle=.0, x_vel=.0, y_vel=.0,
					  angular_velocity=0., texture="sheep", selectNow=True, sensor = False, collision_type = 0, color=(1,1,1,1)):
		shape_dict = {'inner_radius': 0, 'outer_radius': radius,
					  'mass': mass, 'offset': (0, 0)}
		col_shape = {'shape_type': 'circle', 'elasticity': elasticity,
					 'collision_type': collision_type, 'shape_info': shape_dict, 'friction': friction}
		col_shapes = [col_shape]
		physics_component = {'main_shape': 'circle',
							 'velocity': (x_vel, y_vel),
							 'position': pos, 'angle': angle,
							 'angular_velocity': angular_velocity,
							 'vel_limit': 2048,
							 'ang_vel_limit': radians(2000),
							 'mass': mass, 'col_shapes': col_shapes}
		create_component_dict = {'physics': physics_component,
								 'physics_renderer': {'texture': texture, 'size': (radius * 2, radius * 2)}, 'color':color,
								 'position': pos, 'rotate': 0}
		component_order = ['color', 'position', 'rotate',
						   'physics', 'physics_renderer']
		entityID = self.gameworld.init_entity(create_component_dict, component_order)
		self.entIDs.append(entityID)
		if self.mainTools.paused: (self.gameworld.systems['physics'].update(0.00001))
		if selectNow: self.mainTools.setShape(self.gameworld.entities[entityID].physics.shapes[0])
		self.gameworld.entities[entityID].physics.shapes[0].sensor = sensor
		return entityID
	def getEntFromID(self, entID):
		return self.gameworld.entities[entID]
	def create_box(self, pos, width=40., height=40., mass=10., friction=1.0, elasticity=.5, angle=.0, x_vel=.0, y_vel=.0,
				   angular_velocity=.0, texture="face_box", selectNow=True, sensor = False, collision_type = 0, color=(1,1,1,1)):
		box_dict = {
			'width': width,
			'height': height,
			'mass': mass}
		col_shape = {'shape_type': 'box', 'elasticity': elasticity,
					 'collision_type': collision_type, 'shape_info': box_dict, 'friction': friction}
		col_shapes = [col_shape]
		physics_component = {'main_shape': 'box',
							 'velocity': (x_vel, y_vel),
							 'position': pos, 'angle': angle,
							 'angular_velocity': angular_velocity,
							 'vel_limit': 2048,
							 'ang_vel_limit': radians(2000),
							 'mass': mass, 'col_shapes': col_shapes}
		create_component_dict = {'physics': physics_component,
								 'physics_renderer': {'texture': texture, 'size': (width, height)}, 'color':color,
								 'position': pos, 'rotate': 0}
		component_order = ['color', 'position', 'rotate',
						   'physics', 'physics_renderer']
		entityID = self.gameworld.init_entity(create_component_dict, component_order)
		self.entIDs.append(entityID)
		if self.mainTools.paused: (self.gameworld.systems['physics'].update(0.00001))
		if selectNow: self.mainTools.setShape(self.gameworld.entities[entityID].physics.shapes[0])
		self.gameworld.entities[entityID].physics.shapes[0].sensor = sensor
		return entityID

	def setup_map(self):
		gameworld = self.gameworld
		gameworld.currentmap = gameworld.systems['map']
	def getShapeAt(self, x,y):
		position = cy.Vec2d(x,y)
		return self.space.point_query_first(position)
	def getShapesAt(self, x,y):
		return self.getShapesAtVec(cy.Vec2d(x,y))
	def getShapesAtVec(self, position):
		b = cy.Body()
		b.position = position
		shapeos = cy.Circle(b, 1)
		return self.space.shape_query(shapeos)
	def setEntIDPosSizeRot(self, entID, x,y,w,h,r=0):
		self.setEntPosSizeRot(self.gameworld.entities[entID], x,y,w,h,r)
	def setEntPosSizeRot(self, ent, x,y,w,h,r=0):
		ent.position.x = x
		ent.position.y = y
		ent.renderer.width = w
		ent.renderer.height = h
		ent.rotate.r = r
	def deleteJoint(self, j):
		if j in self.space.constraints:
			print "removing ",j, " from space"
			print "constraints before joint removal: ", self.space.constraints
			print j.a, j.b
			self.space.remove(j)
			print "constraints after joint removal: ", self.space.constraints
			#if j in self.space.constraints:
			#	self.space.constraints.remove(j)
		if j in  self.jointEnts:
			print "removing ent and from dict"
			jent = self.jointEnts[j]
			eid = jent.entity_id
			self.gameworld.remove_entity(eid)
			#if self.selectedShapeID == eid: self.mainTools.setShape(None)
			del self.jointEnts[j]
	def create_joint(self, b1, b2, a1=(0, 0), a2=(0, 0),
								 type='PivotJoint', **kwargs):
		if b1 is b2:return
		space = self.space
		qj = None
		if type == "PivotJoint":
			qj = cy.PivotJoint(b1, b2, a1, a2)
			space.add(qj)
		if type == "PinJoint":
			qj = cy.PinJoint(b1, b2, a1, a2)
			space.add(qj)
		if type == "DampedSpring":
			qj = cy.DampedSpring(b1, b2, a1,a2, kwargs['rest_length'],
								 kwargs['stiffness'],
								 kwargs['damping'])
			space.add(qj)

		jrid = self.create_decoration(pos=(b1.position.x, b1.position.y), width=20, height=20,
														texture='plank')
		jrent = self.getEntFromID(jrid)
		jrent.joint = qj
		#print dir(qj)
		#qj.entity_id = jrid
		self.jointEnts[qj] = jrent


	def on_touch_move(self, touch):
		if touch.id not in self.touches: return
		self.mainTools.on_touch_move(touch)
		space = self.space
		ctouch = self.touches[touch.id]
		pos = self.getWorldPosFromTouch(touch)
		spos = ctouch['pos']
		currentTool = ctouch['tool']
		ctouch['newpos'] = pos
		ctouch['ownbody'].position = pos

		shape = self.getShapeAt(pos[0], pos[1])
		ctouch['touchingnow'] = shape

		if currentTool == "camera":
			super(TestGame, self).on_touch_move(touch)
		if 'previewShape' in ctouch:
			psid = ctouch['previewShape']
			xd = spos[0] - pos[0]
			yd = spos[1] - pos[1]
			midx = (spos[0] + pos[0]) / 2.0
			midy = (spos[1] + pos[1]) / 2.0
			dist = sqrt(xd ** 2 + yd ** 2)
			angle = atan2(yd, xd)

			if currentTool == "box":
				self.setEntIDPosSizeRot(psid, midx,midy,xd,yd)
			if currentTool == "circle":
				self.setEntIDPosSizeRot(psid, spos[0],spos[1],dist*2,dist*2,angle)
			if currentTool == "square":
				self.setEntIDPosSizeRot(psid, spos[0],spos[1],dist*2,dist*2,angle)
			if currentTool == "plank":
				self.setEntIDPosSizeRot(psid, midx,midy,dist,10, angle)
			if currentTool == "draw":
				self.setEntIDPosSizeRot(psid, midx,midy,dist,10, angle)
				if dist > 10:
					mass = self.mainTools.massSlider.value
					self.create_box((midx, midy), mass=mass, width=dist, height=10, angle=angle,
									texture=self.mainTools.spriteSpinner.text, selectNow=False)
					ctouch['pos'] = pos

		shape = ctouch['touching']
		if currentTool == 'rotate' and shape:
			xd = shape.body.position.x - pos[0]
			yd = shape.body.position.y - pos[1]
			angle = atan2(yd, xd)
			if 'origAngle' not in ctouch: ctouch['origAngle'] = shape.body.angle-angle
			shape.body.angle = (angle+ctouch['origAngle'])
		if (currentTool == 'drag' or currentTool == 'paste') and shape and (shape.body.is_static or self.mainTools.paused):
			shape.body.position = (shape.body.position.x + touch.dx, shape.body.position.y + touch.dy)
			self.reindexEntID(shape.body.data)
			if self.mainTools.paused:
				(self.gameworld.systems['physics'].update(0.00000001))
				(self.gameworld.systems['physics_renderer'].update(0.00000001))
				(self.gameworld.systems['renderer'].update(0.00000001))
				#space.reindex_shape(shape)


	def on_touch_up(self, touch):
		self.mainTools.on_touch_up(touch)
		if touch.id not in self.touches:
			print super(TestGame, self).on_touch_up(touch)
			print "touchdown not found, mousewheel?"
			return
		ctouch = self.touches[touch.id]
		pos = self.getWorldPosFromTouch(touch)
		spos = ctouch['pos']
		currentTool = ctouch['tool']
		if 'previewShape' in ctouch:
			self.gameworld.remove_entity(ctouch['previewShape'])
		#  self.canvas.before.remove(ctouch['previewShape'])

		space = self.space
		position = cy.Vec2d(pos[0], pos[1])
		shape = space.point_query_first(position)
		ctouch['touchingnow'] = shape

		if 'mousejoint' in ctouch and (currentTool != "pin"):
			if ctouch['mousejoint'] in self.space.constraints:
				space.remove(ctouch['mousejoint'])

		if ctouch['onmenu']: return


		tshape = ctouch['touching']
		if tshape and shape:
			sposition = cy.Vec2d(spos[0], spos[1])
			b1 = tshape.body
			b2 = shape.body
			b1l = b1.world_to_local(sposition)
			b2l = b2.world_to_local(position)
			if currentTool == 'c2p':
				self.create_joint(b1, b2, (0, 0),
								 (b2l['x'], b2l['y']), "PinJoint")
				#qj = cy.PinJoint(b1, b2, (0, 0),
				#				 (b2l['x'], b2l['y']))
				#space.add(qj)

			if currentTool == 'p2p':
				self.create_joint(b1, b2, (b1l['x'], b1l['y']),
								 (b2l['x'], b2l['y']), "PinJoint")
				#space.add(qj)

			if currentTool == 'p2ps':
				dvec = cy.Vec2d(position.x - sposition.x, position.y - sposition.y)
				dist = sqrt(dvec.x ** 2 + dvec.y ** 2)
				self.create_joint(b1, b2, (b1l['x'], b1l['y']), (b2l['x'], b2l['y']), "DampedSpring"
				                     , rest_length=dist, stiffness=100,
									 damping=0.1)
				#space.add(qj) kwargs['rest_length'],
								# kwargs['stiffness'],
								# kwargs['damping'])

			if currentTool == 'c2c':
				self.create_joint(b1, b2, (0, 0),
								 (0, 0), "PinJoint")
				#b2.physics.shapes[0].group=1
				#b1.physics.shapes[0].group=1
				#space.add(qj)


		xd = spos[0] - pos[0]
		yd = spos[1] - pos[1]
		midx = (spos[0] + pos[0]) / 2.0
		midy = (spos[1] + pos[1]) / 2.0
		mass = self.mainTools.massSlider.value
		angle = atan2(yd, xd)
		dist = sqrt(xd ** 2 + yd ** 2)

		if (currentTool == "draw" or currentTool == "plank"):
			if dist < 4: dist = 8
			self.create_box((midx, midy), mass=mass, width=dist, height=10, angle=angle,
							texture=self.mainTools.spriteSpinner.text)

		if currentTool == "start":
			if self.startID < 0:
				self.startID = self.create_circle(pos, mass=0, radius=30, texture="orb")
			else:
				ent = self.gameworld.entities[self.startID]
				ent.physics.body.position = pos
				self.reindexEnt(ent)
		if currentTool == "end":
			if self.finishID < 0:
				self.finishID = self.create_circle(pos, mass=0, radius=30, texture="checksphere")
			else:
				ent = self.gameworld.entities[self.finishID]
				ent.physics.body.position = pos
				self.reindexEnt(ent)

		if currentTool == "circle":
			if dist < 4: dist = 8
			self.create_circle(spos, mass=mass, radius=dist, texture=self.mainTools.spriteSpinner.text, angle=angle)
		if currentTool == "box":
			width = fabs(xd)
			height = fabs(yd)
			if width< 4: width=8
			if height< 4: height=8
			self.create_box((midx, midy), mass=mass, width=width, height=height, angle=0,
							texture=self.mainTools.spriteSpinner.text)
		if currentTool == "square":
			if dist < 4: dist = 8
			self.create_box(spos, mass=mass, width=dist * 2, height=dist * 2, angle=angle,
							texture=self.mainTools.spriteSpinner.text)
		self.touches[touch.id] = {"active": False, "newpos": pos, "screenpos": (touch.x, touch.y)}

	def on_touch_down(self, touch):
		print "TOUCHDOWN\n"
		pos = self.getWorldPosFromTouch(touch)
		position = cy.Vec2d(pos[0], pos[1])
		space = self.space
		shape = None#space.point_query_first(position)
		shapes = self.getShapesAtVec(position)
		if len(shapes) >0: shape = shapes[0]
		if shapes==self.lastlist and shapes != []:
			self.selectedListIndex +=1
			if self.selectedListIndex == len(shapes):self.selectedListIndex=0
			shape=shapes[self.selectedListIndex]
		else: self.selectedListIndex =0
		self.lastlist = shapes
		#self.selectedShape = shape
		print "touched shape:", shape
		print "touched shapes:", shapes
		self.touches[touch.id] = {"active": False, "pos": pos, "newpos": pos, "screenpos": (touch.x, touch.y),
								  "tool": self.mainTools.currentTool, "onmenu": False, "touching": shape,
								  "touchingnow": shape, "ownbody": cy.Body()}
		ctouch = self.touches[touch.id]
		if self.mainTools.on_touch_down(touch):  #True:#touch.x < self.width*.1:
			ctouch["onmenu"] = True
			#sresult = super(TestGame, self).on_touch_down(touch)
			print "clicked in menu"
			return
		print "not in menu"
		currentTool = self.mainTools.currentTool
		print "Tool is: " + currentTool
		ctouch['active'] = True


		if currentTool in ["draw", "square", "box", "circle", "plank"]:
			ctouch['previewShape'] = self.create_decoration(pos=(0, 0), width=0, height=0,
															texture=self.mainTools.spriteSpinner.text)

		if shape and currentTool == 'del':
			if shape == self.mainTools.selectedItem:
				self.mainTools.setShape(None)
			self.delObj(shape.body.data)
			ctouch['touchingnow'] = None
			return


		if currentTool == "paste" and self.mainTools.entcpy:
			pastedEID = self.serials.loadEntFromDict(self.mainTools.entcpy)
			phys = self.gameworld.entities[pastedEID].physics
			phys.body.position = pos
			shape = phys.shapes[0]
			#self.mainTools.setShape(shape)
			space.reindex_shape(shape)
			ctouch['touching'] = shape
		self.mainTools.setShape(shape)


		if shape and not shape.body.is_static and (
				currentTool == 'drag' or currentTool == 'paste' or currentTool == 'pin'):
			body = ctouch['ownbody']
			body.position = pos
			ctouch['mousejoint'] = cy.PivotJoint(shape.body, body, position)
			space.add(ctouch['mousejoint'])

	def clearAll(self):
		self.startID = -1
		self.finishID = -1

		self.mainTools.setShape(None)
		space = self.space
		print "clearing objects"
		for eid in list(self.entIDs):
			print "beforedel"
			self.delObj(eid)
			print "afterdel"
		#space.remove(list(space.constraints))
		print "clearing joints"
		for c in list(space.constraints):
			self.deleteJoint(c)
	def delObjNext(self, objid):
		if objid not in self.todelete:self.todelete.append(objid)
	def delObj(self, objid):
		#todo check before removing these items
		#print "removing:", objid
		ent =  self.getEntFromID(objid)
		if hasattr(ent, "physics"):
			b = ent.physics.body
			removeus = self.getJointsOnBody(b)
			for rmu in removeus:
				print rmu in self.space.constraints
			for c in removeus:
				#print "removing", c
				self.deleteJoint(c)
		print ent, self.mainTools.selectedEntity
		if ent == self.mainTools.selectedEntity:
			self.mainTools.setShape(None)
		self.gameworld.remove_entity(objid)
		if objid in self.entIDs: self.entIDs.remove(objid)
	def getJointsOnBody(self, b):
		joints = []
		for c in self.space.constraints:
			if c.a == b or c.b == b:
				joints.append(c)
		return joints
	def getWorldPosFromTouch(self, touch):

		viewport = self.gameworld.systems['gameview']
		return touch.x - viewport.camera_pos[0], touch.y - viewport.camera_pos[1]

	def update(self, dt):
		for o in self.todelete:
			self.delObj(o)
		self.todelete = []
		self.mainTools.update(dt)
		ent = self.mainTools.selectedEntity

		if self.selectedShapeID != None and ent != None:
			sbox = self.getEntFromID(self.selectedShapeID)
			sbox.position.x =ent.position.x
			sbox.position.y =ent.position.y
			bb = ent.physics.shapes[0].cache_bb()
			sbox.renderer.width = (bb['r']-bb['l'])*1.05+5
			sbox.renderer.height = (bb['t']-bb['b'])*1.05+5
		for j, je in self.jointEnts.iteritems():
			#j = je.joint
			b1l = j.a.local_to_world(cy.Vec2d(j.anchor1['x'],j.anchor1['y']))
			b2l = j.b.local_to_world(cy.Vec2d(j.anchor2['x'],j.anchor2['y']))
			b1l = cy.Vec2d(b1l['x'], b1l['y'])
			b2l = cy.Vec2d(b2l['x'], b2l['y'])
			xd = b1l.x - b2l.x
			yd = b1l.y - b2l.y
			midx = (b1l.x + b2l.x) / 2.0
			midy = (b1l.y + b2l.y) / 2.0
			dist = sqrt(xd ** 2 + yd ** 2)
			angle = atan2(yd, xd)
			self.setEntIDPosSizeRot(je.entity_id, midx,midy,dist,10, angle)
			#self.setEntIDPosSizeRot(je.entity_id, midx,midy,xd,yd)
		if not self.mainTools.paused:
			self.gameworld.update(dt)
			for t in self.touches:
				ctouch = self.touches[t]
				if ctouch['active']:
					pos = ctouch['newpos']
					if ctouch['tool'] == 'vortex':
						self.pull2point(pos)
					elif ctouch['tool'] == 'del' and 'touchingnow' in ctouch:
						shape = self.getShapeAt(pos[0], pos[1])
						if shape:
							self.delObj(shape.body.data)
							ctouch['touchingnow'] = None

	def pull2point(self, pos):
		for aid in self.entIDs:
			entity = self.gameworld.entities[aid]
			if entity.physics.body.is_static == 0:
				apos = entity.position
				dvecx = (pos[0] - apos.x) * entity.physics.body.mass * 0.02
				dvecy = (pos[1] - apos.y) * entity.physics.body.mass * 0.02
				entity.physics.body.apply_impulse((dvecx, dvecy))
				#entity.physics.body.apply_force((dvecx,dvecy))

	def setup_states(self):
		self.gameworld.add_state(state_name='main',
								 systems_added=['color', 'rotate', 'renderer', 'physics_renderer'],
								 systems_removed=[], systems_paused=[],
								 systems_unpaused=['color', 'rotate', 'renderer', 'physics_renderer'],
								 screenmanager_screen='main')

	def set_state(self):
		self.gameworld.state = 'main'



class KivEntEd(App):
	def build(self):
		Window.clearcolor = (0, 0, 0, 1.)
		dataDir = self.get_application_storage_dir()
		print "dd="+dataDir
		if not os.path.exists(dataDir):
			os.makedirs(dataDir)
		self.root.dataDir = dataDir

	def on_pause(self):
		print "pausing"
		self.root.serials.exportJSON(fileName="pauselevel.json")
		return True
	def on_resume(self):
		pass
		#self.root.clearAll()
		#self.root.serials.loadJSON(fileName="pauselevel.json")


	def get_application_storage_dir(self, extra=""):
		defaultpath = '~/.%(appname)s/'
		if platform == 'android':
			defaultpath = '/sdcard/.%(appname)s/'
		elif platform == 'ios':
			defaultpath = '~/Documents/%(appname)s/'
		elif platform == 'win':
			defaultpath = defaultpath.replace('/', sep)
		defaultpath+=extra
		return expanduser(defaultpath) % {
			'appname': self.name, 'appdir': self.directory}
		#return super(KivEntEd, self).get_application_config(
		#	'~/.%(appname)s/' + extra)

	def get_application_config(self):
		return self.get_application_storage_dir("%(appname)s.ini")
'''    def on_start(self):
        self.profile = cProfile.Profile()
        self.profile.enable()

    def on_stop(self):
        self.profile.disable()
        self.profile.dump_stats('myapp.profile')'''

if __name__ == '__main__':
	KivEntEd().run()
	#cProfile.run('KivEntEd().run()', 'kivented.prof')
	'''sd_card_path = os.path.dirname('/sdcard/profiles/')
	print sd_card_path
	if not os.path.exists(sd_card_path):
		print 'making directory'
		os.mkdir(sd_card_path)
	print 'path: ', sd_card_path
	cProfile.run('KivEntEd().run()', sd_card_path + '/kivented.prof')'''
