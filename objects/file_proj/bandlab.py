# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json

# --------------------------------------------------------- AUTOMATION ---------------------------------------------------------

class bandlab_autopoint:
	def __init__(self, indict=None):
		self.position = 0
		self.value = 0
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'position' in indict: self.position = indict['position']
		if 'value' in indict: self.value = indict['value']

	def write(self):
		return {'position': self.position, 'value': self.value}

class bandlab_automation:
	def __init__(self):
		self.points = []

	def read(self, indict):
		self.points = [bandlab_autopoint(x) for x in indict]

	def add_point(self, position, value):
		point = bandlab_autopoint(None)
		point.position = position
		point.value = value
		self.points.append(point)

	def write(self):
		return [x.write() for x in self.points]

class bandlab_track_automation:
	def __init__(self, indict=None):
		self.id = None
		self.pan = bandlab_automation()
		self.volume = bandlab_automation()
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'id' in indict: self.id = indict['id']
		if 'pan' in indict: self.pan.read(indict['pan'])
		if 'volume' in indict: self.volume.read(indict['volume'])

	def write(self):
		outdata = {}
		if self.id != None: outdata['id'] = self.id
		outdata['pan'] = self.pan.write()
		outdata['volume'] = self.volume.write()
		return outdata

# --------------------------------------------------------- DEVICES ---------------------------------------------------------

class bandlab_effect:
	def __init__(self, indict=None):
		self.automation = {}
		self.bypass = False
		self.params = {}
		self.slug = ''
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'automation' in indict: 
			for n, a in indict['automation'].items():
				auto_obj = bandlab_automation()
				auto_obj.read(a)
				self.automation[n] = auto_obj
		if 'bypass' in indict: self.bypass = indict['bypass']
		if 'params' in indict: self.params = indict['params']
		if 'slug' in indict: self.slug = indict['slug']

	def write(self):
		outdata = {}
		automation = outdata['automation'] = {}
		for n, a in self.automation.items(): automation[n] = a.write()
		outdata['bypass'] = self.bypass
		outdata['params'] = self.params
		outdata['slug'] = self.slug
		return outdata

class bandlab_autoPitch:
	def __init__(self, indict=None):
		self.algorithm = "original"
		self.bypass = True
		self.mix = 1.0
		self.responseTime = 0.0
		self.scale = "scale_chromatic"
		self.slug = ""
		self.targetNotes = []
		self.tonic = "tonic_C"
		self.version = "0.2"
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'algorithm' in indict: self.algorithm = indict['algorithm']
		if 'bypass' in indict: self.bypass = indict['bypass']
		if 'mix' in indict: self.mix = indict['mix']
		if 'responseTime' in indict: self.responseTime = indict['responseTime']
		if 'scale' in indict: self.scale = indict['scale']
		if 'slug' in indict: self.slug = indict['slug']
		if 'targetNotes' in indict: self.targetNotes = indict['targetNotes']
		if 'tonic' in indict: self.tonic = indict['tonic']
		if 'version' in indict: self.version = indict['version']

	def write(self):
		outdata = {}
		outdata['algorithm'] = self.algorithm
		outdata['bypass'] = self.bypass
		outdata['mix'] = self.mix
		outdata['responseTime'] = self.responseTime
		outdata['scale'] = self.scale
		outdata['slug'] = self.slug
		outdata['targetNotes'] = self.targetNotes
		outdata['tonic'] = self.tonic
		outdata['version'] = self.version
		return outdata

# --------------------------------------------------------- CLIP ---------------------------------------------------------

