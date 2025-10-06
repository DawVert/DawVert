# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.exceptions import ProjectFileParserException
from external.easybinrw import easybinrw
from functions import data_bytes

class track_tempo:
	def __init__(self): 
		self.name = ''
		self.tempo = 120
		self.events = []

	def load(self, ebrw_readstr): 
		self.name = ebrw_readstr.string(15)
		self.tempo = ebrw_readstr.float()
		self.events = [[ebrw_readstr.int_u16(), ebrw_readstr.float()] for _ in range(ebrw_readstr.int_u16())]

class track_voice:
	def __init__(self): 
		self.name = ''
		self.events = []

	def load(self, ebrw_readstr): 
		self.name = ebrw_readstr.string(15)
		nTicks = ebrw_readstr.int_u16()
		curtickpos = 0
		while curtickpos < nTicks: 
			value = ebrw_readstr.int_u16()
			deltatime = ebrw_readstr.int_u16()
			curtickpos += deltatime
			self.events.append([value, deltatime])

class track_timbre:
	def __init__(self): 
		self.name = ''
		self.events = []

	def load(self, ebrw_readstr): 
		self.name = ebrw_readstr.string(15)
		numevents = ebrw_readstr.int_u16()
		for _ in range(numevents):
			timbre_pos = ebrw_readstr.int_u16()
			timbre_name = ebrw_readstr.string(9)
			ebrw_readstr.skip(3)
			self.events.append([timbre_pos, timbre_name])

class track_float:
	def __init__(self): 
		self.name = ''
		self.events = []

	def load(self, ebrw_readstr): 
		self.name = ebrw_readstr.string(15)
		numevents = ebrw_readstr.int_u16()
		self.events = [[ebrw_readstr.int_u16(), ebrw_readstr.float()] for _ in range(numevents)]

class adlib_rol_track:
	def __init__(self): 
		self.voice = track_voice()
		self.timbre = track_timbre()
		self.volume = track_float()
		self.pitch = track_float()

	def load(self, ebrw_readstr): 
		self.voice.load(ebrw_readstr)
		self.timbre.load(ebrw_readstr)
		self.volume.load(ebrw_readstr)
		self.pitch.load(ebrw_readstr)

class adlib_rol_project:
	def __init__(self): 
		self.majorVersion = 0
		self.minorVersion = 4
		self.tickBeat = 8
		self.beatMeasure = 4
		self.scaleY = 48
		self.scaleX = 48
		self.isMelodic = 0
		self.cTicks = (0,0,0,0,0,0,0,0,0,0,0)
		self.cTimbreEvents = (0,0,0,0,0,0,0,0,0,0,0)
		self.cVolumeEvents = (0,0,0,0,0,0,0,0,0,0,0)
		self.cPitchEvents = (0,0,0,0,0,0,0,0,0,0,0)
		self.cPitchEvents = (0,0,0,0,0,0,0,0,0,0,0)
		self.cTempoEvents = 4
		self.track_tempo = track_tempo()
		self.tracks = [adlib_rol_track() for _ in range(10)]

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)
		self.majorVersion = ebrw_readstr.int_u16()
		self.minorVersion = ebrw_readstr.int_u16()
		
		try: 
			ebrw_readstr.magic_check(b'\\roll\\default\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		except ValueError as t:
			raise ProjectFileParserException('adlib_rol: '+str(t))

		self.tickBeat = ebrw_readstr.int_u16()
		self.beatMeasure = ebrw_readstr.int_u16()
		self.scaleY = ebrw_readstr.int_u16()
		self.scaleX = ebrw_readstr.int_u16()

		ebrw_readstr.skip(1)
		self.isMelodic = ebrw_readstr.int_u8()

		self.cTicks = ebrw_readstr.list_int_u16(11)
		self.cTimbreEvents = ebrw_readstr.list_int_u16(11)
		self.cVolumeEvents = ebrw_readstr.list_int_u16(11)
		self.cPitchEvents = ebrw_readstr.list_int_u16(11)

		self.cTempoEvents = ebrw_readstr.int_u16()

		ebrw_readstr.skip(38)
		self.track_tempo.load(ebrw_readstr)

		for tracknum in range(10): 
			self.tracks[tracknum].load(ebrw_readstr)
		return True