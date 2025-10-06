# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from external.easybinrw import easybinrw
import numpy as np

notes_dtype = np.dtype([
	('time', np.uint32),
	('key', np.int8),
	('vol', np.uint8)
	])

pc_dtype = np.dtype([
	('time', np.uint32),
	('p', np.uint8)
	])

pb_dtype = np.dtype([
	('time', np.uint32),
	('p', np.uint8),
	('b', np.uint8)
	])

class v2m_track:
	def __init__(self, ebrw_readstr):
		numnotes = ebrw_readstr.int_u32()
		self.notes = np.zeros(numnotes, dtype=notes_dtype)
		self.cc = []

		if numnotes:
			ebrw_readstr.isolate_size(5*numnotes)
			self.notes[:]['time'] += ebrw_readstr.list_int_u8(numnotes).astype(np.uint32)
			self.notes[:]['time'] += ebrw_readstr.list_int_u8(numnotes).astype(np.uint32)<<8
			self.notes[:]['time'] += ebrw_readstr.list_int_u8(numnotes).astype(np.uint32)<<16
			self.notes[:]['key'] = ebrw_readstr.list_int_s8(numnotes)
			self.notes[:]['vol'] = ebrw_readstr.list_int_u8(numnotes)
			ebrw_readstr.isolate_end()

			pcnum = ebrw_readstr.int_u32()
			self.pc = np.zeros(pcnum, dtype=pc_dtype)
			if pcnum:
				ebrw_readstr.isolate_size(4*pcnum)
				self.pc[:]['time'] += ebrw_readstr.list_int_u8(pcnum).astype(np.uint32)
				self.pc[:]['time'] += ebrw_readstr.list_int_u8(pcnum).astype(np.uint32)<<8
				self.pc[:]['time'] += ebrw_readstr.list_int_u8(pcnum).astype(np.uint32)<<16
				self.pc[:]['p'] = ebrw_readstr.list_int_u8(pcnum)
				ebrw_readstr.isolate_end()
	
			pbnum = ebrw_readstr.int_u32()
			self.pb = np.zeros(pbnum, dtype=pb_dtype)
			if pbnum:
				ebrw_readstr.isolate_size(5*pbnum)
				self.pb[:]['time'] += ebrw_readstr.list_int_u8(pbnum).astype(np.uint32)
				self.pb[:]['time'] += ebrw_readstr.list_int_u8(pbnum).astype(np.uint32)<<8
				self.pb[:]['time'] += ebrw_readstr.list_int_u8(pbnum).astype(np.uint32)<<16
				self.pb[:]['p'] = ebrw_readstr.list_int_u8(pbnum)
				self.pb[:]['b'] = ebrw_readstr.list_int_u8(pbnum)
				ebrw_readstr.isolate_end()
	
			for j in range(7):
				ccnum = ebrw_readstr.int_u32()
				cc_data = np.zeros(ccnum, dtype=pc_dtype)
				if ccnum:
					ebrw_readstr.isolate_size(4*ccnum)
					cc_data[:]['time'] += ebrw_readstr.list_int_u8(ccnum).astype(np.uint32)
					cc_data[:]['time'] += ebrw_readstr.list_int_u8(ccnum).astype(np.uint32)<<8
					cc_data[:]['time'] += ebrw_readstr.list_int_u8(ccnum).astype(np.uint32)<<16
					cc_data[:]['p'] = ebrw_readstr.list_int_u8(ccnum)
					ebrw_readstr.isolate_end()
					self.cc.append([ccnum, cc_data])

class v2m_song:
	def __init__(self):
		self.timediv = 1
		self.maxtime = 0
		self.gdnum = 0
		self.gptr = None
		self.tracks = []

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)

		self.timediv = ebrw_readstr.int_u32()
		self.maxtime = ebrw_readstr.int_u32()
		self.gdnum = ebrw_readstr.int_u32()
		self.gptr = ebrw_readstr.raw(10*self.gdnum)
		self.tracks = [v2m_track(ebrw_readstr) for x in range(16)]
		self.globals = ebrw_readstr.raw(ebrw_readstr.int_u32())
		self.patchmap = ebrw_readstr.raw(ebrw_readstr.int_u32())
		return True