import cymunk as cy

import os
import glob
import re

import math

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
#if 'chozabu' in os.getcwd():serverURL = 'http://0.0.0.0:8080'

class FloatInput(TextInput):

    pat = re.compile('[^0-9]')
    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
        return super(FloatInput, self).insert_text(s, from_undo=from_undo)

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
class levelItem(BoxLayout):
	def __init__(self, info=None,callback=None):
		super(levelItem,self).__init__()
		self.info = info
		self.callback = callback
		Clock.schedule_once(self.initUI)
	def initUI(self, dt):
		if self.info == None:
			self.remove_widget(self.downloadButton)
			self.add_widget(Label(text="Downloads"))
			return
		self.nameLabel.text = self.info['name']
		self.authorLabel.text = self.info['author']
		self.createdLabel.text = str(self.info['dateAdded'])[:10]
		self.modifiedLabel.text = str(self.info['dateModified'])[:10]
		self.downloadsLabel.text = str(self.info['downloads'])[:10]
		self.downloadButton.bind(on_press=self.callback)
		self.downloadButton.info = self.info
		self.screenShot.source = serverURL+"/downloadSS?fullname="+self.info['filename']+".png"
class saveas(BoxLayout):
	def __init__(self, mtref):
		self.mtref = mtref
		super(saveas,self).__init__()
	def initUI(self, dt=0):
		self.nameLabel.text = self.mtref.nameBox.text
	def savePressed(self, instance):
		self.mtref.nameBox.text = self.nameLabel.text
		self.mtref.savePressed()
		self.mtref.sapopup.dismiss()
		Popup(title="Saved",
				content=Label(text="saved "+self.nameLabel.text),
				size_hint=(0.6, 0.3), size=(400, 400)).open()
