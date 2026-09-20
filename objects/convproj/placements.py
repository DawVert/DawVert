
# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later


from objects.convproj import project as convproj
from functions import xtramath
import copy

from objects.convproj import notelist
from objects.convproj import midievents
from objects.convproj import tracks

from objects.convproj import placements_midi
from objects.convproj import placements_notes
from objects.convproj import placements_audio
from objects.convproj import placements_index
from objects.convproj import placements_video
from objects.convproj import placements_custom
from objects.convproj import time
from objects.convproj import stretch

from objects.convproj import time
from objects.convproj import visual

def internal_tempo_calc(placements):
	for pl_obj in placements:
		time_obj = pl_obj.time
		time_obj.realtime_tempo = time_obj.position.get_tempo(time_obj.time_ppq)

def internal_tempo_calc_audio(placements):
	for pl_obj in placements:
		time_obj = pl_obj.time
		time_obj.realtime_tempo = time_obj.position.get_tempo(time_obj.time_ppq)
		stretch_obj = pl_obj.sample.stretch
		stretch_timing = stretch_obj.timing
		if stretch_timing.time_type == 'real_rate': 
			stretch_timing.original_bpm = time_obj.realtime_tempo

def internal_tempo_calc_nested(placements):
	for pl_obj in placements:
		time_obj = pl_obj.time
		time_obj.realtime_tempo = time_obj.position.get_tempo(time_obj.time_ppq)
		for x in pl_obj.events:
			x.time.realtime_tempo = time_obj.realtime_tempo

