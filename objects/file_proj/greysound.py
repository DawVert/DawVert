# SPDX-FileCopyrightText: 2026 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import json
from objects.exceptions import ProjectFileParserException
logger_projparse = logging.getLogger('projparse')

DEBUG_IN_OUT = True

class greysound_insert:
	def __init__(self):
		self.id = ""
		self.trackId = ""
		self.slotIndex = ""
		self.pluginType = 0
		self.bypassed = 0
		self.parameters = 0

	def read(self, pd):
		for n, v in pd.items():
			if n == 'id': self.id = v
			elif n == 'trackId': self.trackId = v
			elif n == 'slotIndex': self.slotIndex = v
			elif n == 'pluginType': self.pluginType = v
			elif n == 'bypassed': self.bypassed = v
			elif n == 'parameters': self.parameters = v
			else: logger_projparse.warning('greysound: insert: unimplemented attrib: '+n)

	def write(self):
		out = {}
		out['id'] = self.id
		out['trackId'] = self.trackId
		out['slotIndex'] = self.slotIndex
		out['pluginType'] = self.pluginType
		out['bypassed'] = self.bypassed
		out['parameters'] = self.parameters
		return out

class greysound_send:
	def __init__(self):
		self.id = ""
		self.sourceTrackId = 0
		self.destinationTrackId = 0
		self.slotIndex = 2
		self.levelDb = 0
		self.channelPans = [0]
		self.bypassed = False
		self.preFader = False

	def read(self, pd):
		for n, v in pd.items():
			if n == 'id': self.id = v
			elif n == 'sourceTrackId': self.sourceTrackId = v
			elif n == 'destinationTrackId': self.destinationTrackId = v
			elif n == 'slotIndex': self.slotIndex = v
			elif n == 'levelDb': self.levelDb = v
			elif n == 'channelPans': self.channelPans = v
			elif n == 'bypassed': self.bypassed = v
			elif n == 'preFader': self.preFader = v
			else: logger_projparse.warning('greysound: send: unimplemented attrib: '+n)

	def write(self):
		out = {}
		out['id'] = self.id
		out['sourceTrackId'] = self.sourceTrackId
		out['destinationTrackId'] = self.destinationTrackId
		out['slotIndex'] = self.slotIndex
		out['levelDb'] = self.levelDb
		out['channelPans'] = self.channelPans
		out['bypassed'] = self.bypassed
		out['preFader'] = self.preFader
		return out

class greysound_marker:
	def __init__(self):
		self.id = ""
		self.name = ""
		self.position = {}

	def read(self, pd):
		for n, v in pd.items():
			if n == 'id': self.id = v
			elif n == 'name': self.name = v
			elif n == 'position': self.position = v
			else: logger_projparse.warning('greysound: marker: unimplemented attrib: '+n)

	def write(self):
		out = {}
		out['id'] = self.id
		out['name'] = self.name
		out['position'] = self.position
		return out

class greysound_midinote:
	def __init__(self):
		self.pitch = 60
		self.startTicks = 0
		self.durationTicks = 3840
		self.velocity = 100

	def read(self, pd):
		for n, v in pd.items():
			if n == 'pitch': self.pitch = v
			elif n == 'startTicks': self.startTicks = v
			elif n == 'durationTicks': self.durationTicks = v
			elif n == 'velocity': self.velocity = v
			else: logger_projparse.warning('greysound: midinote: unimplemented attrib: '+n)

	def write(self):
		out = {}
		out['pitch'] = self.pitch
		out['startTicks'] = self.startTicks
		out['durationTicks'] = self.durationTicks
		out['velocity'] = self.velocity
		return out

class greysound_clip:
	def __init__(self):
		self.id = ""
		self.filename = ""
		self.storagePath = ""
		self.durationSec = 0

	def read(self, pd):
		for n, v in pd.items():
			if n == 'id': self.id = v
			elif n == 'filename': self.filename = v
			elif n == 'storagePath': self.storagePath = v
			elif n == 'durationSec': self.durationSec = v
			else: logger_projparse.warning('greysound: clip: unimplemented attrib: '+n)

	def write(self):
		out = {}
		out['id'] = self.id
		out['filename'] = self.filename
		out['storagePath'] = self.storagePath
		out['durationSec'] = self.durationSec
		return out

