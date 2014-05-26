__author__ = 'chozabu'


import cymunk as cy
from util import TwoWayDict
from math import *
import os
import glob
import importlib

class ObjScripts():
	def __init__(self, gameref):
		self.gameref = gameref
		self.dataDir = gameref.dataDir
		self.gameworld = gameref.gameworld
		self.space = gameref.space

		self.add_col_func('None')

		self.colfuncs = {}

		foundmods = [ os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__)+"/scripts/collision/*.py")]
		#foundmods.remove("__init__")
		basepath = "scripts.collision."
		for m in foundmods:
			inmod = importlib.import_module(basepath+m)
			if hasattr(inmod, "collision_func"):
				inmod.scripty = self
				self.colfuncs[m] = inmod.collision_func
				self.add_col_func(m)

		self.collision_types = TwoWayDict()
		self.cctype = 0
		self.add_col_type('default')
		self.add_col_type('vortex')
		self.add_col_type('physzone')
		#self.collision_funcs = ['pull2_first','grav2_first']
		#self.collision_handlers = {'vortex':{'pre_solve':('default','grav2_first')}}
		#self.add_col_func('grav2_first')
		#self.add_col_func('pull2_first')
		self.collision_handlers = {
			'vortex':{
				'default':{'pre_solve':'grav2first'},
				'vortex':{'pre_solve':'grav2first'}
			}
		}
		self.loadHandlersFromDict(self.collision_handlers)
	def loadHandlersFromDict(self, handlers):
		for typeastr, ch in handlers.iteritems():
			typea = self.collision_types[typeastr]
			for typebstr, funcsargs in ch.iteritems():
				typeb = self.collision_types[typebstr]
				for caller, callee in funcsargs.iteritems():
					func = self.getCBFunc(callee)
					funcdict = {caller:func,"love":"love"}
					print typea, typeb, func
					self.space.add_collision_handler(typea, typeb, **funcdict)
	def add_col_func(self, funcstr):
		if funcstr in self.gameref.mainTools.col_funcs: return
		self.gameref.mainTools.col_funcs.append(funcstr)
	def add_col_type(self,namestr):
		if namestr in self.collision_types: return
		self.collision_types[namestr] = self.cctype
		self.gameref.mainTools.col_types.append(namestr)
		self.cctype+=1
	def add_col_handler(self,typeastr,typebstr,caller,callee):
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

	def getCBFunc(self, fname):
		if hasattr(self, fname):
			return getattr(self, fname)
		if fname in self.colfuncs:
			return self.colfuncs[fname]
		return None