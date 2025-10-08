# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from external.easybinrw import easybinrw
from objects.exceptions import ProjectFileParserException

import logging
logger_projparse = logging.getLogger('projparse')

class nbs_key:
	def __init__(self):
		self.pos = 0
		self.inst = 0
		self.key = 0
		self.vel = 100
		self.pan = 100
		self.pitch = 0

	def read(self, ebrw_readstr, nbs_newformat):
		self.inst = ebrw_readstr.int_u8()
		self.key = ebrw_readstr.int_u8()
		if nbs_newformat == 1:
			self.vel = ebrw_readstr.int_u8()
			self.pan = ebrw_readstr.int_u8()
			self.pitch = ebrw_readstr.int_s16()

class nbs_layer:
	def __init__(self):
		self.notes = []
		self.name = ''
		self.lock = 0
		self.vol = 100
		self.stereo = 100

class nbs_custom_inst:
	def __init__(self):
		self.name = ''
		self.file = ''
		self.key = 0
		self.presskey = 0

class nbs_song:
	def __init__(self):
		pass

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)

		startbyte = ebrw_readstr.int_u16()
		if startbyte == 0: 
			self.newformat = 1
			version = ebrw_readstr.int_u8()
			if version != 5:
				raise ProjectFileParserException('mnbs: only version 5 new-NBS or old format is supported.')
			self.inst_count = ebrw_readstr.int_u8()
			self.song_length = ebrw_readstr.int_u16()
			self.layers_count = ebrw_readstr.int_u16()
		else: 
			version = 0
			self.newformat = 0
			self.song_length = startbyte
			self.layers_count = ebrw_readstr.int_u16()

		self.custom = []

		self.layers = [nbs_layer() for _ in range(self.layers_count)]
		self.name = ebrw_readstr.string_i32()
		self.author = ebrw_readstr.string_i32()
		self.orgauthor = ebrw_readstr.string_i32()
		self.description = ebrw_readstr.string_i32()

		self.tempo = ebrw_readstr.int_u16()
		self.autosave_on = ebrw_readstr.int_u8()
		self.autosave_duration = ebrw_readstr.int_u8()
		self.numerator = ebrw_readstr.int_u8()

		self.stat_minutes_spent = ebrw_readstr.int_u32()
		self.stat_clicks_left = ebrw_readstr.int_u32()
		self.stat_clicks_right = ebrw_readstr.int_u32()
		self.stat_notes_added = ebrw_readstr.int_u32()
		self.stat_notes_removed = ebrw_readstr.int_u32()

		self.source_filename = ebrw_readstr.string_i32()
		if self.newformat == 1:
			nbs_loopon = ebrw_readstr.int_u8()
			nbs_maxloopcount = ebrw_readstr.int_u8()
			nbs_loopstarttick = ebrw_readstr.int_u16()
		else:
			nbs_loopon = 1
			nbs_maxloopcount = 1
			nbs_loopstarttick = 128

		notes_done = 0
		note_tick = -1

		while notes_done == 0:
			jump_tick = ebrw_readstr.int_u16()
			if jump_tick != 0:
				jump_layer = ebrw_readstr.int_u16()
				note_tick += jump_tick
				if jump_layer != 0:
					note_layer = jump_layer
					layer_done = 0
					while layer_done == 0:
						note_obj = nbs_key()
						note_obj.pos = note_tick
						note_obj.read(ebrw_readstr, self.newformat)
						outlayer = note_layer-1
						if outlayer < len(self.layers): self.layers[outlayer].notes.append(note_obj)
						jump_layer = ebrw_readstr.int_u16()
						if jump_layer == 0: layer_done = 1
						note_layer += jump_layer
			if jump_tick == 0:
				notes_done = 1

		if ebrw_readstr.remaining():
			for layernum in range(self.layers_count): 
				layer_obj = self.layers[layernum]
				layer_obj.name = ebrw_readstr.string_i32()
				if self.newformat == 1: 
					layer_obj.lock = ebrw_readstr.int_u8()
					layer_obj.vol = ebrw_readstr.int_u8()
					layer_obj.stereo = ebrw_readstr.int_u8()
				else:
					layer_obj.vol = ebrw_readstr.int_u8()

		if ebrw_readstr.remaining():
			for _ in range(ebrw_readstr.int_u8()):
				custom_obj = nbs_custom_inst()
				custom_obj.name = ebrw_readstr.string_i32()
				custom_obj.file = ebrw_readstr.string_i32()
				custom_obj.key = ebrw_readstr.int_u8()
				custom_obj.presskey = ebrw_readstr.int_u8()
				self.custom.append(custom_obj)

		return True