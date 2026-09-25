# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from lxml import etree
from objects.exceptions import ProjectFileParserException

DEBUG_IN_OUT = False

class jummbox_filter:
	def __init__(self, indict, starttxt):
		self.Filter = []
		self.FilterType = False
		self.SimpleCut = 10
		self.SimplePeak = 0
		self.SubFilters0 = []
		if indict and starttxt:
			if starttxt+'Filter' in indict: self.Filter = indict[starttxt+'Filter']
			if starttxt+'FilterType' in indict: self.FilterType = indict[starttxt+'FilterType']
			if starttxt+'SimpleCut' in indict: self.SimpleCut = indict[starttxt+'SimpleCut']
			if starttxt+'SimplePeak' in indict: self.SimplePeak = indict[starttxt+'SimplePeak']
			if starttxt+'SubFilters0' in indict: self.SubFilters0 = indict[starttxt+'SubFilters0']

	def write(self, indict, starttxt):
		indict[starttxt+'Filter'] = self.Filter
		indict[starttxt+'FilterType'] = self.FilterType
		indict[starttxt+'SimpleCut'] = self.SimpleCut
		indict[starttxt+'SimplePeak'] = self.SimplePeak
		indict[starttxt+'SubFilters0'] = self.SubFilters0

class jummbox_instrument_effects:
	def __init__(self):
		self.used = []

		self.pan = 0
		self.panDelay = 10

		self.transition = 'interrupt'
		self.clicklessTransition = False

		self.chord = 'arpeggio'
		self.fastTwoNoteArp = True
		self.arpeggioSpeed = 1

		self.chorus = 100

		self.reverb = 100

		self.echoSustain = 0
		self.echoDelayBeats = 0

		self.distortion = 0

		self.vibrato = 'light'
		self.vibratoDepth = 0.15
		self.vibratoDelay = 0
		self.vibratoSpeed = 10
		self.vibratoType = 0

		self.notefilter = jummbox_filter(None, None)

		self.bitcrusherQuantization = 14
		self.bitcrusherOctave = 8

		self.pitchShiftSemitones = 0

		self.detuneCents = 0

	def write(self, indict):
		indict['effects'] = self.used

		if 'transition type' in self.used:
			indict['transition'] = self.transition
			indict['clicklessTransition'] = self.clicklessTransition
	
		if 'chord type' in self.used:
			indict['chord'] = self.chord
			indict['fastTwoNoteArp'] = self.fastTwoNoteArp
			indict['arpeggioSpeed'] = self.arpeggioSpeed
	
		if 'note filter' in self.used:
			self.notefilter.write(indict, 'note')
	
		if 'pitch shift' in self.used:
			indict['pitchShiftSemitones'] = self.pitchShiftSemitones
	
		if 'detune' in self.used:
			indict['detuneCents'] = self.detuneCents

		if 'vibrato' in self.used:
			indict['vibrato'] = self.vibrato
			indict['vibratoDepth'] = self.vibratoDepth
			indict['vibratoDelay'] = self.vibratoDelay
			indict['vibratoSpeed'] = self.vibratoSpeed
			indict['vibratoType'] = self.vibratoType
	
		if 'distortion' in self.used:
			indict['distortion'] = self.distortion
	
		if 'bitcrusher' in self.used:
			indict['bitcrusherOctave'] = self.bitcrusherOctave
			indict['bitcrusherQuantization'] = self.bitcrusherQuantization
	
		if 'panning' in self.used:
			indict['pan'] = self.pan
			indict['panDelay'] = self.panDelay
	
		if 'chorus' in self.used:
			indict['chorus'] = self.chorus
	
		if 'echo' in self.used:
			indict['echoSustain'] = self.echoSustain
			indict['echoDelayBeats'] = self.echoDelayBeats
	
		if 'reverb' in self.used:
			indict['reverb'] = self.reverb
	
