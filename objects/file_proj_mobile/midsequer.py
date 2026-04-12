# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
import logging

# ============================================= track ============================================= 

class midsequer_event_note:
	def __init__(self):
		self.note = 60
		self.vel = 100
		self.dur = 1
		self.time = 0

	def read(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'n': self.note = int(v)
			elif n == 'v': self.vel = int(v)
			elif n == 'd': self.dur = int(v)
			elif n == 't': self.time = int(v)

class midsequer_track_ini:
	def __init__(self):
		self.inst_pc = 0
		self.volume = 100

	def read(self, xmldata):
		for x_part in xmldata:
			name = x_part.tag
			if name == 'volume': self.volume = int(x_part.text)
			if name == 'inst': 
				pc = x_part.get('pc')
				if pc: self.inst_pc = int(pc)

class midsequer_track:
	def __init__(self):
		self.ini = midsequer_track_ini()
		self.evts = []

	def read(self, xmldata):
		for x_part in xmldata:
			name = x_part.tag
			if name == 'ini': self.ini.read(x_part)
			if name == 'evts': 
				for x_evt in x_part:
					if x_evt.tag == 'nt':
						n = midsequer_event_note()
						n.read(x_evt)
						self.evts.append(n)

# ============================================= data ============================================= 

class midsequer_data_mstr:
	def __init__(self):
		self.tempo = 120
		self.tim_sig = [4, 4]

	def read(self, xmldata):
		for x_part in xmldata:
			name = x_part.tag
			if name == 'tempo': self.tempo = int(x_part.text)
			if name == 'tim_sig': 
				ts_1 = x_part.get('unit')
				ts_2 = x_part.get('times')
				if ts_1: self.tim_sig[0] = int(ts_1)
				if ts_2: self.tim_sig[1] = int(ts_2)

class midsequer_data:
	def __init__(self):
		self.mstr = midsequer_data_mstr()
		self.tracks = []

	def read(self, xmldata):
		for x_part in xmldata:
			name = x_part.tag
			if name == 'mstr': self.mstr.read(x_part)
			if name == 'trk': 
				track = midsequer_track()
				track.read(x_part)
				self.tracks.append(track)

# ============================================= sng ============================================= 

class midsequer_sng_meta:
	def __init__(self):
		self.title = ''
		self.create_date = False

	def read(self, xmldata):
		for x_part in xmldata:
			name = x_part.tag
			if name == 'title': self.title = x_part.text
			if name == 'create_date': self.create_date = x_part.text

class midsequer_sng:
	def __init__(self):
		self.meta = midsequer_sng_meta()
		self.data = midsequer_data()

	def read(self, xmldata):
		for x_part in xmldata:
			name = x_part.tag
			if name == 'meta': self.meta.read(x_part)
			if name == 'data': self.data.read(x_part)

# ============================================= main ============================================= 

class midsequer_editstate:
	def __init__(self):
		self.filename = ''
		self.edited = False

	def read(self, xmldata):
		for x_part in xmldata:
			name = x_part.tag
			if name == 'filename': self.filename = x_part.text
			if name == 'edited': self.edited = x_part.text=='true'

class midsequer_project:
	def __init__(self):
		self.editstate = midsequer_editstate()
		self.sng = midsequer_sng()

	def load_from_file(self, input_file):
		x_root = ET.parse(input_file).getroot()
		for x_part in x_root:
			name = x_part.tag
			if name == 'editstate': self.editstate.read(x_part)
			if name == 'sng': self.sng.read(x_part)
		return True
