__author__ = 'chozabu'


import xml.etree.ElementTree as ET
from math import cos, sin
import math

xmTexDict = {
	"Grass1":"default",
	"Dirt":"Dirt",
	"snow":"snow",
	"wood":"wood",
	"windows1":"windows1",
	"Wood3":"Wood3",

	"face_ball":"default",
    "firefox": "default",
    "cliffs2": "DarkDirt",
    "square": "default",
    "grassyrock": "DarkDirt",
    "sheep": "ball",
    "ice": "ice2",
    "start": "default",
    "emptybox": "default",
    "checksphere": "default",
    "circle": "default",
    "wrecker": "default",
    "awheel": "default",
    "orb": "default",
    "plank": "Wood2",
    "dirtclod": "default",
    "concreteplates": "Asphalt1",
    "arrow": "default",
    "magicball": "default"

}


class Serials():
	def __init__(self, gameref):
		self.gameref = gameref
		self.dataDir = gameref.dataDir
		self.gameworld = gameref.gameworld
		self.space = gameref.space
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


	def entToXML(self, e, root, xmScale):
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

		if (not hasattr(e, "physics") or not hasattr(e, "physics_renderer")) and not hasattr(e, 'polyshape'):
			print "not doing shape"
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
		shape_type = 'poly'

		#<position y="31.9388731278" x="8.00786973338" background="true"/>
		#<usetexture id="Dirt"/>
		pd = ET.SubElement(ed,'position')
		pd.set("x", str(e.position.x*xmScale))
		pd.set("y", str(e.position.y*xmScale))
		#pd.set("background", "false")

		if hasattr(e, "physics"):
			pd.set("background", "false")
			phd = ET.SubElement(ed,'physics')
			phd.set("grip", str(e.physics.shapes[0].friction*20.0))
			phd.set("friction", str(e.physics.shapes[0].friction))
			b = e.physics.body
			shape_type = e.physics.shape_type
			if not e.physics.body.is_static:
				pd.set("physics", "true")
				phd.set("mass", str(e.physics.body.mass))
				#<physics mass="1.0"/>
			else:
				self.laststatic = e.entity_id
		else:
			pd.set("background", "true")
		pr = None
		texname = None
		if hasattr(e, 'physics_renderer'):
			pr = e.physics_renderer
			texname = pr.texture
		if hasattr(e, 'poly_renderer'):
			pr = e.poly_renderer
			texname = pr.texture.split('/')[-1][:-4]
		if texname:
			td = ET.SubElement(ed,'usetexture')
			texname = xmTexDict.get(texname,texname)
			td.set("id", texname)
		verts = []
		if shape_type == "box":
			verts = self.getboxverts(b.angle, e.physics_renderer.width, e.physics_renderer.height)
		elif shape_type == "circle":
			verts = self.getcircleverts(e.physics_renderer.width/2.0)
		elif shape_type == "poly":
			verts = e.polyshape.poly[0]
		for v in verts:
			vd = ET.SubElement(ed,'vertex')
			vd.set("x", str(v[0]*xmScale))
			vd.set("y", str(v[1]*xmScale))

		#e.physics_renderer.texture

	def exportEntsToXML(self, root, xmScale):
		entsdict = []
		for eid in self.gameref.entIDs:
			e = self.gameworld.entities[eid]
			self.entToXML(e, root, xmScale)

	'''
	<entity id="rect14476jl_joint1" typeid="Joint">
		<size r="0.5"/>
		<position y="9.691309" x="-69.88762075"/>
		<joint connection-end="rect14476jl_block1" type="pivot" connection-start="rect14476jl_block0"/>
	</entity>'''
	def exportJointsToXML(self, root, xmScale):
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

	def exportXML(self, fileName="defaultlevel.lvl", xmScale = 0.05):
		root = ET.Element('level')
		info = ET.SubElement(root,'info')
		info.set('id','levelid')
		name = ET.SubElement(info,'name')
		name.text="LevelName"
		sky = ET.SubElement(info,'sky')
		sky.text="sky1"

		limits = ET.SubElement(root,'info')
		limits.set('id','levelid')
		self.exportEntsToXML(root, xmScale)
		self.exportJointsToXML(root, xmScale)

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