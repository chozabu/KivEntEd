__author__ = 'chozabu'

import json
import cymunk as cy
import os
import xml.etree.ElementTree as ET
from math import cos, sin
import math

xmScale = 0.08

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
		if hasattr(e, "color"):
			ed["color"] = [e.color.r,e.color.g,e.color.b,e.color.a]
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
		if hasattr(e, 'datadict'):
			ed['datadict'] = e.datadict
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

	def getcircleverts(self, radius):
		angle = 0
		count = 6.0
		step = math.pi/count
		verts = []
		for i in range(int(count*2)):
			angle = step*i
			verts.append((cos(angle)*radius,sin(angle)*radius))
		return verts

#http://stackoverflow.com/questions/22364828/create-a-square-polygon-random-oriented-from-midpoints-in-python
	def getboxverts(self, angle, width, height):
		""" Calculate coordinates of a rotated square centered at 'cx, cy'
		    given its 'size' and rotation by 'degrees' about its center.
		"""
		l, r, b, t = -width/2, width/2,-height/2, height/2
		a = angle#radians(degrees)
		cosa, sina = cos(-a), sin(-a)
		pts = [(l, b), (l, t), (r, t), (r, b)]
		return [(( (x)*cosa + (y)*sina),
		         (-(x)*sina + (y)*cosa)) for x, y in pts]


	def entToXML(self, e, root):
		'''
	<block id="path4821">
		<position y="31.9388731278" x="8.00786973338" background="true"/>
		<usetexture id="Dirt"/>
		<vertex x="-40.035368" y="-33.729557"/>
		'''
		'''
		info = ET.SubElement(root,'info')
		info.set('id','levelid')
		name = ET.SubElement(info,'name')
		name.text="LevelName"
		'''

		if not hasattr(e, "physics") or not hasattr(e, "physics_renderer"):
			return None

		if e.entity_id == self.gameref.startID or e.entity_id == self.gameref.finishID:
			ed = ET.SubElement(root,'entity')
			pd = ET.SubElement(ed,'position')
			if e.entity_id == self.gameref.startID:
				ed.set('typeid', 'PlayerStart')
			if e.entity_id == self.gameref.finishID:
				ed.set('typeid', 'EndOfLevel')
			pd.set("x", str(e.position.x*xmScale))
			pd.set("y", str(e.position.y*xmScale))
			sd = ET.SubElement(ed,'size')
			sd.set("r", "0.5")
			return
		ed = ET.SubElement(root,'block')
		ed.set("id", str(e.entity_id))



		#info = ET.SubElement(root,'info')
		#info.set('id','levelid')
		#if hasattr(e, "color"):
		#	ed["color"] = [e.color.r,e.color.g,e.color.b,e.color.a]
		b = e.physics.body
		shape_type = e.physics.shape_type
		#<position y="31.9388731278" x="8.00786973338" background="true"/>
		#<usetexture id="Dirt"/>
		pd = ET.SubElement(ed,'position')
		pd.set("x", str(e.position.x*xmScale))
		pd.set("y", str(e.position.y*xmScale))
		pd.set("background", "false")

		if not e.physics.body.is_static:
			pd.set("physics", "true")
			phd = ET.SubElement(ed,'physics')
			phd.set("mass", str(e.physics.body.mass))
			#<physics mass="1.0"/>
		else:
			self.laststatic = e.entity_id

		td = ET.SubElement(ed,'usetexture')
		td.set("id", e.physics_renderer.texture)
		verts = []
		if shape_type == "box":
			verts = self.getboxverts(b.angle, e.physics_renderer.width, e.physics_renderer.height)
		if shape_type == "circle":
			verts = self.getcircleverts(e.physics_renderer.width/2.0)
		for v in verts:
			vd = ET.SubElement(ed,'vertex')
			vd.set("x", str(v[0]*xmScale))
			vd.set("y", str(v[1]*xmScale))

		#e.physics_renderer.texture

	def exportEntsToXML(self, root):
		entsdict = []
		for eid in self.gameref.entIDs:
			e = self.gameworld.entities[eid]
			self.entToXML(e, root)

	'''
	<entity id="rect14476jl_joint1" typeid="Joint">
		<size r="0.5"/>
		<position y="9.691309" x="-69.88762075"/>
		<joint connection-end="rect14476jl_block1" type="pivot" connection-start="rect14476jl_block0"/>
	</entity>'''
	def exportJointsToXML(self, root):
		space = self.space
		for j in space.constraints:
			jtype = j.__class__.__name__
			anchor1 = j.anchor1
			#if None == j.a.data and j.a != space.static_body:
			#  anchor1 = {'x':j.a.position.x, 'y':j.a.position.y}

			anchor2 = j.anchor2
			if anchor2['x'] == 0 and anchor2['y'] == 0 and j.b.data is None:
				anchor2 = {'x': j.b.position.x, 'y': j.b.position.y}
			print jtype
			if jtype == "PivotJoint" or jtype == "PinJoint":
				ed = ET.SubElement(root,'entity')
				ed.set('id', str(j))
				ed.set('typeid', 'Joint')

				pd = ET.SubElement(ed,'position')
				#pd.set("x", str(e.position.x*xmScale))
				#pd.set("y", str(e.position.y*xmScale))
				pd.set("x", str(j.a.position.x*xmScale))
				pd.set("y", str(j.a.position.y*xmScale))

				sd = ET.SubElement(ed,'size')
				sd.set("r", "0.5")
				end = j.b.data
				if end == None: end=self.laststatic
				jd = ET.SubElement(ed,'joint')
				jd.set("type", "pivot")
				jd.set("connection-end", str(j.a.data))
				jd.set("connection-start", str(end))
			'''
			jd = {"type": jtype, "a": j.a.data, "b": j.b.data,
				  "anchor1": anchor1, "anchor2": anchor2}
			if jtype == "DampedSpring":
				jd['rest_length'] = j.rest_length
				jd['stiffness'] = j.stiffness
				jd['damping'] = j.damping
			jds.append(jd)'''

	def exportXML(self, fileName="defaultlevel.lvl"):
		root = ET.Element('level')
		info = ET.SubElement(root,'info')
		info.set('id','levelid')
		name = ET.SubElement(info,'name')
		name.text="LevelName"
		sky = ET.SubElement(info,'sky')
		sky.text="sky1"

		limits = ET.SubElement(root,'info')
		limits.set('id','levelid')
		self.exportEntsToXML(root)
		self.exportJointsToXML(root)

		#info = ET.SubElement(root,'info')
		#info.set('id','levelid')

		tree = ET.ElementTree(root)
		from kivy.utils import platform
		if platform == 'android':
			if not os.path.exists('/sdcard/xlvls/'):
				os.makedirs('/sdcard/xlvls/')
			fileName = '/sdcard/xlvls/'+fileName
		tree.write(fileName)
		print "saved", fileName
	def exportDict(self):
		space = self.space
		entslist = self.exportEntsToDicts()
		jointslist = self.exportJointsToDicts()

		collision_typeslist = self.gameref.mainTools.col_types
		collision_typesdict = self.gameref.scripty.collision_handlers

		worlddict = {"ents": entslist, "jointslist": jointslist,
					 "collision_typeslist": collision_typeslist, "collision_typesdict": collision_typesdict,
					 "settings": {"gravity": (space.gravity.x, space.gravity.y),
								  "startID":self.gameref.startID, "finishID": self.gameref.finishID}}
		return worlddict

	def exportJSON(self, fileName="defaultlevel.json"):
		dataDir = self.dataDir
		worlddict = self.exportDict()
		with open(dataDir + fileName, 'w') as fo:
			json.dump(worlddict, fo)
		settingsDict = {"lastSave":fileName}
		with open(dataDir + "settings.jso", 'w') as fo:
			json.dump(settingsDict, fo)
		#print "dir=", dataDir
		#print "done"
		print "saved", fileName
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
			if texture == "Grass2": texture = "Grass1"
			color = (1,1,1,1)
			if 'color' in e:
				cl = e['color']
				color = (cl[0],cl[1],cl[2],cl[3])
			collision_type = 0
			if 'collision_type' in shape:
				coltypestr = shape['collision_type']
				ct = self.gameref.scripty.collision_types
				if coltypestr in ct:
					collision_type = ct[coltypestr]
			if str(mass) == 'inf': mass = 0
			entID = None
			if stype == "circle":
				entID = self.gameref.create_circle(bp, radius=shape['radius'], mass=mass,
															  friction=shape['friction'],
															  elasticity=shape['elasticity'], angle=body['angle'],
															  x_vel=body['velocity'][0], y_vel=body['velocity'][1],angular_velocity=body['angular_velocity'],
															  texture=texture, selectNow=False, collision_type=collision_type, color=color)
			elif stype == "box":
				entID = self.gameref.create_box(bp, width=shape['width'], height=shape['height'],
														   mass=mass, friction=shape['friction'],
														   elasticity=shape['elasticity'], angle=body['angle'],
														   x_vel=body['velocity'][0], y_vel=body['velocity'][1],angular_velocity=body['angular_velocity'],
														   texture=texture, selectNow=False, collision_type=collision_type, color=color)
			if entID != None:
				if idConvDict!=None: idConvDict[e['orig_id']] = entID
				newent = self.gameref.getEntFromID(entID)
				if 'datadict' in e:
					newent.datadict = e['datadict']
			return entID
	def loadFromDict(self, data):
		print "LOADING"
		space = self.space
		if "collision_typeslist" in data and "collision_typesdict" in data:
			self.loadCollisionTypesFromDict(data["collision_typeslist"],data["collision_typesdict"])
		ents = data['ents']
		idConvDict = {}
		for e in ents:
			self.loadEntFromDict(e, idConvDict=idConvDict)
		if "jointslist" in data:
			jointslist = data['jointslist']
			for j in jointslist:
				if j['a'] in idConvDict:
					b1id = idConvDict[j['a']]
					print j['a'], b1id
					b1 = self.gameworld.entities[b1id].physics.body
				else:
					b1 = cy.Body()
				if j['b'] in idConvDict:
					b2id = idConvDict[j['b']]
					print j['b'], b2id
					b2 = self.gameworld.entities[b2id].physics.body
				else:
					b2 = cy.Body()
				kwargs = {}
				b1l = j['anchor1']
				b2l = j['anchor2']
				if str(j['type']) == "DampedSpring":
					kwargs = {'rest_length':j['rest_length'],
					'stiffness':j['stiffness'],
					'damping':j['damping']}
				self.gameref.create_joint(b1, b2, (b1l['x'], b1l['y']), (
					b2l['x'], b2l['y']), str(j['type']), **kwargs)
					#space.add(qj)
		if "settings" in data:
			settings = data['settings']
			self.gameref.setGrav(settings['gravity'])
			#space.gravity = (g[0], g[1])
			if "startID" in settings:
				sid = settings['startID']
				if sid != -1:
					self.gameref.startID = idConvDict[sid]
			if "finishID" in settings:
				fid = settings['finishID']
				if fid != -1:
					self.gameref.finishID = idConvDict[fid]

