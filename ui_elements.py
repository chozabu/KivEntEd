import cymunk as cy

import os
import glob

import json

from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.properties import ListProperty

serverURL = 'http://www.kiventedserve.chozabu.net'
#serverURL = 'http://0.0.0.0:8080'


class PlainButton(Button):
	def on_touch_down(self, touch):
		sres = super(PlainButton, self).on_touch_down(touch)
		print "pb=", sres
		return sres

class entDataItem(BoxLayout):
	def __init__(self,iname,prnt):
		super(entDataItem, self).__init__()
		self.ddict = prnt.ddict
		self.iname = iname
		self.keyLabel.text = iname
		if iname in self.ddict: self.valueLabel.text = str(self.ddict[iname])


	def valueChanged(self, instance):
		self.ddict[self.iname] = instance.text
		#print self.ddict
	#def newType(self, btn):
	#	Popup(title="Create New Collision Type",
	#		  content=TextInput(focus=True,multiline = False),
	#		  size_hint=(0.6, None), height=100,
	#		  on_dismiss=self.setNewType).open()
	#
	#def setNewType(self, popup):
	#	pw = self.get_parent_window()
	#	print pw
	#	pw.children[-1].mainTools.data_key_types.append(popup.content.text)
	#	#self.button.text = popup.content.text
class entDataBox(BoxLayout):
	def __init__(self, ddict):
		super(entDataBox, self).__init__()
		print ddict
		self.ddict = ddict
		for key in ddict.keys():
			self.add_widget(entDataItem(iname=key, prnt=self))

	def newItem(self):
		Popup(title="Create New Variable",
			  content=TextInput(focus=True,multiline = False),
			  size_hint=(0.6, None), height=100,
			  on_dismiss=self.setNewVar).open()

	def setNewVar(self, popup):
		#pw = self.get_parent_window()
		#print pw
		#pw.children[-1].mainTools.data_key_types.append()
		#self.button.text = popup.content.text
		iname = popup.content.text
		print iname
		if iname in self.ddict:
			Popup(title="Create New Variable",
			  content=Label(text="variable already exists"),
			  size_hint=(0.6, None), height=100).open()
			return
		self.ddict[iname] = ""
		self.add_widget(entDataItem(iname=iname, prnt=self))
	#def __init__(self, mtref):
import urllib
from kivy.network.urlrequest import UrlRequest
class downloads(BoxLayout):
	def __init__(self, mtref):
		self.mtref = mtref
		super(downloads,self).__init__()
		self.cursor = 0

	def bug_posted(req, result):
	    print('Our bug is posted !')
	    print(result)

	#wget -qO- http://0.0.0.0:8080/listLevels
	def prevPage(self):
		self.cursor -=20
		if self.cursor<0:self.cursor = 0
		self.listLevels()
	def nextPage(self):
		self.cursor +=20
		self.listLevels()
	def goPressed(self, instance):
		print "go pressed"
		self.cursor = 0
		self.listLevels()
	def listLevels(self):
		print "requesting levels", serverURL+'/listLevels'
		headers = {'Content-type': 'application/x-www-form-urlencoded',
	          'Accept': 'text/plain'}

		params = {"cursor":self.cursor, "limit":20,"sortKey": self.sortSpinner.text}
		if self.reverseButton.state == 'down':params['reverse']=True
		params = urllib.urlencode(params)
		print self.reverseButton.state
		req = UrlRequest(serverURL+'/queryLevels', on_success=self.got_levels,
	        req_headers=headers
	        ,on_error=self.on_error,on_failure=self.on_failure, on_redirect=self.on_redirect,req_body=params)
		print "waiting"
		req.wait()
		print "waited"
	def on_error(self, info, result):
		print "on_error", info, result
	def on_redirect(self, info, result):
		print "on_redirect", info, result
	def on_failure(self, info, result):
		print "on_failure", info, result
	def got_levels(self, info, result):
		print "got levels:"
		print info
		print result
		data = json.loads(result)
		print data
		if data['result'] == "OK":
			print "OK"
			self.setChildren(data['data'])
	def setChildren(self, data):
		#data = json.loads(data)
		print data
		self.levelBox.clear_widgets()
		print len(data)
		for item in data:
			print item
			i=item#data[item]
			b = Button(text=i['name'], on_press=self.dllevel)
			b.info = i
			self.levelBox.add_widget(b)

	def dllevel(self,instance):
		print instance.info
		print "making request"
		params = urllib.urlencode({'fullname': instance.info['filename']})
		req = UrlRequest(serverURL+'/downloadLevel', on_success=self.got_level, timeout=1000, req_body=params
	        ,on_error=self.on_error,on_failure=self.on_failure, on_redirect=self.on_redirect)
		req.levelname = instance.info['name']
		print "made request"
		req.wait()
		print "wait over"
	def got_level(self, info, result):
		print "got level"
		print "info=",info
		print "result=",result
		rd = json.loads(result)
		dd = json.loads(rd['data'])
		print "--------------"
		print dd
		for i in dd:
			print i, dd[i]
		self.mtref.gameref.clearAll()
		self.mtref.gameref.serials.loadFromDict(dd)
		self.mtref.nameBox.text = info.levelname
		self.mtref.dlpopup.dismiss()



	#wget -qO- --post-data "author=alex&passHash=123&name=test2&levelData=asdagrdh" http://0.0.0.0:8080/uploadLevel
	def uploadLevel(self):
		print "uploading level"
		lname = self.mtref.nameBox.text
		updata = self.mtref.gameref.serials.exportDict()
		#req = UrlRequest('/listLevels', on_success=self.got_levels, timeout=1000)
		params = urllib.urlencode({
		'author':'alex', 'passHash': 123, 'name':lname,"levelData":json.dumps(updata)
		})
		headers = {'Content-type': 'application/x-www-form-urlencoded',
	          'Accept': 'text/plain'}
		req = UrlRequest(serverURL+'/uploadLevel', on_success=self.level_posted, req_body=params,
	        req_headers=headers)
		req.wait()
	def level_posted(self, info, result):
		print "sent level"
		print info
		print result

