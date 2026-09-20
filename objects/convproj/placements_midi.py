# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
import copy
import math
import numpy as np
import os

from objects.convproj import autopoints
from objects.convproj import visual
from objects.convproj import midievents
from objects.convproj import time
from objects.convproj import placements_base

class cvpj_placement_midi(placements_base.cvpj_placement_base):
	__slots__ = ['midievents','auto','pitch','visual_roll']
	def __init__(self, time_ppq):
		super().__init__(time_ppq)
		self.midievents = midievents.midievents()
		self.auto = {}
		self.pitch = 0
		self.visual_roll = visual.cvpj_visual_placement_notes()

	def make_base(self):
		plb_obj = cvpj_placement_midi(self.time_ppq)
		plb_obj.time = self.time.copy()
		plb_obj.time_ppq = self.time_ppq
		plb_obj.muted = self.muted
		plb_obj.visual = self.visual
		plb_obj.group = self.group
		plb_obj.locked = self.locked
		return plb_obj

	def add_autopoints(self, a_type):
		self.auto[a_type] = autopoints.cvpj_autopoints(self.time_ppq, 'float')
		return self.auto[a_type]

	def midi_from(self, input_file):
		from objects.midi_file.parser import MidiFile
		if os.path.exists(input_file):
			midifile = MidiFile.fromFile(input_file)
			self.from_midiparser(midifile)

	def midi_from_bin(self, rawdata):
		from objects.midi_file.parser import MidiFile
		if rawdata is not None:
			midifile = MidiFile.fromRaw(rawdata)
			self.from_midiparser(midifile)

	def from_midiparser(self, midifile):
		from objects.midi_file import events as MidiEvents
		events_obj = self.midievents
		events_obj.ppq = midifile.ppqn

		if midifile.tracks:
			for eventlist in midifile.tracks:
				curpos = 0
				for msg in eventlist.events:
					curpos += msg.deltaTime
					if type(msg) == MidiEvents.NoteOnEvent: events_obj.add_note_on(curpos, msg.channel, msg.note, msg.velocity)
					elif type(msg) == MidiEvents.NoteOffEvent: events_obj.add_note_off(curpos, msg.channel, msg.note)
					elif type(msg) == MidiEvents.CopyrightEvent: events_obj.add_copyright(msg.copyright)
					elif type(msg) == MidiEvents.PitchBendEvent: events_obj.add_pitch(curpos, msg.channel, msg.pitch)
					elif type(msg) == MidiEvents.ControllerEvent: events_obj.add_control(curpos, msg.channel, msg.controller, msg.value)
					elif type(msg) == MidiEvents.ProgramEvent: events_obj.add_program(curpos, msg.channel, msg.program)
					elif type(msg) == MidiEvents.EndOfTrackEvent: break
					elif type(msg) == MidiEvents.TrackNameEvent:
						if not events_obj.track_name: events_obj.track_name = msg.name

class cvpj_placements_midi(placements_base.cvpj_placements_multi_base):
	__slots__ = []
	def __init__(self, time_ppq):
		super().__init__(time_ppq, cvpj_placement_midi)

	def change_timings(self, time_ppq):
		for pl in self.data:
			pl.time.change_timing(self.time_ppq, time_ppq)
			for mpename, autodata in pl.auto.items():
				autodata.change_timings(time_ppq)
		self.time_ppq = time_ppq

	def change_seconds(self, is_seconds, bpm, ppq):
		for pl in self.data: 
			pl.time.change_seconds(is_seconds, bpm, ppq)
			for _, a in pl.auto.items(): a.change_seconds(is_seconds, bpm, ppq)
		
	def make_base_from_notes(self, notesp):
		plb_obj = cvpj_placement_midi(self.time_ppq)
		plb_obj.time = notesp.time.copy()
		plb_obj.time_ppq = notesp.time_ppq
		plb_obj.muted = notesp.muted
		plb_obj.visual = notesp.visual
		plb_obj.group = notesp.group
		plb_obj.locked = notesp.locked
		self.data.append(plb_obj)
		return plb_obj

	def add(self, time_ppq):
		pl_obj = cvpj_placement_midi(time_ppq)
		self.data.append(pl_obj)
		return pl_obj
