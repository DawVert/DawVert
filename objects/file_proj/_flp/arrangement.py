# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import struct
from io import BytesIO
from external.easybinrw import easybinrw

def calcaudiopos(i_value):
	i_out = (i_value)/125
	return i_out

def calcaudiopos_enc(i_value):
	i_out = i_value*125
	return i_out

VERBOSE_PRINT = False
VERBOSE_BYTES = False

class flp_arrangement_clip:
	def __init__(self):
		self.position = 0
		self.patternbase = 20480
		self.itemindex = 20480
		self.length = 384
		self.trackindex = 499
		self.unknown1 = 120
		self.flags = 64
		self.unknown2 = 2155897920
		self.id = 0
		self.f_in_dur = 0.0
		self.f_in_tens = 0.0
		self.f_out_dur = 0.0
		self.f_out_tens = 0.0
		self.vol = 1.0
		self.fade_flags = b'\0\0\0\0'
		self.startoffset = 4294967295
		self.endoffset = 4294967295
		self.unknown3 = 0
		self.stretch_mul = 1.0
		self.unknown4 = b'\0\0\0\0\0\0\0\0'

	def read(self, ebrw_readstr, version_split, num_tracks):
		p = ebrw_readstr.tell()

		self.position = ebrw_readstr.int_u32()
		self.patternbase = ebrw_readstr.int_u16()
		self.itemindex = ebrw_readstr.int_u16()
		self.length = ebrw_readstr.int_u32()
		self.trackindex = ebrw_readstr.int_u32()
		self.unknown1 = ebrw_readstr.int_u16()
		self.flags = ebrw_readstr.int_u16()
		self.unknown2 = ebrw_readstr.int_u32()

		startoffset_bytes = ebrw_readstr.read(4)
		endoffset_bytes = ebrw_readstr.read(4)

		if VERBOSE_PRINT: print('I', self.position
		,self.patternbase
		,self.itemindex
		,self.length
		,self.trackindex
		,self.unknown1
		,self.flags
		,startoffset_bytes.hex()
		,endoffset_bytes.hex()
		,self.unknown2, end=' ')

		self.trackindex = num_tracks-self.trackindex

		startoffset = int.from_bytes(startoffset_bytes, "little")
		endoffset = int.from_bytes(endoffset_bytes, "little")
		startoffset_float = struct.unpack('<f', startoffset_bytes)[0]
		endoffset_float = struct.unpack('<f', endoffset_bytes)[0]

		if self.itemindex > self.patternbase:
			if startoffset != 4294967295 and startoffset != 3212836864: self.startoffset = startoffset
			if endoffset != 4294967295 and endoffset != 3212836864: self.endoffset = endoffset
		else:
			self.startoffset = calcaudiopos(startoffset_float)
			self.endoffset = calcaudiopos(endoffset_float)

		if (version_split[0] == 20 and version_split[1] >= 99) or (version_split[0] > 20): 
			self.id = ebrw_readstr.int_u32()
			self.f_in_dur = ebrw_readstr.float()
			self.f_in_tens = ebrw_readstr.float()
			self.f_out_dur = ebrw_readstr.float()
			self.f_out_tens = ebrw_readstr.float()
			self.vol = ebrw_readstr.float()
			self.fade_flags = ebrw_readstr.read(4)

			if VERBOSE_PRINT: print('-E-'
			,self.id
			,self.f_in_dur
			,self.f_in_tens
			,self.f_out_dur
			,self.f_out_tens
			,self.vol
			,self.fade_flags.hex(), end=' ')

		if (version_split[0] >= 25): 
			self.unknown3 = ebrw_readstr.int_u32()
			self.stretch_mul = ebrw_readstr.double()
			self.unknown4 = ebrw_readstr.raw(8)

			if VERBOSE_PRINT: print('-N-'
			,self.unknown3
			,self.stretch_mul
			,self.unknown4.hex()
			, end=' ')

		if VERBOSE_PRINT: print()

		if VERBOSE_BYTES: 
			maxv = ebrw_readstr.tell()-p
			ebrw_readstr.seek(p)
			print( 'I', ebrw_readstr.raw(maxv).hex() )

	def write(self, flversion, num_tracks):
		ebrw_writestr = easybinrw.binwrite()

		ebrw_writestr.int_u32(self.position)
		ebrw_writestr.int_u16(self.patternbase)
		ebrw_writestr.int_u16(self.itemindex)
		ebrw_writestr.int_u32(self.length)
		ebrw_writestr.int_u32(num_tracks-self.trackindex)
		ebrw_writestr.int_u16(self.unknown1)
		ebrw_writestr.int_u16(self.flags)
		ebrw_writestr.int_u32(self.unknown2)

		if self.itemindex > self.patternbase:
			ebrw_writestr.int_u32(self.startoffset)
			ebrw_writestr.int_u32(self.endoffset)
		else:
			ebrw_writestr.float(calcaudiopos_enc(self.startoffset))
			ebrw_writestr.float(calcaudiopos_enc(self.endoffset))

		assert ebrw_writestr.tell()==32

		if VERBOSE_PRINT: print('O', self.position
		,self.patternbase
		,self.itemindex
		,self.length
		,num_tracks-self.trackindex
		,self.unknown1
		,self.flags
		,'XXXXXXXX'
		,'XXXXXXXX'
		,self.unknown2, end=' ')

		if (flversion > 20): 
			ebrw_writestr.int_u32(self.id)
			ebrw_writestr.float(self.f_in_dur)
			ebrw_writestr.float(self.f_in_tens)
			ebrw_writestr.float(self.f_out_dur)
			ebrw_writestr.float(self.f_out_tens)
			ebrw_writestr.float(self.vol)
			ebrw_writestr.raw(self.fade_flags)

			if VERBOSE_PRINT: print('-E-'
			,self.id
			,self.f_in_dur
			,self.f_in_tens
			,self.f_out_dur
			,self.f_out_tens
			,self.vol
			,self.fade_flags.hex(), end=' ')
			assert ebrw_writestr.tell()==60

		if (flversion >= 25): 
			ebrw_writestr.int_u32(self.unknown3)
			ebrw_writestr.double(self.stretch_mul)
			ebrw_writestr.raw(self.unknown4)

			if VERBOSE_PRINT: print('-N-'
			,self.unknown3
			,self.stretch_mul
			,self.unknown4.hex()
			, end=' ')
			assert ebrw_writestr.tell()==80

		if VERBOSE_PRINT: print()

		if VERBOSE_BYTES: 
			print( 'O', ebrw_writestr.getvalue().hex() )

		return ebrw_writestr.getvalue()

