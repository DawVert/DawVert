# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from external.easybinrw import easybinrw
from objects.exceptions import ProjectFileParserException
import numpy as np

# ============================================= instrument ============================================= 

class ceol_instrument:
	def __init__(self, ebrw_readstr):
		self.inst = 0
		self.type = 0
		self.palette = 0
		self.cutoff = 128
		self.resonance = 0
		self.volume = 256
		if ebrw_readstr:
			self.inst = ebrw_readstr.int_u16()
			self.type = ebrw_readstr.int_u16()
			self.palette = ebrw_readstr.int_u16()
			self.cutoff = ebrw_readstr.int_u16()
			self.resonance = ebrw_readstr.int_u16()
			self.volume = ebrw_readstr.int_u16()

# ============================================= pattern ============================================= 

class ceol_note:
	__slots__ = ['key','len','pos']
	def __init__(self):
		self.key = 0
		self.len = 0
		self.pos = 0

class ceol_pattern:
	def __init__(self, ebrw_readstr):
		self.notes = []
		self.recordfilter = None
		if ebrw_readstr:
			self.key = ebrw_readstr.int_u16()
			self.scale = ebrw_readstr.int_u16()
			self.inst = ebrw_readstr.int_u16()
			self.palette = ebrw_readstr.int_u16()
			numnotes = ebrw_readstr.int_u16()
			for _ in range(numnotes):
				note_obj = ceol_note()
				note_obj.key = ebrw_readstr.int_u16()
				note_obj.len = ebrw_readstr.int_u16()
				note_obj.pos = ebrw_readstr.int_u16()
				ebrw_readstr.skip(2)
				self.notes.append(note_obj)
			if ebrw_readstr.int_u16():
				self.recordfilter = ebrw_readstr.list_int_u16(16*3)
				self.recordfilter = np.reshape(self.recordfilter, [16, 3])

# ============================================= song ============================================= 

class ceol_song:
	def __init__(self):
		self.swing = 0
		self.effect_type = 0
		self.effect_value = 0
		self.bpm = 120
		self.pattern_length = 16
		self.bar_length = 4
		self.instruments = []
		self.patterns = []
		self.spots = []
		self.length = 0
		self.loopstart = 0
		self.loopend = 0

	def load_from_file(self, input_file):
		ceol_file = open(input_file, 'r')

		try: ceolnums = ceol_file.readline().split(',')[:-1]
		except: raise ProjectFileParserException('boscaceoil: File is not text.')

		ceol_array = np.asarray([int(x) for x in ceolnums], dtype=np.int16)

		if not len(ceol_array): raise ProjectFileParserException('boscaceoil: array is empty')
		
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_data(ceol_array.tobytes())
		self.versionnum = ebrw_readstr.int_u16()

		self.swing = ebrw_readstr.int_u16()
		self.effect_type = ebrw_readstr.int_u16()
		self.effect_value = ebrw_readstr.int_u16()
		self.bpm = ebrw_readstr.int_u16()
		self.pattern_length = ebrw_readstr.int_u16()
		self.bar_length = ebrw_readstr.int_u16()
		self.instruments = [ceol_instrument(ebrw_readstr) for x in range(ebrw_readstr.int_u16())]
		self.patterns = [ceol_pattern(ebrw_readstr) for x in range(ebrw_readstr.int_u16())]

		self.length = ebrw_readstr.int_u16()
		self.loopstart = ebrw_readstr.int_u16()
		self.loopend = ebrw_readstr.int_u16()
		self.spots = ebrw_readstr.list_int_s16(self.length*8)
		self.spots = np.reshape(self.spots, [self.length, 8])
		return True
