__author__ = 'chozabu'
import cymunk as cy
from math import *

#this is a refrence to kiventeds scripting system
scripty = None

defaults  = {
	"xvelmul": 1,
	"yvelmul": 1,
	"xforce": 0,
	"yforce": 0,
}

def collision_func(space, arbiter):
	first_body = arbiter.shapes[0].body
	second_body = arbiter.shapes[1].body


	e1 = scripty.gameref.getEntFromID(first_body.data)
	if hasattr(e1, 'datadict'):
		dd = e1.datadict
		vel = second_body.velocity
		if 'xvelmul' in dd:
			vel.x*=float(dd['xvelmul'])
		if 'yvelmul' in dd:
			vel.y*=float(dd['yvelmul'])
		second_body.velocity = vel
		impulse = cy.Vec2d(0,0)
		if 'xforce' in dd:
			impulse.x=float(dd['xforce'])
		if 'yforce' in dd:
			impulse.y=float(dd['yforce'])
		second_body.apply_impulse(impulse)
	return False