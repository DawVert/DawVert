# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import struct
import zlib
from external.easybinrw import easybinrw
from external.easybinrw import chunked

chunk_size_data = chunked.chunk_part_size()
chunk_size_data.name_size = 2
chunk_size_data.name_numeric = True

def printchunk(num, chunk_obj, ebrw_readstr, view):

	if view:
		if chunk_obj.size==1: outview = ebrw_readstr.int_s8()
		elif chunk_obj.size==2: outview = ebrw_readstr.int_u16()
		elif chunk_obj.size==4: outview = ebrw_readstr.int_u32()
		else: outview = ebrw_readstr.raw(min(chunk_obj.size, 28))
	else:
		outview = ''

	print('    '*(num) + ('--> ' if (num>0) else '') + str(chunk_obj.id), chunk_obj.size if view else '', outview)

class dms_note:
	def __init__(self):
		self.pos = 0
		self.dur = 0
		self.key = 0
		self.vel = 0

	def read(self, ebrw_readstr):
		for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, chunk_size_data):
			if chunk_obj.id == 1001: self.pos = ebrw_readstr.int_u32()
			if chunk_obj.id == 2001: self.key = ebrw_readstr.int_u8()
			if chunk_obj.id == 2002: self.vel = ebrw_readstr.int_u8()
			if chunk_obj.id == 2003: self.dur = ebrw_readstr.int_u32()

class dms_ctrl:
	def __init__(self):
		self.pos = 0
		self.cc = 0
		self.data1 = 0
		self.data2 = 0

	def read(self, ebrw_readstr):
		for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, chunk_size_data):
			if chunk_obj.id == 1001: self.pos = ebrw_readstr.int_u32()
			if chunk_obj.id == 2001: self.cc = ebrw_readstr.int_u16()
			if chunk_obj.id == 2002: self.data1 = ebrw_readstr.raw(chunk_obj.size)
			if chunk_obj.id == 2003: self.data2 = ebrw_readstr.raw(chunk_obj.size)

class dms_text:
	def __init__(self):
		self.pos = 0
		self.text = ''

	def read(self, ebrw_readstr):
		for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, chunk_size_data):
			if chunk_obj.id == 1001: self.pos = ebrw_readstr.int_u32()
			if chunk_obj.id == 2001: self.text = ebrw_readstr.string(chunk_obj.size, encoding='shiftjis')

class dms_sysex:
	def __init__(self):
		self.pos = 0
		self.text = ''
		self.sysex = b''

	def read(self, ebrw_readstr):
		for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, chunk_size_data):
			if chunk_obj.id == 1001: self.pos = ebrw_readstr.int_u32()
			if chunk_obj.id == 2001: self.text = ebrw_readstr.string(chunk_obj.size, encoding='shiftjis')
			if chunk_obj.id == 2002: self.sysex = ebrw_readstr.raw(chunk_obj.size)

class dms_expression:
	def __init__(self):
		self.pos = 0
		self.var = ''
		self.value = ''

	def read(self, ebrw_readstr):
		for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, chunk_size_data):
			if chunk_obj.id == 1001: self.pos = ebrw_readstr.int_u32()
			if chunk_obj.id == 2001: self.var = ebrw_readstr.string(chunk_obj.size, encoding='shiftjis')
			if chunk_obj.id == 2002: self.value = ebrw_readstr.string(chunk_obj.size, encoding='shiftjis')

class dms_measurelink:
	def __init__(self):
		self.pos = 0
		self.measure_dest = 1
		self.key_transpose = 0

	def read(self, ebrw_readstr):
		for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, chunk_size_data):
			if chunk_obj.id == 1001: self.pos = ebrw_readstr.int_u32()
			if chunk_obj.id == 2001: self.measure_dest = ebrw_readstr.int_u32()
			if chunk_obj.id == 2002: self.key_transpose = ebrw_readstr.int_s32()

class dms_timesig:
	def __init__(self):
		self.pos = 0
		self.num = 4
		self.nenom = 4

	def read(self, ebrw_readstr):
		for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, chunk_size_data):
			if chunk_obj.id == 1001: self.pos = ebrw_readstr.int_u32()
			if chunk_obj.id == 2001: self.num = ebrw_readstr.int_u8()
			if chunk_obj.id == 2002: self.nenom = ebrw_readstr.int_u8()

class dms_keysig:
	def __init__(self):
		self.pos = 0
		self.key = 0

	def read(self, ebrw_readstr):
		for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, chunk_size_data):
			if chunk_obj.id == 1001: self.pos = ebrw_readstr.int_u32()
			if chunk_obj.id == 2001: self.key = ebrw_readstr.int_u8()

