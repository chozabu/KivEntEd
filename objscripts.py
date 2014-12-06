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
		self.defaults = {}

		foundmods = [ os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__)+"/scripts/collision/*.py")]
		foundmods2 = [ os.path.basename(f)[:-4] for f in glob.glob(os.path.dirname(__file__)+"/scripts/collision/*.pyo")]
		foundmods = foundmods+foundmods2
		#foundmods.remove("__init__")
		basepath = "scripts.collision."
		for m in foundmods:
			#basemod = __import__(basepath+m)
			#inmod = getattr(basemod.collision, m)
			inmod = __import__(basepath+m,
			                 globals=globals(),
			                 locals=locals(),
			                 fromlist=[m], level=0)
			#inmod = importlib.import_module(basepath+m)
			if hasattr(inmod, "collision_func"):
				inmod.scripty = self
				self.colfuncs[m] = inmod.collision_func
				self.add_col_func(m)
				if hasattr(inmod, "defaults"):
					print inmod.defaults
					self.defaults[m] = inmod.defaults

		self.collision_types = TwoWayDict()
		self.cctype = 0
		self.add_col_type('default')
		self.add_col_type('vortex')
		self.add_col_type('physzone')
		self.add_col_type('start')
		self.add_col_type('finish')
		self.collision_handlers = {
			'vortex':{
				'default':{'pre_solve':'grav2first'},
				'physzone':{'pre_solve':'grav2first'},
				'vortex':{'pre_solve':'grav2first'}
			},
			'physzone':{
				'default':{'pre_solve':'physicsZone'}
			},
			'start':{
				'default':{'pre_solve':'startScript'}
			},
			'finish':{
				'default':{'pre_solve':'endScript'}
			}
		}
		self.loadHandlersFromDict(self.collision_handlers)
	def startScript(self, space, arbiter):
		return False
	def endScript(self, space, arbiter):
		return False
	def getHandlersForType(self, ctype):
		ctype = self.collision_types[ctype]
		results = []
		print "getting results for", ctype
		if ctype in self.collision_handlers:
			ch = self.collision_handlers[ctype]
			print "ch", ch
			for i in ch.values():
				print "i", i
				for j in i.values():
					print "j", j
					if j not in results:
						results.append(j)
		return results
	def loadHandlersFromDict(self, handlers):
		for typeastr, ch in handlers.iteritems():
			#typea = self.collision_types[typeastr]
			for typebstr, funcsargs in ch.iteritems():
				#typeb = self.collision_types[typebstr]
				#print "funcargs=",funcsargs
				self.set_col_handlers(typeastr,typebstr,
				                **funcsargs)
	def add_col_func(self, funcstr):
		if funcstr in self.gameref.mainTools.col_funcs: return
		self.gameref.mainTools.col_funcs.append(funcstr)
	def add_col_type(self,namestr):
		if namestr in self.collision_types: return self.collision_types[namestr]
		self.collision_types[namestr] = self.cctype
		self.gameref.mainTools.col_types.append(namestr)
		self.cctype+=1
		return self.collision_types[namestr]
	def set_col_handlers(self,typeastr,typebstr,begin=None, pre_solve=None, post_solve=None, separate=None):
		typea = self.collision_types[typeastr]
		typeb = self.collision_types[typebstr]
		beginF = self.getCBFunc(begin)
		pre_solveF = self.getCBFunc(pre_solve)
		post_solveF = self.getCBFunc(post_solve)
		separateF = self.getCBFunc(separate)
		#print "typea, typeb, func", typea, typeb
		self.space.add_collision_handler(typea, typeb, begin=beginF, pre_solve=pre_solveF, post_solve=post_solveF, separate=separateF)
		if typeastr not in self.collision_handlers:
			self.collision_handlers[typeastr] = {}
		otherTypes = self.collision_handlers[typeastr]
		if typebstr not in otherTypes:
			otherTypes[typebstr] = {}
		callers = otherTypes[typebstr]
		callers.clear()
		if begin: callers['begin'] = begin
		if pre_solve: callers['pre_solve'] = pre_solve
		if post_solve: callers['post_solve'] = post_solve
		if separate: callers['separate'] = separate

	def getCBFunc(self, fname):
		if fname  == None:return None
		if hasattr(self, fname):
			return getattr(self, fname)
		if fname in self.colfuncs:
			return self.colfuncs[fname]
		return None