class bandlab_region:
	def __init__(self, indict=None):
		self.endPosition = 0
		self.fadeIn = 0.0
		self.fadeOut = 0.0
		self.gain = 1.0
		self.id = ""
		self.key = None
		self.loopLength = 0.0
		self.name = ""
		self.pitchShift = 0.0
		self.playbackRate = 1.0
		self.sampleId = ""
		self.sampleOffset = 0.0
		self.sampleStartPosition = 0.0
		self.startPosition = 0.0
		self.trackId = ""
		self.file = ""
		self.post = {}
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'endPosition' in indict: self.endPosition = indict['endPosition']
		if 'fadeIn' in indict: self.fadeIn = indict['fadeIn']
		if 'fadeOut' in indict: self.fadeOut = indict['fadeOut']
		if 'gain' in indict: self.gain = indict['gain']
		if 'id' in indict: self.id = indict['id']
		if 'key' in indict: self.key = indict['key']
		if 'loopLength' in indict: self.loopLength = indict['loopLength']
		if 'name' in indict: self.name = indict['name']
		if 'pitchShift' in indict: self.pitchShift = indict['pitchShift']
		if 'playbackRate' in indict: self.playbackRate = indict['playbackRate']
		if 'sampleId' in indict: self.sampleId = indict['sampleId']
		if 'sampleOffset' in indict: self.sampleOffset = indict['sampleOffset']
		if 'sampleStartPosition' in indict: self.sampleStartPosition = indict['sampleStartPosition']
		if 'startPosition' in indict: self.startPosition = indict['startPosition']
		if 'trackId' in indict: self.trackId = indict['trackId']
		if 'file' in indict: self.file = indict['file']

	def write(self):
		outdata = {}
		outdata['endPosition'] = self.endPosition
		outdata['fadeIn'] = self.fadeIn
		outdata['fadeOut'] = self.fadeOut
		outdata['gain'] = self.gain
		outdata['id'] = self.id
		outdata['key'] = self.key
		outdata['loopLength'] = self.loopLength
		outdata['name'] = self.name
		outdata['pitchShift'] = self.pitchShift
		outdata['playbackRate'] = self.playbackRate
		outdata['sampleId'] = self.sampleId
		outdata['sampleOffset'] = self.sampleOffset
		outdata['sampleStartPosition'] = self.sampleStartPosition
		outdata['startPosition'] = self.startPosition
		outdata['trackId'] = self.trackId
		if self.file: outdata['file'] = self.file
		return outdata

class bandlab_pattern:
	def __init__(self, indict=None):
		self.notes = []
		self.sampleId = ''
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'notes' in indict: self.notes = indict['notes']
		if 'sampleId' in indict: self.sampleId = indict['sampleId']

	def write(self):
		outdata = {}
		outdata['notes'] = self.notes
		outdata['sampleId'] = self.sampleId
		return outdata

# --------------------------------------------------------- TRACK ---------------------------------------------------------

class bandlab_auxChannel:
	def __init__(self, indict=None):
		self.effects = None
		self.id = ''
		self.preset = 'sharedReverb'
		self.returnLevel = 1.0
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'effects' in indict: self.effects = indict['effects']
		if 'id' in indict: self.id = indict['id']
		if 'preset' in indict: self.preset = indict['preset']
		if 'returnLevel' in indict: self.returnLevel = indict['returnLevel']

	def write(self):
		outdata = {}
		outdata['effects'] = self.effects
		outdata['id'] = self.id
		outdata['preset'] = self.preset
		outdata['returnLevel'] = self.returnLevel
		return outdata

class bandlab_auxSend:
	def __init__(self, indict=None):
		self.automation = bandlab_automation()
		self.id = ''
		self.sendLevel = 0.0
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'automation' in indict: self.automation.read(indict['automation'])
		if 'id' in indict: self.id = indict['id']
		if 'sendLevel' in indict: self.sendLevel = indict['sendLevel']

	def write(self):
		outdata = {}
		outdata['automation'] = self.automation.write()
		outdata['id'] = self.id
		outdata['sendLevel'] = self.sendLevel
		return outdata

