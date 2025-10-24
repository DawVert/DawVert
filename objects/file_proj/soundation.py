# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
logger_projparse = logging.getLogger('projparse')

# ============================================= device ============================================= 

class soundation_param:
	def __init__(self, pd):
		self.value = 0
		self.automation = []
		self.has_auto = False
		if pd != None: self.read(pd)

	def read(self, pd):
		for n, v in pd.items():
			if n == 'value': 
				self.value = v
			elif n == 'automation': 
				self.automation = v
				self.has_auto = True
			else: logger_projparse.warning('soundation: param: unimplemented attrib: '+n)

class soundation_paramset:
	def __init__(self):
		self.data = {}

	def add(self, name, value, automation):
		param_obj = soundation_param(None)
		param_obj.value = value
		param_obj.automation = automation
		param_obj.has_auto = True
		param_obj.exists = True
		self.data[name] = param_obj

	def add_from_sng(self, name, dictin):
		param_obj = soundation_param(dictin)
		self.data[name] = param_obj

	def get(self, name):
		if name in self.data:
			return self.data[name]
		else:
			param_obj = soundation_param(None)
			param_obj.value = 0
			param_obj.automation = []
			return param_obj

	def write(self, dictin):
		for n, x in self.data.items():
			param_data = {}
			param_data['value'] = x.value
			if x.has_auto: param_data['automation'] = x.automation
			dictin[n] = param_data

class soundation_device:
	def __init__(self, pd):
		self.rackName = None
		self.identifier = None
		self.bypass = None
		self.params = soundation_paramset()
		self.data = {}

		if pd != None:
			for n, v in pd.items():
				if n == 'bypass': self.bypass = v
				elif n == 'rackName': self.rackName = v
				elif n == 'identifier': self.identifier = v
				else: 
					if isinstance(v, dict) and 'value' in v: 
						self.params.add_from_sng(n, v)
					else: 
						self.data[n] = v

	def write(self):
		sng_device = {}
		if self.rackName != None: sng_device['rackName'] = self.rackName
		sng_device['identifier'] = self.identifier
		if self.bypass != None: sng_device['bypass'] = self.bypass
		self.params.write(sng_device)
		for name, param in self.data.items(): sng_device[name] = param
		return sng_device

# ============================================= track ============================================= 

class soundation_region:
	def __init__(self, pd):
		self.color = None
		self.position = 0
		self.autoStretchBpm = None
		self.contentPosition = 0
		self.file = None
		self.isAutoStretched = None
		self.isPattern = None
		self.length = 0
		self.loopcount = None
		self.muted = False
		self.name = ''
		self.notes = None
		self.reversed = None
		self.stretchMode = None
		self.stretchRate = None
		self.type = None
		self.pitchShiftSemitones = 0
		self.pitchShiftCents = 0
		self.formantCorrection = 0
		if pd != None: self.read(pd)

	def read(self, pd):
		for n, v in pd.items():
			if n == 'color': self.color = v
			elif n == 'position': self.position = v
			elif n == 'autoStretchBpm': self.autoStretchBpm = v
			elif n == 'contentPosition': self.contentPosition = v
			elif n == 'file': self.file = v
			elif n == 'isAutoStretched': self.isAutoStretched = v
			elif n == 'isPattern': self.isPattern = v
			elif n == 'length': self.length = v
			elif n == 'loopcount': self.loopcount = v
			elif n == 'muted': self.muted = v
			elif n == 'name': self.name = v
			elif n == 'notes': self.notes = v
			elif n == 'reversed': self.reversed = v
			elif n == 'stretchMode': self.stretchMode = v
			elif n == 'stretchRate': self.stretchRate = v
			elif n == 'type': self.type = v
			elif n == 'pitchShiftSemitones': self.pitchShiftSemitones = v
			elif n == 'pitchShiftCents': self.pitchShiftCents = v
			elif n == 'formantCorrection': self.formantCorrection = v
			else: logger_projparse.warning('soundation: region: unimplemented attrib: '+n)

	def write(self):
		sng_region = {}
		if self.color != None: sng_region['color'] = self.color
		sng_region['position'] = int(self.position)
		sng_region['length'] = int(self.length)
		if self.loopcount != None: sng_region['loopcount'] = self.loopcount
		sng_region['contentPosition'] = self.contentPosition
		sng_region['muted'] = self.muted
		sng_region['name'] = self.name
		if self.type != None: sng_region['type'] = self.type
		if self.type == 1: sng_region['autoStretchBpm'] = self.autoStretchBpm
		if self.isAutoStretched != None: sng_region['isAutoStretched'] = self.isAutoStretched
		if self.file != None: sng_region['file'] = self.file
		if self.notes != None: sng_region['notes'] = self.notes
		if self.reversed != None: sng_region['reversed'] = self.reversed
		if self.stretchMode != None: sng_region['stretchMode'] = self.stretchMode
		if self.stretchRate != None: sng_region['stretchRate'] = self.stretchRate
		if self.isPattern != None: sng_region['isPattern'] = self.isPattern
		sng_region['pitchShiftSemitones'] = self.pitchShiftSemitones
		sng_region['pitchShiftCents'] = self.pitchShiftCents
		sng_region['formantCorrection'] = self.formantCorrection
		return sng_region

