__author__ = 'chozabu'
import cymunk as cy

from kivy.core.audio import SoundLoader, Sound

sound = SoundLoader.load('sounds/bing.wav')

#Sound().status()
def collision_func(space, arbiter):
	if arbiter.is_first_contact == 1:
		second_body = arbiter.shapes[1].body
		bv= second_body.velocity
		s2 = (bv.x*bv.x+bv.y*bv.y)
		#print s2
		if s2>1000:
			if sound.status == 'play': sound.stop()
			sound.play()
	return True