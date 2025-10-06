# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.file_proj_past._cakewalk_wrk import events
from objects.file_proj_past._cakewalk_wrk import chunks

class cakewalk_effect:
	def __init__(self, ebrw_readstr):
		self.id = None
		self.name = ''
		self.unk1 = 1
		self.unk2 = 1
		self.data = b''
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.id = ebrw_readstr.raw(16)
		self.name = ebrw_readstr.string(128)
		self.unk1 = ebrw_readstr.int_u32()
		self.unk2 = ebrw_readstr.int_u32()
		datasize = ebrw_readstr.int_u32()
		self.data = ebrw_readstr.raw(datasize)

	#def write(self, byw_stream):
	#	byw_stream.raw_l(self.id, 16)
	#	byw_stream.string(self.name, 128)
	#	byw_stream.uint32(self.unk1)
	#	byw_stream.uint32(self.unk2)
	#	byw_stream.uint32(len(self.data))
	#	byw_stream.raw(self.data)




class chunk_gen2_track_header:
	def __init__(self, ebrw_readstr):
		self.trackno = 0
		self.name = ''
		self.bank = -1
		self.patch = 0
		self.vol = 0
		self.pan = 0
		self.key = 0
		self.vel = 0
		self.port = -1
		self.channel = 0
		self.muted = True
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.trackno = ebrw_readstr.int_u16()
		self.name = ebrw_readstr.raw_i8()
		self.bank = ebrw_readstr.int_s16()
		self.patch = ebrw_readstr.int_s16()
		self.vol = ebrw_readstr.int_u16()
		self.pan = ebrw_readstr.int_s16()
		self.key = ebrw_readstr.int_s8()
		self.vel = ebrw_readstr.int_u8()
		ebrw_readstr.skip(7) # b'\x00\x00\x00\x00\x00\x81\x00'
		self.port = ebrw_readstr.int_s8()
		self.channel = ebrw_readstr.int_u8()
		self.muted = ebrw_readstr.int_u8() != 0

	#def write(self, byw_stream):
	#	ebrw_readstr.int_u16(self.trackno) 
	#	byw_stream.c_string__int8(self.name)
	#	ebrw_readstr.int_s16(self.bank) 
	#	ebrw_readstr.int_u16(self.patch) 
	#	ebrw_readstr.int_u16(self.vol) 
	#	ebrw_readstr.int_s16(self.pan) 
	#	ebrw_readstr.int_s8(self.key) 
	#	ebrw_readstr.int_u8(self.vel) 
	#	ebrw_readstr.raw(b'\x00\x00\x00\x00\x00\x81\x00')
	#	ebrw_readstr.int_s8(self.port) 
	#	ebrw_readstr.int_u8(self.channel) 
	#	ebrw_readstr.int_u8(self.muted) 

class chunk_gen2_track_events:
	def __init__(self, ebrw_readstr):
		self.trackno = 0
		self.events = []
		self.name = b''
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.trackno = ebrw_readstr.int_u16()
		self.name = ebrw_readstr.raw_i8()
		numevents = ebrw_readstr.int_u32()
		for _ in range(numevents):
			event = events.cakewalk_event()
			event.read_new(ebrw_readstr)
			self.events.append(event)

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.trackno)
	#	byw_stream.c_string__int8(self.name)
	#	byw_stream.uint32(len(self.events))
	#	for x in self.events: x.write_new(byw_stream)

class chunk_gen2_track_effects:
	def __init__(self, ebrw_readstr):
		self.trackno = 0
		self.effects = []
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.trackno = ebrw_readstr.int_u32()
		num_fx = ebrw_readstr.int_u32()
		for _ in range(num_fx): cakewalk_effect(ebrw_readstr)

	#def write(self, byw_stream):
	#	byw_stream.uint32(self.trackno)
	#	byw_stream.uint32(len(self.effects))
	#	for x in self.effects: x.write(byw_stream)

