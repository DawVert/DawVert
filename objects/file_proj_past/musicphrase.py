# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from external.easybinrw import easybinrw

VERBOSE = False

class musicphrase_control:
	def __init__(self, ebrw_readstr):
		self.pos = ebrw_readstr.int_u32()
		self.type, self.chan = ebrw_readstr.int_u4_2()
		self.data1 = ebrw_readstr.int_u8()
		self.data2 = ebrw_readstr.int_u8()
		if VERBOSE: print('CTRL -', self.pos, self.type, self.chan, self.data1, self.data2)

class musicphrase_note:
	def __init__(self, ebrw_readstr):
		self.pos = ebrw_readstr.int_u16()
		self.unk2 = ebrw_readstr.int_u16()
		self.end = ebrw_readstr.int_u16()
		self.unk3 = ebrw_readstr.int_u16()
		self.note = ebrw_readstr.int_u8()
		self.vel = ebrw_readstr.int_u8()
		self.vel_off = ebrw_readstr.int_u8()
		if VERBOSE: print('NOTE -', self.pos, self.unk2, self.end, self.unk3, self.note, self.vel, self.vel_off)

class musicphrase_unkp:
	def __init__(self, ebrw_readstr):
		self.pos = ebrw_readstr.int_u32()
		self.end = ebrw_readstr.int_u32()
		self.data = ebrw_readstr.list_int_u8(3)
		#if VERBOSE: print('unkp -', self.pos, self.end, self.data)

class musicphrase_segment:
	def __init__(self, ebrw_readstr):
		if VERBOSE: print('--PART--')
		numevents = ebrw_readstr.int_u32()
		self.notes = [musicphrase_note(ebrw_readstr) for x in range(numevents)]
		numctrls = ebrw_readstr.int_u32()
		self.ctrls = [musicphrase_control(ebrw_readstr) for x in range(numctrls)]
		self.size = ebrw_readstr.int_u32()
		self.name = ebrw_readstr.string(ebrw_readstr.int_u8())
		self.color = ebrw_readstr.list_int_u8(4)
		self.unk2 = ebrw_readstr.int_u32()
		self.start = ebrw_readstr.int_u32()
		if VERBOSE: print('PART PROP - ', self.name, self.size, self.unk2, self.start)

class musicphrase_track:
	def __init__(self, ebrw_readstr):
		self.name = ebrw_readstr.string(ebrw_readstr.int_u8())
		self.color = ebrw_readstr.list_int_u8(4)
		numpoints = ebrw_readstr.int_u32()
		numclips = ebrw_readstr.int_u32()
		if VERBOSE: print('-------TRACK---------------', self.name, self.color, numpoints, numclips)

		self.clips = []
		for _ in range(numclips):
			clip = musicphrase_segment(ebrw_readstr)
			self.clips.append(clip)

		ebrw_readstr.skip(1)
		ebrw_readstr.skip(5)
		self.channel = ebrw_readstr.int_u8()
		ebrw_readstr.skip(12)
		self.unk1 = ebrw_readstr.int_u8()
		self.unk2 = ebrw_readstr.int_u8()
		self.unk3 = ebrw_readstr.int_u8()
		self.unk4 = ebrw_readstr.int_u8()
		self.program = ebrw_readstr.int_s8()
		self.vol = ebrw_readstr.int_s8()
		self.pan = ebrw_readstr.int_s8()
		self.unk5 = ebrw_readstr.int_s32()
		self.unk6 = ebrw_readstr.int_s32()
		self.unk7 = ebrw_readstr.int_s32()
		self.unk8 = ebrw_readstr.int_s32()
		ebrw_readstr.skip(6)
		self.groove = ebrw_readstr.string(ebrw_readstr.int_u8())

class musicphrase_song:
	def __init__(self):
		pass

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)

		ebrw_readstr.magic_check(b'\x17musicphrase file format')
		assert ebrw_readstr.int_u32()==100
		self.name = ebrw_readstr.string(ebrw_readstr.int_u8())
		self.copyright = ebrw_readstr.string(ebrw_readstr.int_u8())
		self.author = ebrw_readstr.string(ebrw_readstr.int_u8())
		self.comment = ebrw_readstr.string(ebrw_readstr.int_u8())
		self.unk1 = ebrw_readstr.int_u32()
		self.unk2 = ebrw_readstr.int_u32()
		self.unk3 = ebrw_readstr.int_u32()
		self.unk4 = ebrw_readstr.int_u32()
		self.unk5 = ebrw_readstr.int_u32()
		numtracks = ebrw_readstr.int_u32()
		self.tracks = []

		for x in range(numtracks):
			track = musicphrase_track(ebrw_readstr)
			self.tracks.append(track)

		return True