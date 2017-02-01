import bge
import aud
from math import floor
from mathutils import Vector
import ColorTheme
from ColorUtils import transparent, clamp
from random import randrange
import RPSLS
from VelociText import VelociText
from Typewriter import increment

device = aud.device()
sounds = {
	"tie": aud.Factory(bge.logic.expandPath('//sounds/load.wav')).volume(.5).fadeout(0, 1.8),
	"win": aud.Factory(bge.logic.expandPath('//sounds/save.wav')).volume(.5).fadeout(1, 2),
	"loss": aud.Factory(bge.logic.expandPath('//sounds/misc_sound.wav')).volume(.5).fadeout(1, 2),
	"pick": aud.Factory(bge.logic.expandPath('//sounds/misc_menu_4.wav')).volume(.5),
	"nopick": aud.Factory(bge.logic.expandPath('//sounds/negative_2.wav')).volume(.5),
	}
	
# would rather these not be global, but o well.
picks = {
"player": None,
"computer": None
}
	
	
class GameStateHandler():
	def __init__(self):
		self.init = False
		self.time_now = bge.logic.getRealTime()
		self.time_begin = 0
		self.time_elapsed = 0
		self.doing_cleanup = False
		
	def run(self):
		#self.scn = bge.logic.getCurrentScene()
		self.time_now = bge.logic.getRealTime()
		self.time_elapsed = self.time_now - self.time_begin
		self.gameobject = bge.logic.getCurrentController().owner
		
		if self.init is False:
			self.init = True
			self.handler_init = False
			self.cleanup_init = False
			self.doing_cleanup = False
			self.time_begin = self.time_now
			# bleh. Can't define these as None or something otherwise they won't be overridden by subclass methods, apparently. So have consider possible complete non-existance
			# unfortunatly this as the side-effect of silencing ALL attribute errors which occur anywhere within state handler code D:
			try:
				self.setup()
			except AttributeError:
				pass
		
		# this basically a substate could probably be implented very neatly as a full on state (recursive class definitions, anyone?) but whatever.
		if self.doing_cleanup:
			if not self.cleanup_init:
				self.cleanup_init = True
				self.time_begin = self.time_now
				self.time_elapsed = self.time_now - self.time_begin
				
			try:
				c = self.cleanup()
				if c == "finished":
					self.init = False
					return "finished"
			except AttributeError:
				self.init = False
				return "finished"
				# question, how to avoid copy/pasting things in try/catch blocks like this?
				# see line 28 of Button.py for a more terrible example
		else:
			if not self.handler_init:
				self.handler_init = True
				self.time_begin = self.time_now
				self.time_elapsed = self.time_now - self.time_begin
			
			try:
				h = self.handler()
				if h == "finished":
					self.doing_cleanup = True
			except AttributeError:
				pass
	
# TODO: this thing should be split up into smaller pieces
class ShowWinner(GameStateHandler):
	def setup(self):
		global picks
		scn = bge.logic.getCurrentScene()
		
		self.outcome, self.outcome_version = RPSLS.result(picks["player"], picks["computer"])
		
		self.score_obj = scn.objects['count_' + self.outcome]
		self.textplace = False
		
		if self.outcome == "win":
			self.win_obj = scn.objects[str(picks["player"])]
			self.lose_pos = scn.objects[str(picks["computer"])].worldPosition.copy()
			self.win_col = ColorTheme.primary
		elif self.outcome == "loss":
			self.win_obj = scn.objects[str(picks["computer"])]
			self.lose_pos = scn.objects[str(picks["player"])].worldPosition.copy()
			self.win_col = ColorTheme.alternate
		if self.outcome == "tie":
			device.play(sounds[self.outcome])
			increment(self.score_obj)
		else:
			self.win_pos = self.win_obj.worldPosition.copy()
			self.winlose_dist = (self.win_pos - self.lose_pos).length
			self.distfac = (self.winlose_dist - .88) / self.winlose_dist
			
	def handler(self):
		scn = bge.logic.getCurrentScene()

		if self.outcome == "tie":
			if self.time_now >= 3:
				return "finished"
			else:
				return "not finished"
		
		fac = clamp((self.time_elapsed) * 2)**2
		self.win_obj.worldPosition = self.win_pos.lerp(self.lose_pos, fac*self.distfac)
		if self.textplace != True and fac >= 1:
			self.textplace = True
			if self.outcome_version is not None:
				t = VelociText(scn.addObject("GenericText", self.win_obj))
				t.text = self.win_obj["win_msg" + str(self.outcome_version+1)]
				t.velocity = Vector((0,.03,0))
				device.play(sounds[self.outcome])
				increment(self.score_obj)
				expand = scn.addObject("Expandipoo", self.win_obj)
				expand.color = self.win_col
				return "finished"
	
	def cleanup(self):
		self.win_obj.worldPosition = self.win_obj.worldPosition.lerp(self.win_pos, .1)
		if self.time_elapsed >= 2 if self.outcome != "tie" else .5:
			return "finished"
		


class CountDown(GameStateHandler):
	def setup(self):
		self.next_count = -1
		bge.logic.sendMessage("kill_highlights")
	
	def handler(self):
		scn = bge.logic.getCurrentScene()
		elapsed = self.time_elapsed*2
		
		if elapsed >= self.next_count+1 and self.next_count < 4:
			self.next_count = floor(elapsed)
			scn.addObject("Countdown" + str(self.next_count))
		else:
			if elapsed >= 6:
				return "finished"
		
		
class Pick(GameStateHandler):
	def setup(self):
		global picks
		scn = bge.logic.getCurrentScene()
		
		self.player_pick = None
		self.computer_pick = randrange(0, 4)
		picks["computer"] = self.computer_pick
		picks["player"] = None
		self.computer_click = scn.objects[str(self.computer_pick)]
		self.computer_click.activate(ColorTheme.alternate)
		
	def handler(self):
		global picks
		scn = bge.logic.getCurrentScene()
		
		
		if self.time_elapsed <= .5:
			if len(self.gameobject.sensors['Inbox'].bodies) > 0:
				self.player_click = scn.objects[self.gameobject.sensors['Inbox'].bodies[0]]
				self.player_pick = self.player_click['strat']
				picks["player"] = self.player_pick
				self.player_click.activate(ColorTheme.primary)
				device.play(sounds["pick"])
				return "finished"
		else:
			print("You didn't pick at the right time")
			device.play(sounds["nopick"])
			return "finished"
		

class GameControl(bge.types.KX_GameObject):
	def __init__(self, own):
		self.gamestate = "intro"
			
		self.show_winner = ShowWinner()
		self.countdown = CountDown()
		self.pick = Pick()
		

	def prettyfade(self):
		#TODO: do pretty graphical flippantry here
		self.gamestate = "play"
		
	
	def main(self):
		
		# possibly make this cleaner by letting the next state be specified by the individual state handlers
		if self.gamestate == "intro":
			self.prettyfade()
			
		elif self.gamestate == "play":
			status = self.countdown.run()
			if status == "finished":
				self.gamestate = "pick"
				
		elif self.gamestate == "pick":
			status = self.pick.run()
			if status == "finished":
				# this is why
				if picks["player"] is None:
					self.gamestate = "play"
				else:
					self.gamestate = "show_winner"
			
		elif self.gamestate == "show_winner":
			status = self.show_winner.run()
			if status == "finished":
				self.gamestate = "play"
			
		
def main(cont):
	own = cont.owner
	
	if "game_init" not in own:
		own["game_init"] = True
		own = GameControl(own)
	own.main()
	
	