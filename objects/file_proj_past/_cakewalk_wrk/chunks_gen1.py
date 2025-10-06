# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.file_proj_past._cakewalk_wrk import events

class cakewalk_chunk_globalsettings:
	def __init__(self, ebrw_readstr):
		self.Now = 1344
		self.From = 0
		self.Thru = 0
		self.KeySig = 0
		self.Clock = 4
		self.AutoSave = 0
		self.PlayDelay = 0
		self.ZeroCtrls = True
		self.SendSPP = False
		self.SendCont = True
		self.PatchSearch = True
		self.AutoStop = False
		self.StopTime = 0
		self.AutoRewind = False
		self.RewindTime = 0
		self.MetroPlay = False
		self.MetroRecord = True
		self.MetroAccent = True
		self.CountIn = 0
		self.ThruOn = True
		self.AutoRestart = False
		self.CurTempoOfs = 1
		self.TempoOfs1 = 32
		self.TempoOfs2 = 64
		self.TempoOfs3 = 128
		self.PunchEnabled = False
		self.PunchInTime = 0
		self.PunchOutTime = 0
		self.EndAllTime = 576
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.Now = ebrw_readstr.int_u32()
		self.From = ebrw_readstr.int_u32()
		self.Thru = ebrw_readstr.int_u32()
		self.KeySig = ebrw_readstr.int_u8()
		self.Clock = ebrw_readstr.int_u8()
		self.AutoSave = ebrw_readstr.int_u8()
		self.PlayDelay = ebrw_readstr.int_u8()
		ebrw_readstr.skip(1)
		self.ZeroCtrls = bool(ebrw_readstr.int_u8())
		self.SendSPP = bool(ebrw_readstr.int_u8())
		self.SendCont = bool(ebrw_readstr.int_u8())
		self.PatchSearch = bool(ebrw_readstr.int_u8())
		self.AutoStop = bool(ebrw_readstr.int_u8())
		self.StopTime = ebrw_readstr.int_u32()
		self.AutoRewind = bool(ebrw_readstr.int_u8())
		self.RewindTime = ebrw_readstr.int_u32()
		self.MetroPlay = bool(ebrw_readstr.int_u8())
		self.MetroRecord = bool(ebrw_readstr.int_u8())
		self.MetroAccent = bool(ebrw_readstr.int_u8())
		self.CountIn = ebrw_readstr.int_u8()
		ebrw_readstr.skip(2)
		self.ThruOn = bool(ebrw_readstr.int_u8())
		ebrw_readstr.skip(19)
		self.AutoRestart = bool(ebrw_readstr.int_u8())
		self.CurTempoOfs = ebrw_readstr.int_u8()
		self.TempoOfs1 = ebrw_readstr.int_u8()
		self.TempoOfs2 = ebrw_readstr.int_u8()
		self.TempoOfs3 = ebrw_readstr.int_u8()
		ebrw_readstr.skip(2)
		self.PunchEnabled = bool(ebrw_readstr.int_u8())
		self.PunchInTime = ebrw_readstr.int_u32()
		self.PunchOutTime = ebrw_readstr.int_u32()
		self.EndAllTime = ebrw_readstr.int_u32()

	#def write(self, byw_stream):
	#	byw_stream.uint32(self.Now)
	#	byw_stream.uint32(self.From)
	#	byw_stream.uint32(self.Thru)
	#	byw_stream.uint8(self.KeySig)
	#	byw_stream.uint8(self.Clock)
	#	byw_stream.uint8(self.AutoSave)
	#	byw_stream.uint8(self.PlayDelay)
	#	byw_stream.raw(b'\x00')
	#	byw_stream.uint8(int(self.ZeroCtrls))
	#	byw_stream.uint8(int(self.SendSPP))
	#	byw_stream.uint8(int(self.SendCont))
	#	byw_stream.uint8(int(self.PatchSearch))
	#	byw_stream.uint8(int(self.AutoStop))
	#	byw_stream.uint32(self.StopTime)
	#	byw_stream.uint8(int(self.AutoRewind))
	#	byw_stream.uint32(self.RewindTime)
	#	byw_stream.uint8(int(self.MetroPlay))
	#	byw_stream.uint8(int(self.MetroRecord))
	#	byw_stream.uint8(int(self.MetroAccent))
	#	byw_stream.uint8(self.CountIn)
	#	byw_stream.raw(b'\xff\xff')
	#	byw_stream.uint8(int(self.ThruOn))
	#	byw_stream.raw(b'[\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
	#	byw_stream.uint8(int(self.AutoRestart))
	#	byw_stream.uint8(self.CurTempoOfs)
	#	byw_stream.uint8(self.TempoOfs1)
	#	byw_stream.uint8(self.TempoOfs2)
	#	byw_stream.uint8(self.TempoOfs3)
	#	byw_stream.raw(b'\x00\x00')
	#	byw_stream.uint8(int(self.PunchEnabled))
	#	byw_stream.uint32(self.PunchInTime)
	#	byw_stream.uint32(self.PunchOutTime)
	#	byw_stream.uint32(self.EndAllTime)
	#	byw_stream.raw(b'\xfe\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