class uploads(BoxLayout):
	def __init__(self, mtref):
		self.mtref = mtref
		super(uploads,self).__init__()
		#Clock.schedule_once(self.initUI)
	def initUI(self, dt=0):
		self.nameLabel.text = self.mtref.nameBox.text
		self.screenShot.source = self.nameLabel.text+".png"
		self.screenShot.reload()
		#descLabel: descLabel
		#self.gameref.export_to_png(filename=self.nameBox.text+".png")

	#wget -qO- --post-data "userName=alex&passHash=123&name=test2&creating=true" http://0.0.0.0:8080/createUser
	def userPressed(self, instance):
		params = urllib.urlencode({
		'userName':self.userName.text, 'passHash': self.password.text, 'creating':"true"
		})
		headers = {'Content-type': 'application/x-www-form-urlencoded',
	          'Accept': 'text/plain'}
		req = UrlRequest(serverURL+'/createUser', on_success=self.user_posted, req_body=params,
	        req_headers=headers)
		req.wait()
	def user_posted(self, info, result):
		print "sent user"
		print info
		print result
		#self.mtref.ulpopup.dismiss()
		Popup(title="Info",
				content=Label(text=str(result)),
				size_hint=(0.6, 0.4), size=(400, 400)).open()
	#wget -qO- --post-data "author=alex&passHash=123&name=test2&levelData=asdagrdh" http://0.0.0.0:8080/uploadLevel
	def uploadPressed(self, instance):
		self.uploadLevel()
	def uploadLevel(self):
		print "uploading level"
		lname = self.mtref.nameBox.text
		updata = self.mtref.gameref.serials.exportDict()
		#req = UrlRequest('/listLevels', on_success=self.got_levels, timeout=1000)
		import base64
		params = urllib.urlencode({
		'author':self.userName.text, 'passHash': self.password.text,
		'name':lname,"levelData":json.dumps(updata),
		"sshot":base64.b64encode(open(lname+".png", 'r').read())
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
		self.mtref.ulpopup.dismiss()
		Popup(title="Uploaded",
				content=Label(text=str(result)),
				size_hint=(0.6, 0.4), size=(400, 400)).open()
class downloads(BoxLayout):
	def __init__(self, mtref):
		self.mtref = mtref
		super(downloads,self).__init__()
		self.cursor = 0
		self.pagesize = 8

	def setSort(self, stype):
		if stype == self.sortSpinner.text:
			print self.reverseButton.state
			if self.reverseButton.state == 'down':
				self.reverseButton.state = 'normal'
			else:
				self.reverseButton.state = 'down'
		else:
			self.sortSpinner.text = stype
		self.goPressed()
	def prevPage(self):
		self.cursor -=self.pagesize
		if self.cursor<0:self.cursor = 0
		self.listLevels()
	def nextPage(self):
		self.cursor +=self.pagesize
		self.listLevels()
	def goPressed(self, instance=None):
		print "go pressed"
		self.cursor = 0
		self.listLevels()
	def listLevels(self):
		headers = {'Content-type': 'application/x-www-form-urlencoded',
	          'Accept': 'text/plain'}

		params = {"cursor":self.cursor, "limit":self.pagesize,"sortKey": self.sortSpinner.text}
		if self.reverseButton.state == 'down':params['reverse']=True
		print "requesting levels", serverURL+'/queryLevels',params
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
		#self.levelBox.add_widget(levelItem())
		for item in data:
			#print item
			i=item#data[item]
			#b = Button(text=i['name'], on_press=self.dllevel)
			li = levelItem(i,self.dllevel)
			#b.info = i
			self.levelBox.add_widget(li)

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

class callbacks(BoxLayout):
	def __init__(self, mtref):
		self.mtref = mtref
		#self.scripty = mtref.gameref.scripty
		super(callbacks,self).__init__()
		#self.typeChanged()
		self.nofire = True
	def setTypeA(self,ta):
		self.colTypeASpinner.text = ta
		self.typeChanged()
	def typeChanged(self, instance=None):
		handlers = self.mtref.gameref.scripty.collision_handlers
		if self.colTypeASpinner.text not in handlers: handlers[self.colTypeASpinner.text] = {}
		tbd = handlers[self.colTypeASpinner.text]
		print "tbd=",tbd
		if self.colTypeBSpinner.text not in tbd: tbd[self.colTypeBSpinner.text] = {}
		methods = tbd[self.colTypeBSpinner.text]
		print "methods=", methods
		self.nofire = True
		self.beginSpinner.text = methods["begin"] if "begin" in methods else "None"
		self.pre_solveSpinner.text = methods["pre_solve"] if "pre_solve" in methods else "None"
		self.post_solveSpinner.text = methods["post_solve"] if "post_solve" in methods else "None"
		self.separateSpinner.text = methods["separate"] if "separate" in methods else "None"
		self.nofire = False

	def calleeChanged(self, instance, caller):
		if self.nofire: return
		print "changing col handler:",\
			self.colTypeASpinner.text,\
			self.colTypeBSpinner.text,\
			caller,\
			instance.text
		'''self.mtref.gameref.scripty.add_col_handler(
			self.colTypeASpinner.text,
			self.colTypeBSpinner.text,
			caller,
			instance.text
		)'''
		self.mtref.gameref.scripty.set_col_handlers(
			self.colTypeASpinner.text,
			self.colTypeBSpinner.text,
			begin=self.beginSpinner.text,
			pre_solve=self.pre_solveSpinner.text,
			post_solve=self.post_solveSpinner.text,
			separate=self.separateSpinner.text)
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
		self.grav_backup = cy.Vec2d(0,0)
		self.staticOn = False
		self.paused = False
		self.killMomem = False
		self.selectedItem = None
		self.selectedEntity = None
		self.toolSettings = {"circle": {"texture": "sheep"},
							 "square": {"texture": "Dirt"},
							 "box": {"texture": "face_box"},
							 "draw": {"texture": "Grass1"},
							 "poly": {"texture": "Grass1"},
							 "plank": {"texture": "plank"},
		}
		self.callbacksBox = None
		self.currentTool = ""
		self.testsave = []
		self.gameref = None
		self.entcpy = None #item on the clipboard
		self.fireText = True
		self.cpointids = []
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
		self.l2menus = [self.settingsMenu, self.joinMenu, self.createMenu, self.entityMenu,
		                self.fileMenu, self.polyMenu, self.splineMenu]
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

		self.uploadBox = uploads(self)
		self.ulpopup = Popup(title="Upload",
				content=self.uploadBox,
				size_hint=(0.8, 0.8), size=(400, 400))

		self.saveasBox = saveas(self)
		self.sapopup = Popup(title="Save As",
				content=self.saveasBox,
				size_hint=(0.8, 0.4), size=(400, 400))

		exampleLevels = [ os.path.basename(f)[:-5] for f in glob.glob(os.path.dirname(__file__)+"/examples/*.json")]
		for levelname in exampleLevels:
			newb = Button(text=levelname, font_size=14)
			newb.bind(on_press=self.loadExample)
			self.examplesMenu.add_widget(newb)
		#self.spriteSpinner.values = os.listdir("./sprites")

	def update(self, dt):
		self.fireText = False
		shape = self.selectedItem
		ent = self.selectedEntity
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
		elif ent:
			if not self.selectedMenu.xvelLabel.focus:
				self.selectedMenu.xvelLabel.text = "0"
			if not self.selectedMenu.yvelLabel.focus:
				self.selectedMenu.yvelLabel.text = "0"
			if hasattr(ent, 'position'):
				#if not self.selectedMenu.xposLabel.focus:
				self.selectedMenu.xposLabel.text = "%0.2f" % ent.position.x
				#if not self.selectedMenu.yposLabel.focus:
				ypostr = "%0.2f" % ent.position.y
				self.selectedMenu.yposLabel.text = ypostr
			if hasattr(ent, 'rotate'):
				#if not self.selectedMenu.angleLabel.focus:
				tv = "%0.2f" % ent.rotate.r
				self.selectedMenu.angleLabel.text = tv

		self.fireText = True
	#def examplesPressed(self, instance):


	def loadPressed(self, instance):
		self.gameref.clearAll()
		self.gameref.serials.loadJSON(self.nameBox.text+".json")
		#self.gameref.loadFromDict(self.testsave)

	def savePressed(self, instance=None):
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
		#self.spritePreview.source = 'atlas://assets/myatlas/'+ self.spriteSpinner.text
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
		self.inputPreview.text = instance.text
		try:
			fval = float(instance.text)
		except ValueError:
			return
		shape = self.selectedItem
		if shape:
			shape.body.velocity = (fval, shape.body.velocity.y)
	def yvelChanged(self, instance):
		self.inputPreview.text = instance.text
		try:
			fval = float(instance.text)
		except ValueError:
			return
		shape = self.selectedItem
		if shape:
			shape.body.velocity = (shape.body.velocity.x, fval)
	def xposChanged(self, instance):
		self.inputPreview.text = instance.text
		fval = float(instance.text)
		shape = self.selectedItem
		if shape:
			shape.body.position = (fval, shape.body.position.y)
			self.gameref.reindexEnt(self.selectedEntity)

	def yposChanged(self, instance):
		self.inputPreview.text = instance.text
		fval = float(instance.text)
		shape = self.selectedItem
		if shape:
			shape.body.position = (shape.body.position.x, fval)
			self.gameref.reindexEnt(self.selectedEntity)

	def angleChanged(self, instance):
		self.inputPreview.text = instance.text
		fval = float(instance.text)
		shape = self.selectedItem
		if shape:
			shape.body.angle = fval
			self.gameref.reindexEnt(self.selectedEntity)
	def brush_size_changed(self, value):
		sides = int(8+math.sqrt(value))
		sidelen =value*math.pi*2/sides
		self.polyMenu.minlenslider.value = (sidelen-1)*0.3
		print sidelen


	def simplifyPolyPressed(self, instance):
		ent = self.selectedEntity
		if hasattr(ent, 'poly_renderer'):
			#ent.polyshape.remove_short_lines()
			ent.polyshape.remove_some_pts(.8)

			self.gameref.create_poly((0,0),ent.polyshape,ent.entity_id)

	def textureChanged(self, instance):
		ent = self.selectedEntity
		if hasattr(ent, 'physics_renderer'):
			ent.physics_renderer.texture = instance.text
		elif hasattr(ent, 'poly_renderer'):
			tex = 'sprites/'+instance.text+'.png'
			ent.poly_renderer.texture = tex
			self.gameref.gameworld.systems['poly_renderer'].redraw_entity(ent.entity_id)
		else:
			self.gameref.create_poly((0,0),ent.polyshape,ent.entity_id,texture=instance.text)

	def redChanged(self, strval):
		self.inputPreview.text = strval
		fval = float(strval)
		ent = self.selectedEntity
		if ent:
			ent.color.r = fval
			if self.selectedItem.__class__.__name__ == 'Poly':
				c = ent.color
				color = (c.r, c.g ,c.b ,c.a)
				self.gameref.create_poly((0,0),ent.polyshape,ent.entity_id,color=color)
	def greenChanged(self, strval):
		self.inputPreview.text = strval
		fval = float(strval)
		ent = self.selectedEntity
		if ent:
			ent.color.g = fval
			if self.selectedItem.__class__.__name__ == 'Poly':
				c = ent.color
				color = (c.r, c.g ,c.b ,c.a)
				self.gameref.create_poly((0,0),ent.polyshape,ent.entity_id,color=color)
	def blueChanged(self, strval):
		self.inputPreview.text = strval
		fval = float(strval)
		ent = self.selectedEntity
		if ent:
			ent.color.b = fval
			if self.selectedItem.__class__.__name__ == 'Poly':
				c = ent.color
				color = (c.r, c.g ,c.b ,c.a)
				self.gameref.create_poly((0,0),ent.polyshape,ent.entity_id,color=color)
	def opacityChanged(self, strval):
		self.inputPreview.text = strval
		fval = float(strval)
		ent = self.selectedEntity
		if ent:
			ent.color.a = fval
			if self.selectedItem.__class__.__name__ == 'Poly':
				c = ent.color
				color = (c.r, c.g ,c.b ,c.a)
				self.gameref.create_poly((0,0),ent.polyshape,ent.entity_id,color=color)

	def frictionChanged(self, instance):
		self.inputPreview.text = instance.text
		fval = float(instance.text)
		if self.selectedEntity:
			for shape in self.selectedEntity.physics.shapes:
				shape.friction = fval
				self.gameref.reindexEnt(self.selectedEntity)
		elif self.selectedItem:
			self.selectedItem.friction = fval
		self.gameref.reindexEnt(self.selectedEntity)

	def massChanged(self, instance):
		self.inputPreview.text = instance.text
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
		self.inputPreview.text = instance.text
		fval = float(instance.text)
		if self.selectedEntity:
			for shape in self.selectedEntity.physics.shapes:
				shape.elasticity = fval
				self.gameref.reindexEnt(self.selectedEntity)
		elif self.selectedItem:
			self.selectedItem.elasticity = fval

		self.gameref.reindexEnt(self.selectedEntity)

	def on_rad_change(self, instance, value):
		self.inputPreview.text = instance.text
		newrad = float(value)
		print "rad change", newrad
		if self.selectedItem and self.selectedEntity:
			self.selectedItem.radius = newrad
			self.selectedItem.unsafe_set_radius(newrad)
			self.selectedEntity.physics_renderer.width = newrad * 2
			self.selectedEntity.physics_renderer.height = newrad * 2
			self.selectedItem.body.moment = cy.moment_for_circle(self.selectedItem.body.mass,
																 newrad,0)  #seems ineffective?
			self.gameref.reindexEnt(self.selectedEntity)

	def on_width_change(self, instance, value):
		self.inputPreview.text = instance.text
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
		self.inputPreview.text = instance.text
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

	def setEnt(self, ent, fshape=None):
		self.fireText = False
		self.selectedItem = None
		self.selectedMenu.selectedLabel.text = "None"
		self.selectedEntity = ent
		self.inputPreview.text = ""
		self.selectedMenu.shapeInfo.clear_widgets()
		for id in self.cpointids:
			self.gameref.delObj(id)
		self.cpointids = []
		if ent:
			self.selectedEntity = ent#self.gameref.gameworld.entities[shape.body.data]
			#ent = self.selectedEntity
			if hasattr(ent, 'splineshape'):

				for p in ent.splineshape.ControlPoints:
					pid = self.gameref.create_decoration(pos=(p[0], p[1]), width=20, height=20,
																texture='plank')
					self.cpointids.append(pid)
			#print dir(ent.physics)
			if hasattr(ent, 'physics'):
				if fshape:
					shape=fshape
				else:
					shape = self.selectedEntity.physics.shapes[0]
				self.selectedItem = shape
				self.selectedMenu.selectedLabel.text = ent.physics.shape_type+" "+str(shape.body.data)
				#tv = "x=%f\ny=%f" % (shape.body.position.x, shape.body.position.y)
				#self.selectedMenu.posLabel.text = tv
				self.selectedMenu.frictionLabel.text = "%0.2f" % shape.friction
				self.selectedMenu.massLabel.text = "%0.2f" % shape.body.mass
				self.selectedMenu.elasLabel.text = "%0.2f" % shape.elasticity
				#print self.gameref.scripty.collision_types[shape.collision_type], shape.collision_type
				self.selectedMenu.colTypeSpinner.text = self.gameref.scripty.collision_types[shape.collision_type]

				if shape.__class__.__name__ == "Circle":
					cs = CircleSettings()
					cs.radiusLabel.text = "%0.2f" % shape.radius
					cs.radiusLabel.bind(text=self.on_rad_change)
					self.selectedMenu.shapeInfo.add_widget(cs)
				elif shape.__class__.__name__ == "BoxShape":
					bs = BoxSettings()
					bs.widthLabel.text = "%0.2f" % shape.width
					bs.heightLabel.text = "%0.2f" % shape.height
					bs.widthLabel.bind(text=self.on_width_change)
					bs.heightLabel.bind(text=self.on_height_change)
					self.selectedMenu.shapeInfo.add_widget(bs)
				#elif shape.__class__.__name__ == "Poly":

		if self.gameref.selectedShapeID != None:
			self.gameref.delObj(self.gameref.selectedShapeID)
			self.gameref.selectedShapeID = None
		if ent:
			if self.selectedMenuView not in self.rightMenu.children:
				self.rightMenu.add_widget(self.selectedMenuView)
			if hasattr(ent, 'physics_renderer'):
				self.selectedMenu.texLabel.text = ent.physics_renderer.texture
			if hasattr(ent, 'poly_renderer'):
				texname = ent.poly_renderer.texture.split('/')[-1][:-4]
				self.selectedMenu.texLabel.text = texname
				ps = Button(text="simplify", on_press=self.simplifyPolyPressed)
				self.selectedMenu.shapeInfo.add_widget(ps)
			if hasattr(ent, 'color'):
				self.selectedMenu.redLabel.text = str(ent.color.r)
				self.selectedMenu.greenLabel.text = str(ent.color.g)
				self.selectedMenu.blueLabel.text = str(ent.color.b)
				self.selectedMenu.opacityLabel.text = str(ent.color.a)
			r  = None
			if hasattr(ent,"physics_renderer"):
				self.gameref.selectedShapeID = self.gameref.create_decoration(pos=(shape.body.position.x, shape.body.position.y),
				                                                 width=ent.physics_renderer.width*1.1+10, height=ent.physics_renderer.height*1.1+10,
																texture='emptybox')
		else:
			self.rightMenu.remove_widget(self.selectedMenuView)
		self.fireText = True
	def setShape(self, shape):
		if shape:
			ent = self.gameref.gameworld.entities[shape.body.data]
			if ent:
				self.setEnt(ent,shape)
		else:
			self.setEnt(None)

	def delSelPressed(self, instance):
		if self.selectedEntity and self.gameref:
			self.gameref.delObj(self.selectedEntity.entity_id)
			self.setEnt(None)
		#if self.selectedItem and self.gameref:
		#	self.gameref.delObj(self.selectedItem.body.data)
		#	self.setShape(None)
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
		self.gameref.touches = {}
	def downloadsPressed(self, instance):
		self.dlpopup.open()
		self.downloadsBox.listLevels()
		self.gameref.touches = {}
	def saveThumb(self):
		filename = self.nameBox.text+".png"
		self.gameref.export_to_png(filename=filename)
		baseWidth = 150
		from PIL import Image
		# Open the image file.
		img = Image.open(filename)

		# Calculate the height using the same aspect ratio
		widthPercent = (baseWidth / float(img.size[0]))
		height = int((float(img.size[1]) * float(widthPercent)))

		# Resize it.
		img = img.resize((baseWidth, height), Image.BILINEAR)

		# Save it back to disk.
		img.save(filename)

	def saveAsPressed(self, instance):
		#self.saveThumb()
		self.sapopup.open()
		self.saveasBox.initUI()
		self.gameref.touches = {}
	def uploadPressed(self, instance):
		self.saveThumb()
		self.ulpopup.open()
		self.uploadBox.initUI()
		self.gameref.touches = {}

	def makeEntDataDict(self, ent):
		#create entity datadict if missing
		if not hasattr(ent, "datadict"):
			print "initing datadict"
			ent.datadict = {}

	def putDefaultsInDataDict(self):
		if self.selectedEntity == None:return
		self.makeEntDataDict(self.selectedEntity)
		scripty = self.gameref.scripty
		colfuncs = scripty.getHandlersForType(self.selectedItem.collision_type)
		print "defaults=",scripty.defaults
		print "colfuncs=",colfuncs
		for cf in colfuncs:
			if cf in scripty.defaults:
			#if len(colfunc)>0 and colfunc[0] in scripty.defaults:
				defaultdict = scripty.defaults[cf]
				print "defaultdict=",defaultdict
				for i in defaultdict.keys():
					if i not in self.selectedEntity.datadict:
						self.selectedEntity.datadict[i] = defaultdict[i]

	def varsPressed(self, btn):
		if self.selectedEntity:
			self.putDefaultsInDataDict()
			Popup(title="Entity Varables",
				  content=entDataBox(ddict = self.selectedEntity.datadict),
				  size_hint=(0.8, 0.8),
				  on_dismiss=None).open()
	def colTypeChanged(self, instance):
		if self.selectedEntity and self.gameref:
			newval = self.gameref.scripty.collision_types[instance.text]
			for shape in self.selectedEntity.physics.shapes:
				shape.collision_type = newval
				#self.gameref.reindexEnt(self.selectedEntity)
			print newval, instance.text
			self.putDefaultsInDataDict()


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


	def playPressed(self, instance=None):
		self.paused = not self.paused
		if instance: instance.text = "Resume" if self.paused else "Pause"
	def momemPressed(self, instance=None):
		self.grav_backup, self.gameref.space.gravity = self.gameref.space.gravity, self.grav_backup
		self.killMomem = not self.killMomem
		#instance.text = "Resume" if self.paused else "Pause"