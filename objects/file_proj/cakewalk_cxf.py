# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json

class cxf_meta:
	def __init__(self, indict=None):
		self.type = "cxf"
		self.version = "1.0"
		self.clientId = "Next"
		self.clientVersion = "1.0.1.605"
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'type' in indict: self.type = indict['type']
		if 'version' in indict: self.version = indict['version']
		if 'clientId' in indict: self.clientId = indict['clientId']
		if 'clientVersion' in indict: self.clientVersion = indict['clientVersion']

	def write(self):
		outdata = {}
		outdata['type'] = self.type
		outdata['version'] = self.version
		outdata['clientId'] = self.clientId
		outdata['clientVersion'] = self.clientVersion
		return outdata

class cxf_song:
	def __init__(self, indict=None):
		self.id = ""
		self.stamp = ""
		self.name = ""
		self.forkable = False
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'id' in indict: self.id = indict['id']
		if 'stamp' in indict: self.stamp = indict['stamp']
		if 'name' in indict: self.name = indict['name']
		if 'forkable' in indict: self.forkable = indict['forkable']

	def write(self):
		outdata = {}
		outdata['id'] = self.id
		outdata['stamp'] = self.stamp
		outdata['name'] = self.name
		outdata['forkable'] = self.forkable
		return outdata

class cxf_metronome:
	def __init__(self, indict=None):
		self.bpm = 120
		self.signature = {"notesCount": 4,"noteValue": 4}
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'bpm' in indict: self.bpm = indict['bpm']
		if 'signature' in indict: self.signature = indict['signature']

	def write(self):
		outdata = {}
		outdata['bpm'] = self.bpm
		outdata['signature'] = self.signature
		return outdata

class cxf_sample:
	def __init__(self, indict):
		self.id = ""
		self.isMidi = False
		self.name = "regions-mix"
		self.file = None
		if indict: self.read(indict)
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'id' in indict: self.id = indict['id']
		if 'isMidi' in indict: self.isMidi = indict['isMidi']
		if 'name' in indict: self.name = indict['name']
		if 'file' in indict: self.file = indict['file']

	def write(self):
		outdata = {}
		outdata['id'] = self.id
		outdata['isMidi'] = self.isMidi
		outdata['name'] = self.name
		outdata['file'] = self.file
		return outdata

class cxf_autopoint:
	def __init__(self, indict):
		self.position = 0
		self.utposition = None
		self.value = 0
		if indict: self.read(indict)
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'position' in indict: self.position = indict['position']
		if 'utposition' in indict: self.utposition = indict['utposition']
		if 'value' in indict: self.value = indict['value']

	def write(self):
		outdata = {}
		outdata['position'] = self.position
		if self.utposition is not None: outdata['utposition'] = self.utposition
		outdata['value'] = self.value
		return outdata

class cxf_automation:
	def __init__(self, indict=None):
		self.points = []
		if indict is not None: self.read(indict)

	def read(self, indict):
		self.points = [cxf_autopoint(x) for x in indict]

	def add_point(self, position, value):
		point = cxf_autopoint(None)
		point.position = position
		point.value = value
		self.points.append(point)

	def write(self):
		return [x.write() for x in self.points]

class cxf_plugin:
	def __init__(self, indict):
		self.format = ""
		self.name = ""
		self.uniqueId = 0
		self.slug = ""
		self.bypass = False
		self.automation = {}
		self.params = {}
		if indict: self.read(indict)
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'format' in indict: self.format = indict['format']
		if 'name' in indict: self.name = indict['name']
		if 'uniqueId' in indict: self.uniqueId = indict['uniqueId']
		if 'slug' in indict: self.slug = indict['slug']
		if 'bypass' in indict: self.bypass = indict['bypass']
		if 'automation' in indict: 
			for n, a in indict['automation'].items():
				auto_obj = cxf_automation()
				auto_obj.read(a)
				self.automation[n] = auto_obj
		if 'params' in indict: self.params = indict['params']

	def write(self):
		outdata = {}
		outdata['format'] = self.format
		outdata['name'] = self.name
		outdata['uniqueId'] = self.uniqueId
		if self.slug: outdata['slug'] = self.slug
		outdata['bypass'] = self.bypass
		automation = outdata['automation'] = {}
		for n, a in self.automation.items(): automation[n] = a.write()
		if self.params: outdata['params'] = self.params
		return outdata