class cakewalk_chunk_timebase:
	def __init__(self, ebrw_readstr):
		self.timebase = 120
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.timebase = ebrw_readstr.int_u16()

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.timebase)

class cakewalk_chunk_comment:
	def __init__(self, ebrw_readstr):
		self.data = b''
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.data = ebrw_readstr.raw_i16()

	#def write(self, byw_stream):
	#	byw_stream.raw_i16(self.data, False)

class cakewalk_chunk_variable:
	def __init__(self, ebrw_readstr):
		self.name = ''
		self.value = b''
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.name = ebrw_readstr.string(32)
		self.value = ebrw_readstr.rest()

	#def write(self, byw_stream):
	#	byw_stream.string(self.name, 32)
	#	byw_stream.raw(self.value)

class cakewalk_chunk_stringtable:
	def __init__(self, ebrw_readstr):
		self.data = {}
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		num = ebrw_readstr.int_u16()
		for _ in range(num):
			data = ebrw_readstr.raw_i8()
			self.data[ebrw_readstr.int_u8()] = data

	#def write(self, byw_stream):
	#	byw_stream.uint16(len(self.data))
	#	for k, v in self.data.items():
	#		byw_stream.raw_i8(v)
	#		byw_stream.uint8(k)

class cakewalk_chunk_smpte_time:
	def __init__(self, ebrw_readstr):
		self.fmt = 30
		self.ofs = 0
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.fmt = ebrw_readstr.int_u16()
		self.ofs = ebrw_readstr.int_u16()

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.fmt)
	#	byw_stream.uint16(self.ofs)

class cakewalk_chunk_ext_thru:
	def __init__(self, ebrw_readstr):
		self.port = 0
		self.channel = 0
		self.keyPlus = 0
		self.velPlus = 0
		self.localPort = 0
		self.mode = 0
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		ebrw_readstr.skip(2)
		self.port = ebrw_readstr.int_u8()
		self.channel = ebrw_readstr.int_u8()
		self.keyPlus = ebrw_readstr.int_u8()
		self.velPlus = ebrw_readstr.int_u8()
		self.localPort = ebrw_readstr.int_u8()
		self.mode = ebrw_readstr.int_u8()

	#def write(self, byw_stream):
	#	byw_stream.raw('\0\0')
	#	byw_stream.uint8(self.port)
	#	byw_stream.uint8(self.channel)
	#	byw_stream.uint8(self.keyPlus)
	#	byw_stream.uint8(self.velPlus)
	#	byw_stream.uint8(self.localPort)
	#	byw_stream.uint8(self.mode)

class cakewalk_chunk_tracknewoffset:
	def __init__(self, ebrw_readstr):
		self.trackno = 0
		self.offset = 0
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.trackno = ebrw_readstr.int_u16()
		self.offset = ebrw_readstr.int_s32()

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.trackno)
	#	byw_stream.int32(self.offset)

