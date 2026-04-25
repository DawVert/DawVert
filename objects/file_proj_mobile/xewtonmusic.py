# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from external.easybinrw import easybinrw
import numpy as np

class xewtonmusic_track:
	def __init__(self):
		self.unk = []
		self.tracknum = 0
		self.instnum = 0
		self.color = None
		self.fx_on = 0
		self.selected = 0
		self.volume = 1
		self.pan = 0
		self.notes = []

	def read(self, ebrw_readstr):
		self.unk = []
		self.tracknum = ebrw_readstr.int_u32()
		self.instnum = ebrw_readstr.int_u32()
		self.color = ebrw_readstr.list_int_u8(4)
		self.unk.append(  ebrw_readstr.int_u8()  )
		self.unk.append(  ebrw_readstr.int_u8()  )
		self.fx_on = ebrw_readstr.int_u8()
		self.selected = ebrw_readstr.int_u8()
		self.volume = ebrw_readstr.float()
		self.pan = ebrw_readstr.float()

class xewtonmusic_header:
	def __init__(self):
		self.unk = []
		self.seconds = 0
		self.tempo = 120
		self.timesig1 = 4
		self.timesig2 = 4

	def read(self, ebrw_readstr):
		self.unk = []
		ebrw_readstr.skip(2)
		self.seconds = ebrw_readstr.float()
		ebrw_readstr.skip(6)
		self.tempo = ebrw_readstr.float()
		self.timesig1 = ebrw_readstr.int_u8()
		self.timesig2 = ebrw_readstr.int_u8()
		#self.unk.append(  ebrw_readstr.int_u8()  )
		#self.unk.append(  ebrw_readstr.int_u32()  )
		#self.unk.append(  ebrw_readstr.int_u32()  )
		#self.unk.append(  ebrw_readstr.int_u32()  )
		#self.unk.append(  ebrw_readstr.int_u16()  )
		#self.unk.append(  ebrw_readstr.int_u16()  )

#class xewtonmusic_effx:
#	def __init__(self):
#		self.unk = []

#	def read(self, ebrw_readstr):
#		print(  ebrw_readstr.rest().hex()  )

notes_dtype = np.dtype([
	('pos', np.uint32),
	('dur', np.uint32),
	('key', np.uint8),
	('vol', np.uint8),
	('unk', np.uint16),
	])

class xewtonmusic_note:
	def __init__(self):
		self.pos = 0
		self.dur = 0
		self.key = 0
		self.vol = 0
		self.unk = 0
		self.unk1_data = b''

	def read(self, ebrw_readstr):
		self.pos = ebrw_readstr.int_u32()
		self.dur = ebrw_readstr.int_u32()
		self.key = ebrw_readstr.int_u8()
		self.vol = ebrw_readstr.int_u8()
		self.unk1 = ebrw_readstr.int_u8()
		self.unk2 = ebrw_readstr.int_u8()
		if self.unk1: self.unk1_data = ebrw_readstr.raw(self.unk1*4)

class xewtonmusic_notes:
	def __init__(self):
		self.tracknum = 0
		self.notes = []

	def read(self, ebrw_readstr):
		self.tracknum = ebrw_readstr.int_u16()
		self.unk = ebrw_readstr.int_u16()
		num_notes = ebrw_readstr.int_u32()
		for n in range(num_notes):
			note = xewtonmusic_note()
			note.read(ebrw_readstr)
			self.notes.append(note)

class xewtonmusic_file:
	def __init__(self):
		self.tracks = {}
		self.header = xewtonmusic_header()

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)

		ebrw_readstr.magic_check(b'\x99XMS')
		ebrw_readstr.skip(4)

		self.tracks = {}
		while ebrw_readstr.remaining():
			chunk_name = ebrw_readstr.raw(4)
			chunk_size = ebrw_readstr.int_u32()

			ebrw_readstr.isolate_size(chunk_size)

			if chunk_name==b'TINF':
				tinf_obj = xewtonmusic_track()
				tinf_obj.read(ebrw_readstr)
				self.tracks[tinf_obj.tracknum] = tinf_obj
			elif chunk_name==b'TNOT':
				tnot_obj = xewtonmusic_notes()
				tnot_obj.read(ebrw_readstr)
				if tnot_obj.tracknum in self.tracks:
					self.tracks[tnot_obj.tracknum].notes = tnot_obj
			elif chunk_name==b'HEAD':
				self.header.read(ebrw_readstr)
			#elif chunk_name==b'EFFX':
			#	tinf_obj = xewtonmusic_effx()
			#	tinf_obj.read(ebrw_readstr)
			#	#exit()
			#else:
			#	print(chunk_name)
			#	chunk_data = ebrw_readstr.raw(chunk_size)

			ebrw_readstr.isolate_end()
		return True
