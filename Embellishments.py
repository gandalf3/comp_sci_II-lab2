import bge
import aud
import ColorTheme
from ColorUtils import transparent, clamp

device = aud.device()
click = aud.Factory(bge.logic.expandPath('//sounds/click_2.wav'))
click_alt = aud.Factory(bge.logic.expandPath('//sounds/click.wav'))

# TODO: This is a big ol' mess. Future me: just rewrite this from scratch
def count_char(cont):
    own = cont.owner
    now = bge.logic.getRealTime()
    
    if "char_init" not in own:
        own["char_init"] = True
        own["start_time"] = now
        own["start_z"] = own.worldPosition.z
        own["clicked"] = False
        
    own.worldPosition.z = \
        own["start_z"] * max(own["start_time"]+1 - now, 0)**(1/3)

    fade =\
        clamp(clamp((own["start_time"]+2 - now))*own.get("linger", 1))

    asdf = clamp(2-own.worldPosition.z) * own.get("linger", 1)    
    
    
    if own.worldPosition.z <= 0:
        if not own["clicked"]:
            if own.name == "Countdown4":
                device.play(click_alt)
            else:
                device.play(click)
            own["clicked"] = True
        
        own.worldPosition.z = clamp((own["start_z"] * (own["start_time"]+1 - now)*.1)*(1/own.get("linger", 1)), -1, 0)
        asdf = 1-abs(own.worldPosition.z)*own.get("linger", 1)*2
        
    own.color[3] = asdf
    
    if fade <= 0:
        own.endObject()
        
        
        
def highlighter(cont):
    own = cont.owner
    
    if "highlight_init" not in own:
        own["highlight_init"] = True
        own["fade"] = 1.5
        
    own['fade'] = own['fade']-.05
    own.color[3] = clamp(own['fade'])
    if own['fade'] <= 0:
        own.endObject()

def filler(cont):
    own = cont.owner
    
    if "filler_init" not in own:
        own["filler_init"] = True
        own['scale'] = 0.0
        own["fade"] = 0.0
        own['done'] = False
        own.localScale = (0.0, 0.0, 0.0)
        
    own['scale'] += .03
    if own['fade'] < 1.2:
        own['fade'] += .04
    own.localScale.xyz = clamp(own['scale']**(1/5))
    own.color[3] = clamp(own['fade'])
    
    if own.sensors['Message'].positive:
        own['done'] = True
    
    if own['done']:
        own['fade'] -= .05
        
    if own['fade'] <= 0:
        own.endObject()
        
        
def support_fade(cont):
    own = cont.owner
    
    own.color = own.color.lerp(ColorTheme.support, .003)
    
def fixfont(cont):
    own = cont.owner
    
    own.resolution = 4