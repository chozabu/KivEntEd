__author__ = 'chozabu'
import cymunk as cy
#from math import *

def collision_func(space, arbiter):
	first_body = arbiter.shapes[0].body
	second_body = arbiter.shapes[1].body
	first_pos = first_body.position
	second_pos = second_body.position
	diff = cy.Vec2d(first_pos.x-second_pos.x,first_pos.y-second_pos.y)
	#diff.x*=10
	#diff.y*=10
	second_body.apply_impulse(diff)
	#print diff
	return False