class cvpj_placements:
	__slots__ = ['pl_midi','pl_notes','pl_audio','pl_notes_indexed','pl_audio_indexed','pl_audio_nested','pl_video','pl_custom','notelist','midievents','time_ppq','uses_placements','is_indexed']
	def __init__(self, time_ppq, uses_placements, is_indexed):
		self.uses_placements = uses_placements
		self.is_indexed = is_indexed
		self.time_ppq = time_ppq

		self.notelist = notelist.cvpj_notelist(time_ppq)
		self.midievents = midievents.midievents()

		self.pl_midi = placements_midi.cvpj_placements_midi(self.time_ppq)

		self.pl_notes = placements_notes.cvpj_placements_notes(self.time_ppq)
		self.pl_audio = placements_audio.cvpj_placements_audio(self.time_ppq)

		self.pl_notes_indexed = placements_index.cvpj_placements_index(self.time_ppq)
		self.pl_audio_indexed = placements_index.cvpj_placements_index(self.time_ppq)

		self.pl_audio_nested = placements_audio.cvpj_placements_nested_audio(self.time_ppq)

		self.pl_video = placements_video.cvpj_placements_video(self.time_ppq)
		self.pl_custom = placements_custom.cvpj_placements_custom(self.time_ppq)

	def do_tempo(self, get_pos_temp):
		internal_tempo_calc(self.pl_midi.data)
		internal_tempo_calc(self.pl_notes.data)
		internal_tempo_calc_audio(self.pl_audio.data)
		internal_tempo_calc(self.pl_notes_indexed.data)
		internal_tempo_calc(self.pl_audio_indexed.data)
		internal_tempo_calc_nested(self.pl_audio_nested.data)
		internal_tempo_calc(self.pl_video.data)
		internal_tempo_calc(self.pl_custom.data)

	def sort(self):
		self.pl_notes.sort()
		self.pl_audio.sort()
		self.pl_notes_indexed.sort()
		self.pl_audio_indexed.sort()
		self.pl_audio_nested.sort()
		self.pl_video.sort()
		self.pl_custom.sort()

	def autosplit(self):
		self.pl_notes.autosplit(self.time_ppq)

	def merge_crop(self, pl_obj, pos, dur, visualfill, groupid):
		if (self.uses_placements==pl_obj.uses_placements) and (self.is_indexed==pl_obj.is_indexed) and (self.time_ppq==pl_obj.time_ppq) and (type(self.time_ppq)==type(pl_obj.time_ppq)):
			self.pl_notes.merge_crop(pl_obj.pl_notes, pos, dur, visualfill)
		if (self.uses_placements==pl_obj.uses_placements) and (self.is_indexed==pl_obj.is_indexed) and (self.time_ppq==pl_obj.time_ppq) and (type(self.time_ppq)==type(pl_obj.time_ppq)):
			self.pl_audio.merge_crop(pl_obj.pl_audio, pos, dur, visualfill, groupid)

	def merge_crop_nestedaudio(self, pl_obj, pos, dur, visualfill):
		if (self.uses_placements==pl_obj.uses_placements) and (self.is_indexed==pl_obj.is_indexed) and (self.time_ppq==pl_obj.time_ppq) and (type(self.time_ppq)==type(pl_obj.time_ppq)):
			self.pl_notes.merge_crop(pl_obj.pl_notes, pos, dur, visualfill)
		if (self.uses_placements==pl_obj.uses_placements) and (self.is_indexed==pl_obj.is_indexed) and (self.time_ppq==pl_obj.time_ppq) and (type(self.time_ppq)==type(pl_obj.time_ppq)):
			placement_obj = self.add_nested_audio()
			placement_obj.time.set_posdur(pos, dur)
			placement_obj.events = copy.deepcopy(pl_obj.pl_audio)
			if visualfill: placement_obj.visual = visualfill

	def get_dur(self):
		#print(self.pl_notes.get_dur(),self.pl_audio.get_dur(),self.notelist.get_dur())
		return max(self.pl_notes.get_dur(),self.pl_audio.get_dur(),self.pl_notes_indexed.get_dur(),self.pl_audio_indexed.get_dur(),self.notelist.get_dur())

	def get_start(self):
		outcount = min(self.pl_notes.get_start(),self.pl_audio.get_start())
		if self.notelist.count(): outcount = min(self.notelist.get_start_end()[0], outcount)
		return outcount

	def change_seconds(self, is_seconds, bpm, ppq):
		self.pl_notes.change_seconds(is_seconds, bpm, ppq)
		self.pl_audio.change_seconds(is_seconds, bpm, ppq)
		self.pl_custom.change_seconds(is_seconds, bpm, ppq)
		self.pl_video.change_seconds(is_seconds, bpm, ppq)
		self.pl_midi.change_seconds(is_seconds, bpm, ppq)

	def remove_cut(self):
		self.pl_notes.remove_cut()

	def remove_loops(self, out__placement_loop):
		self.pl_notes.remove_loops(out__placement_loop)
		self.pl_midi.remove_loops(out__placement_loop)
		self.pl_audio.remove_loops(out__placement_loop)
		self.pl_audio_nested.remove_loops(out__placement_loop)
		self.pl_notes_indexed.remove_loops(out__placement_loop)
		self.pl_audio_indexed.remove_loops(out__placement_loop)
		self.pl_video.remove_loops(out__placement_loop)
		self.pl_custom.remove_loops(out__placement_loop)

	def add_loops(self, loopcompat):
		self.pl_notes.add_loops(loopcompat)
		self.pl_notes_indexed.add_loops(loopcompat)
		#self.pl_audio.add_loops(loopcompat)
		self.pl_audio_indexed.add_loops(loopcompat)

	def add_notes(self): return self.pl_notes.add(self.time_ppq)

	def add_notes_timed(self, time_ppq): return self.pl_notes.add(time_ppq)

	def add_audio(self): return self.pl_audio.add()

	def add_notes_indexed(self): return self.pl_notes_indexed.add()

	def add_audio_indexed(self): return self.pl_audio_indexed.add()

	def add_video(self): return self.pl_video.add()

	def add_midi(self): return self.pl_midi.add(self.time_ppq)

	def add_custom(self): return self.pl_custom.add()

	#def all_stretch_set_pitch_nonsync(self):
	#	if not self.is_indexed: 
	#		self.pl_audio.all_stretch_set_pitch_nonsync()
	#		for x in self.pl_audio_nested: 
	#			for i in x.events: 
	#				i.all_stretch_set_pitch_nonsync()

	def changestretch(self, convproj_obj, target, tempo):
		if not self.is_indexed: 
			self.pl_audio.changestretch(convproj_obj, target, tempo)
			for x in self.pl_audio_nested: 
				for i in x.events: 
					i.changestretch(convproj_obj, target, tempo)

	def change_timings(self, time_ppq):
		self.notelist.change_timings(time_ppq)

		self.pl_notes.change_timings(time_ppq, self.is_indexed)
		self.pl_notes.change_timings(time_ppq, self.is_indexed)
		self.pl_audio.change_timings(time_ppq)
		self.pl_midi.change_timings(time_ppq)
		self.pl_notes_indexed.change_timings(time_ppq)
		self.pl_audio_indexed.change_timings(time_ppq)
		self.pl_audio_nested.change_timings(time_ppq)
		self.pl_video.change_timings(time_ppq)
		self.pl_custom.change_timings(time_ppq)

		self.time_ppq = time_ppq

	def add_inst_to_notes(self, inst):
		for x in self.pl_notes:
			x.notelist.inst_all(inst)

	def used_insts(self):
		used_insts = []
		for notespl_obj in self.pl_notes: 

			for instid in notespl_obj.notelist.get_used_inst():
				if instid not in used_insts: used_insts.append(instid)

		for instid in self.notelist.get_used_inst():
			if instid not in used_insts: used_insts.append(instid)

		return used_insts

	def inst_split(self):
		splitted_pl = {}
		for notespl_obj in self.pl_notes: notespl_obj.inst_split(splitted_pl)
		return splitted_pl

	def unindex_notes(self, notelist_index):
		for indexpl_obj in self.pl_notes_indexed:
			new_notespl_obj = placements_notes.cvpj_placement_notes(self.time_ppq)
			new_notespl_obj.time = indexpl_obj.time.copy()
			new_notespl_obj.muted = indexpl_obj.muted

			if indexpl_obj.fromindex in notelist_index:
				nle_obj = notelist_index[indexpl_obj.fromindex]
				new_notespl_obj.notelist = copy.deepcopy(nle_obj.notelist)
				new_notespl_obj.visual = nle_obj.visual
				new_notespl_obj.timesig_auto = nle_obj.timesig_auto.copy()
				new_notespl_obj.timemarkers = copy.deepcopy(nle_obj.timemarkers)
				new_notespl_obj.visual_roll = nle_obj.visual_roll.copy()

			self.pl_notes.data.append(new_notespl_obj)
		self.pl_notes_indexed = placements_index.cvpj_placements_index(self.time_ppq)
		self.is_indexed = False

	def unindex_audio(self, sample_index):
		for indexpl_obj in self.pl_audio_indexed:
			apl_obj = placements_audio.cvpj_placement_audio(self.time_ppq)

			if indexpl_obj.fromindex in sample_index:
				sle_obj = sample_index[indexpl_obj.fromindex]
				apl_obj.time = indexpl_obj.time.copy()
				apl_obj.muted = indexpl_obj.muted
				apl_obj.fade_in = indexpl_obj.fade_in
				apl_obj.fade_out = indexpl_obj.fade_out
				
				apl_obj.visual = sle_obj.visual
				apl_obj.sample = copy.deepcopy(sle_obj)

				apl_obj.sample.vol *= indexpl_obj.vol
				self.pl_audio.data.append(apl_obj)

		self.pl_audio_indexed = placements_index.cvpj_placements_index(self.time_ppq)
		self.is_indexed = False

	def to_indexed_notes(self, existingpatterns, pattern_number):
		existingpatterns = []
		self.pl_notes_indexed = placements_index.cvpj_placements_index(self.time_ppq)

		for notepl_obj in self.pl_notes:
			nle_data = [notepl_obj.notelist, notepl_obj.visual.name, notepl_obj.visual.color]

			dupepatternfound = None
			for existingpattern in existingpatterns:
				if existingpattern[1] == nle_data: 
					dupepatternfound = existingpattern[0]
					break

			if dupepatternfound == None:
				patid = 'm2mi_' + str(pattern_number)
				existingpatterns.append([patid, nle_data])
				dupepatternfound = patid
				pattern_number += 1

			new_index_obj = placements_index.cvpj_placement_index(self.time_ppq)
			new_index_obj.time = notepl_obj.time.copy()
			new_index_obj.fromindex = dupepatternfound
			new_index_obj.muted = notepl_obj.muted

			self.pl_notes_indexed.data.append(new_index_obj)

		self.is_indexed = True
		self.pl_notes = placements_notes.cvpj_placements_notes(self.time_ppq)
		return existingpatterns, pattern_number

	def to_indexed_audio(self, existingsamples, sample_number):
		new_data_audio = []
		self.pl_audio_indexed = placements_index.cvpj_placements_index(self.time_ppq)

		for audiopl_obj in self.pl_audio:
			sle_obj = audiopl_obj.sample

			dupepatternfound = None
			for existingsample in existingsamples:
				if existingsample[1] == sle_obj: 
					dupepatternfound = existingsample[0]
					break

			if dupepatternfound == None:
				patid = 'm2mi_audio_' + str(sample_number)
				existingsamples.append([patid, sle_obj])
				dupepatternfound = patid
				sample_number += 1

			new_index_obj = placements_index.cvpj_placement_index(self.time_ppq)
			new_index_obj.time = audiopl_obj.time.copy()
			new_index_obj.fromindex = dupepatternfound
			new_index_obj.muted = audiopl_obj.muted
			self.pl_audio_indexed.data.append(new_index_obj)

		self.pl_audio = placements_audio.cvpj_placements_audio(self.time_ppq)
		return existingsamples, sample_number

	def add_nested_audio(self):
		return self.pl_audio_nested.add()

	def add_fxrack_channel(self, fxnum):
		if not self.is_indexed:
			for pl_obj in self.pl_audio:
				if pl_obj.sample.fxrack_channel == -1: 
					pl_obj.sample.fxrack_channel = fxnum
			for nestedpl_obj in self.pl_audio_nested:
				for e in nestedpl_obj.events:
					e.sample.fxrack_channel = fxnum

	def remove_nested(self):

		self.pl_audio_nested.remove_loops([])
		for nestedpl_obj in self.pl_audio_nested:
			nest_time_obj = nestedpl_obj.time
			main_s = nest_time_obj.get_offset()
			main_e = nest_time_obj.get_dur()+main_s
			basepos = nest_time_obj.get_pos()

			#print('PL', end=' ')
			#for x in [main_s, main_e]:
			#	print(str(x).ljust(19), end=' ')
			#print()

			for e in nestedpl_obj.events:
				e_time_obj = e.time
				event_s = e_time_obj.get_pos()
				event_et = e_time_obj.get_dur()
				event_o = e_time_obj.get_offset()

				event_e = event_s+event_et

				if main_e>=event_s and main_s<=event_e:
					out_start = max(main_s, event_s)
					out_end = min(main_e, event_e)

					scs = out_start-event_s
					
					if False:
						print('E ', end='| ')
						for x in [main_s+event_o, main_e]: print(str(round(x, 4)).ljust(7), end=' ')
						print('|', end=' ')
						for x in [event_s, event_e]: print(str(round(x, 4)).ljust(7), end=' ')
						print('|', end=' ')
						for x in [out_start, out_end]: print(str(round(x, 4)).ljust(7), end=' ')
						print('|', end=' ')
						for x in [scs]: print(str(round(x, 4)).ljust(7), end=' ')
						print()

					cutplpl_obj = copy.deepcopy(e)

					cpl_time_obj = cutplpl_obj.time
					cpl_time_obj.set_pos((out_start+basepos)-main_s)
					sco = out_start-event_o
					offset_d = (main_e-main_s)-sco
					cpl_time_obj.set_dur(min(max(out_end-out_start, offset_d), event_et))
					cpl_time_obj.cut_type = 'cut'
					cpl_time_obj.calc_offset_add(scs)

					cpl_time_obj.position.timeid = nest_time_obj.position.timeid

					cutplpl_obj.muted = cutplpl_obj.muted or nestedpl_obj.muted
					if not cutplpl_obj.visual.name: 
						cutplpl_obj.visual.name = nestedpl_obj.visual.name
					self.pl_audio.data.append(cutplpl_obj)

		self.pl_audio_nested = placements_audio.cvpj_placements_nested_audio(self.time_ppq)

	def debugtxt(self, starttxt):
		outtxt = starttxt+' | '
		if self.notelist.count(): outtxt += 'Npl Notes: %i |' % self.notelist.count()
		if len(self.midievents): outtxt += 'Npl Midi: %i |' % len(self.midievents)

		if len(self.pl_midi): outtxt += 'Midi: %i |' % len(self.pl_midi)
		if len(self.pl_notes): outtxt += 'Notes: %i |' % len(self.pl_notes)
		if len(self.pl_audio): outtxt += 'Audio: %i |' % len(self.pl_audio)
		if len(self.pl_notes_indexed): outtxt += 'Indexed Notes: %i |' % len(self.pl_notes_indexed)
		if len(self.pl_audio_indexed): outtxt += 'Indexed Audio: %i |' % len(self.pl_audio_indexed)
		if len(self.pl_audio_nested): outtxt += 'Nested Audio: %i |' % len(self.pl_audio_nested)
		if len(self.pl_video): outtxt += 'Video: %i |' % len(self.pl_video)
		if len(self.pl_custom): outtxt += 'Custom: %i |' % len(self.pl_custom)

		print(outtxt)
		#outtxt += []
		#print(len(self.notelist.nl), end='|')
		#print(str(len(self.pl_notes.data))+'-'+str(len(self.pl_audio.data)), end='|')
		#print(str(len(self.pl_notes_indexed.data))+'-'+str(len(self.pl_audio_indexed.data)))