class soundation_channel:
	def __init__(self, pd):
		self.name = ''
		self.type = ''
		self.mute = False
		self.solo = False
		self.volume = 1
		self.pan = 0.5
		self.color = None
		self.volumeAutomation = []
		self.panAutomation = []
		self.effects = []
		self.regions = []
		self.instrument = None
		self.userSetName = None
		if pd != None: self.read(pd)

	def read(self, pd):
		for n, v in pd.items():
			if n == 'name': self.name = v
			elif n == 'type': self.type = v
			elif n == 'color': self.color = v
			elif n == 'mute': self.mute = v
			elif n == 'solo': self.solo = v
			elif n == 'volume': self.volume = v
			elif n == 'pan': self.pan = v
			elif n == 'volumeAutomation': self.volumeAutomation = v
			elif n == 'panAutomation': self.panAutomation = v
			elif n == 'effects': self.effects = [soundation_device(x) for x in v]
			elif n == 'instrument': self.instrument = soundation_device(v)
			elif n == 'userSetName': self.userSetName = v
			elif n == 'regions': self.regions = [soundation_region(x) for x in v]
			else: logger_projparse.warning('soundation: channel: unimplemented attrib: '+n)

	def write(self):
		sng_channel = {}
		sng_channel['name'] = self.name
		sng_channel['type'] = self.type
		if self.color: sng_channel['color'] = self.color
		sng_channel['mute'] = self.mute
		sng_channel['solo'] = self.solo
		sng_channel['volume'] = self.volume
		sng_channel['pan'] = self.pan
		sng_channel['volumeAutomation'] = self.volumeAutomation
		sng_channel['panAutomation'] = self.panAutomation
		sng_channel['effects'] = [x.write() for x in self.effects]
		if self.instrument: sng_channel['instrument'] = self.instrument.write()
		if self.userSetName != None: sng_channel['userSetName'] = self.userSetName
		sng_channel['regions'] = [x.write() for x in self.regions]
		return sng_channel

# ============================================= song ============================================= 

class soundation_project:
	def __init__(self, pd):
		self.version = 2.3
		self.studio = "3.124.5"
		self.bpm = 120
		self.timeSignature = "4/4"
		self.looping = False
		self.loopStart = 0
		self.loopEnd = 4102
		self.channels = []
		if pd != None: self.read(pd)

	def read(self, pd):
		for n, v in pd.items():
			if n == 'version': self.version = v
			elif n == 'studio': self.studio = v
			elif n == 'bpm': self.bpm = v
			elif n == 'timeSignature': self.timeSignature = v
			elif n == 'looping': self.looping = v
			elif n == 'loopStart': self.loopStart = v
			elif n == 'loopEnd': self.loopEnd = v
			elif n == 'channels': 
				for channel in v: self.channels.append(soundation_channel(channel))
			else: logger_projparse.warning('soundation: project: unimplemented attrib: '+n)

	def write(self):
		sng_proj = {}
		sng_proj['version'] = self.version
		sng_proj['studio'] = self.studio
		sng_proj['bpm'] = self.bpm
		sng_proj['timeSignature'] = self.timeSignature
		sng_proj['looping'] = self.looping
		sng_proj['loopStart'] = self.loopStart
		sng_proj['loopEnd'] = self.loopEnd
		sng_proj['channels'] = [x.write() for x in self.channels]
		return sng_proj