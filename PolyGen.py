__author__ = 'chozabu'


import Polygon as po
#Polygon.
from Polygon import *
from Polygon.Shapes import Star, Circle, Rectangle, SierpinskiCarpet
from random import random
from Polygon.IO import *
import Polygon.IO as pio
from Polygon.Utils import tileEqual, tileBSP, convexHull, reducePoints
from numpy import array
import cymunk as cy
import math

#import triangle



def poly_area(verts):#Tartley - Jonathan Hartley, http://tartley.com
	"""
	Return area of a simple (ie. non-self-intersecting) polygon.
	Will be negative for counterclockwise winding.
	"""
	accum = 0.0
	for i in range(len(verts)):
		j = (i + 1) % len(verts)
		accum += verts[j][0] * verts[i][1] - verts[i][0] * verts[j][1]
	return accum / 2

def col_shapes_from_tris(triangles, verts,submass,elasticity,collision_type,friction):
		col_shapes = []
		tindex = -1
		remlist = []
		for t in triangles:
			tindex +=1
			pts = []
			for i in t:
				v = verts[i]
				pts.append((v[0],v[1]))
			iscw2 = poly_area(pts)
			iscw= cy.is_clockwise(pts)
			if not iscw:
				pts = [pts[0],pts[2],pts[1]]
			if (iscw2 > 2 or iscw2 < -2):
				poly_dict = {
					'vertices':pts, 'offset': (0, 0), 'mass':submass}
				col_shape = {'shape_type': 'poly', 'elasticity': elasticity,
					 'collision_type': collision_type, 'shape_info': poly_dict, 'friction': friction}
				col_shapes.append(col_shape)
			else:
				remlist.append(tindex)
		return col_shapes, remlist

def tristripToKDict(ts, color, texscale=.01):
	tri_verts = []
	new_triangles = []
	vert_ap = tri_verts.append
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
			vert_ap(vert)
			vindex+=1
			sindex+=1

	new_vertices = []
	nv_ap = new_vertices.append
	vert_count = 0
	for tvert in tri_verts:
		x=tvert[0]
		y=tvert[1]
		nv_ap([x, y, x*texscale, y*texscale, color[0], color[1], color[2], color[3]])
		vert_count += 1
	return new_triangles, new_vertices,  tri_count, vert_count

class PolyGen():
	def __init__(self, poly=None, color=(1,1,1,0.9), keepsimple = False, minlinelen=2):
		self.color = color
		self.poly = poly
		self.keepsimple = keepsimple
		po.setTolerance(0.1)
		self.minlinelen = minlinelen

	def from_spline(self, points):
		newp = Polygon()
		#print points
		newp.addContour(points)
		self.poly = newp

	def sub_circle_polygon(self, pos, sides=None, radius=30):
		if sides is None:sides = int(8+math.sqrt(radius))
		p1 = Circle(radius, pos, sides)# - Circle(0.5)
		if self.poly == None:
			print "poly never created!"
			return
		check = self.poly-p1
		if (self.keepsimple and len(check)<2) or not self.keepsimple:
			self.poly = check
	def draw_circle_polygon(self, pos, sides=None, radius=30):
		if sides is None:sides = int(8+math.sqrt(radius))
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
		self.remove_short_lines(self.minlinelen)
		pts = self.poly[0]
		#writeSVG('Operations.svg', [self.poly], width=800)
		new_triangles, new_vertices,  tri_count, vert_count =self.pts_to_tristrip(pts)

		left=99999
		right=-99999
		top=-99999
		bottom=99999

		for tvert in new_vertices:
			x=tvert[0]
			y=tvert[1]
			bottom=min(y,bottom)
			top=max(y,bottom)
			left=min(x,left)
			right=max(x,right)
		self.bbox = (left,right,top,bottom)
		return {'triangles': new_triangles, 'vertices': new_vertices,
			'vert_count': vert_count, 'tri_count': tri_count,
			'vert_data_count': 5}
	def get_bbox(self):
		if not hasattr(self, 'bbox'):
			self.draw_from_Polygon()
		return self.bbox
	def remove_short_lines(self, minlen = 1):
		minlen*=minlen
		newp = Polygon()
		c=-1
		for cont in self.poly:
			if len(cont)<10:return
			c+=1
			#cont=self.poly[0]
			keeplist = []
			lastp = None
			pindex = -1
			for p in cont:
				pindex+=1
				if lastp:
					#check here
					xd = p[0]-lastp[0]
					yd = p[0]-lastp[0]
					td = xd*xd+yd*yd
					if td < minlen:
						pass
						#lastp = None
					else:
						keeplist.append(p)
						lastp = p
				else:
					keeplist.append(p)
					lastp = p
			ishole = self.poly.isHole(c)
			newp.addContour(keeplist,ishole)
		self.poly = newp
	def remove_some_pts(self, prop=.9):
		newp = Polygon()
		c=-1
		for cont in self.poly:
			c+=1
			cr = reducePoints(cont,int(len(cont)*prop))
			ishole = self.poly.isHole(c)
			if len(cr)>2:
				newp.addContour(cr, ishole)
		parea = self.poly.area()
		nparea = newp.area()
		#areadiff = math.fabs(nparea-parea)
		arearatio = parea/nparea
		arearatio = math.fabs(arearatio-1)
		#print areadiff, arearatio
		if arearatio < 0.1:
			self.poly = newp
	def pts_to_tristrip(self, pts):
		ts = self.poly.triStrip()
		color = self.color
		return tristripToKDict(ts,color)

	'''def initentity(self):
		#create_dict = self.draw_rect_polygon(
		#	20, 100, (150, 150), 3, .5, .005, '150')
		create_dict = self.draw_from_Polygon()
		#create_dict['do_texture'] = True
		#create_dict['texture'] = 'assets/planetgradient2.png'
		a = self.gameworld.init_entity({'noise_renderer2': create_dict},
			['noise_renderer2'])'''