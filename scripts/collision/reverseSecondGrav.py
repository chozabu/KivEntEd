__author__ = 'chozabu'
import cymunk as cy


def collision_func(space, arbiter):
	second_body = arbiter.shapes[1].body
	diff = cy.Vec2d(space.gravity.x*-0.25,space.gravity.y*-0.25)
	second_body.apply_impulse(diff)
	return False