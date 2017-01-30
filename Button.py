import bge
import ColorTheme

class Button(bge.types.KX_GameObject):
    def __init__(self, own):
        self.own = own
        self.enabled = False
        self.active = False
        self.highlight = None
        
    def enable(self):
        #TODO highlight button here
        self.enabled = True
        
    def activate(self, color):
        scn = bge.logic.getCurrentScene()
        fill = scn.addObject("ActiveFill", self)
        fill.color.xyz = color.xyz
        
        self.children[0].color = (1,1,1,1)
        
    def deactivate(self):
        self.children[0].color = ColorTheme.support
        
    def mouseOver(self):
        scn = bge.logic.getCurrentScene()
        
        try:
            if not self.highlight.invalid:
                self.highlight["fade"] = 1.5
            else:
                self.highlight = scn.addObject("SelectionRing", self)
        except AttributeError:
            self.highlight = scn.addObject("SelectionRing", self)
            
        
    def mouseOff(self):
#        if self.highlight:
#            self.highlight.endObject()
        pass
        
    def mouseClick(self):
        print("button click")
        bge.logic.sendMessage("clickEvent", self.name)

# the current "controller" is automatically passed into any function which takes an argument and is called from a controller
def initialize(cont):
    own = cont.owner
    
    # ensure this only runs once
    if "button_init" not in own:
        own['button_init'] = True
        own = Button(own)
    
def main(cont):
    own = cont.owner
    senses = cont.sensors
    
    if senses['MouseOver'].positive:
        own.mouseOver()
        if senses['LeftMouse'].positive:
            own.mouseClick()
    else:
        own.mouseOff()
        
        
    own.children[0].color = own.children[0].color.lerp(ColorTheme.support, .01)