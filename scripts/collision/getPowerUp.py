__author__ = 'chozabu'

import cymunk as cy
from math import *

#this is a refrence to kiventeds scripting system
scripty = None

defaults  = {
	"type": 'jetpack',
	"duration": '1.',
}

def collision_func(space, arbiter):
	#implemented in gameonly
	return False