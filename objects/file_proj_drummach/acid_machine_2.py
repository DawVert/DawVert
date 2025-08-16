# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json

class acid_amx_info:
	def __init__(self, projectdata):
		self.appTitle = ""
		self.appAuthor = ""
		self.appWebsite = ""
		self.appVersion = ""
		self.songTitle = ""
		self.songAuthor = ""
		self.songDate = ""
		if projectdata: self.read(projectdata)

	def read(self, indata):
		if 'appTitle' in indata: self.appTitle = indata['appTitle']
		if 'appAuthor' in indata: self.appAuthor = indata['appAuthor']
		if 'appWebsite' in indata: self.appWebsite = indata['appWebsite']
		if 'appVersion' in indata: self.appVersion = indata['appVersion']
		if 'songTitle' in indata: self.songTitle = indata['songTitle']
		if 'songAuthor' in indata: self.songAuthor = indata['songAuthor']
		if 'songDate' in indata: self.songDate = indata['songDate']

class acid_amx_note:
	def __init__(self, indata):
		self.type = 0
		self.start = 0
		self.val = 0
		self.duration = 0
		self.offset = 0
		self.slide = 0
		self.accent = 0
		self.octUp = 0
		self.octDown = 0
		if indata: self.read(indata)

	def read(self, indata):
		if 'type' in indata: self.type = indata['type']
		if 'start' in indata: self.start = indata['start']
		if 'val' in indata: self.val = indata['val']
		if 'duration' in indata: self.duration = indata['duration']
		if 'offset' in indata: self.offset = indata['offset']
		if 'slide' in indata: self.slide = indata['slide']
		if 'accent' in indata: self.accent = indata['accent']
		if 'octUp' in indata: self.octUp = indata['octUp']
		if 'octDown' in indata: self.octDown = indata['octDown']

class acid_amx_pattern:
	def __init__(self, projectdata):
		self.barLength = 1
		self.pattern = {}
		if projectdata: self.read(projectdata)

	def read(self, indata):
		if 'barLength' in indata: self.barLength = indata['barLength']
		if 'pattern' in indata: 
			for n, d in enumerate(indata['pattern']):
				if d: self.pattern[n] = [acid_amx_note(x) for x in d]

class acid_amx_instrument:
	def __init__(self, projectdata):
		self.machineName = ""
		self.instrumentID = ""
		self.controls = []
		if projectdata: self.read(projectdata)

	def read(self, indata):
		if 'machineName' in indata: self.machineName = indata['machineName']
		if 'instrumentID' in indata: self.instrumentID = indata['instrumentID']
		if 'controls' in indata: self.controls = indata['controls']

class acid_amx_song:
	def __init__(self, projectdata):
		self.instruments = ""
		self.instrumentCounts = ""
		self.patterns = ""
		self.currentPattern = ""
		self.currentBank = ""
		self.fxUnits = {}
		self.mixer = ""
		self.pglobal = ""
		self.patternList = ""
		if projectdata: self.read(projectdata)

	def read(self, indata):
		self.fxUnits = {}
		self.patterns = {}
		if 'instruments' in indata: 
			self.instruments = dict([(k, acid_amx_instrument(x)) for k, x in indata['instruments'].items()])
		if 'instrumentCounts' in indata: self.instrumentCounts = indata['instrumentCounts']
		if 'patterns' in indata: 
			for instname, patdata in indata['patterns'].items():
				self.patterns[instname] = {}
				for patnum, patdata in enumerate(patdata):
					if patdata is not None:
						self.patterns[instname][patnum] = acid_amx_pattern(patdata)
		if 'currentPattern' in indata: self.currentPattern = indata['currentPattern']
		if 'currentBank' in indata: self.currentBank = indata['currentBank']
		if 'fxUnits' in indata: 
			for fxh, fxd in indata['fxUnits'].items():
				instnum, slotnum, fxtype = [int(x) for x in fxh.split('_')]
				if instnum not in self.fxUnits: self.fxUnits[instnum] = {}
				if slotnum not in self.fxUnits[instnum]:
					self.fxUnits[instnum][slotnum] = [fxtype, fxd]
		if 'mixer' in indata: self.mixer = indata['mixer']
		if 'pglobal' in indata: self.pglobal = indata['pglobal']
		if 'patternList' in indata: self.patternList = indata['patternList']

class acid_amx_project:
	def __init__(self):
		self.info = acid_amx_info(None)
		self.song = acid_amx_song(None)

	def load_from_file(self, input_file):
		f = open(input_file, 'rb')
		projectdata = json.load(f)
		self.read(projectdata)
		return True

	def read(self, projectdata):
		self.info.read(projectdata['info'])
		self.song.read(projectdata['song'])

apeinst_obj = acid_amx_project()
apeinst_obj.load_from_file("G:\\RandomMusicFiles\\web\\acid\\Acid_Machine_2_1755347645744.amx")