class bandlab_track:
	def __init__(self, indict=None):
		self.automation = None
		self.autoPitch = None
		self.auxSends = []

		self.canEdit = True
		self.color = "#AECA59"
		self.colorName = "Green"

		self.effects = []
		self.effectsData = None

		self.id = ""
		self.inputEffect = 0
		self.isFrozen = False
		self.isMuted = False
		self.isSolo = False
		self.loopPack = None
		self.name = "speed"
		self.order = 0
		self.pan = 0.0
		self.patterns = None
		self.preset = "none"

		self.regions = []
		self.regionsMix = None

		self.revisionId = ""
		self.sampleId = ""
		self.samplerKit = None
		self.soundbank = None
		self.trackGroupId = None
		self.type = ""
		self.volume = 1.0
		self.assetFormat = ""

		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'automation' in indict: self.automation = bandlab_track_automation(indict['automation'])
		if 'autoPitch' in indict: 
			if indict['autoPitch']:
				self.autoPitch = bandlab_autoPitch(indict['autoPitch'])
		if 'auxSends' in indict: self.auxSends = [bandlab_auxSend(x) for x in indict['auxSends']]
		if 'canEdit' in indict: self.canEdit = indict['canEdit']
		if 'color' in indict: self.color = indict['color']
		if 'colorName' in indict: self.colorName = indict['colorName']

		if 'effects' in indict: self.effects = [bandlab_effect(x) for x in indict['effects']]
		if 'effectsData' in indict: self.effectsData = indict['effectsData']

		if 'id' in indict: self.id = indict['id']
		if 'inputEffect' in indict: self.inputEffect = indict['inputEffect']
		if 'isFrozen' in indict: self.isFrozen = indict['isFrozen']
		if 'isMuted' in indict: self.isMuted = indict['isMuted']
		if 'isSolo' in indict: self.isSolo = indict['isSolo']
		if 'loopPack' in indict: self.loopPack = indict['loopPack']
		if 'name' in indict: self.name = indict['name']
		if 'order' in indict: self.order = indict['order']
		if 'pan' in indict: self.pan = indict['pan']
		if 'patterns' in indict: self.patterns = [bandlab_pattern(x) for x in indict['patterns']] if indict['patterns'] else None
		if 'preset' in indict: self.preset = indict['preset']
		if 'regions' in indict: self.regions = [bandlab_region(x) for x in indict['regions']]
		if 'regionsMix' in indict: self.regionsMix = bandlab_region(indict['regionsMix'])

		if 'revisionId' in indict: self.revisionId = indict['revisionId']
		if 'sampleId' in indict: self.sampleId = indict['sampleId']
		if 'samplerKit' in indict: self.samplerKit = indict['samplerKit']
		if 'soundbank' in indict: self.soundbank = indict['soundbank']
		if 'trackGroupId' in indict: self.trackGroupId = indict['trackGroupId']
		if 'type' in indict: self.type = indict['type']
		if 'volume' in indict: self.volume = indict['volume']
		if 'assetFormat' in indict: self.assetFormat = indict['assetFormat']

	def write(self):
		outdata = {}
		if self.automation: outdata['automation'] = self.automation.write()
		outdata['autoPitch'] = self.autoPitch.write() if self.autoPitch else None
		outdata['auxSends'] = [x.write() for x in self.auxSends]
		outdata['canEdit'] = self.canEdit
		outdata['color'] = self.color
		outdata['colorName'] = self.colorName
		outdata['effects'] = [x.write() for x in self.effects] if self.effects != None else None
		outdata['effectsData'] = self.effectsData
		outdata['id'] = self.id
		outdata['inputEffect'] = self.inputEffect
		outdata['isFrozen'] = self.isFrozen
		outdata['isMuted'] = self.isMuted
		outdata['isSolo'] = self.isSolo
		outdata['loopPack'] = self.loopPack
		outdata['name'] = self.name
		outdata['order'] = self.order
		outdata['pan'] = self.pan
		outdata['patterns'] = [x.write() for x in self.patterns] if self.patterns != None else None
		outdata['preset'] = self.preset

		outdata['regions'] = [x.write() for x in self.regions]
		outdata['regionsMix'] = self.regionsMix.write() if self.regionsMix else None

		outdata['revisionId'] = self.revisionId
		outdata['sampleId'] = self.sampleId
		outdata['samplerKit'] = self.samplerKit
		outdata['soundbank'] = self.soundbank
		outdata['trackGroupId'] = self.trackGroupId
		outdata['type'] = self.type
		outdata['volume'] = self.volume
		if self.assetFormat: outdata['assetFormat'] = self.assetFormat

		return outdata