class cxf_auxChannel:
	def __init__(self, indict):
		self.type = ""
		self.id = ""
		self.order = 0
		self.name = ""
		self.colorName = ""
		self.color = ""
		self.volume = 1.0
		self.pan = 0.0
		self.isMuted = False
		self.isSolo = False
		self.effects = []
		self.idOutput = ""
		self.automation = {}
		self.auxSends = []
		if indict: self.read(indict)

	def add_effect(self):
		o = cxf_plugin(None)
		self.effects.append(o)
		return o
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'type' in indict: self.type = indict['type']
		if 'id' in indict: self.id = indict['id']
		if 'order' in indict: self.order = indict['order']
		if 'name' in indict: self.name = indict['name']
		if 'colorName' in indict: self.colorName = indict['colorName']
		if 'color' in indict: self.color = indict['color']
		if 'volume' in indict: self.volume = indict['volume']
		if 'pan' in indict: self.pan = indict['pan']
		if 'isMuted' in indict: self.isMuted = indict['isMuted']
		if 'isSolo' in indict: self.isSolo = indict['isSolo']
		if 'effects' in indict: self.effects = [cxf_plugin(x) for x in indict['effects']]
		if 'idOutput' in indict: self.idOutput = indict['idOutput']
		if 'automation' in indict: 
			for n, a in indict['automation'].items():
				auto_obj = cxf_automation()
				auto_obj.read(a)
				self.automation[n] = auto_obj
		if 'auxSends' in indict: self.auxSends = [cxf_auxSend(x) for x in indict['auxSends']]

	def add_auxSend(self):
		o = cxf_auxSend(None)
		self.auxSends.append(o)
		return o

	def write(self):
		outdata = {}
		outdata['type'] = self.type
		outdata['id'] = self.id
		outdata['order'] = self.order
		outdata['name'] = self.name
		outdata['colorName'] = self.colorName
		outdata['color'] = self.color
		outdata['volume'] = self.volume
		outdata['pan'] = self.pan
		outdata['isMuted'] = self.isMuted
		outdata['isSolo'] = self.isSolo
		outdata['effects'] = [x.write() for x in self.effects]
		outdata['idOutput'] = self.idOutput
		if self.auxSends is not None: outdata['auxSends'] = [x.write() for x in self.auxSends]
		automation = outdata['automation'] = {}
		for n, a in self.automation.items(): automation[n] = a.write()
		return outdata

class cxf_region:
	def __init__(self, indict):
		self.file = ""
		self.name = ""
		self.sampleId = ""
		self.sampleOffset = 0
		self.sampleStartPosition = 0
		self.playbackRate = 0
		self.startPosition = 0
		self.endPosition = 0
		self.loopLength = 0
		if indict: self.read(indict)
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'file' in indict: self.file = indict['file']
		if 'name' in indict: self.name = indict['name']
		if 'sampleId' in indict: self.sampleId = indict['sampleId']
		if 'sampleOffset' in indict: self.sampleOffset = indict['sampleOffset']
		if 'sampleStartPosition' in indict: self.sampleStartPosition = indict['sampleStartPosition']
		if 'playbackRate' in indict: self.playbackRate = indict['playbackRate']
		if 'startPosition' in indict: self.startPosition = indict['startPosition']
		if 'endPosition' in indict: self.endPosition = indict['endPosition']
		if 'loopLength' in indict: self.loopLength = indict['loopLength']

	def write(self):
		outdata = {}
		outdata['file'] = self.file
		outdata['name'] = self.name
		outdata['sampleId'] = self.sampleId
		outdata['sampleOffset'] = self.sampleOffset
		outdata['sampleStartPosition'] = self.sampleStartPosition
		outdata['playbackRate'] = self.playbackRate
		outdata['startPosition'] = self.startPosition
		outdata['endPosition'] = self.endPosition
		outdata['loopLength'] = self.loopLength
		return outdata

	def printtime(self):
		print([str(x).ljust(20) for x in 
			[self.sampleOffset, 
			self.sampleStartPosition, 
			self.startPosition, 
			self.endPosition, 
			self.loopLength]]
			)

class cxf_auxSend:
	def __init__(self, indict):
		self.id = ""
		self.bypass = False
		self.sendLevel = 1.0
		self.sendPan = 0.0
		self.automation = {}
		if indict: self.read(indict)
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'id' in indict: self.id = indict['id']
		if 'bypass' in indict: self.bypass = indict['bypass']
		if 'sendLevel' in indict: self.sendLevel = indict['sendLevel']
		if 'sendPan' in indict: self.sendPan = indict['sendPan']
		if 'automation' in indict: 
			for n, a in indict['automation'].items():
				auto_obj = cxf_automation()
				auto_obj.read(a)
				self.automation[n] = auto_obj

	def write(self):
		outdata = {}
		outdata['id'] = self.id
		outdata['bypass'] = self.bypass
		outdata['sendLevel'] = self.sendLevel
		outdata['sendPan'] = self.sendPan
		automation = outdata['automation'] = {}
		for n, a in self.automation.items(): automation[n] = a.write()
		return outdata