class cakewalk_chunk_markers:
	def __init__(self, ebrw_readstr):
		self.markers = []
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		numevents = ebrw_readstr.int_u32()
		for _ in range(numevents):
			smpte = ebrw_readstr.int_u8()
			ebrw_readstr.skip(1)
			time = ebrw_readstr.int_u24()
			ebrw_readstr.skip(5)
			data = ebrw_readstr.raw_i8()
			self.markers.append([smpte, time, data])

	#def write(self, byw_stream):
	#	byw_stream.uint32(len(self.markers))
	#	for smpte, time, data in self.markers: 
	#		byw_stream.uint8(smpte)
	#		byw_stream.zeros(1)
	#		byw_stream.uint24(time)
	#		byw_stream.zeros(5)
	#		byw_stream.raw_i8(data)

class cakewalk_chunk_tempo:
	def __init__(self, ebrw_readstr):
		self.points = []
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		numevents = ebrw_readstr.int_u16()
		for _ in range(numevents):
			time = ebrw_readstr.int_u32()
			ebrw_readstr.skip(4)
			tempo = ebrw_readstr.int_u16()
			ebrw_readstr.skip(8)
			self.points.append([time, tempo])

	#def write(self, byw_stream):
	#	byw_stream.uint16(len(self.points))
	#	for time, tempo in self.points: 
	#		byw_stream.uint32(time)
	#		byw_stream.zeros(4)
	#		byw_stream.uint16(tempo)
	#		byw_stream.zeros(8)

class cakewalk_chunk_meter_map:
	def __init__(self, ebrw_readstr):
		self.points = []
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		numevents = ebrw_readstr.int_u16()
		for _ in range(numevents):
			ebrw_readstr.skip(4)
			measure = ebrw_readstr.int_u16()
			num = ebrw_readstr.int_u8()
			den = ebrw_readstr.int_u8()
			ebrw_readstr.skip(4)
			self.points.append([measure, num, den])

	#def write(self, byw_stream):
	#	byw_stream.uint16(len(self.points))
	#	for measure, num, den in self.points: 
	#		byw_stream.zeros(4)
	#		byw_stream.uint16(measure)
	#		byw_stream.uint8(num)
	#		byw_stream.uint8(den)
	#		byw_stream.zeros(4)

class cakewalk_chunk_meter_key:
	def __init__(self, ebrw_readstr):
		self.points = []
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		numevents = ebrw_readstr.int_u16()
		for _ in range(numevents):
			measure = ebrw_readstr.int_u16()
			num = ebrw_readstr.int_u8()
			den = ebrw_readstr.int_u8()
			alt = ebrw_readstr.int_u8()
			self.points.append([measure, num, den, alt])

	#def write(self, byw_stream):
	#	byw_stream.uint16(len(self.points))
	#	for measure, num, den, alt in self.points: 
	#		byw_stream.uint16(measure)
	#		byw_stream.uint8(num)
	#		byw_stream.uint8(den)
	#		byw_stream.uint8(alt)

class cakewalk_chunk_sysex:
	def __init__(self, ebrw_readstr):
		self.bank = 0
		self.autosend = 0
		self.name = b''
		self.data = b''
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.bank = ebrw_readstr.int_u8()
		length = ebrw_readstr.int_u16()
		self.autosend = ebrw_readstr.int_u8()
		self.name = ebrw_readstr.raw_i8()
		self.data = ebrw_readstr.raw(length)

	#def write(self, byw_stream):
	#	byw_stream.uint8(self.bank)
	#	byw_stream.uint16(len(self.data))
	#	byw_stream.uint8(self.autosend)
	#	byw_stream.raw_i8(self.name)
	#	byw_stream.raw(self.data)

