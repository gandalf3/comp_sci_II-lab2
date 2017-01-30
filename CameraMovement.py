import bge
from mathutils import Vector

def main(cont):
    own = cont.owner
    
    if "mouse_init" not in own:
        w = bge.render.getWindowWidth()
        h = bge.render.getWindowHeight()
        bge.render.setMousePosition(int(w/2), int(h/2))
        
        own["mouse_init"] = True
    
    mpos = bge.logic.mouse.position
    mpos = Vector((mpos[0] - .5, 1-mpos[1] - .5))
    campos = own.worldPosition
    
    own.worldPosition.xy = campos.xy.lerp(mpos.xy*2, .05)
    own.alignAxisToVect((0, 1, 0), 1, 1) # keep local Y locked to global Y
    own.alignAxisToVect(own.worldPosition, 2, 1)