class greysound_region:
	def __init__(self):
		self.id = ""
		self.trackId = 0
		self.start = {}
		self.end = {}
		self.clipId = ""
		self.color = ''
		self.clipStartOffset = {}
		self.clipDuration = {}
		self.fadeIn = {}
		self.fadeOut = {}
		self.clipGain = 0
		self.midiNotes = []
		self.loopEnabled = False
		self.loopLength = {}

	def read(self, pd):
		for n, v in pd.items():
			if n == 'id': self.id = v
			elif n == 'trackId': self.trackId = v
			elif n == 'start': self.start = v
			elif n == 'end': self.end = v
			elif n == 'clipId': self.clipId = v
			elif n == 'color': self.color = v
			elif n == 'clipStartOffset': self.clipStartOffset = v
			elif n == 'clipDuration': self.clipDuration = v
			elif n == 'fadeIn': self.fadeIn = v
			elif n == 'fadeOut': self.fadeOut = v
			elif n == 'clipGain': self.clipGain = v
			elif n == 'midiNotes':
				self.midiNotes = []
				for t in v:
					o = greysound_midinote()
					o.read(t)
					self.midiNotes.append(o)
			elif n == 'loopEnabled': self.loopEnabled = v
			elif n == 'loopLength': self.loopLength = v
			else: logger_projparse.warning('greysound: region: unimplemented attrib: '+n)

	def write(self):
		out = {}
		out['id'] = self.id
		out['trackId'] = self.trackId
		out['start'] = self.start
		out['end'] = self.end
		if self.clipId: out['clipId'] = self.clipId
		if self.color: out['color'] = self.color
		if self.clipStartOffset: out['clipStartOffset'] = self.clipStartOffset
		if self.clipDuration: out['clipDuration'] = self.clipDuration
		if self.midiNotes: out['midiNotes'] = [x.write() for x in self.midiNotes]
		if self.fadeIn: out['fadeIn'] = self.fadeIn
		if self.fadeOut: out['fadeOut'] = self.fadeOut
		if self.clipGain: out['clipGain'] = self.clipGain
		return out

class greysound_automationLane_target:
	def __init__(self):
		self.type = "TRACK"
		self.parameterId = ""
		self.label = ""
		self.minValue = 0
		self.maxValue = 1
		self.defaultValue = 0
		self.unit = None

	def read(self, pd):
		for n, v in pd.items():
			if n == 'type': self.type = v
			elif n == 'parameterId': self.parameterId = v
			elif n == 'label': self.label = v
			elif n == 'minValue': self.minValue = v
			elif n == 'maxValue': self.maxValue = v
			elif n == 'defaultValue': self.defaultValue = v
			elif n == 'unit': self.unit = v
			else: logger_projparse.warning('greysound: automationLane_target: unimplemented attrib: '+n)

	def write(self):
		out = {}
		out['type'] = self.type
		out['parameterId'] = self.parameterId
		out['label'] = self.label
		out['minValue'] = self.minValue
		out['maxValue'] = self.maxValue
		out['defaultValue'] = self.defaultValue
		if self.unit: out['unit'] = self.unit
		return out

class greysound_automationLane_point:
	def __init__(self):
		self.id = ""
		self.position = {}
		self.value = 0

	def read(self, pd):
		for n, v in pd.items():
			if n == 'id': self.id = v
			elif n == 'position': self.position = v
			elif n == 'value': self.value = v
			else: logger_projparse.warning('greysound: greysound_automationLane_point: unimplemented attrib: '+n)

	def write(self):
		out = {}
		out['id'] = self.id
		out['position'] = self.position
		out['value'] = self.value
		return out

