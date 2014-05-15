from kivent import (GameScreenManager, GameScreen)
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

from kivy.uix.textinput import TextInput

import cymunk as cy

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
    
class tbox(TextInput):
    def on_touch_down(self, touch):
      super(tbox, self).on_touch_down(touch)
      if self.collide_point( *touch.pos ):
          #touch.grab( self )
          return True
      return False
class CircleSettings(BoxLayout):
    def on_touch_down(self, touch):
      super(CircleSettings, self).on_touch_down(touch)
      if self.collide_point( *touch.pos ):
          #touch.grab( self )
          return True
      return False
class BoxSettings(BoxLayout):
    def on_touch_down(self, touch):
      super(BoxSettings, self).on_touch_down(touch)
      if self.collide_point( *touch.pos ):
          #touch.grab( self )
          return True
      return False

class MainTools(FloatLayout):
    def __init__(self, **kwargs):
        super(MainTools, self).__init__(**kwargs)
        self.staticOn = False
        self.paused = False
        self.selectedItem = None
        self.selectedEntity = None
        #self.gameref = None
        Clock.schedule_once(self.init_tools)
    def init_tools(self, dt):
        self.l2menus = [self.joinMenu, self.createMenu, self.entityMenu]
        #self.leftMenu.remove_widget(self.joinMenu)
        #self.spriteSpinner.text="square"
        self.clearl2()
        #self.spriteSpinner.values = os.listdir("./sprites")
    def update(self, dt):
       shape = self.selectedItem
       #self.selectedMenu.selectedLabel.text = str(shape)
       #self.selectedMenu.xposLabel.text = ""
       #self.selectedMenu.yposLabel.text = ""
       if (shape):
         if not self.selectedMenu.xposLabel.focus:
          self.selectedMenu.xposLabel.text = str(shape.body.position.x)
         if not self.selectedMenu.yposLabel.focus:
          ypostr = "%f" % (shape.body.position.y)
          self.selectedMenu.yposLabel.text = ypostr
         if not self.selectedMenu.angleLabel.focus:
          tv = "%f" % (shape.body.angle)
          self.selectedMenu.angleLabel.text = tv
         
    def setTool(self, tool):
       self.currentTool = tool
       print "Tool is now: %s" % tool
    def setRef(self, ref):
        self.gameref = ref
        print ref
    def xposChanged(self, instance):
      fval = float(instance.text)
      shape = self.selectedItem
      space =self.gameref.gameworld.systems['physics'].space
      if shape:
        shape.body.position=(fval,shape.body.position.y)
        entity = self.selectedEntity
        for s in entity.physics.shapes:
              space.reindex_shape(s)
    def yposChanged(self, instance):
      fval = float(instance.text)
      shape = self.selectedItem
      space =self.gameref.gameworld.systems['physics'].space
      if shape:
        shape.body.position=(shape.body.position.x,fval)
        entity = self.selectedEntity
        for s in entity.physics.shapes:
              space.reindex_shape(s)
    def angleChanged(self, instance):
      fval = float(instance.text)
      shape = self.selectedItem
      space =self.gameref.gameworld.systems['physics'].space
      if shape:
        shape.body.angle=fval
        entity = self.selectedEntity
        for s in entity.physics.shapes:
              space.reindex_shape(s)
    def on_rad_change(self, instance, value):
      newrad = float(value)
      print "rad change", newrad
      if self.selectedItem and self.selectedEntity:
        self.selectedItem.unsafe_set_radius(newrad)
        self.selectedEntity.physics_renderer.width = newrad*2
        self.selectedEntity.physics_renderer.height = newrad*2
    def on_width_change(self, instance, value):
      space =self.gameref.gameworld.systems['physics'].space
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
        self.selectedItem = newshape
        self.selectedEntity.physics_renderer.width = newrad
    def on_height_change(self, instance, value):
      space =self.gameref.gameworld.systems['physics'].space
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
        self.selectedItem = newshape
        self.selectedEntity.physics_renderer.height = newrad
    def setShape(self, shape):
       self.selectedItem = shape
       self.selectedMenu.selectedLabel.text = str(shape)
       self.selectedEntity = None
       if (shape):
         self.selectedEntity = self.gameref.gameworld.entities[shape.body.data]
         #tv = "x=%f\ny=%f" % (shape.body.position.x, shape.body.position.y)
         #self.selectedMenu.posLabel.text = tv
         self.selectedMenu.shapeInfo.clear_widgets()
         if shape.__class__.__name__ == "Circle":
           cs = CircleSettings()
           cs.radiusLabel.text = str(shape.radius)
           cs.radiusLabel.bind(text=self.on_rad_change)
           self.selectedMenu.shapeInfo.add_widget(cs)
         if shape.__class__.__name__ == "BoxShape":
           bs = BoxSettings()
           bs.widthLabel.text = str(shape.width)
           bs.heightLabel.text = str(shape.height)
           bs.widthLabel.bind(text=self.on_width_change)
           bs.heightLabel.bind(text=self.on_height_change)
           self.selectedMenu.shapeInfo.add_widget(bs)
         
       ent = self.selectedEntity
       print "selected ent:", ent
       if ent:
         self.selectedMenu.texLabel.text = ent.physics_renderer.texture
    def delSelPressed(self, instance):
       if (self.selectedItem) and self.gameref:
        self.gameref.delObj(self.selectedItem.body.data)
        self.setShape(None)
    def camPressed(self, instance):
        self.setTool("camera")
        #for i in range(10):
        #  self.add_random_circle()
    def dragPressed(self, instance):
        self.setTool("drag")
    def clearl2(self):
        for i in self.l2menus:
          if i in self.leftMenu.children:
            self.leftMenu.remove_widget(i)
    def startPressed(self, instance):
        self.setTool("start")
    def endPressed(self, instance):
        self.setTool("end")
    def blankPressed(self, instance):
        self.setTool("blank")
    def entityPressed(self, instance):
        if self.entityMenu in self.leftMenu.children:
          self.clearl2()
          self.leftMenu.size_hint_x=.1
        else:
          self.clearl2()
          self.leftMenu.add_widget(self.entityMenu)
          self.leftMenu.size_hint_x=.2
    def joinPressed(self, instance):
        if self.joinMenu in self.leftMenu.children:
          self.clearl2()
          self.leftMenu.size_hint_x=.1
        else:
          self.clearl2()
          print self.leftMenu
          print self.joinMenu
          self.leftMenu.add_widget(self.joinMenu)
          self.leftMenu.size_hint_x=.2
          
    def createPressed(self, instance):
        if self.createMenu in self.leftMenu.children:
          self.clearl2()
          self.leftMenu.size_hint_x=.1
        else:
          self.clearl2()
          print self.leftMenu
          print self.createMenu
          self.leftMenu.add_widget(self.createMenu)
          self.leftMenu.size_hint_x=.2
    def circlePressed(self, instance):
        self.setTool("circle")
        self.spriteSpinner.text="sheep"
    def squarePressed(self, instance):
        self.setTool("square")
        self.spriteSpinner.text="grassyrock"
    def boxPressed(self, instance):
        self.setTool("box")
        self.spriteSpinner.text="face_box"
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
        self.spriteSpinner.text="Grass2"
    def plankPressed(self, instance):
        self.setTool("plank")
        self.spriteSpinner.text="plank"
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