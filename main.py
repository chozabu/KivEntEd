from random import randint
from random import random
from math import radians
import json
import os
import cymunk as cy
from math import *
import os
import PolyGen
import Spline

#import cProfile

__version__ = "0.1"

import serialisation
from objscripts import ObjScripts

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
import kivent
from kivent import texture_manager

texture_manager.load_atlas('assets/myatlas.atlas')
from kivy.graphics import *
from kivy.atlas import Atlas


from kivy.utils import platform
from os.path import dirname, join, exists, sep, expanduser, isfile

import ui_elements

import sys
#import debugprint


def cross(a, b):
	return a[0]*b[1]-a[1]*b[0]

def cross3d(a, b):
	c = [a[1]*0 - 0*b[1],
		 0*b[0] - a[0]*0,
		 a[0]*b[1] - a[1]*b[0]]
	return c

class TestGame(Widget):
	def __init__(self, **kwargs):
		self.dataDir = ""
		super(TestGame, self).__init__(**kwargs)
		Clock.schedule_once(self.init_game)
		self.entIDs = []
		self.mainTools = self.ids['gamescreenmanager'].ids['main_screen'].ids['mainTools']
		self.mainTools.setRef(self)
		self.mainTools.setTool("circle")
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
		self.touches = {}#0: {"active": False, "pos": (0, 0), "screenpos": (0, 0)}}
		self.atlas = Atlas('assets/myatlas.atlas')
		try:
			self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
			self._keyboard.bind(on_key_down=self._on_keyboard_down)
		except:
			print 'Python python no keyboard'

		size = Window.size
		with self.canvas.before:
			#Color(0.5, 0.65, 0.95)
			self.bgrect = Rectangle(source='sprites/bgm.jpg', size=size)
		Window.bind(on_resize=self.redogb)
	def redogb(self, a,b,c):
		size = Window.size
		self.bgrect.size =Window.size

	def init_game(self, dt):
		if platform == 'android' or True:#apply kovaks hack to android only
			try:
				self._init_game(0)
			except KeyError as err:
				print 'failed: rescheduling init'
				print err
				Clock.schedule_once(self.init_game)
		else:
			self._init_game(0)


	def ensure_startup(self):
		systems_to_check = ['map', 'physics', 'renderer', 'rotate', 'position']
		systems = self.gameworld.systems
		for each in systems_to_check:
			if each not in systems:
				return False
		return True

	def _init_game(self, dt):
		self.setup_map()
		self.setup_states()
		self.set_state()
		Clock.schedule_once(self.__init_game)
	def __init_game(self, dt):
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
					try:
						settingsDict = json.load(fo)
						self.serials.loadJSON(settingsDict['lastSave'])
						self.mainTools.nameBox.text = settingsDict['lastSave'][0:-5]
						noload = False
					except:
						print "could not load settings.jso level"
						import traceback
						traceback.print_exc()

		if noload:
			self.draw_some_stuff()
			print "level not loaded - making some stuff"

		Clock.schedule_interval(self.update, 0)
		Clock.schedule_once(self.init_sprites)

	def init_sprites(self, dt):
		#self.gameworld.systems['renderer'].do_rotate = True
		#self.gameworld.systems['renderer'].on_do_rotate(None,None)
		return
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
		self.mainTools.inputPreview.text = str(self.space.gravity)
		return True

	def setGrav(self, g):
		self.space.gravity = (g[0], g[1])
		self.mainTools.gravxSlider.value = g[0]
		self.mainTools.gravySlider.value = g[1]
		self.mainTools.inputPreview.text = str(self.space.gravity)
	def create_decoration(self, pos=(0, 0), width=40, height=40, angle=0, texture="sheep", color=(1,1,1,1)):
		create_component_dict = {
			'renderer': {'texture': texture, 'size': (width, height)},
			'position': pos, 'rotate': angle ,'color':color, 'scale':1.}
		component_order = ['color', 'position', 'rotate', 'renderer', 'scale']
		entityID = self.gameworld.init_entity(create_component_dict, component_order)
		return entityID

	def create_circle(self, pos, radius=6., mass=10., friction=1.0, elasticity=.5, angle=.0, x_vel=.0, y_vel=.0,
					  angular_velocity=0., texture="sheep", selectNow=True, sensor = False, collision_type = 0,
					  color=(1,1,1,1), do_physics = True):
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
		create_component_dict = {#'physics': physics_component,
								 'color':color,
								 'position': pos, 'rotate': angle, 'scale':1}
		#component_order = ['color', 'position', 'rotate',
		#				   'renderer']
		render_component = {'texture': texture, 'size': (radius * 2, radius * 2)}
		if do_physics:
			create_component_dict['physics'] = physics_component
			create_component_dict['renderer'] = render_component
			component_order = ['color', 'position', 'rotate',
						   'physics', 'renderer', 'scale']
		else:
			create_component_dict['renderer'] = render_component
			component_order = ['color', 'position', 'rotate',
						   'renderer']
		return self.create_ent_from_dict(create_component_dict, component_order, selectNow)
	def getEntFromID(self, entID):
		return self.gameworld.entities[entID]
	def create_ent_from_dict(self,create_component_dict, component_order, selectNow = True):
		entityID = self.gameworld.init_entity(create_component_dict, component_order)
		self.entIDs.append(entityID)
		if self.mainTools.paused: (self.gameworld.systems['physics'].update(0.00001))
		#if selectNow: self.mainTools.setShape(self.gameworld.entities[entityID].physics.shapes[0])
		if selectNow:
			do_physics = 'physics' in component_order
			if do_physics:
				self.mainTools.setShape(self.gameworld.entities[entityID].physics.shapes[0])
			else:
				self.mainTools.setEnt(self.gameworld.entities[entityID])
		return entityID
	def create_segment(self, pos, width=40., height=40., mass=10., friction=1.0, elasticity=.5, angle=.0, x_vel=.0, y_vel=.0,
				   angular_velocity=.0, texture="face_box", selectNow=True, sensor = False, collision_type = 0, color=(1,1,1,1)):
		a= cy.Vec2d(-width/2,0)
		b= cy.Vec2d(width/2,0)
		box_dict = {
			'a': a,
			'b': b,
			'radius': height,
			'mass': mass}
		col_shape = {'shape_type': 'segment', 'elasticity': elasticity,
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
								 'renderer': {'texture': texture, 'size': (width, height)}, 'color':color,
								 'position': pos, 'rotate': angle}
		component_order = ['color', 'position', 'rotate',
						   'physics', 'renderer']
		return self.create_ent_from_dict(create_component_dict, component_order, selectNow)
	def create_box(self, pos, width=40., height=40., mass=10., friction=1.0, elasticity=.5, angle=.0, x_vel=.0, y_vel=.0,
				   angular_velocity=.0, texture="face_box", selectNow=True, sensor = False, collision_type = 0,
				   color=(1,1,1,1), do_physics = True):
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
		create_component_dict = {'color':color,
								 'position': pos, 'rotate': angle, 'scale':1}
		#component_order = ['color', 'position', 'rotate',
		#				   'physics', 'renderer']

		render_component = {'texture': texture, 'size': (width, height)}
		if do_physics:
			create_component_dict['physics'] = physics_component
			create_component_dict['renderer'] = render_component
			component_order = ['color', 'position', 'rotate',
						   'physics', 'renderer', 'scale']
		else:
			create_component_dict['renderer'] = render_component
			component_order = ['color', 'position', 'rotate',
						   'renderer']
		return self.create_ent_from_dict(create_component_dict, component_order, selectNow)
	def create_sprite(self, pos, shape_type='box', radius=40., width=None, height=None, mass=10., friction=None, elasticity=None, angle=.0, x_vel=.0, y_vel=.0,
				   angular_velocity=.0, texture=None, selectNow=True, sensor = False, collision_type = 0,
				   color=None, do_physics = True, old_shape_id=None, old_shape=None, replace_old_shape=False):
		if width == None:width=radius*2
		if height == None:height=radius*2
		print "color=",color
		print "old_shape_id=",old_shape_id
		print "old_shape=",old_shape
		if old_shape_id:old_shape = self.getEntFromID(old_shape_id)
		print "old_shape=",old_shape
		if old_shape:

			if do_physics == None:
				#print oldpoly.load_order
				do_physics = 'physics' in old_shape.load_order
				#print do_physics
			if hasattr(old_shape, 'physics'):
				if friction == None: friction = old_shape.physics.shapes[0].friction
				if elasticity == None: elasticity = old_shape.physics.shapes[0].elasticity
			if color == None:
				c = old_shape.color
				print "c=",c
				color = (c.r, c.g ,c.b ,c.a)
				print color
			if texture == None:
				texture = old_shape.poly_renderer.texture
			if replace_old_shape: self.delObj(old_shape_id)
		if friction == None: friction = 1.0
		if elasticity == None: elasticity = .5
		if color == None:color = (1,1,1,1)
		print color
		if texture == None: texture = "snow"
		if do_physics == None: do_physics = True

		if shape_type == 'box':
			shape_dict = {
				'width': width,
				'height': height,
				'mass': mass}
		elif shape_type == 'circle':
			shape_dict = {'inner_radius': 0, 'outer_radius': radius,
						  'mass': mass, 'offset': (0, 0)}
		col_shape = {'shape_type': shape_type, 'elasticity': elasticity,
					 'collision_type': collision_type, 'shape_info': shape_dict, 'friction': friction}
		col_shapes = [col_shape]
		physics_component = {'main_shape': shape_type,
							 'velocity': (x_vel, y_vel),
							 'position': pos, 'angle': angle,
							 'angular_velocity': angular_velocity,
							 'vel_limit': 2048,
							 'ang_vel_limit': radians(2000),
							 'mass': mass, 'col_shapes': col_shapes}
		create_component_dict = {'color':color,
								 'position': pos, 'rotate': angle, 'scale':1}
		#component_order = ['color', 'position', 'rotate',
		#				   'physics', 'renderer']

		render_component = {'texture': texture, 'size': (width, height)}
		if do_physics:
			create_component_dict['physics'] = physics_component
			create_component_dict['renderer'] = render_component
			component_order = ['color', 'position', 'rotate',
						   'physics', 'renderer', 'scale']
		else:
			create_component_dict['renderer'] = render_component
			component_order = ['color', 'position', 'rotate',
						   'renderer', 'scale']
		return self.create_ent_from_dict(create_component_dict, component_order, selectNow)
	def create_spline(self, pos, spline, lastpolyid=None, mass=0., friction=None, elasticity=None, angle=.0, x_vel=.0, y_vel=.0,
	angular_velocity=.0, texture=None, selectNow=True, do_physics = None, collision_type = 0, color=None):
		pg = PolyGen.PolyGen()
		spline.DrawCurve()
		pg.from_spline(spline.subpoints)
		#do_physics = self.mainTools.polyMenu.polyPhysButton.state != 'down'
		spline_ent_id = self.create_poly(pos,pg,lastpolyid=lastpolyid, mass=mass, friction=friction,
		                        elasticity=elasticity, angle=angle, x_vel=x_vel, y_vel=y_vel,
		                        angular_velocity=angular_velocity, texture=texture, selectNow=selectNow,
		                        do_physics = do_physics, collision_type = collision_type, color=color)#, do_physics=do_physics)

		spline_ent = self.getEntFromID(spline_ent_id)
		spline_ent.splineshape = spline
		print "made spline"
		return spline_ent_id
	def create_poly(self, pos, polygon, lastpolyid=None, mass=0., friction=None, elasticity=None, angle=.0, x_vel=.0, y_vel=.0,
	angular_velocity=.0, texture=None, selectNow=True, do_physics = None, collision_type = 0, color=None):
		#print "poly, oldpoly=", lastpolyid

		#print do_physics
		if lastpolyid:
			oldpoly = self.getEntFromID(lastpolyid)
			if do_physics == None:
				#print oldpoly.load_order
				do_physics = 'physics' in oldpoly.load_order
				#print do_physics
			if hasattr(oldpoly, 'physics'):
				if friction == None: friction = oldpoly.physics.shapes[0].friction
				if elasticity == None: elasticity = oldpoly.physics.shapes[0].elasticity
			if color == None:
				c = oldpoly.color
				color = (c.r, c.g ,c.b ,c.a)
			if texture == None:
				texture = oldpoly.poly_renderer.texture
			self.delObj(lastpolyid)
		if friction == None: friction = 1.0
		if elasticity == None: elasticity = .5
		if color == None:color = (1,1,1,1)
		if texture == None: texture = "snow"
		if do_physics == None: do_physics = True

		pg = polygon


		pg.color = color
		create_dict = pg.draw_from_Polygon()
		if create_dict == False:return
		create_dict['do_texture'] = True
		if texture[-4:] != '.png': texture = 'sprites/'+texture+'.png'
		create_dict['texture'] = texture
		print texture

		triangles = create_dict['triangles']
		tricount = len(triangles)
		if tricount < 1: return
		submass = mass/tricount
		verts = create_dict['vertices']
		#print "bothtest, cptest, crtest, failtest"
		#print bothtest, cptest, crtest, failtest
		#print remlist #TODO really, this should be empty!

		col_shapes, remlist = PolyGen.col_shapes_from_tris(triangles,verts,submass,elasticity,collision_type,friction)

		remlist.reverse()
		for r in remlist:
			triangles.remove(triangles[r])
		create_dict['tri_count'] = len(triangles)
		if len(col_shapes) == 0:return None
		physics_component = {'main_shape': 'poly',
							 'velocity': (x_vel, y_vel),
							 'position': (0,0), 'angle': angle,
							 'angular_velocity': angular_velocity,
							 'vel_limit': 2048,
							 'ang_vel_limit': radians(2000),
							 'mass': mass, 'col_shapes': col_shapes}

		create_component_dict = {'color':color,
						 'position': pos, 'rotate': 0, 'poly_renderer': create_dict}
		component_order = ['color', 'position', 'rotate', 'poly_renderer']
		if do_physics:
			create_component_dict['physics'] = physics_component
			component_order = ['color', 'position', 'rotate', 'physics', 'poly_renderer']
		if lastpolyid and 0:
			poly = self.getEntFromID(lastpolyid)

			poly.poly_renderer.vert_mesh.load_from_python(verts, triangles)#, create_dict['vert_count'], create_dict['tri_count'])
			self.gameworld.systems['poly_renderer'].redraw_entity(lastpolyid)
			return lastpolyid
		else:
			#print "col_shapes=",col_shapes
			newpolyID = self.gameworld.init_entity(create_component_dict, component_order)
			self.entIDs.append(newpolyID)
			newpoly = self.getEntFromID(newpolyID)
			newpoly.polyshape = pg

			print newpoly.poly_renderer.texture
			#if not do_physics:
			#	newpoly.load_order.remove('physics')
			#newpoly.load_order = ['color', 'position', 'rotate', 'poly_renderer']
			if selectNow: self.mainTools.setEnt(self.gameworld.entities[newpolyID])

			#newpoly.poly_renderer.texture.wrap = 'repeat'

			#print "poly has: " + str(len(triangles)) + " triangles"
			return newpolyID
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
		print "--------"
		print ent.position.x
		ent.position.x = x#*0.1
		viewport = self.gameworld.systems['gameview']
		print viewport.camera_scale
		print viewport.camera_pos
		print viewport.size
		ent.position.y = y
		#ent.renderer.width = w
		#ent.renderer.height = h
		ent.rotate.r = r
		ent.scale.s = w/80.
		print '--------'
	def deleteJoint(self, j):
		if j in self.space.constraints:
			#print "removing ",j, " from space"
			#print "constraints before joint removal: ", self.space.constraints
			#print j.a, j.b
			self.space.remove(j)
			#print "constraints after joint removal: ", self.space.constraints
			#if j in self.space.constraints:
			#	self.space.constraints.remove(j)
		if j in  self.jointEnts:
			#print "removing ent and from dict"
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

		if ctouch['onmenu']: return
		pos = self.getWorldPosFromTouch(touch)
		spos = ctouch['pos']
		currentTool = ctouch['tool']
		ctouch['newpos'] = pos
		ctouch['ownbody'].position = pos

		shape = self.getShapeAt(pos[0], pos[1])
		ctouch['touchingnow'] = shape


		xd = spos[0] - pos[0]
		yd = spos[1] - pos[1]
		dist = sqrt(xd ** 2 + yd ** 2)
		midx = (spos[0] + pos[0]) / 2.0
		midy = (spos[1] + pos[1]) / 2.0
		angle = atan2(yd, xd)
		if currentTool == 'polysub':
			if dist > 10:
				polys = self.get_touching_polys(pos, radius=self.mainTools.polyMenu.brushSizeSlider.value)
				for p in polys:
					pg = p.polyshape
					pg.sub_circle_polygon(pos, radius=self.mainTools.polyMenu.brushSizeSlider.value)
					pg.sub_square_polygon((midx,midy),dist,self.mainTools.polyMenu.brushSizeSlider.value*1.96, angle)
					self.create_poly(pos,p.polyshape,p.entity_id)
				ctouch['pos'] = pos

		if 'polygen' in ctouch:
			pg = ctouch['polygen']
			if dist > 10:

				pg.draw_circle_polygon(pos, radius=self.mainTools.polyMenu.brushSizeSlider.value)
				pg.draw_square_polygon((midx,midy),dist,self.mainTools.polyMenu.brushSizeSlider.value*1.96, angle)
				#pg.draw_square_polygon(pos, 100, self.mainTools.polyMenu.brushSizeSlider.value*2)
				lpid=None
				if 'lastpolyid' in ctouch:
					lpid = ctouch['lastpolyid']
					del ctouch['lastpolyid']
				ctouch['lastpolyid'] = self.create_poly(pos,pg,lpid)
				ctouch['pos'] = pos

		if currentTool == 'splineed':
			ent = self.mainTools.selectedEntity
			if ent:
				if hasattr(ent, 'splineshape'):
					#print "entid=", ent.entity_id
					ss = ent.splineshape
					#ss.add_or_select(pos, 40)

					if ss.selected_point != None:
						ss.ControlPoints[ss.selected_point] = pos
						ss.DrawCurve()
					ent.polyshape.from_spline(ss.subpoints)
					#print ss.ControlPoints

					if ent.polyshape.poly.area()>10:
						spline_ent_id = self.create_poly(pos,ent.polyshape,ent.entity_id)
						#print "spline_ent_id=",spline_ent_id
						spline_ent = self.getEntFromID(spline_ent_id)
						spline_ent.splineshape = ss
						shape = spline_ent.physics.shapes[0]
						self.mainTools.setEnt(spline_ent)
						#self.create_poly((0,0),pg,ent.entity_id)

		if currentTool == "camera":
			#print len(self.touches)
			ccount=0
			viewport = self.gameworld.systems['gameview']
			for t in self.touches:
				to = self.touches[t]
				if to['tool'] == 'camera':
					ccount+=1
			if ccount < 2:
				#super(TestGame, self).on_touch_move(touch)
				viewport.camera_pos[0]-=xd
				viewport.camera_pos[1]-=yd
			else:
				screen_mid = (viewport.size[0]*0.5,viewport.size[1]*0.5)
				#screen_mid = ctouch['screenpos']
				sf = 1.0-touch.dy*0.001#+yd*0.00003
				#print touch.dy
				#camera_scale = viewport.camera_scale*sf+yd*0.0001
				#camera_scale = max(0.2, min(20, camera_scale))
				self.zoomcam(sf, screen_mid)
				#print camera_scale
				#viewport.camera_scale=camera_scale


		if 'previewShape' in ctouch:
			psid = ctouch['previewShape']
			#xd = spos[0] - pos[0]
			#yd = spos[1] - pos[1]
			#dist = sqrt(xd ** 2 + yd ** 2)

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
					do_physics = self.mainTools.createMenu.spritePhysButton.state != 'down'
					self.create_box((midx, midy), mass=mass, width=dist, height=10, angle=angle,
									texture=self.mainTools.spriteSpinner.text, selectNow=False,
									do_physics=do_physics)
					ctouch['pos'] = pos

		shape = ctouch['touching']
		if currentTool == 'rotate' and shape:
			cpos = (shape.body.position.x,shape.body.position.y)
			if shape.__class__.__name__ == 'Poly':
				bb = self.getEntFromID(shape.body.data).polyshape.poly.boundingBox()
				cpos = ((bb[0]+bb[1])/2,(bb[2]+bb[3])/2)
			xd = cpos[0] - pos[0]
			yd = cpos[1] - pos[1]
			angle = atan2(yd, xd)
			if 'origAngle' not in ctouch: ctouch['origAngle'] = shape.body.angle-angle
			shape.body.angle = (angle+ctouch['origAngle'])
		if (currentTool == 'drag' or currentTool == 'paste'):
			viewport = self.gameworld.systems['gameview']
			if shape and (shape.body.is_static or self.mainTools.paused):
				dx = touch.dx*viewport.camera_scale
				dy = touch.dy*viewport.camera_scale
				shape.body.position = (shape.body.position.x + dx, shape.body.position.y + dy)
				self.reindexEntID(shape.body.data)
				if self.mainTools.paused:
					(self.gameworld.systems['physics'].update(0.00000001))
					(self.gameworld.systems['renderer'].update(0.00000001))
					(self.gameworld.systems['renderer'].update(0.00000001))
					#space.reindex_shape(shape)
			#else:
			#	ent = self.mainTools.selectedEntity#TODO alter position component here


	def on_touch_up(self, touch):
		self.mainTools.on_touch_up(touch)
		if touch.id not in self.touches:
			print super(TestGame, self).on_touch_up(touch)
			print "touchdown not found, mousewheel?"
			return
		ctouch = self.touches[touch.id]
		del self.touches[touch.id]
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

		if 'polygen' in ctouch:
			pg = ctouch['polygen']
			lpid=None
			if 'lastpolyid' in ctouch:
				lpid = ctouch['lastpolyid']
				del ctouch['lastpolyid']
			ctouch['lastpolyid'] = self.create_poly(pos,pg,lpid)

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

		ent = self.mainTools.selectedEntity
		#print currentTool, tshape
		if currentTool == 'drag':
			if ent:
				if hasattr(ent, 'splineshape'):
					ss = ent.splineshape
					cps = ss.ControlPoints

					for pindex in range(len(cps)):
						p = cps[pindex]
						cps[pindex]=(p[0]-xd, p[1]-yd)
						#p[0]-=xd
						#p[1]-=yd
					self.create_spline((0,0),ss,ent.entity_id)
				elif hasattr(ent, 'polyshape'):
					pg = ent.polyshape
					pg.poly.shift(-xd,-yd)
					self.create_poly((0,0),pg,ent.entity_id)

		if currentTool == 'rotate' and tshape:
			ispoly =  tshape.__class__.__name__ == 'Poly'
			if ispoly:
				bang =  tshape.body.angle
				entID = tshape.body.data
				ent = self.getEntFromID(entID)
				pg = ent.polyshape
				pg.poly.rotate(bang)
				self.create_poly((0,0),pg,entID)


		do_physics = self.mainTools.createMenu.spritePhysButton.state != 'down'
		last_obj = None
		print "lastobj=",last_obj
		if self.mainTools.selectedEntity and self.mainTools.cloneSpriteButton.state == 'down':
			last_obj = self.mainTools.selectedEntity
		if (currentTool == "draw" or currentTool == "plank"):
			if dist < 4: dist = 8
			#self.create_box((midx, midy), mass=mass, width=dist, height=10, angle=angle,
			#				texture=self.mainTools.spriteSpinner.text, do_physics=do_physics)
			self.create_sprite((midx, midy), mass=mass, width=dist, height=10, angle=angle,
							texture=self.mainTools.spriteSpinner.text, do_physics=do_physics,
							old_shape=last_obj)

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
			#self.create_circle(spos, mass=mass, radius=dist, texture=self.mainTools.spriteSpinner.text,
			#                   angle=angle, do_physics=do_physics)
			self.create_sprite(spos, mass=mass, radius=dist, texture=self.mainTools.spriteSpinner.text,
			                   angle=angle, do_physics=do_physics, shape_type='circle',
							old_shape=last_obj)
		if currentTool == "box":
			width = fabs(xd)
			height = fabs(yd)
			if width< 4: width=8
			if height< 4: height=8
			self.create_sprite((midx, midy), mass=mass, width=width, height=height, angle=0,
							texture=self.mainTools.spriteSpinner.text, do_physics=do_physics,
							old_shape=last_obj)
		if currentTool == "square":
			if dist < 4: dist = 8
			self.create_sprite(spos, mass=mass, width=dist * 2, height=dist * 2, angle=angle,
							texture=self.mainTools.spriteSpinner.text, do_physics=do_physics,
							old_shape=last_obj)
		#self.touches[touch.id] = {"active": False, "newpos": pos, "screenpos": (touch.x, touch.y)}
		#del self.touches[touch.id]
	def get_cam_scale(self):
		viewport = self.gameworld.systems['gameview']
		return viewport.camera_scale
	def zoomcam(self, sf, pos = (0,0)):
		pwp = self.getWorldPosFromTuple(pos)
		viewport = self.gameworld.systems['gameview']
		camera_scale = viewport.camera_scale*sf
		camera_scale = max(0.2, min(20, camera_scale))
		viewport.camera_scale=camera_scale
		pap = self.getWorldPosFromTuple(pos)
		diff = (pap[0]-pwp[0], pap[1]-pwp[1])
		viewport.camera_pos[0]+=diff[0]
		viewport.camera_pos[1]+=diff[1]
		self.mainTools.scale_cpoints(camera_scale)
	def on_touch_down(self, touch):
		print "TOUCHDOWN\n"
		#print dir(touch)
		if hasattr(touch, 'button'):
			if touch.button == 'scrollup':
				self.zoomcam(1.02, (touch.x,touch.y))
				return
			if touch.button == 'scrolldown':
				self.zoomcam(0.98, (touch.x,touch.y))
				return

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


		if currentTool == 'spline':
			newspline = Spline.Spline(stepsize=1./self.mainTools.splineMenu.smoothnessSlider.value)
			newspline.add_or_select((pos[0]-150, pos[1]), 2)
			newspline.add_or_select((pos[0], pos[1]+170), 2)
			newspline.add_or_select((pos[0]+150, pos[1]), 2)
			newspline.DrawCurve()

			spline_ent_id = self.create_spline(pos,newspline,selectNow=True)
			#pg = PolyGen.PolyGen()
			#pg.from_spline(newspline.subpoints)
			#do_physics = self.mainTools.polyMenu.polyPhysButton.state != 'down'
			#spline_ent_id =  self.create_poly(pos,pg,selectNow=True)#, do_physics=do_physics)
			spline_ent = self.getEntFromID(spline_ent_id)
			#self.mainTools.setEnt(spline_ent_id)
			shape = spline_ent.physics.shapes[0]
			#ctouch['polygen'] = pg
			self.mainTools.setTool('splineed')
			self.mainTools.splineMenu.splineButton.state = 'normal'
			self.mainTools.splineMenu.splineEdButton.state = 'down'


		if currentTool == 'splineed':
			ent = self.mainTools.selectedEntity
			if ent:
				if not hasattr(ent, 'splineshape') and hasattr(ent, 'polyshape'):
					pg = ent.polyshape
					cont = pg.poly[0]
					print len(cont)
					cp = []
					for pindex in xrange(0, len(cont), 4):
						p=cont[pindex]
						cp.append(p)
					if len(cp)>4:
						newspline = Spline.Spline()
						newspline.ControlPoints = cp
						ent.splineshape = newspline

				if hasattr(ent, 'splineshape'):
					ss = ent.splineshape
					camera_scale = self.gameworld.systems['gameview'].camera_scale
					print camera_scale*300
					ss.add_or_select(pos, 40*camera_scale, 300*camera_scale)
					ss.DrawCurve()
					ent.polyshape.from_spline(ss.subpoints)


					spline_ent_id = self.create_poly(pos,ent.polyshape,ent.entity_id)
					spline_ent = self.getEntFromID(spline_ent_id)
					spline_ent.splineshape = ss
					shape = spline_ent.physics.shapes[0]
					#self.create_poly((0,0),pg,ent.entity_id)

		if currentTool == 'splinesub':
			ent = self.mainTools.selectedEntity
			if ent:
				if not hasattr(ent, 'splineshape') and hasattr(ent, 'polyshape'):
					pg = ent.polyshape
					cont = pg.poly[0]
					print len(cont)
				if hasattr(ent, 'splineshape'):
					print "entid=", ent.entity_id
					ss = ent.splineshape
					if len(ss.ControlPoints)>3:
						viewport = self.gameworld.systems['gameview']
						ss.remove_point(pos, 40*viewport.camera_scale)
						ss.DrawCurve()
						ent.polyshape.from_spline(ss.subpoints)
						spline_ent_id = self.create_poly(pos,ent.polyshape,ent.entity_id)
						spline_ent = self.getEntFromID(spline_ent_id)
						spline_ent.splineshape = ss
						shape = spline_ent.physics.shapes[0]
					#self.create_poly((0,0),pg,ent.entity_id)

		if currentTool == 'polysub':
			polys = self.get_touching_polys(pos, radius=self.mainTools.polyMenu.brushSizeSlider.value)
			for p in polys:
				p.polyshape.sub_circle_polygon(pos, radius=self.mainTools.polyMenu.brushSizeSlider.value)
				self.create_poly(pos,p.polyshape,p.entity_id)



		if currentTool == 'poly':
			polys = []
			lastpolyid = None
			if self.mainTools.polyMenu.polyMergeButton.state != 'normal':
				polys = self.get_touching_polys(pos, radius=self.mainTools.polyMenu.brushSizeSlider.value)
			if len(polys)>0:
				e = polys[0]
				lastpolyid = e.entity_id
				pg = e.polyshape
			else:
				polyMenu = self.mainTools.polyMenu
				pg = PolyGen.PolyGen(keepsimple=polyMenu.polySimpleButton.state != 'normal',
				                     minlinelen=polyMenu.minlenslider.value)
			pg.draw_circle_polygon(pos, radius=self.mainTools.polyMenu.brushSizeSlider.value)
			do_physics = self.mainTools.polyMenu.polyPhysButton.state != 'down'
			ctouch['lastpolyid'] = self.create_poly(pos,pg, lastpolyid=lastpolyid, do_physics=do_physics)
			ctouch['polygen'] = pg

		if currentTool in ["draw", "square", "box", "circle", "plank"]:
			color = (1,1,1,1)
			if self.mainTools.selectedEntity and self.mainTools.cloneSpriteButton.state == 'down':
				c = self.mainTools.selectedEntity.color
				color = (c.r, c.g ,c.b ,c.a)
			ctouch['previewShape'] = self.create_decoration(pos=(0, 0), width=40, height=40,
															texture=self.mainTools.spriteSpinner.text,
															color=color)

		if shape and currentTool == 'del':
			if shape == self.mainTools.selectedItem:
				self.mainTools.setShape(None)
			self.delObj(shape.body.data)
			ctouch['touchingnow'] = None
			return


		if currentTool == "paste" and self.mainTools.entcpy:
			pastedEID = self.serials.loadEntFromDict(self.mainTools.entcpy)
			ent = self.gameworld.entities[pastedEID]
			if hasattr(ent, 'polyshape'):
				po = ent.polyshape.poly
				poc = po.center()
				shifter = (pos[0] - poc[0], pos[1] - poc[1])
				if hasattr(ent, 'polyshape'):
					ss = ent.splineshape
					cps = ss.ControlPoints
					for pindex in range(len(cps)):
						p = cps[pindex]
						cps[pindex]=(p[0]+shifter[0], p[1]+shifter[1])
					self.create_spline((0,0),ss,ent.entity_id)
				else:
					po.shift(shifter[0], shifter[1])
					self.create_poly((0,0),ent.polyshape,ent.entity_id)
			elif hasattr(ent, 'physics'):
				phys = ent.physics
				phys.body.position = pos
				shape = phys.shapes[0]
				#self.mainTools.setShape(shape)
				space.reindex_shape(shape)
				ctouch['touching'] = shape

		canselect = currentTool in ['camera', 'drag', 'vortex','rotate', 'delete']
		if canselect:
			if shape:
				self.mainTools.setShape(shape)
			else:
				ents = self.getNonPhysAtPoint(pos)
				ent = None
				if len(ents):ent=ents[0]
				self.mainTools.setEnt(ent)


		if shape and not shape.body.is_static and (
				currentTool == 'drag' or currentTool == 'paste' or currentTool == 'pin'):
			body = ctouch['ownbody']
			body.position = pos
			ctouch['mousejoint'] = cy.PivotJoint(shape.body, body, position)
			space.add(ctouch['mousejoint'])
	def getNonPhysAtPoint(self, pos):
		ents = []
		for aid in self.entIDs:
			entity = self.gameworld.entities[aid]
			if not hasattr(entity, 'physics'):
				if hasattr(entity, 'polyshape'):
					isin = entity.polyshape.poly.isInside(pos[0],pos[1])
					if isin:ents.append(entity)
				else:
					isin = self.get_point_in_renderer(pos,entity)
					#isin = entity.polyshape.poly.isInside(pos[0],pos[1])
					if isin:ents.append(entity)
		return ents
	def get_point_in_renderer(self, point, ent):
		if hasattr(ent, 'renderer'):
			p = list(point)
			p[0]-=ent.position.x
			p[1]-=ent.position.y
			x=p[0]
			y=p[1]
			angle = -ent.rotate.r
			transp = [
			(x * cos(angle)) - (y * sin(angle)),
			(y * cos(angle)) + (x * sin(angle))]
			r = ent.renderer
			#print transp, r.width/2., r.height/2.
			if abs(transp[0]) < abs(r.width/2.) and abs(transp[1]) < abs(r.height/2.):
				return True
		return False

	def get_touching_polys(self, pos, radius=30):
		cs = PolyGen.Circle(radius, pos, 16)
		polys = []
		for eid in self.entIDs:
			e = self.getEntFromID(eid)
			if hasattr(e, "polyshape"):
				if cs.overlaps(e.polyshape.poly):
					polys.append(e)
		return polys
	def get_touching_polys_cp(self, pos, radius=30):
		space = self.space
		cs = cy.Circle(cy.Body(), radius=radius, offset=pos)
		colshapes = space.shape_query(cs)
		polys = []
		if len(colshapes)>0:
			#print colshapes
			ents = {}
			for shape in colshapes:
				id = shape.body.data
				ents[id]=True
			for eid in ents:
				e = self.getEntFromID(eid)
				if hasattr(e, "polyshape"):
					polys.append(e)
		return polys

	def clearAll(self):
		self.startID = -1
		self.finishID = -1

		self.mainTools.setShape(None)
		space = self.space
		print "clearing objects"
		for eid in list(self.entIDs):
			#print "beforedel"
			self.delObj(eid)
			#print "afterdel"
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
		if hasattr(ent, 'polyshape'):
			delattr(ent, 'polyshape')
		if hasattr(ent, 'splineshape'):
			delattr(ent, 'splineshape')
		if hasattr(ent, "physics"):
			b = ent.physics.body
			if b.data == self.startID:self.startID=None
			if b.data == self.finishID:self.finishID=None
			removeus = self.getJointsOnBody(b)
			#for rmu in removeus:
			#	print rmu in self.space.constraints
			for c in removeus:
				#print "removing", c
				self.deleteJoint(c)
		#print ent, self.mainTools.selectedEntity
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
		return self.getWorldPosFromTuple((touch.x,touch.y))

	def getWorldPosFromTuple(self, tup):

		viewport = self.gameworld.systems['gameview']
		return tup[0]*viewport.camera_scale - viewport.camera_pos[0], tup[1]*viewport.camera_scale - viewport.camera_pos[1]

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
			#sbox.renderer.width = (bb['r']-bb['l'])*1.05+5
			#sbox.renderer.height = (bb['t']-bb['b'])*1.05+5
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
		if self.mainTools.killMomem:
			for aid in self.entIDs:
				entity = self.gameworld.entities[aid]
				if hasattr(entity, 'physics') and entity.physics.body.is_static == 0:
					v = entity.physics.body.velocity
					entity.physics.body.velocity = (v[0]*0.1,v[1]*0.1)
					entity.physics.body.angular_velocity *=0.1

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
			if hasattr(entity, 'physics') and entity.physics.body.is_static == 0:
				apos = entity.position
				dvecx = (pos[0] - apos.x) * entity.physics.body.mass * 0.02
				dvecy = (pos[1] - apos.y) * entity.physics.body.mass * 0.02
				entity.physics.body.apply_impulse((dvecx, dvecy))
				#entity.physics.body.apply_force((dvecx,dvecy))

	def setup_states(self):
		self.gameworld.add_state(state_name='main',
								 systems_added=['color', 'rotate', 'renderer', 'renderer', 'scale'],
								 systems_removed=[], systems_paused=[],
								 systems_unpaused=['color', 'rotate', 'renderer', 'renderer', 'scale'],
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
	'''def on_start(self):
		self.profile = cProfile.Profile()
		self.profile.enable()

	def on_stop(self):
		self.profile.disable()
		self.profile.dump_stats('myapp.profile')'''


def uploadCrash(crashstr):
	print "uploading crash to ", ui_elements.serverURL
	#req = UrlRequest('/listLevels', on_success=self.got_levels, timeout=1000)
	import urllib
	from kivy.network.urlrequest import UrlRequest
	params = urllib.urlencode({
	'version':__version__,
	"crashData":crashstr
	})
	headers = {'Content-type': 'application/x-www-form-urlencoded',
          'Accept': 'text/plain'}
	req = UrlRequest(ui_elements.serverURL+'/uploadCrash', on_success=None, req_body=params,
        req_headers=headers)
	req.wait()
	print "crash uploaded"

if __name__ == '__main__':
	try:
		KivEntEd().run()
	except:
		print "unexpected error"
		import traceback
		traceback.print_exc()
		print "---"
		uploadCrash(traceback.format_exc())
		print "---"
		raise
