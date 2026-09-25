# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import json

class coolbeat_auto_main:
	def __init__(self, indict=None):
		self.state = False
		self.sections = []
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'state' in indict: self.state = indict['state']
		if 'sections' in indict: self.sections = [coolbeat_auto_section(x) for x in indict['sections']]

class coolbeat_auto_section:
	def __init__(self, indict=None):
		self.startTick = 0
		self.length = 0
		self.nodes = []
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'startTick' in indict: self.startTick = indict['startTick']
		if 'length' in indict: self.length = indict['length']
		if 'nodes' in indict: self.nodes = [coolbeat_auto_node(x) for x in indict['nodes']]

class coolbeat_auto_node:
	def __init__(self, indict=None):
		self.position = 0
		self.value = 0
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'position' in indict: self.position = indict['position']
		if 'value' in indict: self.value = indict['value']

# --------------------------------------------------------- TRACK ---------------------------------------------------------

class coolbeat_track:
	def __init__(self, indict=None):
		self.type = 0
		self.label = ""
		self.volume = 0.5
		self.pan = 0.5
		self.muteState = 0
		self.solo = False
		self.showingAuto = True
		self.currentAutoIndex = 0
		self.scTrackIndex = -1
		self.fileName = ""
		self.soundPack = ""
		self.isSample = False
		self.param = []
		self.sections = []
		self.autos = []
		self.fx = []
		self.fxState = []
		self.tempo = 0
		self.channels = []
		self.filePath = ""
		self.presetIndex = 0
		self.pitchRange = 1
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'type' in indict: self.type = indict['type']
		if 'label' in indict: self.label = indict['label']
		if 'volume' in indict: self.volume = indict['volume']
		if 'pan' in indict: self.pan = indict['pan']
		if 'muteState' in indict: self.muteState = indict['muteState']
		if 'solo' in indict: self.solo = indict['solo']
		if 'showingAuto' in indict: self.showingAuto = indict['showingAuto']
		if 'currentAutoIndex' in indict: self.currentAutoIndex = indict['currentAutoIndex']
		if 'scTrackIndex' in indict: self.scTrackIndex = indict['scTrackIndex']
		if 'fileName' in indict: self.fileName = indict['fileName']
		if 'soundPack' in indict: self.soundPack = indict['soundPack']
		if 'isSample' in indict: self.isSample = indict['isSample']
		if 'sections' in indict: self.sections = [coolbeat_section(x) for x in indict['sections']]
		if 'autos' in indict: self.autos = [coolbeat_auto_main(x) for x in indict['autos']]
		if 'tempo' in indict: self.tempo = indict['tempo']
		if 'channels' in indict: self.channels = [coolbeat_track_channel(x) for x in indict['channels']]
		if 'filePath' in indict: self.filePath = indict['filePath']
		if 'presetIndex' in indict: self.presetIndex = indict['presetIndex']
		if 'pitchRange' in indict: self.pitchRange = indict['pitchRange']

class coolbeat_section:
	def __init__(self, indict=None):
		self.startTick = 0
		self.length = 0
		self.startOffsetTick = 0
		self.endOffsetTick = 0
		self.notes = []
		self.label = ""
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'startTick' in indict: self.startTick = indict['startTick']
		if 'length' in indict: self.length = indict['length']
		if 'startOffsetTick' in indict: self.startOffsetTick = indict['startOffsetTick']
		if 'endOffsetTick' in indict: self.endOffsetTick = indict['endOffsetTick']
		if 'notes' in indict: self.notes = [coolbeat_note(x) for x in indict['notes']]
		if 'label' in indict: self.label = indict['label']

class coolbeat_note:
	def __init__(self, indict=None):
		self.startTick = 0
		self.length = 120
		self.key = 67
		self.volume = 1
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'startTick' in indict: self.startTick = indict['startTick']
		if 'length' in indict: self.length = indict['length']
		if 'key' in indict: self.key = indict['key']
		if 'volume' in indict: self.volume = indict['volume']

class coolbeat_track_channel:
	def __init__(self, indict=None):
		self.fileName = ""
		self.soundPack = "BasicSoundPack"
		self.volume = 1
		self.pan = 0.5
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'fileName' in indict: self.fileName = indict['fileName']
		if 'soundPack' in indict: self.soundPack = indict['soundPack']
		if 'volume' in indict: self.volume = indict['volume']
		if 'pan' in indict: self.pan = indict['pan']

# --------------------------------------------------------- MAIN ---------------------------------------------------------

class coolbeat_root:
	def __init__(self):
		self.version = 4
		self.tempo = 120
		self.timeSigType = 0
		self.masterVolume = 0.5
		self.masterPan = 0.5
		self.masterAutos = []
		self.tracks = []

	def load_from_file(self, input_file):
		f = open(input_file, 'rb')
		projectdata = json.load(f)
		self.read(projectdata)
		return True

	def read(self, indict):
		self.__init__()
		if 'version' in indict: self.version = indict['version']
		if 'tempo' in indict: self.tempo = indict['tempo']
		if 'timeSigType' in indict: self.timeSigType = indict['timeSigType']
		if 'masterVolume' in indict: self.masterVolume = indict['masterVolume']
		if 'masterPan' in indict: self.masterPan = indict['masterPan']
		if 'masterAutos' in indict: self.masterAutos = [coolbeat_auto_main(x) for x in indict['masterAutos']]
		if 'tracks' in indict: self.tracks = [coolbeat_track(x) for x in indict['tracks']]