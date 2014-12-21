__author__ = 'chozabu'
import cymunk as cy
from math import *

#this is a refrence to kiventeds scripting system
scripty = None

defaults  = {
	"xforce": 0,
	"yforce": 0,
}

def collision_func(space, arbiter):
	first_body = arbiter.shapes[0].body
	second_body = arbiter.shapes[1].body


	e1 = scripty.gameref.getEntFromID(first_body.data)
	if hasattr(e1, 'datadict'):
		dd = e1.datadict
		impulse = cy.Vec2d(float(dd.get('xforce',0)),float(dd.get('yforce',0)))
		second_body.apply_impulse(impulse)
	return False