class cxf_track:
	def __init__(self, indict):
		self.type = "Instrument"
		self.id = ""
		self.order = 0
		self.parentId = None
		self.synth = None
		self.soundbank = None
		self.name = ""
		self.colorName = ""
		self.color = ""
		self.volume = 1.0
		self.pan = 0.0
		self.isMuted = False
		self.isSolo = False
		self.regions = None
		self.effects = []
		self.idOutput = ""
		self.automation = {}
		self.auxSends = []
		if indict: self.read(indict)

	def add_auxSend(self):
		o = cxf_auxSend(None)
		self.auxSends.append(o)
		return o

	def add_effect(self):
		o = cxf_plugin(None)
		self.effects.append(o)
		return o

	def add_synth(self):
		o = cxf_plugin(None)
		self.synth = o
		return o
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'type' in indict: self.type = indict['type']
		if 'id' in indict: self.id = indict['id']
		if 'order' in indict: self.order = indict['order']
		if 'parentId' in indict: self.parentId = indict['parentId']
		if 'synth' in indict: self.synth = cxf_plugin(indict['synth'])
		if 'soundbank' in indict: self.soundbank = indict['soundbank']
		if 'name' in indict: self.name = indict['name']
		if 'colorName' in indict: self.colorName = indict['colorName']
		if 'color' in indict: self.color = indict['color']
		if 'volume' in indict: self.volume = indict['volume']
		if 'pan' in indict: self.pan = indict['pan']
		if 'isMuted' in indict: self.isMuted = indict['isMuted']
		if 'isSolo' in indict: self.isSolo = indict['isSolo']
		if 'regions' in indict: self.regions = [cxf_region(x) for x in indict['regions']]
		if 'effects' in indict: self.effects = [cxf_plugin(x) for x in indict['effects']]
		if 'auxSends' in indict: self.auxSends = [cxf_auxSend(x) for x in indict['auxSends']]
		if 'idOutput' in indict: self.idOutput = indict['idOutput']
		if 'automation' in indict: 
			for n, a in indict['automation'].items():
				auto_obj = cxf_automation()
				auto_obj.read(a)
				self.automation[n] = auto_obj

	def add_region(self):
		if self.regions is None: self.regions = []
		o = cxf_region(None)
		self.regions.append(o)
		return o

	def write(self):
		outdata = {}
		outdata['type'] = self.type
		outdata['id'] = self.id
		outdata['order'] = self.order
		if self.parentId is not None: outdata['parentId'] = self.parentId
		if self.synth is not None: outdata['synth'] = self.synth.write()
		if self.soundbank is not None: outdata['soundbank'] = self.soundbank
		outdata['name'] = self.name
		outdata['colorName'] = self.colorName
		outdata['color'] = self.color
		outdata['volume'] = self.volume
		outdata['pan'] = self.pan
		outdata['isMuted'] = self.isMuted
		outdata['isSolo'] = self.isSolo
		if self.regions is not None: outdata['regions'] = [x.write() for x in self.regions]
		outdata['effects'] = [x.write() for x in self.effects]
		if self.auxSends is not None: outdata['auxSends'] = [x.write() for x in self.auxSends]
		outdata['idOutput'] = self.idOutput
		automation = outdata['automation'] = {}
		for n, a in self.automation.items(): automation[n] = a.write()
		return outdata

class cxf_arrangertrack_section:
	def __init__(self, indict):
		self.id = 1
		self.name = ""
		self.typeId = 0
		self.color = 0
		self.startTimeArrTicks = 0
		self.endTimeArrTicks = 0
		if indict: self.read(indict)
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'id' in indict: self.id = indict['id']
		if 'name' in indict: self.name = indict['name']
		if 'typeId' in indict: self.typeId = indict['typeId']
		if 'color' in indict: self.color = indict['color']
		if 'startTimeArrTicks' in indict: self.startTimeArrTicks = indict['startTimeArrTicks']
		if 'endTimeArrTicks' in indict: self.endTimeArrTicks = indict['endTimeArrTicks']

	def write(self):
		outdata = {}
		outdata['id'] = self.id
		outdata['name'] = self.name
		outdata['typeId'] = self.typeId
		if self.color: outdata['color'] = self.color
		outdata['startTimeArrTicks'] = self.startTimeArrTicks
		outdata['endTimeArrTicks'] = self.endTimeArrTicks
		return outdata

