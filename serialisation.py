__author__ = 'chozabu'

import json
import cymunk as cy
import os


class Serials():
	def __init__(self, gameref):
		self.gameref = gameref
		self.dataDir = gameref.dataDir
		self.gameworld = gameref.gameworld
		self.space = gameref.space
	def shapeToDict(self, shape):
		ct = self.gameref.scripty.collision_types
		sd = {'collision_type': ct[shape.collision_type], 'elasticity': shape.elasticity, 'friction': shape.friction,
			  'group': shape.group}
		if hasattr(shape, "radius"):
			sd['radius'] = shape.radius
		else:
			sd['width'] = shape.width
			sd['height'] = shape.height
		return sd

	def entToDict(self, e):
		ed = {"orig_id": e.entity_id}
		#'load_order', 'physics', 'physics_renderer', 'position', 'rotate'
		if hasattr(e, "load_order"):
			ed["load_order"] = e.load_order
		if hasattr(e, "physics"):
			b = e.physics.body
			bd = {'velocity': (b.velocity.x, b.velocity.y),
				  'position': (b.position.x, b.position.y),
				  'angle': b.angle,
				  'angular_velocity': b.angular_velocity,
				  'vel_limit': b.velocity_limit,
				  'ang_vel_limit': b.angular_velocity_limit,
				  'mass': b.mass
			}
			shapes = []
			for s in e.physics.shapes:
				#print s
				#print dir(s)
				shapes.append(self.shapeToDict(s))
			pd = {"shapes": shapes, "shape_type": e.physics.shape_type, "body": bd}
			ed["physics"] = pd
		if hasattr(e, "physics_renderer"):
			prd = {"width": e.physics_renderer.width, "height": e.physics_renderer.height,
				   "texture": e.physics_renderer.texture}
			ed["physics_renderer"] = prd
		if hasattr(e, "position"):
			pd = {"x": e.position.x, "y": e.position.y}
			ed["position"] = pd
		if hasattr(e, "rotate"):
			rd = {"r": e.rotate.r}
			ed["rotate"] = rd
		return ed

	def exportJointsToDicts(self):
		space = self.space
		jds = []
		for j in space.constraints:
			jtype = j.__class__.__name__
			anchor1 = j.anchor1
			#if None == j.a.data and j.a != space.static_body:
			#  anchor1 = {'x':j.a.position.x, 'y':j.a.position.y}

			anchor2 = j.anchor2
			if anchor2['x'] == 0 and anchor2['y'] == 0 and j.b.data is None:
				anchor2 = {'x': j.b.position.x, 'y': j.b.position.y}
			jd = {"type": jtype, "a": j.a.data, "b": j.b.data,
				  "anchor1": anchor1, "anchor2": anchor2}
			if jtype == "DampedSpring":
				jd['rest_length'] = j.rest_length
				jd['stiffness'] = j.stiffness
				jd['damping'] = j.damping
			jds.append(jd)
		return jds

	def exportEntsToDicts(self):
		entsdict = []
		for eid in self.gameref.entIDs:
			e = self.gameworld.entities[eid]
			#print "\n"
			ed = self.entToDict(e)
			entsdict.append(ed)
		return entsdict

	def exportJSON(self, fileName="defaultlevel.json"):
		dataDir = self.dataDir
		space = self.space
		entslist = self.exportEntsToDicts()
		jointslist = self.exportJointsToDicts()

		collision_typeslist = self.gameref.mainTools.col_types
		collision_typesdict = self.gameref.scripty.collision_handlers

		worlddict = {"ents": entslist, "jointslist": jointslist,
					 "collision_typeslist": collision_typeslist, "collision_typesdict": collision_typesdict,
					 "settings": {"gravity": (space.gravity.x, space.gravity.y),
								  "startID":self.gameref.startID, "finishID": self.gameref.finishID}}
		with open(dataDir + fileName, 'w') as fo:
			json.dump(worlddict, fo)
		print "dir=", dataDir
		print "done"
		return worlddict

	def loadJSON(self, fileName="defaultlevel.json"):
		self.loadExtJSON(self.dataDir + fileName)

	def loadExtJSON(self, fileNamePath):
		if not os.path.isfile(fileNamePath): return
		with open(fileNamePath) as fo:
			entsdict = json.load(fo)
		self.loadFromDict(entsdict)

	def loadCollisionTypesFromDict(self, clist, cdata):
		scripty = self.gameref.scripty
		for ct in clist:
			scripty.add_col_type(ct)
		scripty.loadHandlersFromDict(cdata)
	def loadEntFromDict(self, e, idConvDict=None):
		if "physics" in e:
			stype = e['physics']['shape_type']
			pr = e['physics_renderer']
			p = e['physics']
			body = p['body']
			shape = p['shapes'][0]
			bp = (body['position'][0], body['position'][1])
			mass = body['mass']
			texture = str(pr['texture'])
			collision_type = 0
			if 'collision_type' in shape:
				coltypestr = shape['collision_type']
				ct = self.gameref.scripty.collision_types
				if coltypestr in ct:
					collision_type = ct[coltypestr]
			if str(mass) == 'inf': mass = 0
			if stype == "circle":
				entID = self.gameref.create_circle(bp, radius=shape['radius'], mass=mass,
															  friction=shape['friction'],
															  elasticity=shape['elasticity'], angle=body['angle'],
															  x_vel=body['velocity'][0], y_vel=body['velocity'][1],angular_velocity=body['angular_velocity'],
															  texture=texture, selectNow=False, collision_type=collision_type)
				if idConvDict: idConvDict[e['orig_id']] = entID
				return entID
			elif stype == "box":
				entID = self.gameref.create_box(bp, width=shape['width'], height=shape['height'],
														   mass=mass, friction=shape['friction'],
														   elasticity=shape['elasticity'], angle=body['angle'],
														   x_vel=body['velocity'][0], y_vel=body['velocity'][1],angular_velocity=body['angular_velocity'],
														   texture=texture, selectNow=False, collision_type=collision_type)
				if idConvDict: idConvDict[e['orig_id']] = entID
				return entID
	def loadFromDict(self, data):
		print "LOADING"
		space = self.space
		if "collision_typeslist" in data and "collision_typesdict" in data:
			self.loadCollisionTypesFromDict(data["collision_typeslist"],data["collision_typesdict"])
		ents = data['ents']
		idConvDict = {}
		for e in ents:
			self.loadEntFromDict(e, idConvDict)
		if "jointslist" in data:
			jointslist = data['jointslist']
			for j in jointslist:
				if j['a'] in idConvDict:
					b1id = idConvDict[j['a']]
					b1 = self.gameworld.entities[b1id].physics.body
				else:
					b1 = cy.Body()
				if j['b'] in idConvDict:
					b2id = idConvDict[j['b']]
					b2 = self.gameworld.entities[b2id].physics.body
				else:
					b2 = cy.Body()
				b1l = j['anchor1']
				b2l = j['anchor2']
				if str(j['type']) == "PivotJoint":
					qj = cy.PivotJoint(b1, b2, (b1l['x'], b1l['y']), (
					b2l['x'], b2l['y']))  #, (b1.position.x,b1.position.y),(b2.position.x,b2.position.y))
					space.add(qj)
				if str(j['type']) == "PinJoint":
					qj = cy.PinJoint(b1, b2, (b1l['x'], b1l['y']), (
					b2l['x'], b2l['y']))  #, (b1.position.x,b1.position.y),(b2.position.x,b2.position.y))
					space.add(qj)
				if str(j['type']) == "DampedSpring":
					qj = cy.DampedSpring(b1, b2, (b1l['x'], b1l['y']), (b2l['x'], b2l['y']), j['rest_length'],
										 j['stiffness'],
										 j['damping'])  #, (b1.position.x,b1.position.y),(b2.position.x,b2.position.y))
					space.add(qj)
		if "settings" in data:
			settings = data['settings']
			g = settings['gravity']
			space.gravity = (g[0], g[1])
			if "startID" in settings:
				sid = settings['startID']
				if sid != -1:
					self.gameref.startID = idConvDict[sid]
			if "finishID" in settings:
				fid = settings['finishID']
				if fid != -1:
					self.gameref.finishID = idConvDict[fid]