class jummbox_instrument:
	def __init__(self, indict=None):
		self.type = 'pitch'
		self.preset = None
		self.volume = 0
		self.fadeInSeconds = 0
		self.fadeOutTicks = -1
		self.filter = jummbox_filter(indict, 'eq')
		self.envelopes = []
		self.data = {}
		self.fx = jummbox_instrument_effects()
		self.envelopeSpeed = 12
		self.discreteEnvelope = False
		self.envelopes = []
		self.modChannels = [-1, -1, -1, -1, -1, -1]
		self.modInstruments = [0, 0, 0, 0, 0, 0]
		self.modSettings = [0, 0, 0, 0, 0, 0]
		self.modFilterTypes = [0, 0, 0, 0, 0, 0]
		self.modStatuses = []
		self.drums = {}
		if indict is not None: self.read(indict)

	def read(self, indict):
		self.filter = jummbox_filter(indict, 'eq')
		fx_obj = self.fx
		fx_obj.notefilter = jummbox_filter(indict, 'note')
		for n, v in indict.items():
			if n == 'type': self.type = v
			elif n == 'preset': self.preset = v
			elif n == 'volume': self.volume = v
			elif n == 'envelopeSpeed': self.envelopeSpeed = v
			elif n == 'discreteEnvelope': self.discreteEnvelope = v
			elif n == 'drums': self.drums = v
			elif n == 'modChannels': self.modChannels = v
			elif n == 'modInstruments': self.modInstruments = v
			elif n == 'modSettings': self.modSettings = v
			elif n == 'modStatuses': self.modStatuses = v
			elif n == 'modFilterTypes': self.modFilterTypes = v
			elif n == 'octaveScrollBar': self.octaveScrollBar = v
			elif n == 'fadeInSeconds': self.fadeInSeconds = v
			elif n == 'fadeOutTicks': self.fadeOutTicks = v
			elif n == 'effects': fx_obj.used = v
			elif n == 'transition': fx_obj.transition = v
			elif n == 'clicklessTransition': fx_obj.clicklessTransition = v
			elif n == 'pan': fx_obj.pan = v
			elif n == 'panDelay': fx_obj.panDelay = v
			elif n == 'chord': fx_obj.chord = v
			elif n == 'fastTwoNoteArp': fx_obj.fastTwoNoteArp = v
			elif n == 'arpeggioSpeed': fx_obj.arpeggioSpeed = v
			elif n == 'chorus': fx_obj.chorus = v
			elif n == 'reverb': fx_obj.reverb = v
			elif n == 'distortion': fx_obj.distortion = v
			elif n == 'echoSustain': fx_obj.echoSustain = v
			elif n == 'echoDelayBeats': fx_obj.echoDelayBeats = v
			elif n == 'bitcrusherQuantization': fx_obj.bitcrusherQuantization = v
			elif n == 'bitcrusherOctave': fx_obj.bitcrusherOctave = v
			elif n == 'vibrato': fx_obj.vibrato = v
			elif n == 'vibratoDepth': fx_obj.vibratoDepth = v
			elif n == 'vibratoDelay': fx_obj.vibratoDelay = v
			elif n == 'vibratoSpeed': fx_obj.vibratoSpeed = v
			elif n == 'vibratoType': fx_obj.vibratoType = v
			elif n == 'pitchShiftSemitones': fx_obj.pitchShiftSemitones = v
			elif n == 'detuneCents': fx_obj.detuneCents = v
			elif n == 'envelopes': self.envelopes = v
			elif n in ['eqFilter','eqFilterType','eqSimpleCut','eqSimplePeak','noteFilter','noteFilterType','noteSimpleCut','noteSimplePeak']: pass
			elif n.startswith('eqSubFilters') or n.startswith('noteSubFilters'): pass
			else: self.data[n] = v

	def write(self, b_format, b_version):
		jummbox_inst = {}
		jummbox_inst['type'] = self.type
		jummbox_inst['volume'] = self.volume
		self.filter.write(jummbox_inst, 'eq')
		if b_format == 'UltraBox': jummbox_inst['envelopeSpeed'] = self.envelopeSpeed
		if b_format == 'UltraBox': jummbox_inst['discreteEnvelope'] = self.discreteEnvelope
		if self.preset != None: jummbox_inst['preset'] = self.preset
		self.fx.write(jummbox_inst)
		jummbox_inst['volume'] = self.volume
		if self.type == 'drumset': 
			jummbox_inst['drums'] = self.drums
		else:
			jummbox_inst['fadeInSeconds'] = self.fadeInSeconds
			jummbox_inst['fadeOutTicks'] = self.fadeOutTicks
		for n, v in self.data.items(): jummbox_inst[n] = v
		if self.type == 'mod':
			jummbox_inst['modChannels'] = self.modChannels
			jummbox_inst['modInstruments'] = self.modInstruments
			jummbox_inst['modSettings'] = self.modSettings
			if b_format == 'UltraBox': jummbox_inst['modFilterTypes'] = self.modFilterTypes
			else: jummbox_inst['modStatuses'] = self.modStatuses
		jummbox_inst['envelopes'] = self.envelopes

		return jummbox_inst