class cxf_arrangertrack:
	def __init__(self, indict):
		self.id = 1
		self.name = ""
		self.index = 0
		self.visibleIndex = 0
		self.isVisible = 1
		self.isActive = 1
		self.timeFormat = "musical"
		self.sections = []
		if indict: self.read(indict)
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'id' in indict: self.id = indict['id']
		if 'name' in indict: self.name = indict['name']
		if 'index' in indict: self.index = indict['index']
		if 'visibleIndex' in indict: self.visibleIndex = indict['visibleIndex']
		if 'isVisible' in indict: self.isVisible = indict['isVisible']
		if 'isActive' in indict: self.isActive = indict['isActive']
		if 'timeFormat' in indict: self.timeFormat = indict['timeFormat']
		if 'sections' in indict: self.sections = [cxf_arrangertrack_section(x) for x in indict['sections']]

	def add_section(self):
		section = cxf_arrangertrack_section(None)
		self.sections.append(section)
		return section

	def write(self):
		outdata = {}
		outdata['id'] = self.id
		outdata['name'] = self.name
		outdata['index'] = self.index
		outdata['visibleIndex'] = self.visibleIndex
		outdata['isVisible'] = self.isVisible
		outdata['isActive'] = self.isActive
		outdata['timeFormat'] = self.timeFormat
		outdata['sections'] = [x.write() for x in self.sections]
		return outdata

class cxf_arranger:
	def __init__(self, indict=None):
		self.arrangerTracks = []
		self.used = False
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'arrangerTracks' in indict: 
			self.arrangerTracks = [cxf_arrangertrack(x) for x in indict['arrangerTracks']]
			self.used = True

	def write(self):
		outdata = {}
		outdata['arrangerTracks'] = [x.write() for x in self.arrangerTracks]
		return outdata

class cxf_project:
	def __init__(self, indict=None):
		self.meta = cxf_meta()
		self.stamp = ""
		self.song = cxf_song()
		self.description = ""
		self.metronome = cxf_metronome()
		self.description = ""
		self.tempoTrack = None
		self.mainBusId = None
		self.samples = []
		self.auxChannels = []
		self.tracks = []
		self.arranger = cxf_arranger()

	def add_sample(self):
		o = cxf_sample(None)
		self.samples.append(o)
		return o

	def add_auxChannel(self):
		o = cxf_auxChannel(None)
		self.auxChannels.append(o)
		return o

	def add_track(self):
		o = cxf_track(None)
		self.tracks.append(o)
		return o
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'meta' in indict: self.meta.read(indict['meta'])
		if 'stamp' in indict: self.stamp = indict['stamp']
		if 'song' in indict: self.song.read(indict['song'])
		if 'description' in indict: self.description = indict['description']
		if 'metronome' in indict: self.metronome.read(indict['metronome'])
		if 'mainBusId' in indict: self.mainBusId = indict['mainBusId']
		if 'tempoTrack' in indict: self.tempoTrack = indict['tempoTrack']
		self.samples = [cxf_sample(x) for x in indict['samples']]
		self.auxChannels = [cxf_auxChannel(x) for x in indict['auxChannels']]
		self.tracks = [cxf_track(x) for x in indict['tracks']]
		if 'arranger' in indict: self.arranger.read(indict['arranger'])
		return True

	def load_from_file(self, input_file):
		f = open(input_file, 'rb')
		jsontxt = f.read().decode()
		projectdata = json.loads(jsontxt)
		self.read(projectdata)
		return True

	def write(self):
		outdata = {}
		outdata['meta'] = self.meta.write()
		outdata['stamp'] = self.stamp
		outdata['song'] = self.song.write()
		outdata['description'] = self.description
		outdata['metronome'] = self.metronome.write()
		outdata['mainBusId'] = self.mainBusId
		if self.tempoTrack is not None: outdata['tempoTrack'] = self.tempoTrack
		outdata['samples'] = [x.write() for x in self.samples]
		outdata['auxChannels'] = [x.write() for x in self.auxChannels]
		outdata['tracks'] = [x.write() for x in self.tracks]
		if self.arranger.used: outdata['arranger'] = self.arranger.write()
		return outdata

	def save_to_file(self, output_file):
		f = open(output_file, 'wb')
		f.write(json.dumps(self.write(), indent = 2).encode())