class greysound_automationLane:
	def __init__(self):
		self.id = ""
		self.trackId = 0
		self.target = greysound_automationLane_target()
		self.points = []
		self.bypassed = False
		self.visible = False

	def read(self, pd):
		for n, v in pd.items():
			if n == 'id': self.id = v
			elif n == 'trackId': self.trackId = v
			elif n == 'target': self.target.read(v)
			elif n == 'points': 
				self.points = []
				for point in v:
					lane = greysound_automationLane_point()
					lane.read(point)
					self.points.append(lane)
			elif n == 'bypassed': self.bypassed = v
			elif n == 'visible': self.visible = v
			else: logger_projparse.warning('greysound: automationLane: unimplemented attrib: '+n)

	def write(self):
		out = {}
		out['id'] = self.id
		out['trackId'] = self.trackId
		out['target'] = self.target.write()
		out['points'] = [x.write() for x in self.points]
		out['bypassed'] = self.bypassed
		out['visible'] = self.visible
		return out

class greysound_track:
	def __init__(self):
		self.id = 1
		self.name = "Track"
		self.type = "AUDIO"
		self.color = "#888888"
		self.comments = ""
		self.timeBase = "TIME"
		self.channelCount = 1
		self.channelPans = [0]
		self.faderGainDb = 0
		self.muted = False
		self.solo = False
		self.armed = False
		self.inputMonitor = False
		self.position = 0
		self.outputRouting = None
		self.automationLanes = []

	def read(self, pd):
		for n, v in pd.items():
			if n == 'id': self.id = v
			elif n == 'name': self.name = v
			elif n == 'type': self.type = v
			elif n == 'color': self.color = v
			elif n == 'comments': self.comments = v
			elif n == 'timeBase': self.timeBase = v
			elif n == 'channelCount': self.channelCount = v
			elif n == 'channelPans': self.channelPans = v
			elif n == 'faderGainDb': self.faderGainDb = v
			elif n == 'muted': self.muted = v
			elif n == 'solo': self.solo = v
			elif n == 'armed': self.armed = v
			elif n == 'inputMonitor': self.inputMonitor = v
			elif n == 'position': self.position = v
			elif n == 'outputRouting': self.outputRouting = v
			elif n == 'automationLanes': 
				self.automationLanes = []
				for automationLane in v:
					lane = greysound_automationLane()
					lane.read(automationLane)
					self.automationLanes.append(lane)
			else: logger_projparse.warning('greysound: track: unimplemented attrib: '+n)

	def write(self):
		out = {}
		out['id'] = self.id
		out['name'] = self.name
		out['type'] = self.type
		out['color'] = self.color
		if self.comments: out['comments'] = self.comments
		out['timeBase'] = self.timeBase
		out['channelCount'] = self.channelCount
		out['channelPans'] = self.channelPans
		out['faderGainDb'] = self.faderGainDb
		out['muted'] = self.muted
		out['solo'] = self.solo
		out['armed'] = self.armed
		out['inputMonitor'] = self.inputMonitor
		out['position'] = self.position
		out['outputRouting'] = self.outputRouting
		out['automationLanes'] = [x.write() for x in self.automationLanes]
		return out

