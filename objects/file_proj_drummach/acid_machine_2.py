# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json

class acid_amx_info:
	def __init__(self, indict=None):
		self.appTitle = ""
		self.appAuthor = ""
		self.appWebsite = ""
		self.appVersion = ""
		self.songTitle = ""
		self.songAuthor = ""
		self.songDate = ""
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'appTitle' in indict: self.appTitle = indict['appTitle']
		if 'appAuthor' in indict: self.appAuthor = indict['appAuthor']
		if 'appWebsite' in indict: self.appWebsite = indict['appWebsite']
		if 'appVersion' in indict: self.appVersion = indict['appVersion']
		if 'songTitle' in indict: self.songTitle = indict['songTitle']
		if 'songAuthor' in indict: self.songAuthor = indict['songAuthor']
		if 'songDate' in indict: self.songDate = indict['songDate']

class acid_amx_note:
	def __init__(self, indict=None):
		self.type = 0
		self.start = 0
		self.val = 0
		self.duration = 0
		self.offset = 0
		self.slide = 0
		self.accent = 0
		self.octUp = 0
		self.octDown = 0
		self.veloc = 110
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'type' in indict: self.type = indict['type']
		if 'start' in indict: self.start = indict['start']
		if 'val' in indict: self.val = indict['val']
		if 'duration' in indict: self.duration = indict['duration']
		if 'offset' in indict: self.offset = indict['offset']
		if 'slide' in indict: self.slide = indict['slide']
		if 'accent' in indict: self.accent = indict['accent']
		if 'octUp' in indict: self.octUp = indict['octUp']
		if 'octDown' in indict: self.octDown = indict['octDown']
		if 'veloc' in indict: self.veloc = indict['veloc']

class acid_amx_pattern:
	def __init__(self, indict=None):
		self.barLength = 1
		self.pattern = {}
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'barLength' in indict: self.barLength = indict['barLength']
		if 'pattern' in indict: 
			for n, d in enumerate(indict['pattern']):
				if d: self.pattern[n] = [acid_amx_note(x) for x in d]

class acid_amx_instrument:
	def __init__(self, indict=None):
		self.machineName = ""
		self.instrumentID = ""
		self.controls = []
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'machineName' in indict: self.machineName = indict['machineName']
		if 'instrumentID' in indict: self.instrumentID = indict['instrumentID']
		if 'controls' in indict: self.controls = indict['controls']

class acid_amx_song:
	def __init__(self, indict=None):
		self.instruments = ""
		self.instrumentCounts = ""
		self.patterns = ""
		self.currentPattern = ""
		self.currentBank = ""
		self.fxUnits = {}
		self.mixer = ""
		self.pglobal = ""
		self.patternList = ""
		if indict is not None: self.read(indict)

	def read(self, indict):
		self.fxUnits = {}
		self.patterns = {}
		if 'instruments' in indict: 
			self.instruments = dict([(k, acid_amx_instrument(x)) for k, x in indict['instruments'].items()])
		if 'instrumentCounts' in indict: self.instrumentCounts = indict['instrumentCounts']
		if 'patterns' in indict: 
			for instname, patdata in indict['patterns'].items():
				self.patterns[instname] = {}
				for patnum, patdata in enumerate(patdata):
					if patdata is not None:
						self.patterns[instname][patnum] = acid_amx_pattern(patdata)
		if 'currentPattern' in indict: self.currentPattern = indict['currentPattern']
		if 'currentBank' in indict: self.currentBank = indict['currentBank']
		if 'fxUnits' in indict: 
			for fxh, fxd in indict['fxUnits'].items():
				instnum, slotnum, fxtype = [int(x) for x in fxh.split('_')]
				if instnum not in self.fxUnits: self.fxUnits[instnum] = {}
				if slotnum not in self.fxUnits[instnum]:
					self.fxUnits[instnum][slotnum] = [fxtype, fxd]
		if 'mixer' in indict: self.mixer = indict['mixer']
		if 'global' in indict: self.pglobal = indict['global']
		if 'patternList' in indict: self.patternList = indict['patternList']

class acid_amx_project:
	def __init__(self):
		self.info = acid_amx_info(None)
		self.song = acid_amx_song(None)

	def load_from_file(self, input_file):
		f = open(input_file, 'rb')
		indict = json.load(f)
		self.read(indict)
		return True

	def read(self, indict):
		self.info.read(indict['info'])
		self.song.read(indict['song'])