class dms_keyscale:
	def __init__(self):
		self.pos = 0
		self.key = 0
		self.chord = 0
		self.custom = None
		self.name = None

	def read(self, ebrw_readstr):
		for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, chunk_size_data):
			if chunk_obj.id == 1001: self.pos = ebrw_readstr.int_u32()
			if chunk_obj.id == 2001: self.key = ebrw_readstr.int_u8()
			if chunk_obj.id == 2002: self.chord = ebrw_readstr.int_u8()
			if chunk_obj.id == 2003: self.custom = list(ebrw_readstr.list_int_u8(12))
			if chunk_obj.id == 2004: self.name = ebrw_readstr.string(chunk_obj.size, encoding='shiftjis')

class dms_program_change:
	def __init__(self):
		self.pos = 0
		self.patch = 0
		self.unk1 = 0
		self.unk2 = 0
		self.unk3 = 0
		self.unk4 = 0
		self.unk5 = 0

	def read(self, ebrw_readstr):
		for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, chunk_size_data):
			if chunk_obj.id == 1001: self.pos = ebrw_readstr.int_u32()
			if chunk_obj.id == 2001: self.unk1 = ebrw_readstr.int_s8()
			if chunk_obj.id == 2002: self.unk2 = ebrw_readstr.int_s8()
			if chunk_obj.id == 2003: self.patch = ebrw_readstr.int_u8()
			if chunk_obj.id == 2004: self.unk3 = ebrw_readstr.raw(chunk_obj.size)
			if chunk_obj.id == 2005: self.unk4 = ebrw_readstr.int_u8()
			if chunk_obj.id == 2006: self.unk5 = ebrw_readstr.int_s16()

class dms_chord:
	def __init__(self):
		self.pos = 0
		self.key = 0
		self.chord = 0
		self.custom = None
		self.name = None

	def read(self, ebrw_readstr):
		for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, chunk_size_data):
			if chunk_obj.id == 1001: self.pos = ebrw_readstr.int_u32()
			if chunk_obj.id == 2001: self.key = ebrw_readstr.int_u8()
			if chunk_obj.id == 2002: self.chord = ebrw_readstr.int_u32()
			if chunk_obj.id == 2003: self.custom = ebrw_readstr.raw(chunk_obj.size)
			if chunk_obj.id == 2004: self.name = ebrw_readstr.string(chunk_obj.size, encoding='shiftjis')

class dms_tempo:
	def __init__(self):
		self.pos = 0
		self.val = 120

	def read(self, ebrw_readstr):
		for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, chunk_size_data):
			if chunk_obj.id == 1001: self.pos = ebrw_readstr.int_u32()
			if chunk_obj.id == 2001: 
				for inchunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, chunk_size_data):
					self.val = ebrw_readstr.float()