class bandlab_sample:
	def __init__(self, indict=None):
		self.creatorId = ""
		self.device = None
		self.duration = 0.0
		self.file = None
		self.id = ""
		self.isMidi = False
		self.name = "regions-mix"
		self.source = "BandLabWeb-10.1.135"
		self.status = "Empty"
		self.waveform = None
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'creatorId' in indict: self.creatorId = indict['creatorId']
		if 'device' in indict: self.device = indict['device']
		if 'duration' in indict: self.duration = indict['duration']
		if 'file' in indict: self.file = indict['file']
		if 'id' in indict: self.id = indict['id']
		if 'isMidi' in indict: self.isMidi = indict['isMidi']
		if 'name' in indict: self.name = indict['name']
		if 'source' in indict: self.source = indict['source']
		if 'status' in indict: self.status = indict['status']
		if 'waveform' in indict: self.waveform = indict['waveform']

	def write(self):
		outdata = {}
		outdata['creatorId'] = self.creatorId
		outdata['device'] = self.device
		outdata['duration'] = self.duration
		outdata['file'] = self.file
		outdata['id'] = self.id
		outdata['isMidi'] = self.isMidi
		outdata['name'] = self.name
		outdata['source'] = self.source
		outdata['status'] = self.status
		outdata['waveform'] = self.waveform
		return outdata

class bandlab_samplerKits_sample:
	def __init__(self, indict=None):
		self.file = ''
		self.id = ''
		self.status = 'Ready'
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'file' in indict: self.file = indict['file']
		if 'id' in indict: self.id = indict['id']
		if 'status' in indict: self.status = indict['status']

	def write(self):
		outdata = {}
		outdata['file'] = self.file
		outdata['id'] = self.id
		outdata['status'] = self.status
		return outdata

class bandlab_samplerKits:
	def __init__(self, indict=None):
		self.samples = []
		if indict is not None: self.read(indict)

	def read(self, indict):
		self.samples = [bandlab_samplerKits_sample(x) for x in indict['samples']]

	def write(self):
		outdata = {}
		outdata['samples'] = [x.write() for x in self.samples]
		return outdata

