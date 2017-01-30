import bge
import aud
from math import floor
import ColorTheme
from ColorUtils import transparent
from random import randrange
import RPSLS
from Typewriter import increment

device = aud.device()
sounds = {
	"tie": aud.Factory(bge.logic.expandPath('//sounds/load.wav')).volume(.5).fadeout(0, 1.8),
	"win": aud.Factory(bge.logic.expandPath('//sounds/save.wav')).volume(.5).fadeout(1, 2),
	"loss": aud.Factory(bge.logic.expandPath('//sounds/misc_sound.wav')).volume(.5).fadeout(1, 2),
	"pick": aud.Factory(bge.logic.expandPath('//sounds/misc_menu_4.wav')).volume(.5),
	"nopick": aud.Factory(bge.logic.expandPath('//sounds/negative_2.wav')).volume(.5),
	}

class GameControl(bge.types.KX_GameObject):
	def __init__(self, own):
		self.gamestate = "intro"
		
		
	def intro(self):
		pass
	
	
	def countdown(self):
		scn = bge.logic.getCurrentScene()
		
		if not self.get("countdown_init", False):
			self["countdown_init"] = True
			self.downcount_start = bge.logic.getRealTime()
			self.downcount_time = self.downcount_start
			self.next_count = -1
			bge.logic.sendMessage("kill_highlights")
			
		self.downcount_time = bge.logic.getRealTime()
		elapsed = (self.downcount_time - self.downcount_start)*2
		
		if elapsed >= self.next_count+1 and self.next_count < 4:
			self.next_count = floor(elapsed)
			scn.addObject("Countdown" + str(self.next_count))
		else:
			if elapsed >= 6:
				self.gamestate = "pick"
				self["countdown_init"] = False
				
		
	def pick(self):
		scn = bge.logic.getCurrentScene()
		now = bge.logic.getRealTime()
		
		if not self.get("pick_init", 0):
			self["pick_init"] = True
			self.pick_start = now
			self.player_pick = None
			self.computer_pick = randrange(0, 4)
			self.computer_click = scn.objects[str(self.computer_pick)]
			self.computer_click.activate(ColorTheme.alternate)
		
		if now - self.pick_start <= .5:
			if len(self.sensors['Inbox'].bodies) > 0:
				print("reception", self.sensors['Inbox'].bodies[0])
				self.player_click = scn.objects[self.sensors['Inbox'].bodies[0]]
				self.player_pick = self.player_click['strat']
				self.player_click.activate(ColorTheme.primary)
				device.play(sounds["pick"])
				self.gamestate = "show_winner"
				self["pick_init"] = False
				
		else:
			print("You didn't pick at the right time")
			device.play(sounds["nopick"])
			self.gamestate = "play"
			self["pick_init"] = False
		
		
	def show_winner(self):
		scn = bge.logic.getCurrentScene()
		now = bge.logic.getRealTime()
		
		if not self.get("winner_init", 0):
			self['winner_init'] = True
			self['winner_done'] = False
			self.win_display_start = now
			self.outcome, self.outcome_version = RPSLS.result(self.player_pick, self.computer_pick)
		
			score_obj = scn.objects['count_' + self.outcome]
			
			if self.outcome == "tie":
				self.win_obj = scn.objects[str(self.player_pick)]
				self.lose_pos = scn.objects[str(self.player_pick)].worldPosition.copy()
	#   		 self.handle_tie()
			elif self.outcome == "win":
				self.win_obj = scn.objects[str(self.player_pick)]
				self.lose_pos = scn.objects[str(self.computer_pick)].worldPosition.copy()
	#   		 self.handle_win()
			elif self.outcome == "loss":
				self.win_obj = scn.objects[str(self.computer_pick)]
				self.lose_pos = scn.objects[str(self.player_pick)].worldPosition.copy()

			self.win_pos = self.win_obj.worldPosition.copy()
			self.winlose_dist = (self.win_pos - self.lose_pos).length
			
		print("move", self.win_pos, self.lose_pos, self.winlose_dist)
		elapsed = now - self.win_display_start
		self.win_obj.worldPosition = self.win_pos.lerp(self.lose_pos, 1-((elapsed-1)**2))
		if self.outcome_version is not None:
			t = scn.addObject("GenericText", self.win_obj)
			t.text = self.win_obj["win_msg" + str(self.outcome_version+1)]
		#print(win_obj)
		#win_obj.worldPosition.lerp(lose_obj.worldPosition, .5)
#   		 self.handle_loss()

		
		
		if now - self.win_display_start > 1:
			self['winner_init'] = False
			self.gamestate = "play"

	
	def handle_tie(self):
		scn = bge.logic.getCurrentScene()
		score_ob = scn.objects['Ties']
		increment(score_ob)
		device.play(sounds["tie"])
		
		
		print("tie")
		
		
	def handle_win(self):
		scn = bge.logic.getCurrentScene()
		score_ob = scn.objects['Ties']
		increment(score_ob)
		device.play(sounds["win"])
		print("win")
		
		
	def handle_loss(self):
		device.play(sounds["loss"])
		print("loss")
	
	def prettyfade(self):
		#TODO: do pretty graphical flippantry here
		self.gamestate = "play"
		
	
	def main(self):
		if self.gamestate == "intro":
			self.prettyfade()
		elif self.gamestate == "play":
			self.countdown()
		elif self.gamestate == "pick":
			self.pick()
		elif self.gamestate == "show_winner":
			self.show_winner()
		
def main(cont):
	own = cont.owner
	
	if "game_init" not in own:
		own["game_init"] = True
		own = GameControl(own)
	own.main()
	
	
	
def fade(cont):
	own = cont.owner
	
	own.color = ([0.105857, 0.636756, 1.000000, .200000])
	

	