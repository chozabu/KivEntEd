__author__ = 'chozabu'

import cymunk as cy
from math import *

#this is a refrence to kiventeds scripting system
scripty = None

#defaults  = {
#	"pushforce": 30,
#}

def collision_func(space, arbiter):
	first_body = arbiter.shapes[0].body
	second_body = arbiter.shapes[1].body


	e1 = scripty.gameref.getEntFromID(first_body.data)
	dd = e1.datadict
	impulse = cy.Vec2d(cos(first_body.angle),sin(first_body.angle))
	#forcemul = 0
	#if 'pushforce' in dd:
	#	forcemul=float(dd['pushforce'])
	#else:
	#	forcemul=float(defaults['pushforce'])
	g = scripty.gameref.space.gravity
	gpower = sqrt(g.x**2 + g.y**2)
	impulse.x*=gpower
	impulse.y*=gpower
	scripty.gameref.space.gravity = impulse
	#print impulse
	#second_body.apply_impulse(impulse)
	return False