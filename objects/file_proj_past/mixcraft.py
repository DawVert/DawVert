# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import zlib
import logging
import numpy as np
from external.easybinrw import easybinrw
from external.easybinrw import riff_chunks

class mixcraft_audio_clip:
	def __init__(self):
		pass

	def read(self, ebrw_readstr, riffpart):
		self.unknowns = []
		self.unknowns.append(ebrw_readstr.double())
		self.filepath = ebrw_readstr.string(256)
		self.unknowns.append(ebrw_readstr.int_u32())
		self.filepath2 = ebrw_readstr.string(256)
		self.unknowns.append(ebrw_readstr.int_u32())
		self.unknowns.append(ebrw_readstr.double())
		self.pos = ebrw_readstr.double()
		self.dur = ebrw_readstr.double()
		self.loopstart_audio = ebrw_readstr.double()
		self.loopstart_proj = ebrw_readstr.double()
		self.max_milliseconds = ebrw_readstr.double()
		self.id = ebrw_readstr.int_u32()
		self.unknowns.append(ebrw_readstr.int_u32())
		self.speed = ebrw_readstr.double()
		self.pitch = ebrw_readstr.double()
		self.clipname = ebrw_readstr.string(256)
		self.unknowns.append(ebrw_readstr.int_u32())
		self.use_key = ebrw_readstr.int_u32()
		self.key = ebrw_readstr.int_u32()
		self.unknowns.append(ebrw_readstr.int_u32())
		self.tempo = ebrw_readstr.double()
		self.no_tempo = ebrw_readstr.int_u8()
		self.change_pitch = ebrw_readstr.int_u8()
		self.selected = ebrw_readstr.int_u8()
		self.locked = ebrw_readstr.int_u8()
		self.muted = ebrw_readstr.int_u8()
		self.unknowns.append(ebrw_readstr.int_u8())
		self.unknowns.append(ebrw_readstr.int_u8())
		self.unknowns.append(ebrw_readstr.int_u8())
		self.tempo2 = ebrw_readstr.double()
		self.key2 = ebrw_readstr.int_u32()
		self.limit_channel = ebrw_readstr.int_u32()
		self.use_noise_reduction = ebrw_readstr.int_u32()
		self.unknowns.append(ebrw_readstr.int_u32())
		self.noise_reduction_amount = ebrw_readstr.double()
		self.unknowns2 = []
		self.noise_start = ebrw_readstr.int_u32()
		self.noise_end = ebrw_readstr.int_u32()
		self.linked_num = ebrw_readstr.int_u32()
		self.unknowns2.append(ebrw_readstr.int_u32())
		self.selected = ebrw_readstr.int_u32()
		self.unknowns2.append(ebrw_readstr.int_u32())
		self.unknowns2.append(ebrw_readstr.int_u32())
		self.unknowns2.append(ebrw_readstr.int_u32())
		self.unknowns2.append(ebrw_readstr.int_u32())
		self.unknowns2.append(ebrw_readstr.int_u32())
		self.unknowns2.append(ebrw_readstr.int_u32())
		self.unknowns2.append(ebrw_readstr.int_u32())
		self.unknowns2.append(ebrw_readstr.int_u32())
		self.unknowns2.append(ebrw_readstr.int_u32())
		self.unknowns2.append(ebrw_readstr.int_u32())
		self.unknowns2.append(ebrw_readstr.int_u32())
		self.unknowns2.append(ebrw_readstr.int_u32())
		self.unknowns2.append(ebrw_readstr.int_u32())
		self.unknowns2.append(ebrw_readstr.int_u32())
		self.unknowns2.append(ebrw_readstr.int_u32())
		self.unknowns2.append(ebrw_readstr.int_u32())
		self.unknowns2.append(ebrw_readstr.int_u32())
		self.unknowns2.append(ebrw_readstr.int_u32())
		self.unknowns2.append(ebrw_readstr.int_u32())

class mixcraft_audio_track:
	def __init__(self):
		pass

	def read(self, ebrw_readstr, riffpart):
		self.unknowns = []
		self.unknowns.append(ebrw_readstr.double())
		self.unknowns.append(ebrw_readstr.string(256))
		self.unknowns.append(ebrw_readstr.string(256))
		self.unknowns.append(ebrw_readstr.double())
		self.unknowns.append(ebrw_readstr.double())
		self.unknowns.append(ebrw_readstr.double())
		self.unknowns.append(ebrw_readstr.int_u8())
		self.unknowns.append(ebrw_readstr.int_u8())
		self.unknowns.append(ebrw_readstr.int_u8())
		self.unknowns.append(ebrw_readstr.int_u8())
		self.unknowns.append(ebrw_readstr.int_u32())
		self.unknowns.append(ebrw_readstr.int_u32())

		self.unknowns.append(ebrw_readstr.rest())
		print(  self.unknowns  )

class mixcraft_file:
	def __init__(self):
		self.tracks = []

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)
		main_chunk = riff_chunks.riff_chunk()
		main_chunk.read(ebrw_readstr, 0)

		for riffpart in main_chunk.iter_reader(ebrw_readstr):
			print(riffpart.id)
			if riffpart.id==b'TrkA':
				part_obj = mixcraft_audio_track()
				part_obj.read(ebrw_readstr, riffpart)
			if riffpart.id==b'ClpA':
				part_obj = mixcraft_audio_clip()
				part_obj.read(ebrw_readstr, riffpart)

		return True