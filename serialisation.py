__author__ = 'chozabu'

'''This class loads save/load import/export plugins until they are loaded properly as plugins'''

import scripts.serials.KEE as jsonserials
import scripts.serials.wheelz as wheelzserials



class Serials():
	def __init__(self, gameref):
		self.gameref = gameref

		#create import/exporters #TODO load dynamically
		self.jsonserials = jsonserials.Serials(gameref)
		self.wheelzserials = wheelzserials.Serials(gameref)

		#wrap methods from seperated classes for now
		self.loadJSON = self.jsonserials.loadJSON
		self.loadExtJSON = self.jsonserials.loadExtJSON
		self.exportJSON = self.jsonserials.exportJSON
		self.entToDict = self.jsonserials.entToDict
		self.loadEntFromDict = self.jsonserials.loadEntFromDict
		self.exportXML = self.wheelzserials.exportXML
