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
	def __init__(self, poly=None, color=(1,1,1,0.9), keepsimple = False):
		self.color = color
		self.poly = poly
		self.keepsimple = keepsimple

	def sub_circle_polygon(self, pos, sides=12, radius=30):
		p1 = Circle(radius, pos, sides)# - Circle(0.5)
		if self.poly == None:
			print "poly never created!"
			return
		check = self.poly-p1
		if (self.keepsimple and len(check)<2) or not self.keepsimple:
			self.poly = check
	def draw_circle_polygon(self, pos, sides=12, radius=30):
		p1 = Circle(radius, pos, sides)
		if self.poly == None:
			self.poly = p1
			return
		check = self.poly+p1
		if (self.keepsimple and len(check)<2) or not self.keepsimple:
			self.poly = check
	def draw_square_polygon(self, pos, width,height, angle=0):
		p1 = Rectangle(width,height)
		p1.shift(-width/2,-height/2)
		p1.rotate(angle)
		p1.shift(pos[0],pos[1])
		if self.poly == None:
			self.poly = p1
			return
		check = self.poly+p1
		if (self.keepsimple and len(check)<2) or not self.keepsimple:
			self.poly = check
	def sub_square_polygon(self, pos, width,height, angle=0):
		p1 = Rectangle(width,height)
		p1.shift(-width/2,-height/2)
		p1.rotate(angle)
		p1.shift(pos[0],pos[1])
		if self.poly == None:
			self.poly = p1
			return
		check = self.poly-p1
		if (self.keepsimple and len(check)<2) or not self.keepsimple:
			self.poly = check

	def draw_from_Polygon(self):
		if len(self.poly) == 0: return False
		pts = self.poly[0]
		#writeSVG('Operations.svg', [self.poly], width=800)
		new_triangles, new_vertices,  tri_count, vert_count =self.pts_to_tristrip(pts)
		return {'triangles': new_triangles, 'vertices': new_vertices,
			'vert_count': vert_count, 'tri_count': tri_count,
			'vert_data_count': 5}
	def pts_to_tristrip(self, pts):
		ts = self.poly.triStrip()
		color = self.color
		tri_verts = []
		new_triangles = []
		tri_ap = new_triangles.append
		vindex = 0
		tri_count = 0
		for strip in ts:
			sindex = 0
			striplen = len(strip)-2
			for vert in strip:
				#print sindex, striplen
				if sindex < striplen:
					tri_ap((vindex,vindex+1,vindex+2))
					tri_count += 1
				tri_verts.append(vert)
				vindex+=1
				sindex+=1

		new_vertices = []
		nv_ap = new_vertices.append
		vert_count = 0
		for tvert in tri_verts:
			nv_ap([tvert[0], tvert[1], color[0], color[1], color[2], color[3], tvert[0]*0.01, tvert[1]*0.01])
			vert_count += 1
		return new_triangles, new_vertices,  tri_count, vert_count

	'''def initentity(self):
		#create_dict = self.draw_rect_polygon(
		#	20, 100, (150, 150), 3, .5, .005, '150')
		create_dict = self.draw_from_Polygon()
		#create_dict['do_texture'] = True
		#create_dict['texture'] = 'assets/planetgradient2.png'
		a = self.gameworld.init_entity({'noise_renderer2': create_dict},
			['noise_renderer2'])'''