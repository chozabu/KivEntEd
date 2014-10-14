__author__ = 'chozabu'

#this is a refrence to kiventeds scripting system
scripty = None

defaults  = {
	"type": 'jetpack',#boardboost
	"duration": '1.',
}

def collision_func(space, arbiter):
	#implemented in gameonly
	return False