class jummbox_note:
	__slots__ = ['pitches','points','continuesLastPattern']
	def __init__(self, indict=None):
		self.pitches = []
		self.points = []
		self.continuesLastPattern = None
		if indict is not None: self.read(indict)

	def read(self, indict):
		self.pitches = indict['pitches']
		self.points = [[x['tick'],x['pitchBend'],x['volume'],x['forMod']] for x in indict['points']]
		if 'continuesLastPattern' in indict: self.continuesLastPattern = indict['continuesLastPattern']

	def write(self):
		pat = {}
		pat['pitches'] = self.pitches
		pat['points'] = [{'tick': x[0],'pitchBend': x[1],'volume': x[2],'forMod': x[3]} for x in self.points]
		if self.continuesLastPattern != None: pat['continuesLastPattern'] = self.continuesLastPattern
		return pat


class jummbox_pattern:
	def __init__(self, indict=None):
		self.notes = []
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'notes' in indict: self.notes = [jummbox_note(x) for x in indict['notes']]

	def write(self):
		return {'notes': [x.write() for x in self.notes]}

class jummbox_channel:
	def __init__(self, indict=None):
		self.type = "pitch"
		self.name = ''
		self.instruments = []
		self.patterns = []
		self.sequence = []
		self.octaveScrollBar = 4
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'type' in indict: self.type = indict['type']
		if 'name' in indict: self.name = indict['name']
		if 'instruments' in indict: self.instruments = [jummbox_instrument(x) for x in indict['instruments']]
		if 'patterns' in indict: self.patterns = [jummbox_pattern(x) for x in indict['patterns']]
		if 'sequence' in indict: self.sequence = indict['sequence']
		if 'octaveScrollBar' in indict: self.octaveScrollBar = indict['octaveScrollBar']

	def write(self, b_format, b_version):
		jummbox_chan = {}
		jummbox_chan['type'] = self.type
		jummbox_chan['name'] = self.name
		jummbox_chan['instruments'] = [x.write(b_format, b_version) for x in self.instruments]
		jummbox_chan['patterns'] = [x.write() for x in self.patterns]
		jummbox_chan['sequence'] = self.sequence
		if self.type != 'drum': jummbox_chan['octaveScrollBar'] = self.octaveScrollBar
		return jummbox_chan


