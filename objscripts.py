__author__ = 'chozabu'


import cymunk as cy
from util import TwoWayDict
from math import *

class ObjScripts():
	def __init__(self, gameref):
		self.gameref = gameref
		self.dataDir = gameref.dataDir
		self.gameworld = gameref.gameworld
		self.space = gameref.space

		self.collision_types = TwoWayDict()
		self.collision_types['default'] = 0
		self.collision_types['vortex'] = 1
		self.collision_types['physzone'] = 2
		#self.collision_funcs = ['pull2_first','grav2_first']
		#self.collision_handlers = {'vortex':{'pre_solve':('default','grav2_first')}}
		self.collision_handlers = {
			'vortex':{
				'default':{'pre_solve':'grav2_first'},
				'vortex':{'pre_solve':'grav2_first'}
			}
		}


		for typeastr, ch in self.collision_handlers.iteritems():
			typea = self.collision_types[typeastr]
			for typebstr, funcsargs in ch.iteritems():
				typeb = self.collision_types[typebstr]
				for caller, callee in funcsargs.iteritems():
					func = self.getCBFunc(callee)
					funcdict = {caller:func}
					print typea, typeb, func
					self.space.add_collision_handler(typea, typeb, **funcdict)
	def add_col_handeler(self,typeastr,typebstr,caller,callee):
		typea = self.collision_types[typeastr]
		typeb = self.collision_types[typebstr]
		func = self.getCBFunc(callee)
		funcdict = {caller:func}
		print typea, typeb, func
		self.space.add_collision_handler(typea, typeb, **funcdict)
		if typeastr not in self.collision_handlers:
			self.collision_handlers[typeastr] = {}
		otherTypes = self.collision_handlers[typeastr]
		if typebstr not in otherTypes:
			otherTypes[typebstr] = {}
		callers = otherTypes[typebstr]
		callers[caller] = callee
	def pull2_first(self, space, arbiter):
		first_body = arbiter.shapes[0].body
		second_body = arbiter.shapes[1].body
		first_pos = first_body.position
		second_pos = second_body.position
		diff = cy.Vec2d(first_pos.x-second_pos.x,first_pos.y-second_pos.y)
		#diff.x*=10
		#diff.y*=10
		second_body.apply_impulse(diff)
		#print diff
		return False

	def grav2_first(self, space, arbiter):
		firstshape = arbiter.shapes[0]
		if firstshape.__class__.__name__ != "Circle": return True
		first_body = firstshape.body
		second_body = arbiter.shapes[1].body
		first_pos = first_body.position
		second_pos = second_body.position
		diff = cy.Vec2d(first_pos.x-second_pos.x,first_pos.y-second_pos.y)
		dist = sqrt(diff.x**2+diff.y**2)
		uv = cy.Vec2d(diff.x/dist, diff.y/dist)
		invrad = firstshape.radius-dist
		if invrad <=0001: invrad = 0001
		invrad = sqrt(invrad)*second_body.mass
		force = cy.Vec2d(uv.x*invrad, uv.y*invrad)
		second_body.apply_impulse(force)
		return False
	def getCBFunc(self, fname):
		if hasattr(self, fname):
			return getattr(self, fname)
		return None