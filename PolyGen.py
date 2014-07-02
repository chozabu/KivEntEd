__author__ = 'chozabu'


import Polygon
#Polygon.
from Polygon import *
from Polygon.Shapes import Star, Circle, Rectangle, SierpinskiCarpet
from random import random
from Polygon.IO import *
import Polygon.IO as pio
from Polygon.Utils import tileEqual, tileBSP, convexHull
from numpy import array
import cymunk

#import triangle

class PolyGen():
	def __init__(self, poly=None, octaves=3, persistance=.5, scale=.005, size='150'):
		self.octaves = octaves
		self.persistance = persistance
		self.scale = scale
		self.size = size
		self.poly = poly

	def gettiled(self):
		tiles = tileEqual(self.poly,10,10)
		#tiles = tileBSP(self.poly)
		tc = 0
		hulls = []
		ha = hulls.append
		for t in tiles:
			tc+=1
			ha(convexHull(t)[0])
			#print t

		return hulls

	def draw_circle_polygon(self, pos, sides=12, radius=30):
		p1 = Circle(radius, pos, sides)# - Circle(0.5)
		#pstr = pio.encodeBinary(p1)
		#print pstr
		#p1 = pio.decodeBinary(pstr)
		if self.poly == None:
			self.poly = p1
			return
		check = self.poly+p1
		#if len(check)<2:
		self.poly = check
		#print self.poly
		#print len(self.poly)
		#print len(self.poly[0])
		#p2 = Circle(radius/2, pos, sides)
		#p2.shift(-radius*2,-radius)
		#p=p1 + p2
		#return self.draw_from_Polygon(p)

	def draw_from_Polygon(self):
		#print p1
		pts = self.poly[0]
		#writeSVG('Operations.svg', [self.poly], width=800)
		new_triangles, new_vertices,  tri_count, vert_count =self.pts_to_tristrip(pts)
		#print "vertices=", new_vertices
		#print "triangles=", new_triangles

		#new_triangles, new_vertices,  tri_count, vert_count = self.pts_to_triangle(pts)
		#print "new_vertices=", new_vertices
		#print "new_triangles=", new_triangles
		return {'triangles': new_triangles, 'vertices': new_vertices,
			'vert_count': vert_count, 'tri_count': tri_count,
			'vert_data_count': 5}
	def pts_to_tristrip(self, pts):
		octaves, persistance, scale, size = self.octaves, self.persistance, self.scale, self.size
		ts = self.poly.triStrip()
		#print "\n\n"
		#print "ts=",ts
		#print len(ts)
		tri_verts = []
		tri_indices = []
		lasti = None
		llasti = None
		vindex = 0
		for strip in ts:
			sindex = 0
			striplen = len(strip)-2
			for vert in strip:
				#print sindex, striplen
				if sindex < striplen:
					tri_indices.append((vindex,vindex+1,vindex+2))
				tri_verts.append(vert)
				llasti = lasti
				lasti = vert
				vindex+=1
				sindex+=1
			#break #uncomment to see only 1 tristrip

		new_triangles = []
		new_vertices = []
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
		return new_triangles, new_vertices,  tri_count, vert_count
	'''def pts_to_triangle(self, pts):
		octaves, persistance, scale, size = self.octaves, self.persistance, self.scale, self.size
		segments = []
		for i in range(len(pts)-1):
			segments.append([int(i),int(i+1)])
		segments.append([int(i+1),int(0)])
		print "made segments"
		A = {'vertices':array(pts), 'segments':array(segments)}#,
			#'segment_markers':array(segmark), 'vertex_markers':array(vertmark)}
		command = 'p'#a' + size + 'YY'
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
		return new_triangles, new_vertices,  tri_count, vert_count'''

	'''def initentity(self):
		#create_dict = self.draw_rect_polygon(
		#	20, 100, (150, 150), 3, .5, .005, '150')
		create_dict = self.draw_from_Polygon()
		#create_dict['do_texture'] = True
		#create_dict['texture'] = 'assets/planetgradient2.png'
		a = self.gameworld.init_entity({'noise_renderer2': create_dict},
			['noise_renderer2'])'''