class chunk_gen2_track_segment:
	def __init__(self, ebrw_readstr):
		self.trackno = 0
		self.offset = 0
		self.events = []
		self.name = b''
		self.id = 0
		self.is_nonlinked = 1
		self.color = None
		self.other3 = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.trackno = ebrw_readstr.int_u16()
		self.offset = ebrw_readstr.int_u32()
		self.id = ebrw_readstr.int_u32()
		self.is_nonlinked = ebrw_readstr.int_u32()
		if self.is_nonlinked:
			self.name = ebrw_readstr.raw_i8()
			self.color = ebrw_readstr.list_int_u8(3)
			self.other3 = ebrw_readstr.raw(17)
			numevents = ebrw_readstr.int_u32()
			for _ in range(numevents):
				event = events.cakewalk_event()
				event.read_new(ebrw_readstr)
				self.events.append(event)

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.trackno)
	#	byw_stream.uint32(self.offset)
	#	byw_stream.uint32(self.id)
	#	byw_stream.uint32(self.is_nonlinked)
	#	if self.is_nonlinked:
	#		byw_stream.c_string__int8(self.name)
	#		byw_stream.l_uint8(self.color)
	#		byw_stream.raw_l(self.other2, 17)
	#		byw_stream.uint32(len(self.events))
	#		for x in self.events: x.write_new(byw_stream)

class chunk_gen2_audiosource:
	def __init__(self, ebrw_readstr):
		self.data = []
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.data = ebrw_readstr.list_int_u32(ebrw_readstr.remaining()//4)

	#def write(self, byw_stream):
	#	ebrw_readstr.list_int_u32(self.data)

class chunk_gen2_midichans:
	def __init__(self, ebrw_readstr):
		self.data = []
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.data = ebrw_readstr.list_int_u32(ebrw_readstr.remaining()//4)

	#def write(self, byw_stream):
	#	ebrw_readstr.list_int_u32(self.data)

#class chunk_gen2_consoleparams:
#	def __init__(self, ebrw_readstr):
#		self.data = []
#		if ebrw_readstr: self.read(ebrw_readstr)
#
#	def read(self, ebrw_readstr):
#		numparams = ebrw_readstr.int_u32()
#		print(numparams)
#		for x in range(numparams):
#			print(ebrw_readstr.raw(8).hex())
#
#		print(ebrw_readstr.rest())

	#def write(self, byw_stream):
	#	ebrw_readstr.list_int_u32(self.data)

class chunk_gen2_audiostretch_part:
	def __init__(self, ebrw_readstr):
		self.data = []
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.unk1 = ebrw_readstr.int_u32()
		self.looping = ebrw_readstr.int_u32()
		self.stretch_enabled = ebrw_readstr.int_u32()
		self.followpitch = ebrw_readstr.int_u32()
		self.unk2 = ebrw_readstr.int_u32()
		self.unk3 = ebrw_readstr.int_u32()
		self.beats = ebrw_readstr.int_u32()
		self.key = ebrw_readstr.int_u32()
		self.tempo = ebrw_readstr.double()
		self.pitch = ebrw_readstr.double()
		self.unk4 = ebrw_readstr.int_u32()
		self.unk5 = ebrw_readstr.int_u32()

		num_something = ebrw_readstr.int_u32()
		self.unk6 = []
		for x in range(num_something): 
			self.unk6.append( [ebrw_readstr.int_u32(), ebrw_readstr.float()] )

		try:
			num_something = ebrw_readstr.int_u32()
			self.unk7 = []
			for x in range(num_something): 
				self.unk7.append([ 
					ebrw_readstr.int_u32(),
					ebrw_readstr.int_u32(),
					ebrw_readstr.int_u32(),
					ebrw_readstr.int_u32(),
					ebrw_readstr.int_u16(),
					ebrw_readstr.int_u16(),
					ebrw_readstr.int_u16(),
					ebrw_readstr.int_u16(),
					])
				ebrw_readstr.skip(8)
		except:
			pass

class chunk_gen2_audiostretch:
	def __init__(self, ebrw_readstr):
		self.data = []
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		while ebrw_readstr.remaining():
			self.data.append(chunk_gen2_audiostretch_part(ebrw_readstr))

class chunk_gen2_audiosize_part:
	def __init__(self, ebrw_readstr):
		self.data = []
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.id = ebrw_readstr.raw(16).hex()
		self.unk1 = ebrw_readstr.int_u32()
		self.unk2 = ebrw_readstr.int_u32()
		self.sec_start = ebrw_readstr.int_u32()
		self.sec_end = ebrw_readstr.int_u32()
		self.unk5 = ebrw_readstr.int_u32()
		self.unk6 = ebrw_readstr.int_u32()
		self.unk7 = ebrw_readstr.int_u32()
		self.unk8 = ebrw_readstr.int_u32()

class chunk_gen2_audiosize:
	def __init__(self, ebrw_readstr):
		self.data = []
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		while ebrw_readstr.remaining():
			self.data.append(chunk_gen2_audiosize_part(ebrw_readstr))
