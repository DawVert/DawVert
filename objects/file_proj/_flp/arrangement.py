# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import struct
from io import BytesIO
from external.easybinrw import easybinrw
from objects.file_proj._flp import chunks

def calcaudiopos(i_value):
	i_out = (i_value)/125
	return i_out

def calcaudiopos_enc(i_value):
	i_out = i_value*125
	return i_out

class flp_arrangement:
	def __init__(self, num_tracks):
		self.tracks = {}
		self.items = chunks.arrdata(num_tracks)
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