class callbacks(BoxLayout):
	def __init__(self, mtref):
		self.mtref = mtref
		#self.scripty = mtref.gameref.scripty
		super(callbacks,self).__init__()
		#self.typeChanged()
	def setTypeA(self,ta):
		self.colTypeASpinner.text = ta
		self.typeChanged()
	def typeChanged(self, instance=None):
		handlers = self.mtref.gameref.scripty.collision_handlers
		if self.colTypeASpinner.text not in handlers: handlers[self.colTypeASpinner.text] = {}
		tbd = handlers[self.colTypeASpinner.text]
		if self.colTypeBSpinner.text not in tbd: tbd[self.colTypeBSpinner.text] = {}
		methods = tbd[self.colTypeBSpinner.text]

		self.beginSpinner.text = methods["begin"] if "begin" in methods else "None"
		self.pre_solveSpinner.text = methods["pre_solve"] if "pre_solve" in methods else "None"
		self.post_solveSpinner.text = methods["post_solve"] if "post_solve" in methods else "None"
		self.separateSpinner.text = methods["separate"] if "separate" in methods else "None"

	def calleeChanged(self, instance, caller):
		self.mtref.gameref.scripty.add_col_handler(
			self.colTypeASpinner.text,
			self.colTypeBSpinner.text,
			caller,
			instance.text
		)
	def newType(self, btn):
		Popup(title="Create New Collision Type",
			  content=TextInput(focus=True,multiline = False),
			  size_hint=(0.6, None), height=100,
			  on_dismiss=self.setNewType).open()

	def setNewType(self, popup):
		self.mtref.gameref.scripty.add_col_type(popup.content.text)
		self.colTypeASpinner.text = popup.content.text
		#self.button.text = popup.content.text




class tbox(TextInput):
	def on_touch_down(self, touch):
		super(tbox, self).on_touch_down(touch)
		if self.collide_point(*touch.pos):
			#touch.grab( self )
			return True
		return False


class CircleSettings(BoxLayout):
	def on_touch_down(self, touch):
		super(CircleSettings, self).on_touch_down(touch)
		if self.collide_point(*touch.pos):
			#touch.grab( self )
			return True
		return False


class BoxSettings(BoxLayout):
	def on_touch_down(self, touch):
		super(BoxSettings, self).on_touch_down(touch)
		if self.collide_point(*touch.pos):
			#touch.grab( self )
			return True
		return False