class bandlab_project:
	def __init__(self):
		self.auxChannels = []
		self.samplerKits = None
		self.samples = []
		self.tracks = []

		self.canEdit = True
		self.canEditSettings = True
		self.canMaster = True
		self.canPublish = True
		self.clientId = "DawVert"
		self.createdOn = ''
		self.stamp = ''
		self.mixdown = None
		self.trackGroups = ''
		self.modifiedOn = ''
		self.parentId = ''
		self.place = None
		self.post = {}
		self.postId = ''

		self.counters = {}
		self.id = ''
		self.isFork = False
		self.isLiked = False
		self.isPublic = False
		self.key = None
		self.lyrics = None
		self.mastering = None
		self.metronome = {}
		self.song = {}

		self.creator = {}
		self.description = None
		self.genres = []

		self.volume = 1.0
		self.blxVersion = '1.0'

	def read(self, indict):
		if 'canEdit' in indict: self.canEdit = indict['canEdit']
		if 'canEditSettings' in indict: self.canEditSettings = indict['canEditSettings']
		if 'canMaster' in indict: self.canMaster = indict['canMaster']
		if 'canPublish' in indict: self.canPublish = indict['canPublish']
		if 'clientId' in indict: self.clientId = indict['clientId']
		if 'counters' in indict: self.counters = indict['counters']
		if 'createdOn' in indict: self.createdOn = indict['createdOn']
		if 'stamp' in indict: self.stamp = indict['stamp']
		if 'modifiedOn' in indict: self.modifiedOn = indict['modifiedOn']
		if 'parentId' in indict: self.parentId = indict['parentId']
		if 'place' in indict: self.place = indict['place']
		if 'trackGroups' in indict: self.trackGroups = indict['trackGroups']
		if 'volume' in indict: self.volume = indict['volume']
		if 'blxVersion' in indict: self.blxVersion = indict['blxVersion']
		if 'postId' in indict: self.postId = indict['postId']
		if 'post' in indict: self.post = indict['post']
		if 'mixdown' in indict: 
			self.mixdown = bandlab_sample(None)
			self.mixdown.read(indict['mixdown'])

		if 'id' in indict: self.id = indict['id']
		if 'isFork' in indict: self.isFork = indict['isFork']
		if 'isLiked' in indict: self.isLiked = indict['isLiked']
		if 'isPublic' in indict: self.isPublic = indict['isPublic']
		if 'key' in indict: self.key = indict['key']
		if 'lyrics' in indict: self.lyrics = indict['lyrics']
		if 'mastering' in indict: self.mastering = indict['mastering']
		if 'metronome' in indict: self.metronome = indict['metronome']
		if 'song' in indict: self.song = indict['song']

		if 'creator' in indict: self.creator = indict['creator']
		if 'description' in indict: self.description = indict['description']
		if 'genres' in indict: self.genres = indict['genres']

		self.auxChannels = [bandlab_auxChannel(x) for x in indict['auxChannels']]
		self.tracks = [bandlab_track(x) for x in indict['tracks']]
		self.samples = [bandlab_sample(x) for x in indict['samples']]
		self.samplerKits = bandlab_samplerKits(indict['samplerKits'])

	def load_from_file(self, input_file):
		f = open(input_file, 'rb')
		jsontxt = f.read().decode().split('\0')[0]
		projectdata = json.loads(jsontxt)
		self.read(projectdata)
		return True

	def write(self):
		outdata = {}
		outdata['auxChannels'] = [x.write() for x in self.auxChannels]
		outdata['canEdit'] = self.canEdit
		outdata['canEditSettings'] = self.canEditSettings
		outdata['canMaster'] = self.canMaster
		outdata['canPublish'] = self.canPublish
		outdata['clientId'] = self.clientId
		outdata['counters'] = self.counters
		outdata['createdOn'] = self.createdOn

		outdata['creator'] = self.creator
		outdata['description'] = self.description
		outdata['genres'] = self.genres

		outdata['id'] = self.id
		outdata['isFork'] = self.isFork
		outdata['isLiked'] = self.isLiked
		outdata['isPublic'] = self.isPublic
		outdata['key'] = self.key
		outdata['lyrics'] = self.lyrics
		outdata['mastering'] = self.mastering
		outdata['metronome'] = self.metronome

		outdata['mixdown'] = self.mixdown.write() if self.mixdown else {}
		outdata['modifiedOn'] = self.modifiedOn
		outdata['parentId'] = self.parentId
		outdata['place'] = self.place
		outdata['post'] = self.post
		outdata['postId'] = self.postId

		outdata['samplerKits'] = self.samplerKits.write() if self.samplerKits else {}
		outdata['samples'] = [x.write() for x in self.samples]
		outdata['song'] = self.song
		outdata['stamp'] = self.stamp
		outdata['trackGroups'] = self.trackGroups
		outdata['tracks'] = [x.write() for x in self.tracks]
		outdata['volume'] = self.volume
		outdata['blxVersion'] = self.blxVersion
		return outdata

	def save_to_file(self, output_file):
		f = open(output_file, 'wb')
		f.write(json.dumps(self.write(), indent = 2).encode()+b'\0')
