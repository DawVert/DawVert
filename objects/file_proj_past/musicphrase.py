# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader

VERBOSE = False

class musicphrase_control:
	def __init__(self, byr_stream):
		self.pos = byr_stream.uint32()
		self.type, self.chan = byr_stream.bytesplit()
		self.data1 = byr_stream.uint8()
		self.data2 = byr_stream.uint8()
		if VERBOSE: print('CTRL -', self.pos, self.type, self.chan, self.data1, self.data2)

class musicphrase_note:
	def __init__(self, byr_stream):
		self.pos = byr_stream.uint16()
		self.unk2 = byr_stream.uint16()
		self.end = byr_stream.uint16()
		self.unk3 = byr_stream.uint16()
		self.note = byr_stream.uint8()
		self.vel = byr_stream.uint8()
		self.vel_off = byr_stream.uint8()
		if VERBOSE: print('NOTE -', self.pos, self.unk2, self.end, self.unk3, self.note, self.vel, self.vel_off)

class musicphrase_unkp:
	def __init__(self, byr_stream):
		self.pos = byr_stream.uint32()
		self.end = byr_stream.uint32()
		self.data = byr_stream.l_uint8(3)
		#if VERBOSE: print('unkp -', self.pos, self.end, self.data)

class musicphrase_segment:
	def __init__(self, byr_stream):
		if VERBOSE: print('--PART--')
		numevents = byr_stream.uint32()
		self.notes = [musicphrase_note(byr_stream) for x in range(numevents)]
		numctrls = byr_stream.uint32()
		self.ctrls = [musicphrase_control(byr_stream) for x in range(numctrls)]
		self.size = byr_stream.uint32()
		self.name = byr_stream.string(byr_stream.uint8())
		self.color = byr_stream.l_uint8(4)
		self.unk2 = byr_stream.uint32()
		self.start = byr_stream.uint32()
		if VERBOSE: print('PART PROP - ', self.name, self.size, self.unk2, self.start)

class musicphrase_track:
	def __init__(self, byr_stream):
		self.name = byr_stream.string(byr_stream.uint8())
		self.color = byr_stream.l_uint8(4)
		numpoints = byr_stream.uint32()
		numclips = byr_stream.uint32()
		if VERBOSE: print('-------TRACK---------------', self.name, self.color, numpoints, numclips)

		self.clips = []
		for _ in range(numclips):
			clip = musicphrase_segment(byr_stream)
			self.clips.append(clip)

		byr_stream.skip(1)
		byr_stream.skip(5)
		self.channel = byr_stream.uint8()
		byr_stream.skip(12)
		self.unk1 = byr_stream.uint8()
		self.unk2 = byr_stream.uint8()
		self.unk3 = byr_stream.uint8()
		self.unk4 = byr_stream.uint8()
		self.program = byr_stream.int8()
		self.vol = byr_stream.int8()
		self.pan = byr_stream.int8()
		self.unk5 = byr_stream.int32()
		self.unk6 = byr_stream.int32()
		self.unk7 = byr_stream.int32()
		self.unk8 = byr_stream.int32()
		byr_stream.skip(6)
		self.groove = byr_stream.string(byr_stream.uint8())

class musicphrase_song:
	def __init__(self):
		pass

	def load_from_file(self, input_file):
		byr_stream = bytereader.bytereader()
		byr_stream.load_file(input_file)
		byr_stream.magic_check(b'\x17musicphrase file format')
		assert byr_stream.uint32()==100
		self.name = byr_stream.string(byr_stream.uint8())
		self.copyright = byr_stream.string(byr_stream.uint8())
		self.author = byr_stream.string(byr_stream.uint8())
		self.comment = byr_stream.string(byr_stream.uint8())
		self.unk1 = byr_stream.uint32()
		self.unk2 = byr_stream.uint32()
		self.unk3 = byr_stream.uint32()
		self.unk4 = byr_stream.uint32()
		self.unk5 = byr_stream.uint32()
		numtracks = byr_stream.uint32()
		self.tracks = []

		for x in range(numtracks):
			track = musicphrase_track(byr_stream)
			self.tracks.append(track)

		return True

apeinst_obj = musicphrase_song()
apeinst_obj.load_from_file("C:\\Users\\Topaz\\Desktop\\testy.mps")
