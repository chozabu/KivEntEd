__author__ = 'chozabu'
import cymunk as cy
from math import *

#this is a refrence to kiventeds scripting system
scripty = None


defaults  = {
	"forcemul": 1
}

def collision_func(space, arbiter):
	firstshape = arbiter.shapes[0]
	if firstshape.__class__.__name__ != "Circle": return True
	first_body = firstshape.body
	second_body = arbiter.shapes[1].body
	first_pos = first_body.position
	second_pos = second_body.position
	diff = cy.Vec2d(first_pos.x-second_pos.x,first_pos.y-second_pos.y)
	dist = sqrt(diff.x**2+diff.y**2)
	uv = cy.Vec2d(diff.x/dist, diff.y/dist)
	invrad = firstshape.radius-dist
	if invrad <=0001: invrad = 0001
	invrad = sqrt(invrad)*second_body.mass

	e1 = scripty.gameref.getEntFromID(first_body.data)
	if hasattr(e1, 'datadict'):
		if 'forcemul' in e1.datadict:
			invrad*=float(e1.datadict['forcemul'])
	force = cy.Vec2d(uv.x*invrad, uv.y*invrad)
	second_body.apply_impulse(force)
	return False