class cakewalk_chunk_newsysex:
	def __init__(self, ebrw_readstr):
		self.bank = 0
		self.autosend = 0
		self.port = 0
		self.name = b''
		self.data = b''
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.bank = ebrw_readstr.int_u16()
		length = ebrw_readstr.int_u32()
		self.port = ebrw_readstr.int_u16()
		self.autosend = ebrw_readstr.int_u8()
		self.name = ebrw_readstr.raw_i8()
		self.data = ebrw_readstr.raw(length)

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.bank)
	#	byw_stream.uint32(len(self.data))
	#	byw_stream.uint16(self.port)
	#	byw_stream.uint8(self.autosend)
	#	byw_stream.raw_i8(self.name)
	#	byw_stream.raw(self.data)

# --------------------------------------------------------- TRACKS ---------------------------------------------------------

class cakewalk_chunk_track:
	def __init__(self, ebrw_readstr):
		self.trackno = 0
		self.name = ''
		self.channel = 0
		self.pitch = 0
		self.velocity = 100
		self.port = 0
		self.flags = 0
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.trackno = ebrw_readstr.int_u16()
		self.name = ebrw_readstr.raw_i8()
		self.pitch = ebrw_readstr.int_u8()
		self.channel = ebrw_readstr.int_u8()
		self.velocity = ebrw_readstr.int_u8()
		self.port = ebrw_readstr.int_u8()
		self.flags = ebrw_readstr.int_u8()

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.trackno)
	#	byw_stream.raw_i8(self.name)
	#	byw_stream.uint8(self.channel)
	#	byw_stream.uint8(self.pitch)
	#	byw_stream.uint8(self.velocity)
	#	byw_stream.uint8(self.port)
	#	byw_stream.uint8(self.flags)

class cakewalk_chunk_trackname:
	def __init__(self, ebrw_readstr):
		self.trackno = 0
		self.name = ''
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.trackno = ebrw_readstr.int_u16()
		self.name = ebrw_readstr.raw_i8()

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.trackno)
	#	byw_stream.c_string__int8(self.name)

class cakewalk_chunk_trackpatch:
	def __init__(self, ebrw_readstr):
		self.trackno = 0
		self.patch = 0
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.trackno = ebrw_readstr.int_u16()
		self.patch = ebrw_readstr.int_u8()

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.trackno)
	#	byw_stream.uint8(self.patch)

class cakewalk_chunk_trackbank:
	def __init__(self, ebrw_readstr):
		self.trackno = 0
		self.bank = 0
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.trackno = ebrw_readstr.int_u16()
		self.bank = ebrw_readstr.int_u16()

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.trackno)
	#	byw_stream.uint16(self.bank)

class cakewalk_chunk_trackvol:
	def __init__(self, ebrw_readstr):
		self.trackno = 0
		self.vol = 0
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.trackno = ebrw_readstr.int_u16()
		self.vol = ebrw_readstr.int_u16()

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.trackno)
	#	byw_stream.uint16(self.vol)


class cakewalk_chunk_trackoffset:
	def __init__(self, ebrw_readstr):
		self.trackno = 0
		self.offset = 0
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.trackno = ebrw_readstr.int_u16()
		self.offset = ebrw_readstr.int_s16()

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.trackno)
	#	byw_stream.int16(self.offset)


class cakewalk_chunk_eventstream:
	def __init__(self, ebrw_readstr):
		self.trackno = 0
		self.events = []
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.trackno = ebrw_readstr.int_u16()
		numevents = ebrw_readstr.int_u16()
		for _ in range(numevents):
			event = events.cakewalk_event()
			event.read_old(ebrw_readstr)
			self.events.append(event)

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.trackno)
	#	byw_stream.uint16(len(self.events))
	#	for x in self.events: x.write_old(byw_stream)

class cakewalk_chunk_eventsext:
	def __init__(self, ebrw_readstr):
		self.trackno = 0
		self.events = []
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.trackno = ebrw_readstr.int_u16()
		numevents = ebrw_readstr.int_u32()
		for _ in range(numevents):
			event = events.cakewalk_event()
			event.read_new(ebrw_readstr)
			self.events.append(event)

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.trackno)
	#	byw_stream.uint32(len(self.events))
	#	for x in self.events: x.write_new(byw_stream)
