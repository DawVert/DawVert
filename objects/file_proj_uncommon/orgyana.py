# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from external.easybinrw import easybinrw
from objects.exceptions import ProjectFileParserException
import struct

import logging
logger_projparse = logging.getLogger('projparse')

def stream_decode(ebrw_readstr, org_numofnotes, maxchange, org_notelist, tnum):
	global cur_val
	for x in range(org_numofnotes):
		pre_val = ebrw_readstr.int_u8()
		if maxchange != None:
			if 0 <= pre_val <= maxchange: cur_val = pre_val
			org_notelist[x][tnum] = cur_val
		else:
			org_notelist[x][tnum] = pre_val

def stream_encode(invals):
	cur_val = -1
	for n, x in enumerate(invals):
		if cur_val == x: invals[n] = 255
		cur_val = x
	return invals

class orgyana_orgsamp():
	def __init__(self): 
		self.sample_data = []
		self.drum_data = []
		self.num_drums = 0
		self.drum_rate = 0
		self.loaded = False

	def load_from_file(self, input_file):
		self.loaded = True
		ebrw_readstr = easybinrw.binread()
		if not ebrw_readstr.load_file(input_file): return False
		try:
			ebrw_readstr.seek(4)
			self.sample_data = [ebrw_readstr.list_int_s8(256) for x in range(100)]
			self.num_drums = ebrw_readstr.int_u8()
			self.drum_rate = ebrw_readstr.int_u16()
			self.drum_data = [ebrw_readstr.list_int_u8(ebrw_readstr.int_u24_b()) for x in range(self.num_drums)]
			return True
		except:
			return False

class orgyana_track:
	def __init__(self):
		self.pitch = 1000
		self.instrument = 0
		self.disable_sustaining_notes = 0
		self.number_of_notes = 0
		self.notes = []

	def read(self, ebrw_readstr):
		self.pitch = ebrw_readstr.int_u16()
		self.instrument = ebrw_readstr.int_u8()
		self.disable_sustaining_notes = ebrw_readstr.int_u8()
		self.number_of_notes = ebrw_readstr.int_u16()
		self.notes = [[0,0,0,0,0] for _ in range(self.number_of_notes)]

	def write(self, ebrw_writestr):
		ebrw_writestr.int_u16(self.pitch)
		ebrw_writestr.int_u8(self.instrument)
		ebrw_writestr.int_u8(self.disable_sustaining_notes)
		ebrw_writestr.int_u16(len(self.notes))

class orgyana_project:
	def __init__(self):
		self.oldperc = False
		self.wait = 120
		self.stepsperbar = 4
		self.beatsperstep = 4
		self.loop_beginning = 0
		self.loop_end = 0
		self.tracks = [orgyana_track() for x in range(16)]

	def load_from_raw(self, input_data):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_data(input_data)
		return self.load(ebrw_readstr)

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)
		return self.load(ebrw_readstr)

	def load(self, ebrw_readstr):
		try: 
			ebrw_readstr.magic_check(b'Org-')
		except ValueError as t:
			raise ProjectFileParserException('orgyana: '+str(t))

		self.oldperc = ebrw_readstr.raw(2) == b'03'
		self.wait = ebrw_readstr.int_u16()
		self.stepsperbar = ebrw_readstr.int_u8()
		self.beatsperstep = ebrw_readstr.int_u8()
		self.loop_beginning = ebrw_readstr.int_u32()
		self.loop_end = ebrw_readstr.int_u32()

		for n in range(16): self.tracks[n].read(ebrw_readstr)

		for n in range(16):
			org_track = self.tracks[n]
			for x in range(org_track.number_of_notes): org_track.notes[x][0] = ebrw_readstr.int_u32() #position
			stream_decode(ebrw_readstr, org_track.number_of_notes, 95, org_track.notes, 1) #note
			stream_decode(ebrw_readstr, org_track.number_of_notes, 256, org_track.notes, 2) #duration
			stream_decode(ebrw_readstr, org_track.number_of_notes, 254, org_track.notes, 3) #vol
			stream_decode(ebrw_readstr, org_track.number_of_notes, 12, org_track.notes, 4) #pan
		return True

	def write(self, ebrw_writestr):
		ebrw_writestr.raw(b'Org-'+(b'03' if self.oldperc else b'02'))
		ebrw_writestr.int_u16(self.wait)
		ebrw_writestr.int_u8(self.stepsperbar)
		ebrw_writestr.int_u8(self.beatsperstep)
		ebrw_writestr.int_u32(self.loop_beginning)
		ebrw_writestr.int_u32(self.loop_end)

		for n in range(16): self.tracks[n].write(ebrw_writestr)

		for n in range(16):
			org_track = self.tracks[n]
			n_notes = len(org_track.notes)
			m_pos = [x[0] for x in org_track.notes]
			m_note = [x[1] for x in org_track.notes]
			m_dur = [x[2] for x in org_track.notes]
			m_vol = [x[3] for x in org_track.notes]
			m_pan = [x[4] for x in org_track.notes]
			ebrw_writestr.list_int_u32(m_pos, len(m_pos))
			ebrw_writestr.list_int_u8(m_note, len(m_note))
			ebrw_writestr.list_int_u8(m_dur, len(m_dur))
			ebrw_writestr.list_int_u8(m_vol, len(m_vol))
			ebrw_writestr.list_int_u8(m_pan, len(m_pan))

	def save_to_file(self, output_file):
		ebrw_writestr = easybinrw.binwrite()
		self.write(ebrw_writestr)
		f = open(output_file, 'wb')
		f.write(ebrw_writestr.getvalue())