class MainTools(FloatLayout):
	col_types = ListProperty()
	col_funcs = ListProperty()
	sprite_list = ListProperty()
	data_key_types = ListProperty()
	def __init__(self, **kwargs):
		super(MainTools, self).__init__(**kwargs)
		self.staticOn = False
		self.paused = False
		self.selectedItem = None
		self.selectedEntity = None
		self.toolSettings = {"circle": {"texture": "sheep"},
							 "square": {"texture": "Dirt"},
							 "box": {"texture": "face_box"},
							 "draw": {"texture": "Grass1"},
							 "plank": {"texture": "plank"},
		}
		self.callbacksBox = None
		self.currentTool = ""
		self.testsave = []
		self.gameref = None
		self.entcpy = None #item on the clipboard
		#self.exampleLevels
		#self.col_types.append("default")
		#self.col_types.append("vortex")
		Clock.schedule_once(self.init_tools)

	def loadExample(self, instance):
		filename = os.path.dirname(__file__)+"/examples/"+instance.text+".json"
		self.gameref.clearAll()
		self.gameref.serials.loadExtJSON(filename)
		self.nameBox.text = instance.text
	def loadCustom(self, instance):
		self.gameref.clearAll()
		self.gameref.serials.loadJSON(instance.text+".json")
		self.nameBox.text = instance.text
	def customlvlPressed(self):
		levels = [ os.path.basename(f)[:-5] for f in glob.glob(self.gameref.dataDir+"*.json")]
		self.levelsMenu.clear_widgets()
		for levelname in levels:
			newb = Button(text=levelname, font_size=14)
			newb.bind(on_press=self.loadCustom)
			self.levelsMenu.add_widget(newb)
		self.changel3menu(self.levelsMenu)


	def init_tools(self, dt):
		self.l2menus = [self.joinMenu, self.createMenu, self.entityMenu, self.fileMenu]
		self.l3menus = [self.examplesMenu,self.levelsMenu]
		#self.leftMenu.remove_widget(self.joinMenu)
		#self.spriteSpinner.text="square"
		self.rightMenu.remove_widget(self.selectedMenuView)
		self.clearl2()
		self.callbacksBox = callbacks(self)
		self.cbpopup = Popup(title="when",
				content=self.callbacksBox,#Label(text='Hello world'),
				size_hint=(0.8, 0.8), size=(400, 400))

		self.downloadsBox = downloads(self)
		self.dlpopup = Popup(title="Levels",
				content=self.downloadsBox,#Label(text='Hello world'),
				size_hint=(0.8, 0.8), size=(400, 400))

		exampleLevels = [ os.path.basename(f)[:-5] for f in glob.glob(os.path.dirname(__file__)+"/examples/*.json")]
		for levelname in exampleLevels:
			newb = Button(text=levelname, font_size=14)
			newb.bind(on_press=self.loadExample)
			self.examplesMenu.add_widget(newb)
		#self.spriteSpinner.values = os.listdir("./sprites")

	def update(self, dt):
		shape = self.selectedItem
		#self.selectedMenu.selectedLabel.text = str(shape)
		#self.selectedMenu.xposLabel.text = ""
		#self.selectedMenu.yposLabel.text = ""
		if shape:
			if not self.selectedMenu.xvelLabel.focus:
				self.selectedMenu.xvelLabel.text = "%0.2f" % shape.body.velocity.x
			if not self.selectedMenu.yvelLabel.focus:
				self.selectedMenu.yvelLabel.text = "%0.2f" % shape.body.velocity.y
			if not self.selectedMenu.xposLabel.focus:
				self.selectedMenu.xposLabel.text = "%0.2f" % shape.body.position.x
			if not self.selectedMenu.yposLabel.focus:
				ypostr = "%0.2f" % shape.body.position.y
				self.selectedMenu.yposLabel.text = ypostr
			if not self.selectedMenu.angleLabel.focus:
				tv = "%0.2f" % shape.body.angle
				self.selectedMenu.angleLabel.text = tv

	#def examplesPressed(self, instance):


	def loadPressed(self, instance):
		self.gameref.clearAll()
		self.gameref.serials.loadJSON(self.nameBox.text+".json")
		#self.gameref.loadFromDict(self.testsave)

	def savePressed(self, instance):
		self.testsave = self.gameref.serials.exportJSON(self.nameBox.text+".json")

	def wheelzPressed(self, instance):
		fileName = self.nameBox.text+".lvl"
		self.gameref.serials.exportXML(fileName)
		from kivy.utils import platform
		try:
			if platform != 'android':
				bashCommand = "adb push /home/chozabu/git/KivEntEd/" + fileName + " /sdcard/xlvls/"
				#bashCommand = "pwd"
				#os.system(bashCommand)
				import subprocess
				#print bashCommand
				#print bashCommand.split()
				process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
				output = process.communicate()[0]
				print output
				#fileName = '/sdcard/xlvls/'+fileName
		except:
			print "could not push wheelz level to phone"


	def clearPressed(self, instance):
		self.gameref.clearAll()

	def setTool(self, tool):
		if self.currentTool not in self.toolSettings:
			self.toolSettings[self.currentTool] = {}
		lts = self.toolSettings[self.currentTool]
		lts["texture"] = self.spriteSpinner.text
		lts["mass"] = self.massSlider.value
		self.currentTool = tool
		if tool in self.toolSettings:
			cts = self.toolSettings[tool]
			if "texture" in cts:
				self.spriteSpinner.text = cts["texture"]
			if "mass" in cts:
				self.massSlider.value = cts["mass"]
		print "Tool is now: %s" % tool

	def setRef(self, ref):
		self.gameref = ref


	def setygrav(self, value):
		space = self.gameref.space
		space.gravity = space.gravity.x, value
	def setxgrav(self, value):
		space = self.gameref.space
		space.gravity = value, space.gravity.y

	def xvelChanged(self, instance):
		try:
			fval = float(instance.text)
		except ValueError:
			return
		shape = self.selectedItem
		if shape:
			shape.body.velocity = (fval, shape.body.velocity.y)
	def yvelChanged(self, instance):
		try:
			fval = float(instance.text)
		except ValueError:
			return
		shape = self.selectedItem
		if shape:
			shape.body.velocity = (shape.body.velocity.x, fval)
	def xposChanged(self, instance):
		fval = float(instance.text)
		shape = self.selectedItem
		if shape:
			shape.body.position = (fval, shape.body.position.y)
			self.gameref.reindexEnt(self.selectedEntity)

	def yposChanged(self, instance):
		fval = float(instance.text)
		shape = self.selectedItem
		if shape:
			shape.body.position = (shape.body.position.x, fval)
			self.gameref.reindexEnt(self.selectedEntity)

	def angleChanged(self, instance):
		fval = float(instance.text)
		shape = self.selectedItem
		if shape:
			shape.body.angle = fval
			self.gameref.reindexEnt(self.selectedEntity)

	def textureChanged(self, instance):
		ent = self.selectedEntity
		ent.physics_renderer.texture = instance.text

	def redChanged(self, strval):
		fval = float(strval)
		ent = self.selectedEntity
		if ent:
			ent.color.r = fval
	def greenChanged(self, strval):
		fval = float(strval)
		ent = self.selectedEntity
		if ent:
			ent.color.g = fval
	def blueChanged(self, strval):
		fval = float(strval)
		ent = self.selectedEntity
		if ent:
			ent.color.b = fval
	def opacityChanged(self, strval):
		fval = float(strval)
		ent = self.selectedEntity
		if ent:
			ent.color.a = fval

	def frictionChanged(self, instance):
		fval = float(instance.text)
		shape = self.selectedItem
		if shape:
			shape.friction = fval
			self.gameref.reindexEnt(self.selectedEntity)

	def massChanged(self, instance):
		fval = float(instance.text)
		if fval <= 0:
			fval = 0.1
			instance.text = "%0.2f" % fval
		shape = self.selectedItem
		if shape:
			shape.body.mass = fval
			self.gameref.reindexEnt(self.selectedEntity)

			if shape.__class__.__name__ == "BoxShape":
				self.selectedItem.body.moment = cy.moment_for_box(self.selectedItem.body.mass, self.selectedItem.width, self.selectedItem.height)
			if shape.__class__.__name__ == "Circle":
				self.selectedItem.body.moment = cy.moment_for_circle(self.selectedItem.body.mass,
																 self.selectedItem.radius,0)  #seems ineffective?

	def elasChanged(self, instance):
		fval = float(instance.text)
		shape = self.selectedItem
		if shape:
			shape.elasticity = fval
			self.gameref.reindexEnt(self.selectedEntity)

	def on_rad_change(self, instance, value):
		newrad = float(value)
		print "rad change", newrad
		if self.selectedItem and self.selectedEntity:
			self.selectedItem.radius = newrad
			self.selectedItem.unsafe_set_radius(newrad)
			self.selectedEntity.physics_renderer.width = newrad * 2
			self.selectedEntity.physics_renderer.height = newrad * 2
			self.selectedItem.body.moment = cy.moment_for_circle(self.selectedItem.body.mass,
																 newrad,0)  #seems ineffective?

	def on_width_change(self, instance, value):
		space = self.gameref.space
		newrad = float(value)
		#if self.selectedItem and self.selectedEntity:
		#self.selectedItem.width = (newrad)
		#self.selectedEntity.physics_renderer.width = newrad
		#space.reindex_shape(self.selectedItem)
		#print dir(self.selectedEntity)
		#print dir(self.selectedEntity.physics)
		#print self.selectedItem.cache_bb()
		shape = self.selectedItem
		if shape and self.selectedEntity:
			newshape = cy.BoxShape(shape.body, newrad, shape.height)
			newshape.body.moment = cy.moment_for_box(newshape.body.mass, newrad, shape.height)
			newshape.collision_type = shape.collision_type
			newshape.elasticity = shape.elasticity
			newshape.friction = shape.friction
			space.add_shape(newshape)
			space.remove(shape)
			#print shape.body._shapes
			self.selectedEntity.physics.shapes = [newshape]
			self.selectedItem = newshape
			self.selectedEntity.physics_renderer.width = newrad

	def on_height_change(self, instance, value):
		space = self.gameref.space
		newrad = float(value)
		shape = self.selectedItem
		if shape and self.selectedEntity:
			newshape = cy.BoxShape(shape.body, shape.width, newrad)
			newshape.body.moment = cy.moment_for_box(newshape.body.mass, newrad, shape.height)
			newshape.collision_type = shape.collision_type
			newshape.elasticity = shape.elasticity
			newshape.friction = shape.friction
			space.add_shape(newshape)
			space.remove(self.selectedItem)
			self.selectedEntity.physics.shapes = [newshape]
			self.selectedItem = newshape
			self.selectedEntity.physics_renderer.height = newrad

	def setShape(self, shape):
		self.selectedItem = shape
		self.selectedMenu.selectedLabel.text = "None"
		self.selectedEntity = None
		ent=None
		if shape:
			self.selectedEntity = self.gameref.gameworld.entities[shape.body.data]
			ent = self.selectedEntity
			#print dir(ent.physics)
			self.selectedMenu.selectedLabel.text = ent.physics.shape_type+" "+str(shape.body.data)
			#tv = "x=%f\ny=%f" % (shape.body.position.x, shape.body.position.y)
			#self.selectedMenu.posLabel.text = tv
			self.selectedMenu.frictionLabel.text = "%0.2f" % shape.friction
			self.selectedMenu.massLabel.text = "%0.2f" % shape.body.mass
			self.selectedMenu.elasLabel.text = "%0.2f" % shape.elasticity
			print self.gameref.scripty.collision_types[shape.collision_type], shape.collision_type
			self.selectedMenu.colTypeSpinner.text = self.gameref.scripty.collision_types[shape.collision_type]
			self.selectedMenu.shapeInfo.clear_widgets()
			if shape.__class__.__name__ == "Circle":
				cs = CircleSettings()
				cs.radiusLabel.text = "%0.2f" % shape.radius
				cs.radiusLabel.bind(text=self.on_rad_change)
				self.selectedMenu.shapeInfo.add_widget(cs)
			if shape.__class__.__name__ == "BoxShape":
				bs = BoxSettings()
				bs.widthLabel.text = "%0.2f" % shape.width
				bs.heightLabel.text = "%0.2f" % shape.height
				bs.widthLabel.bind(text=self.on_width_change)
				bs.heightLabel.bind(text=self.on_height_change)
				self.selectedMenu.shapeInfo.add_widget(bs)

		if self.gameref.selectedShapeID != None:
			self.gameref.delObj(self.gameref.selectedShapeID)
			self.gameref.selectedShapeID = None
		if ent:
			if self.selectedMenuView not in self.rightMenu.children:
				self.rightMenu.add_widget(self.selectedMenuView)
			self.selectedMenu.texLabel.text = ent.physics_renderer.texture
			if hasattr(ent, 'color'):
				self.selectedMenu.redLabel.text = str(ent.color.r)
				self.selectedMenu.greenLabel.text = str(ent.color.g)
				self.selectedMenu.blueLabel.text = str(ent.color.b)
				self.selectedMenu.opacityLabel.text = str(ent.color.a)

			self.gameref.selectedShapeID = self.gameref.create_decoration(pos=(shape.body.position.x, shape.body.position.y),
			                                                 width=ent.physics_renderer.width*1.1+10, height=ent.physics_renderer.height*1.1+10,
															texture='emptybox')
		else:
			self.rightMenu.remove_widget(self.selectedMenuView)

	def delSelPressed(self, instance):
		if self.selectedItem and self.gameref:
			self.gameref.delObj(self.selectedItem.body.data)
			self.setShape(None)
	def sensorPressed(self, instance):
		if self.selectedItem and self.gameref:
			newval = not self.selectedItem.sensor
			self.selectedItem.sensor = newval
			instance.pressed = newval
	def scriptsPressed(self, instance):
		#if self.selectedItem and self.gameref:
		#
		#	newval = self.gameref.scripty.collision_types[self.selectedItem.collision_type]
		if self.selectedItem:
			self.callbacksBox.setTypeA(self.gameref.scripty.collision_types[self.selectedItem.collision_type])
		self.cbpopup.open()
	def downloadsPressed(self, instance):
		self.dlpopup.open()
		self.downloadsBox.listLevels()

	def varsPressed(self, btn):
		if self.selectedEntity:
			if not hasattr(self.selectedEntity, "datadict"):
				print "initing datadict"
				self.selectedEntity.datadict = {}
			scripty = self.gameref.scripty
			colfunc = scripty.getHandlersForType(self.selectedItem.collision_type)
			print scripty.defaults
			print colfunc
			if len(colfunc)>0 and colfunc[0] in scripty.defaults:
				defaultdict = scripty.defaults[colfunc[0]]
				print defaultdict
				for i in defaultdict.keys():
					if i not in self.selectedEntity.datadict:
						self.selectedEntity.datadict[i] = defaultdict[i]
			Popup(title="Entity Varables",
				  content=entDataBox(ddict = self.selectedEntity.datadict),
				  size_hint=(0.8, 0.8),
				  on_dismiss=None).open()
	def colTypeChanged(self, instance):
		if self.selectedItem and self.gameref:
			newval = self.gameref.scripty.collision_types[instance.text]
			print newval, instance.text
			self.selectedItem.collision_type = newval


	def clearl2(self):
		self.clearl3()
		for i in self.l2menus:
			if i in self.leftMenu.children:
				self.leftMenu.remove_widget(i)
	def clearl3(self):
		for i in self.l3menus:
			if i in self.leftMenu.children:
				self.leftMenu.remove_widget(i)

	def changel2menu(self, newMenu):
		if newMenu in self.leftMenu.children:
			self.clearl2()
			self.leftMenu.size_hint_x = .1
		else:
			self.clearl2()
			self.leftMenu.add_widget(newMenu)
			self.leftMenu.size_hint_x = .2

	def changel3menu(self, newMenu):
		if newMenu in self.leftMenu.children:
			self.clearl3()
			self.leftMenu.size_hint_x = .2
		else:
			self.clearl3()
			self.leftMenu.add_widget(newMenu)
			self.leftMenu.size_hint_x = .3


	def massPressed(self, instance):
		self.massSlider.value = 0 if self.massSlider.value > 0 else 10


	def playPressed(self, instance):
		self.paused = not self.paused
		self.ids['playButton'].text = "Pause/Play" if self.paused else "Play/Pause"