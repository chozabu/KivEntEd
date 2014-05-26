__author__ = 'chozabu'


def collision_func(space, arbiter):
	second_body = arbiter.shapes[1].body
	diff =second_body.velocity
	diff.x*=-0.97
	diff.y*=-0.97
	second_body.apply_impulse(diff)
	return False