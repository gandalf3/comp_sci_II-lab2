import bge

class Typewriter(bge.types.KX_FontObject):
    def __init__(self, own):
        self.line # message to be typed out
        self.speed = 1 #chars per tic
        self.caret_pos = 0 # position of typing cursor thingy
        
    def onEOL(self):
        pass
    
    def typewrite(self):
        if self.caret_pos < len(self.line):
            self
        
        
        
def main(cont):
    own = cont.owner
    
    if "typer_init" not in own:
        own["typer_init"] = True
        own = Typewriter(own)
        
        
def increment(object):
    i = int(object.text)
    print("increment", i)
    object.text = str(i+1)