class dms_track:
	def __init__(self, chunk_obj, ebrw_readstr):
		self.notes = []
		self.ctrls = []
		self.sysex = []
		self.texts = []
		self.markers = []
		self.lyrics = []
		self.cuepoints = []
		self.expressions = []
		self.measurelinks = []
		self.programchanges = []
		self.timesigs = []
		self.keysigs = []
		self.keyscales = []
		self.chords = []
		self.tempos = []

		self.name = ''
		self.channel = 0
		self.tick_adjust = 0
		self.range_low = 0
		self.range_high = 0
		self.transpose = 0
		self.out_port = 0
		self.is_rhythm = 0
		self.rhythm_name = ''
		self.color = 0
		self.volume = 0
		self.gate = 480
		self.gate_adjust = 100
		self.tick_adjust_measure = 0
		self.enabled = 1

		for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, chunk_size_data):
			chunkid = chunk_obj.id

			if chunkid == 1000: self.out_port = ebrw_readstr.int_u16()
			elif chunkid == 1001: self.channel = ebrw_readstr.int_u8()
			elif chunkid == 1002: self.name = ebrw_readstr.string(chunk_obj.size, encoding="shift-jis")
			elif chunkid == 1004: self.is_rhythm = ebrw_readstr.int_u8()
			elif chunkid == 1006: self.volume = ebrw_readstr.int_u8()
			elif chunkid == 1007: self.gate = ebrw_readstr.int_s32()
			elif chunkid == 1009: self.rhythm_name = ebrw_readstr.string(chunk_obj.size, encoding="shift-jis")
			elif chunkid == 1012: self.tick_adjust = ebrw_readstr.int_u32()
			elif chunkid == 1015: self.enabled = ebrw_readstr.int_s32()
			elif chunkid == 1016: self.gate_adjust = ebrw_readstr.int_s32()
			elif chunkid == 1017: self.transpose = ebrw_readstr.int_s32()
			elif chunkid == 1018: self.color = ebrw_readstr.int_u8()
			elif chunkid == 1019: self.tick_adjust_measure = ebrw_readstr.int_u32()
			elif chunkid == 1021: self.range_low = ebrw_readstr.int_u8()
			elif chunkid == 1022: self.range_high = ebrw_readstr.int_u8()

			elif chunkid == 2001:
				note_obj = dms_note()
				note_obj.read(ebrw_readstr)
				self.notes.append(note_obj)

			elif chunkid == 2003:
				ctrl_obj = dms_ctrl()
				ctrl_obj.read(ebrw_readstr)
				self.ctrls.append(ctrl_obj)

			elif chunkid == 2004:
				sysex_obj = dms_sysex()
				sysex_obj.read(ebrw_readstr)
				self.sysex.append(sysex_obj)

			elif chunkid == 2005:
				text_obj = dms_text()
				text_obj.read(ebrw_readstr)
				self.texts.append(text_obj)

			elif chunkid == 2011:
				text_obj = dms_text()
				text_obj.read(ebrw_readstr)
				self.lyrics.append(text_obj)

			elif chunkid == 2017:
				text_obj = dms_text()
				text_obj.read(ebrw_readstr)
				self.markers.append(text_obj)

			elif chunkid == 2012:
				text_obj = dms_text()
				text_obj.read(ebrw_readstr)
				self.cuepoints.append(text_obj)

			elif chunkid == 2007:
				expression_obj = dms_expression()
				expression_obj.read(ebrw_readstr)
				self.expressions.append(expression_obj)

			elif chunkid == 2014:
				measurelink_obj = dms_measurelink()
				measurelink_obj.read(ebrw_readstr)
				self.measurelinks.append(measurelink_obj)

			elif chunkid == 2015:
				timesig_obj = dms_timesig()
				timesig_obj.read(ebrw_readstr)
				self.timesigs.append(timesig_obj)

			elif chunkid == 2016:
				keysig_obj = dms_keysig()
				keysig_obj.read(ebrw_readstr)
				self.keysigs.append(keysig_obj)

			elif chunkid == 2018:
				keyscale_obj = dms_keyscale()
				keyscale_obj.read(ebrw_readstr)
				self.keyscales.append(keyscale_obj)

			elif chunkid == 2002:
				program_obj = dms_program_change()
				program_obj.read(ebrw_readstr)
				self.programchanges.append(program_obj)

			elif chunkid == 2019:
				chord_obj = dms_chord()
				chord_obj.read(ebrw_readstr)
				self.chords.append(chord_obj)

			elif chunkid == 2008:
				tempo_obj = dms_tempo()
				tempo_obj.read(ebrw_readstr)
				self.tempos.append(tempo_obj)

			#elif chunkid in [2017, 2009, 1010, 2008]:
			#	printchunk(1, chunkid, chunk_obj, ebrw_readstr, False)
			#	for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, chunk_size_data):
			#		chunk_obj.id = int.from_bytes(chunk_obj.id, 'little')
			#		printchunk(2, chunk_obj.id, chunk_obj, ebrw_readstr, True)
			#else:
			#	printchunk(1, chunk_obj, ebrw_readstr, True)

class dms_project:
	def __init__(self):
		self.tracks = []
		self.ppq = 96
		self.name = ''
		self.copyright = ''

	def load_from_file(self, input_file):
		pre_ebrw_readstr = easybinrw.binread()
		pre_ebrw_readstr.load_file(input_file)
		pre_ebrw_readstr.magic_check(b'PortalSequenceData')
		pre_ebrw_readstr.skip(4)

		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_data(zlib.decompress(pre_ebrw_readstr.rest(), zlib.MAX_WBITS|32))

		for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, chunk_size_data):
			if chunk_obj.id == 1003: self.tracks.append(dms_track(chunk_obj, ebrw_readstr))
			elif chunk_obj.id == 1000: self.name = ebrw_readstr.string(chunk_obj.size, encoding='shiftjis')
			elif chunk_obj.id == 1001: self.copyright = ebrw_readstr.string(chunk_obj.size, encoding='shiftjis')
			elif chunk_obj.id == 1002: self.ppq = ebrw_readstr.int_u16()
			#elif chunk_obj.id == 1008: 
			#	printchunk(0, chunk_obj, ebrw_readstr, False)
			#	for chunk_obj in chunk_obj.iter(0):
			#		printchunk(1, chunk_obj, ebrw_readstr, True)
			#elif chunk_obj.id == 1017: 
			#	printchunk(0, chunk_obj, ebrw_readstr, False)
			#	for chunk_obj in chunk_obj.iter(0):
			#		printchunk(1, chunk_obj, ebrw_readstr, True)
			#else:
			#	printchunk(0, chunk_obj, ebrw_readstr, True)
		return True