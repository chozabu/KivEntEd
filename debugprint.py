__author__ = 'chozabu'

#based on http://stackoverflow.com/a/1620686/445831
import sys
import traceback

class TracePrints(object):
	def __init__(self):
		self.stdout = sys.stdout
	def write(self, s):
		#self.stdout.write(s+"\n")
		strs = str(s)+"\n"
		self.stdout.write(strs)
		stack = traceback.extract_stack()
		stackout = stack[-2]#[0:10]
		self.stdout.write('File "'+stackout[0]+'", line '+str(stackout[1])+', in '+stackout[2]+'\n')
		#self.stdout.write(str(stack))

sys.stdout =TracePrints()