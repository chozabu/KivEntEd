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
		self.collision_handlers = {
			'vortex':{
				'default':{'pre_solve':'grav2first'},
				'physzone':{'pre_solve':'grav2first'},
				'vortex':{'pre_solve':'grav2first'}
			},
			'physzone':{
				'default':{'pre_solve':'physicsZone'}
			}
		}
		self.loadHandlersFromDict(self.collision_handlers)
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
				print "funcargs=",funcsargs
				self.set_col_handlers(typeastr,typebstr,
				                **funcsargs)
				'''for caller, callee in funcsargs.iteritems():
					self.add_col_handler(typeastr,typebstr,caller,callee)
					#func = self.getCBFunc(callee)
					#funcdict = {caller:func}
					#print typea, typeb, func
					#self.space.add_collision_handler(typea, typeb, **funcdict)'''
	def add_col_func(self, funcstr):
		if funcstr in self.gameref.mainTools.col_funcs: return
		self.gameref.mainTools.col_funcs.append(funcstr)
	def add_col_type(self,namestr):
		if namestr in self.collision_types: return
		self.collision_types[namestr] = self.cctype
		self.gameref.mainTools.col_types.append(namestr)
		self.cctype+=1
	'''def add_col_handler(self,typeastr,typebstr,caller,callee):
		print "caller,callee", caller, callee
		typea = self.collision_types[typeastr]
		typeb = self.collision_types[typebstr]
		func = self.getCBFunc(callee)
		funcdict = {caller:func}
		print "typea, typeb, func", typea, typeb, func
		print funcdict
		self.space.add_collision_handler(typea, typeb, **funcdict)
		if typeastr not in self.collision_handlers:
			self.collision_handlers[typeastr] = {}
		otherTypes = self.collision_handlers[typeastr]
		if typebstr not in otherTypes:
			otherTypes[typebstr] = {}
		callers = otherTypes[typebstr]
		callers[caller] = callee'''
	def set_col_handlers(self,typeastr,typebstr,begin=None, pre_solve=None, post_solve=None, separate=None):
		typea = self.collision_types[typeastr]
		typeb = self.collision_types[typebstr]
		beginstr = begin
		pre_solvestr = pre_solve
		post_solvestr = post_solve
		separatestr = separate
		if(begin): begin = self.getCBFunc(begin)
		else: begin=None
		if(pre_solve):pre_solve = self.getCBFunc(pre_solve)
		else: pre_solve=None
		if(post_solve):post_solve = self.getCBFunc(post_solve)
		else: post_solve=None
		if(separate):separate = self.getCBFunc(separate)
		else: separate=None
		#funcdict = {caller:func}
		print "typea, typeb, func", typea, typeb
		#print funcdict
		self.space.add_collision_handler(typea, typeb, begin=begin, pre_solve=pre_solve, post_solve=post_solve, separate=separate)
		if typeastr not in self.collision_handlers:
			self.collision_handlers[typeastr] = {}
		otherTypes = self.collision_handlers[typeastr]
		if typebstr not in otherTypes:
			otherTypes[typebstr] = {}
		callers = otherTypes[typebstr]
		if begin: callers['begin'] = beginstr
		if pre_solve: callers['pre_solve'] = pre_solvestr
		if post_solve: callers['post_solve'] = post_solvestr
		if separate: callers['separate'] = separatestr

	def getCBFunc(self, fname):
		print "fname=",fname
		if hasattr(self, fname):
			return getattr(self, fname)
		if fname in self.colfuncs:
			return self.colfuncs[fname]
		return None