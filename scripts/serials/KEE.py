__author__ = 'chozabu'

import json
import cymunk as cy
import os
import Polygon.IO as pio
import PolyGen, Spline
#from kivent import VertMesh
from kivent_core.renderers import texture_manager, VertMesh

import base64

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
		shapetype = shape.__class__.__name__
		if shapetype == "Circle":
			sd['radius'] = shape.radius
		elif shapetype == "BoxShape":
			sd['width'] = shape.width
			sd['height'] = shape.height
		elif shapetype == "Poly":
			try:
				verts = shape.get_local_vertices()
				vertups = [(v.x, v.y) for v in verts]
				sd['verts'] = vertups
			except:
				print "verts not exported"
		return sd

	def entToDict(self, e):
		ed = {"orig_id": e.entity_id}
		#'load_order', 'physics', 'renderer', 'position', 'rotate'
		if hasattr(e, "load_order"):
			ed["load_order"] = e.load_order
		if hasattr(e, "color"):
			ed["color"] = [e.color.r,e.color.g,e.color.b,e.color.a]
		if hasattr(e, 'splineshape'):
			ss = e.splineshape
			points = list(ss.ControlPoints)
			ed["splineshape"] = {'ControlPoints':points, 'stepsize':ss.stepsize}
		if hasattr(e, "polyshape"):
			poly = e.polyshape.poly
			polystr = base64.encodestring(pio.encodeBinary(poly))
			ed["polyviewbinary"] = polystr
			ed["polyviewtristrip"] = poly.triStrip()
			ed['outlineinfo'] = {
			       'up':e.polyshape.outlineup, 'down':e.polyshape.outlinedown
			}

			postr = []
			index = 0
			for line in poly:
				postr.append({"ishole":poly.isHole(index), "line":line})
				index+=1
			ed["polyview"] = postr
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
		'''if hasattr(e, "renderer"):
			prd = {"texture": e.renderer.texture}
			ed["renderer"] = prd
		if hasattr(e, "renderer"):
			prd = {"width": e.renderer.width, "height": e.renderer.height,
				   "texture": e.renderer.texture}
			ed["renderer"] = prd'''
		if hasattr(e, "renderer"):
			#print dir(e.renderer)
			#print e.renderer.texture_key
			if e.renderer.width != 0:
				prd = {"width": e.renderer.width, "height": e.renderer.height,
					   "texture": e.renderer.texture_key}
			else:
				prd = {"texture": e.renderer.texture_key}
			ed["renderer"] = prd
		if hasattr(e, "outline_renderer"):
			#print dir(e.renderer)
			#print e.renderer.texture_key
			print dir(e.outline_renderer.vert_mesh)
			prd = {"texture": e.outline_renderer.texture_key,
				"verts":e.outline_renderer.vert_mesh.data,
			    "indices":e.outline_renderer.vert_mesh.indices
			}
			ed["outline_renderer"] = prd
		if hasattr(e, "position"):
			pd = {"x": e.position.x, "y": e.position.y, "z": e.position.z}
			ed["position"] = pd
		if hasattr(e, "rotate"):
			rd = {"r": e.rotate.r}
			ed["rotate"] = rd
		if hasattr(e, "scale"):
			ed["scale"] = e.scale.s
		if hasattr(e, 'datadict'):
			ed['datadict'] = dict(e.datadict)
		return ed

	def exportJointsToDicts(self, constraints):
		jds = []
		for j in constraints:
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
	def exportEntIDsToDicts(self, entids):
		entsdict = []
		for eid in entids:
			e = self.gameworld.entities[eid]
			ed = self.entToDict(e)
			entsdict.append(ed)
		return entsdict
	def exportEntsToDicts(self, ents):
		entsdict = []
		for e in ents:
			ed = self.entToDict(e)
			entsdict.append(ed)
		return entsdict

	def exportDict(self):
		space = self.space
		entslist = self.exportEntIDsToDicts(self.gameref.entIDs)
		jointslist = self.exportJointsToDicts(space.constraints)

		collision_typeslist = self.gameref.mainTools.col_types
		collision_typesdict = self.gameref.scripty.collision_handlers

		gr = None
		gb = self.gameref.mainTools.grav_backup
		if self.gameref.mainTools.killMomem and not (gb.x == 0 and gb.y == 0):
			gr = gb
		else:
			gr = self.gameref.space.gravity
		gt = (gr.x,gr.y)

		viewport = self.gameref.gameworld.systems['gameview']
		camDict = {
		'x':viewport.camera_pos[0],
		'y':viewport.camera_pos[1],
		'scale':viewport.camera_scale}

		bgimg = os.path.split(self.gameref.bgrect.source)[-1][:-4]

		worlddict = {"ents": entslist, "jointslist": jointslist,
					 "collision_typeslist": collision_typeslist, "collision_typesdict": collision_typesdict,
					 "settings": {"gravity": gt,
								  "startID":self.gameref.startID, "finishID": self.gameref.finishID,
								  "killMomem":self.gameref.mainTools.killMomem, "paused": self.gameref.mainTools.paused,
								  'camera':camDict, 'background':bgimg},
					 }
		return worlddict
	def getConstraintsFromEnts(self, ents):
		gameworld = self.gameref.gameworld
		gwe=gameworld.entities
		#for e in ents
	def exportCustomDict(self, ents):
		space = self.space
		gameref = self.gameref
		getJointsOnBody = gameref.getJointsOnBody
		entslist = self.exportEntsToDicts(ents)
		#print entslist
		entiddict={}
		for e in entslist:entiddict[e['orig_id']]=True
		jdict = {}
		#get joints where both ends are connected to one of our ents
		for e in ents:
			if hasattr(e, 'physics'):
				for j in getJointsOnBody(e.physics.body):
					if j.a.data in entiddict and j.b.data in entiddict:
						jdict[j]=True
		jointslist = self.exportJointsToDicts(list(jdict))

		collision_typeslist = self.gameref.mainTools.col_types
		collision_typesdict = self.gameref.scripty.collision_handlers

		customdict = {"ents": entslist, "jointslist": jointslist,
					 "collision_typeslist": collision_typeslist, "collision_typesdict": collision_typesdict}
		return customdict

	def writeSerialisedData(self, data, fileName):
		dataDir = self.dataDir
		fileNamePath=dataDir + 'groups/' + fileName
		with open(fileNamePath, 'wb') as fo:
				fo.write(data)
	def readSerialisedData(self, fileName):
		dataDir = self.dataDir
		fileNamePath=dataDir + 'groups/' + fileName
		with open(fileNamePath, 'r') as fo:
				return fo.read()
	def readExampleSerialisedData(self, fileName):
		fileNamePath='prefabs/' + fileName
		with open(fileNamePath, 'r') as fo:
				return fo.read()
	def exportJSON(self, fileName="defaultlevel.json"):
		dataDir = self.dataDir
		worlddict = self.exportDict()
		with open(dataDir + 'levels/' + fileName, 'w') as fo:
			json.dump(worlddict, fo)
		settingsDict = {"lastSave":fileName}
		with open(dataDir + "settings.jso", 'w') as fo:
			json.dump(settingsDict, fo)
		#print "dir=", dataDir
		#print "done"
		print "saved", fileName
		return worlddict

	def loadJSON(self, fileName="defaultlevel.json"):
		self.loadExtJSON(self.dataDir + 'levels/' + fileName)

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


	def loadColors(self, s, e):
		return tuple(s)
	def loadPosition(self, s, e):
		if 'z' in s:
			return (s['x'],s['y'], s['z'])
		return (s['x'],s['y'])
	def loadRotate(self, s, e):
		return s['r']
	def loadPhysics(self, s, e):
		s=dict(s)
		#print s
		s['col_shapes']=s['shapes']
		submass = s['body']['mass']/float(len(s['col_shapes']))
		for shape in s['col_shapes']:
			#print "shape:", shape
			if 'radius' in shape:
				shape['shape_info']={'inner_radius': 0, 'outer_radius': shape['radius'],
					  'mass': submass, 'offset': (0, 0)}
				shape['shape_type']='circle'
			#print "shape:", shape
			elif 'verts' in shape:
				shape['shape_info']={'vertices': shape['verts'],
					  'mass': submass, 'offset': (0, 0)}
				shape['shape_type']='poly'
				#print shape
			elif 'width' in shape:
				shape['shape_info']={'width': shape['width'],'height': shape['height'],
					  'mass': submass}
				shape['shape_type']='box'
			else:
				print "NOT HANDLING SHAPE", shape
			coltypestr = shape['collision_type']
			ct = self.gameref.scripty.collision_types
			#print "collision types"
			#print shape['collision_type']
			if coltypestr in ct:
				collision_type = ct[coltypestr]
				if collision_type != str(collision_type):
					shape['collision_type'] = collision_type
			#print shape['collision_type']
		for x in s['body']:
			s[x]=s['body'][x]
		if str(s['mass']) == 'inf': s['mass'] = 0
		return s
	def loadPhysics_renderer(self, s, e):
		#{u'width': 60.0, u'texture': u'orb', u'height': 60.0}
		#{'texture': texture, 'size': (radius * 2, radius * 2)}
		if 'width' not in s:
			return self.loadPoly_renderer(s,e)
		return {'texture': str(s['texture']), 'size': (s['width'],s['height'])}
	def loadPoly_renderer(self,s,e):

		triangles, all_verts,  tri_count, vert_count =PolyGen.tristripToKDict(e["polyviewtristrip"], self.loadColors(e['color'], None))

		render_system = self.gameref.gameworld.systems['renderer']
		vert_count = len(all_verts)
		ot=triangles
		triangles=[]
		for t in ot:
			triangles.extend(list(t))
		index_count = len(triangles)
		vert_mesh =  VertMesh(render_system.attribute_count,
			vert_count, index_count)
		#print triangles
		#print all_verts
		vert_mesh.indices = triangles
		for i in range(vert_count):
			vert_mesh[i] = all_verts[i]
		texture = str(s['texture'])
		if texture.endswith('.png'):
			texture=texture.split('/')[-1][:-4]
		rdict = {'texture': texture,
			'vert_mesh': vert_mesh,
			#'size': (64, 64),
			'render': True}

		'''cd = {'triangles': new_triangles, 'vertices': new_vertices,
			'vert_count': vert_count, 'tri_count': tri_count,
			'vert_data_count': 5,'texture': texture, 'do_texture':True}
		'''#print cd
		#print "polytex:",s['texture']
		return rdict
	def load_outline_renderer(self,s,e):

		#triangles, all_verts,  tri_count, vert_count =PolyGen.tristripToKDict(e["polyviewtristrip"], self.loadColors(e['color'], None))

		render_system = self.gameref.gameworld.systems['outline_renderer']
		attrib_num = render_system.attribute_count
		raw_verts = s['verts']
		triangles = s['indices']
		#all_verts = []
		#print 'raw_verts'
		#print raw_verts
		vnum = len(raw_verts)
		vnum = vnum/attrib_num
		'''for v in range(vnum):
			vi = []
			for a in range(attrib_num):
				vi.append(raw_verts[v*attrib_num+a])
			all_verts.append(vi)'''
		vert_count = vnum

		index_count = len(triangles)
		vert_mesh =  VertMesh(attrib_num,
			vert_count, index_count)

		vert_mesh.indices = triangles
		#for i in range(vert_count):
		#	vert_mesh[i] = all_verts[i]
		vert_mesh.data = raw_verts

		texture = str(s['texture'])
		if texture.endswith('.png'):
			texture=texture.split('/')[-1][:-4]
		rdict = {'texture': texture,
			'vert_mesh': vert_mesh,
			'render': True}
		return rdict
	def loadEntFromDict(self, e, idConvDict=None):
		sysfuncs={
		'color':self.loadColors,
		'position':self.loadPosition,
		'rotate':self.loadRotate,
		'physics':self.loadPhysics,
		'renderer':self.loadPhysics_renderer,
		'physics_renderer':self.loadPhysics_renderer,
		'outline_renderer':self.load_outline_renderer,
		'poly_renderer':self.loadPoly_renderer,
		}
		load_order = []#str(li) for li in e['load_order']]
		poly=False
		rname = 'renderer'
		for li in e['load_order']:
			if li=='physics_renderer':
				rname = str(li)
				li='renderer'
			if li=='poly_renderer':
				rname = str(li)
				li='renderer'
				poly=True
			load_order.append(str(li))

		create_dict = {}
		for system in load_order:
			ns = system
			if system=='renderer' and rname!= 'renderer':ns=rname
			if system in sysfuncs:
				#print sysfuncs[ns]
				#print e[ns]
				create_dict[str(system)]=sysfuncs[ns](e[ns],e)
			else:
				print "unknown system:", system, e[system]
				create_dict[str(system)]=e[system]
		if 'scale' not in create_dict:
			create_dict['scale']=1.
			load_order.append('scale')
		entID =  self.gameref.create_ent_from_dict(create_dict, load_order, selectNow=False)
		if entID != None:
			if idConvDict!=None: idConvDict[e['orig_id']] = entID
			#print 'loaded ent', idConvDict
			newent = self.gameref.getEntFromID(entID)
			if 'datadict' in e:
				newent.datadict = e['datadict']
			#if hasattr(newent, 'poly_renderer'):
			if 'polyviewbinary' in e:
				pg = base64.decodestring(e['polyviewbinary'])
				pg = pio.decodeBinary(pg)
				pg = PolyGen.PolyGen(pg)
				newent.polyshape = pg
				if 'outlineinfo' in e:
					ooi = e['outlineinfo']
					pg.outlineup = ooi['up']
					pg.outlinedown = ooi['down']
			if 'splineshape' in e:
				#print "LOADING SPLINE"
				ss = e['splineshape']
				points = ss['ControlPoints']
				newspline = Spline.Spline(stepsize=e['splineshape']['stepsize'])
				newspline.ControlPoints = points
				newspline.DrawCurve()
				newent.splineshape = newspline
		else:
			print 'failed to load ent'
		return entID
	def loadFromDict(self, data):
		print "LOADING"
		space = self.space
		if "collision_typeslist" in data and "collision_typesdict" in data:
			self.loadCollisionTypesFromDict(data["collision_typeslist"],data["collision_typesdict"])
		ents = data['ents']
		idConvDict = {}
		for e in ents:
			#print 'attempting to load', e
			self.loadEntFromDict(e, idConvDict=idConvDict)
		#print idConvDict
		selfgameworldentities = self.gameworld.entities
		if "jointslist" in data:
			jointslist = data['jointslist']
			for j in jointslist:
				if j['a'] in idConvDict:
					b1id = idConvDict[j['a']]
					#print j['a'], b1id
					b1 = selfgameworldentities[b1id].physics.body
				else:
					b1 = cy.Body()
				if j['b'] in idConvDict:
					b2id = idConvDict[j['b']]
					#print j['b'], b2id
					b2 = selfgameworldentities[b2id].physics.body
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
			if "background" in settings:
				bg = settings['background']
				self.gameref.bgrect.source = "backgrounds/"+bg+".png"
				self.gameref.bgrect.texture.wrap = 'repeat'
			if "startID" in settings:
				sid = settings['startID']
				if sid != -1:
					self.gameref.startID = idConvDict[sid]
			if "finishID" in settings:
				fid = settings['finishID']
				if fid != -1 and fid in idConvDict:
					self.gameref.finishID = idConvDict[fid]
			if "killMomem" in settings:
				km = settings['killMomem']
				if not self.gameref.mainTools.killMomem and km:
					self.gameref.mainTools.momemPressed()
			if "paused" in settings:
				pm = settings['paused']
				if not self.gameref.mainTools.paused and pm:
					self.gameref.mainTools.playPressed()
					#self.gameref.mainTools.paused = pm
			if "camera" in settings:
				cm = settings['camera']
				viewport = self.gameref.gameworld.systems['gameview']
				viewport.camera_pos[0]=cm['x']
				viewport.camera_pos[1]=cm['y']
				viewport.camera_scale=cm['scale']
		return [selfgameworldentities[v] for v in idConvDict.itervalues()]