class greysound_session:
	def __init__(self):
		self.schemaVersion = 1
		self.metadata = {}
		self.tempo = 120
		self.tracks = []
		self.clips = []
		self.regions = []
		self.markers = []
		self.sends = []
		self.inserts = []
		self.preferredAudioInputDeviceId = None
		self.preferredAudioOutputDeviceId = None
		self.preferredMidiInputDeviceId = None
		self.preferredMidiInputDeviceLabel = None
		self.audioDeviceSnapshots = [{"id": "","label": "audioinput ()","kind": "INPUT"},{"id": "","label": "audiooutput ()","kind": "OUTPUT"}]
		self.midiDeviceSnapshots = {}
		self.loopRange = None
		self.loopEnabled = False
		self.selectionTrackIds = []
		self.metronomeEnabled = False
		self.countInEnabled = False
		self.playheadPosition = {"ticks": 0, "millis": 0}
		self.keySignature = {"root": "C", "quality": "major"}
		self.timeFormat = "min:sec"

	def read(self, pd):
		for n, v in pd.items():
			if n == 'schemaVersion': 
				self.schemaVersion = v
				if self.schemaVersion!=1:
					raise ProjectFileParserException('greysound: unsupported schema version')
			elif n == 'metadata': self.metadata = v
			elif n == 'tempo': self.tempo = v
			elif n == 'tracks': 
				self.tracks = []
				for t in v:
					o = greysound_track()
					o.read(t)
					self.tracks.append(o)
			elif n == 'clips': 
				self.clips = []
				for t in v:
					o = greysound_clip()
					o.read(t)
					self.clips.append(o)
			elif n == 'regions': 
				self.regions = []
				for t in v:
					o = greysound_region()
					o.read(t)
					self.regions.append(o)
			elif n == 'markers':
				self.markers = []
				for t in v:
					o = greysound_marker()
					o.read(t)
					self.markers.append(o)
			elif n == 'sends':
				self.sends = []
				for t in v:
					o = greysound_send()
					o.read(t)
					self.sends.append(o)
			elif n == 'inserts': 
				self.inserts = []
				for t in v:
					o = greysound_insert()
					o.read(t)
					self.inserts.append(o)
			elif n == 'preferredAudioInputDeviceId': self.preferredAudioInputDeviceId = v
			elif n == 'preferredAudioOutputDeviceId': self.preferredAudioOutputDeviceId = v
			elif n == 'preferredMidiInputDeviceId': self.preferredMidiInputDeviceId = v
			elif n == 'preferredMidiInputDeviceLabel': self.preferredMidiInputDeviceLabel = v
			elif n == 'audioDeviceSnapshots': self.audioDeviceSnapshots = v
			elif n == 'midiDeviceSnapshots': self.midiDeviceSnapshots = v
			elif n == 'loopRange': self.loopRange = v
			elif n == 'loopEnabled': self.loopEnabled = v
			elif n == 'selectionTrackIds': self.selectionTrackIds = v
			elif n == 'metronomeEnabled': self.metronomeEnabled = v
			elif n == 'countInEnabled': self.countInEnabled = v
			elif n == 'playheadPosition': self.playheadPosition = v
			elif n == 'keySignature': self.keySignature = v
			elif n == 'timeFormat': self.timeFormat = v
			else: logger_projparse.warning('greysound: project: unimplemented attrib: '+n)

	def load_from_file(self, input_file):
		f = open(input_file, 'r', encoding='utf8')
		try: gs_json = json.load(f)
		except: raise ProjectFileParserException('greysound: JSON Decoding Error')

		self.read(gs_json)

		if DEBUG_IN_OUT:
			f = open('debug_in.json', 'w')
			f.write(json.dumps(gs_json, indent = 2))
		
			f = open('debug_out.json', 'w')
			f.write(json.dumps(self.write(), indent = 2))

	def write(self):
		out = {}
		out['schemaVersion'] = self.schemaVersion
		out['metadata'] = self.metadata
		out['tempo'] = self.tempo
		out['tracks'] = [x.write() for x in self.tracks]
		out['clips'] = [x.write() for x in self.clips]
		out['regions'] = [x.write() for x in self.regions]
		out['markers'] = [x.write() for x in self.markers]
		out['sends'] = [x.write() for x in self.sends]
		out['inserts'] = [x.write() for x in self.inserts]
		out['preferredAudioInputDeviceId'] = self.preferredAudioInputDeviceId
		out['preferredAudioOutputDeviceId'] = self.preferredAudioOutputDeviceId
		out['preferredMidiInputDeviceId'] = self.preferredMidiInputDeviceId
		out['preferredMidiInputDeviceLabel'] = self.preferredMidiInputDeviceLabel
		out['audioDeviceSnapshots'] = self.audioDeviceSnapshots
		out['midiDeviceSnapshots'] = self.midiDeviceSnapshots
		out['loopRange'] = self.loopRange
		out['loopEnabled'] = self.loopEnabled
		out['selectionTrackIds'] = self.selectionTrackIds
		out['metronomeEnabled'] = self.metronomeEnabled
		out['countInEnabled'] = self.countInEnabled
		out['playheadPosition'] = self.playheadPosition
		out['keySignature'] = self.keySignature
		out['timeFormat'] = self.timeFormat
		return out