class jummbox_project:
	def __init__(self, indict=None):
		self.name = ""
		self.format = "BeepBox"
		self.version = 5
		self.scale = "Free"
		self.customScale = [True,False,False,False,False,False,False,False,False,False,False,False]
		self.keyOctave = 0
		self.key = "C"
		self.introBars = 0
		self.loopBars = 4
		self.beatsPerBar = 8
		self.ticksPerBeat = 4
		self.beatsPerMinute = 150
		self.reverb = 0
		self.masterGain = 1
		self.compressionThreshold = 1
		self.limitThreshold = 1
		self.limitDecay = 4
		self.limitRise = 4000
		self.limitRatio = 1
		self.compressionRatio = 1
		self.layeredInstruments = False
		self.patternInstruments = False
		self.channels = []
		self.customSamples = []
		if indict is not None: self.load(indict)

	def load(self, indict):
		if 'name' in indict: self.name = indict['name']
		if 'format' in indict: self.format = indict['format']
		if 'version' in indict: self.version = indict['version']
		if 'scale' in indict: self.scale = indict['scale']
		if 'key' in indict: self.key = indict['key']
		if 'keyOctave' in indict: self.keyOctave = indict['keyOctave']
		if 'customScale' in indict: self.customScale = indict['customScale']
		if 'customSamples' in indict: self.customSamples = indict['customSamples']
		if 'introBars' in indict: self.introBars = indict['introBars']
		if 'loopBars' in indict: self.loopBars = indict['loopBars']
		if 'beatsPerBar' in indict: self.beatsPerBar = indict['beatsPerBar']
		if 'ticksPerBeat' in indict: self.ticksPerBeat = indict['ticksPerBeat']
		if 'beatsPerMinute' in indict: self.beatsPerMinute = indict['beatsPerMinute']
		if 'reverb' in indict: self.reverb = indict['reverb']
		if 'masterGain' in indict: self.masterGain = indict['masterGain']
		if 'compressionThreshold' in indict: self.compressionThreshold = indict['compressionThreshold']
		if 'limitThreshold' in indict: self.limitThreshold = indict['limitThreshold']
		if 'limitDecay' in indict: self.limitDecay = indict['limitDecay']
		if 'limitRise' in indict: self.limitRise = indict['limitRise']
		if 'limitRatio' in indict: self.limitRatio = indict['limitRatio']
		if 'compressionRatio' in indict: self.compressionRatio = indict['compressionRatio']
		if 'layeredInstruments' in indict: self.layeredInstruments = indict['layeredInstruments']
		if 'patternInstruments' in indict: self.patternInstruments = indict['patternInstruments']
		if 'channels' in indict: self.channels = [jummbox_channel(x) for x in indict['channels']]

	def load_from_file(self, input_file):
		f = open(input_file, 'r', encoding='utf8')
		try: jummb_json = json.load(f)
		except: raise ProjectFileParserException('serato: JSON Decoding Error')

		self.load(jummb_json)

		if DEBUG_IN_OUT:
			f = open('debug_in.json', 'w')
			f.write(json.dumps(jummb_json, indent = 2))
		
			f = open('debug_out.json', 'w')
			f.write(json.dumps(self.dump(), indent = 2))

	def get_durpos(self):
		autodur = {}
		sequencelen = [self.beatsPerBar*self.ticksPerBeat for _ in range(len(self.channels[0].sequence))]
		for channel in self.channels:
			if channel.type == 'mod':
				nextbarfound = None
				modinst = channel.instruments[0]
				for num in range(6):
					autodef = [modinst.modChannels[num],modinst.modInstruments[num],modinst.modSettings[num]]
					if autodef == [-1, 0, 4]:
						nextbarfound = num
						break

				if nextbarfound != None:
					for n, p in enumerate(channel.patterns):
						for a in p.notes:
							if a.pitches[0] == 5-num: autodur[n+1] = a.points[0][0]

					for n, p in enumerate(channel.sequence):
						if p in autodur: sequencelen[n] = autodur[p]

		return sequencelen

	def dump(self):
		jummbox_proj = {}
		jummbox_proj['name'] = self.name
		jummbox_proj['format'] = self.format
		jummbox_proj['version'] = self.version
		jummbox_proj['scale'] = self.scale
		if self.format == 'UltraBox': jummbox_proj['customScale'] = self.customScale
		jummbox_proj['key'] = self.key
		if self.format == 'UltraBox': jummbox_proj['keyOctave'] = self.keyOctave
		jummbox_proj['introBars'] = self.introBars
		jummbox_proj['loopBars'] = self.loopBars
		jummbox_proj['beatsPerBar'] = self.beatsPerBar
		jummbox_proj['ticksPerBeat'] = self.ticksPerBeat
		jummbox_proj['beatsPerMinute'] = self.beatsPerMinute
		jummbox_proj['reverb'] = self.reverb
		jummbox_proj['masterGain'] = self.masterGain
		jummbox_proj['compressionThreshold'] = self.compressionThreshold
		jummbox_proj['limitThreshold'] = self.limitThreshold
		jummbox_proj['limitDecay'] = self.limitDecay
		jummbox_proj['limitRise'] = self.limitRise
		jummbox_proj['limitRatio'] = self.limitRatio
		jummbox_proj['compressionRatio'] = self.compressionRatio
		jummbox_proj['layeredInstruments'] = self.layeredInstruments
		jummbox_proj['patternInstruments'] = self.patternInstruments
		jummbox_proj['channels'] = [x.write(self.format, self.version) for x in self.channels]
		jummbox_proj['customSamples'] = self.customSamples
		return jummbox_proj