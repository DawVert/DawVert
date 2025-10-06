# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from external.easybinrw import easybinrw
import zlib
import logging

class evo_midi_event:
	def __init__(self, ebrw_readstr):
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.unk1 = ebrw_readstr.int_u8()
		self.pos = ebrw_readstr.int_u16_b()
		self.type, self.chan = ebrw_readstr.int_u4_2()
		self.data = []
		if self.type == 9: #note
			self.data.append(ebrw_readstr.int_u8())
			self.data.append(ebrw_readstr.int_u8())
			self.data.append(ebrw_readstr.int_u16_b())
		elif self.type == 10: #aftertouch
			self.data.append(ebrw_readstr.int_u8())
			self.data.append(ebrw_readstr.int_u8())
		elif self.type == 11: #control
			self.data.append(ebrw_readstr.int_u8())
			self.data.append(ebrw_readstr.int_u8())
		elif self.type == 12: #unknown
			self.data.append(ebrw_readstr.int_u8())
		elif self.type == 13: #pressure
			self.data.append(ebrw_readstr.int_u8())
		elif self.type == 14: #pitch
			self.data.append(ebrw_readstr.int_u8())
			self.data.append(ebrw_readstr.int_u8())
		elif self.type == 15: #end
			pass
		else:
			print('unknown event', self.type)
			exit()

class evo_midi_track:
	def __init__(self, ebrw_readstr):
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.name = ebrw_readstr.string(21, encoding='windows-1252')
		self.patch = ebrw_readstr.int_s16()
		self.bank = ebrw_readstr.int_s8()
		self.bank_type = ebrw_readstr.int_s8()
		self.channel = ebrw_readstr.int_s16()
		ebrw_readstr.skip(2)
		self.volume = ebrw_readstr.int_s16()
		self.pan = ebrw_readstr.int_s16()
		self.reverb = ebrw_readstr.int_s16()
		self.chorus = ebrw_readstr.int_s16()
		self.velocity = ebrw_readstr.int_s16()
		self.transpose = ebrw_readstr.int_s16()
		self.time = ebrw_readstr.int_s16()
		self.mute = ebrw_readstr.int_s16()
		self.solo = ebrw_readstr.int_s16()
		self.armed = ebrw_readstr.int_s16()

		self.unkdata = ebrw_readstr.raw(6)
		ebrw_readstr.skip(500)
		self.unkdata2 = ebrw_readstr.raw(10)

class evo_midi_clip:
	def __init__(self, ebrw_readstr):
		self.name = ''
		self.linked = -1
		self.patch = -1
		self.bank = -1
		self.bank_type = -1
		self.channel = -1
		self.volume = -1
		self.pan = -1
		self.reverb = -1
		self.chorus = -1
		self.velocity = -1
		self.transpose = -1
		self.time = -1
		self.position = 0
		self.duration = 0
		self.events_size = 0
		self.tracknum = 0
		self.events = []
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.name = ebrw_readstr.string(21, encoding='windows-1252')
		unknowns = []
		self.linked = ebrw_readstr.int_s16()
		self.patch = ebrw_readstr.int_s16()
		self.bank = ebrw_readstr.int_s8()
		self.bank_type = ebrw_readstr.int_s8()
		self.channel = ebrw_readstr.int_s16()
		ebrw_readstr.skip(2)
		self.volume = ebrw_readstr.int_s16()
		self.pan = ebrw_readstr.int_s16()
		self.reverb = ebrw_readstr.int_s16()
		self.chorus = ebrw_readstr.int_s16()
		self.velocity = ebrw_readstr.int_s16()
		self.transpose = ebrw_readstr.int_s16()
		self.time = ebrw_readstr.int_s16()
		unknowns.append(ebrw_readstr.int_s16())
		unknowns.append(ebrw_readstr.int_u32())
		unknowns.append(ebrw_readstr.int_s16())
		self.position = ebrw_readstr.int_u32()
		self.duration = ebrw_readstr.int_u32()
		self.events_size = ebrw_readstr.int_s32()
		self.tracknum = ebrw_readstr.int_s16()
		unknowns.append(ebrw_readstr.raw(10).hex())

class evo_midi_song:
	def __init__(self):
		self.tracks = []
		self.clips = []

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)
		ebrw_readstr.magic_check(b'sng2')

		ebrw_readstr.skip(3)

		num_tracks = ebrw_readstr.int_u16()
		num_clips = ebrw_readstr.int_u16()
		num_unk = ebrw_readstr.int_u8()

		ebrw_readstr.seek(0x400)
		self.songinfo = ebrw_readstr.string_t(encoding='windows-1252')

		assert num_unk>1
		ebrw_readstr.skip((num_unk*6)-3)

		self.unk1 = ebrw_readstr.int_u16()

		self.unklist2 = ebrw_readstr.list_int_u16(num_tracks)
		self.unklist3 = ebrw_readstr.list_int_u16(num_clips)


		for x in range(num_tracks):
			self.tracks.append( evo_midi_track(ebrw_readstr) )

		for x in range(num_clips):
			self.clips.append( evo_midi_clip(ebrw_readstr) )

		for clip in self.clips:
			if clip.linked == -1:
				ebrw_readstr.isolate_size(clip.events_size)
				while ebrw_readstr.remaining(): clip.events.append(evo_midi_event(ebrw_readstr))
				ebrw_readstr.isolate_end()

		return True