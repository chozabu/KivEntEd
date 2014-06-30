__author__ = 'chozabu'


#import Polygon
#Polygon.
from Polygon import *
from Polygon.Shapes import Star, Circle, Rectangle, SierpinskiCarpet

from Polygon.IO import *
from numpy import array

import triangle

class PolyGen():
	def __init__(self, octaves=3, persistance=.5, scale=.005, size='150'):
		self.octaves = octaves
		self.persistance = persistance
		self.scale = scale
		self.size = size
		self.poly = None

	def draw_circle_polygon(self, pos, sides=12, radius=30):
		p1 = Circle(radius, pos, sides)# - Circle(0.5)
		if self.poly == None:
			self.poly = p1
			return
		check = self.poly+p1
		if len(check)<2:self.poly = check
		print self.poly
		print len(self.poly)
		print len(self.poly[0])
		#p2 = Circle(radius/2, pos, sides)
		#p2.shift(-radius*2,-radius)
		#p=p1 + p2
		#return self.draw_from_Polygon(p)

	def draw_from_Polygon(self):
		#print p1
		octaves, persistance, scale, size = self.octaves, self.persistance, self.scale, self.size
		pts = self.poly[0]
		segments = []
		for i in range(len(pts)-1):
			segments.append([int(i),int(i+1)])
		segments.append([int(i+1),int(0)])
		print "made segments"
		A = {'vertices':array(pts), 'segments':array(segments)}#,
			 #'segment_markers':array(segmark), 'vertex_markers':array(vertmark)}
		writeSVG('Operations.svg', [self.poly], width=800)
		ts = self.poly.triStrip()
		print "\n\n"
		print "ts=",ts
		print len(ts)
		command = 'qpa' + size + 'YY'
		B = triangle.triangulate(A, command)
		print "triangulated"
		#print B
		tri_indices = B['triangles']
		new_triangles = []
		new_vertices = []
		tri_verts = B['vertices']
		nv_ap = new_vertices.append
		new_ap = new_triangles.append
		tri_count = 0
		for tri in tri_indices:
			new_ap((tri[0], tri[1], tri[2]))
			tri_count += 1
		vert_count = 0
		for tvert in tri_verts:
			nv_ap([tvert[0], tvert[1], octaves, persistance, scale])
			vert_count += 1
		return {'triangles': new_triangles, 'vertices': new_vertices,
			'vert_count': vert_count, 'tri_count': tri_count,
			'vert_data_count': 5}

	def initentity(self):
		#create_dict = self.draw_rect_polygon(
		#	20, 100, (150, 150), 3, .5, .005, '150')
		create_dict = self.draw_from_Polygon()
		#create_dict['do_texture'] = True
		#create_dict['texture'] = 'assets/planetgradient2.png'
		a = self.gameworld.init_entity({'noise_renderer2': create_dict},
			['noise_renderer2'])