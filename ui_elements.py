from kivent import (GameScreenManager, GameScreen)
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

import os

'''class YACSButtonCircle(ToggleButton):
    
    def on_touch_down(self, touch):
        if self.weapons_locked:
            pass
        else:
            return super(YACSButtonCircle, self).on_touch_down(touch)
'''

class PlainButton(Button):
    def on_touch_down(self, touch):
      sres = super(PlainButton, self).on_touch_down(touch)
      print "pb=", sres
      #print dir(self)
      print "--"
      return sres
    

class MainTools(BoxLayout):
    def __init__(self, **kwargs):
        super(MainTools, self).__init__(**kwargs)
        self.staticOn = False
        self.paused = False
        Clock.schedule_once(self.init_tools)
    def init_tools(self, dt):
        self.l2menus = [self.joinMenu, self.createMenu]
        self.remove_widget(self.joinMenu)
        self.spriteSpinner.text="square"
        #self.spriteSpinner.values = os.listdir("./sprites")
    def setTool(self, tool):
       self.currentTool = tool
       print "Tool is now: %s" % tool
    def camPressed(self, instance):
        self.setTool("camera")
        #for i in range(10):
        #  self.add_random_circle()
    def dragPressed(self, instance):
        self.setTool("drag")
    def clearl2(self):
        for i in self.l2menus:
          self.remove_widget(i)
    def joinPressed(self, instance):
        if self.joinMenu in self.children:
          self.clearl2()
          self.size_hint_x=.1
        else:
          self.clearl2()
          self.add_widget(self.joinMenu)
          self.size_hint_x=.2
          
    def createPressed(self, instance):
        if self.createMenu in self.children:
          self.clearl2()
          self.size_hint_x=.1
        else:
          self.clearl2()
          self.add_widget(self.createMenu)
          self.size_hint_x=.2
    def circlePressed(self, instance):
        self.setTool("circle")
        self.spriteSpinner.text="sheep"
    def squarePressed(self, instance):
        self.setTool("square")
        self.spriteSpinner.text="face_box"
    def boxPressed(self, instance):
        self.setTool("box")
        self.spriteSpinner.text="square"
    def massPressed(self, instance):
        self.massSlider.value = 0 if self.massSlider.value > 0 else 10
        
    def delPressed(self, instance):
        self.setTool("del")
    def playPressed(self, instance):
        self.paused = not self.paused
        self.ids['playButton'].text = "Pause/Play" if self.paused else "Play/Pause"
    def vortexPressed(self, instance):
        self.setTool("vortex")
    def drawPressed(self, instance):
        self.setTool("draw")
        self.spriteSpinner.text="square"
    def plankPressed(self, instance):
        self.setTool("plank")
        self.spriteSpinner.text="square"
    def joinPinPressed(self, instance):
        self.setTool("pin")
    def joinP2PPressed(self, instance):
        self.setTool("p2p")
    def joinP2PSPressed(self, instance):
        self.setTool("p2ps")
    def joinC2PPressed(self, instance):
        self.setTool("c2p")
    def joinC2CPressed(self, instance):
        self.setTool("c2c")