class flp_arrangement:
	def __init__(self):
		self.tracks = {}
		self.items = []
		self.timemarkers = []
		self.name = None

		for x in range(1,501):
			self.tracks[x] = flp_track()
			self.tracks[x].id = x

class flp_track:
	def __init__(self):
		self.id = 0
		self.color = 5656904
		self.icon = 0
		self.enabled = 1
		self.height = 1.0
		self.lockedtocontent = 255
		self.motion = 16777215
		self.press = 0
		self.triggersync = 0
		self.queued = 5
		self.tolerant = 0
		self.positionSync = 1
		self.grouped = 0
		self.locked = 0
		self.name = ''
		
	def read(self, event_bio, event_len, version_split):
		if event_len >= 44: 
			self.id, self.color, self.icon, self.enabled, self.height, self.lockedtocontent, self.motion, self.press, self.triggersync, self.queued, self.tolerant, self.positionSync, self.grouped, self.locked = struct.unpack('<IIIBfBIIIIIIBB', event_bio.read(44))

	def write(self, versionnum):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u32(self.id)
		ebrw_writestr.int_u32(self.color)
		ebrw_writestr.int_u32(self.icon)
		ebrw_writestr.int_u8(self.enabled)
		ebrw_writestr.float(self.height)
		ebrw_writestr.int_u8(self.lockedtocontent)
		ebrw_writestr.int_u32(self.motion)
		ebrw_writestr.int_u32(self.press)
		ebrw_writestr.int_u32(self.triggersync)
		ebrw_writestr.int_u32(self.queued)
		ebrw_writestr.int_u32(self.tolerant)
		ebrw_writestr.int_u32(self.positionSync)
		ebrw_writestr.int_u8(self.grouped)
		ebrw_writestr.int_u8(self.locked)
		ebrw_writestr.raw(b'\x00\x00\x00\x00\x00')
		if versionnum>=20:
			ebrw_writestr.raw(b'\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\x01\x00\x00\x00\x00')
		return ebrw_writestr.getvalue()


class flp_timemarker:
	def __init__(self):
		self.type = 0
		self.pos = 0
		self.name = ''
		self.numerator = 4
		self.denominator = 4
