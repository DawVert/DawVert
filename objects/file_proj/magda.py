
import json, zlib

DEBUGSTUFF = False

# =========================================== clip ===========================================

class magda_clip_auto_handle:
	def __init__(self, indict=None):
		self.dx = 0
		self.dy = 0
		self.linked = True
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'dx' in indict: self.dx = indict['dx']
		if 'dy' in indict: self.dy = indict['dy']
		if 'linked' in indict: self.linked = indict['linked']

	def write(self):
		o = {}
		o['dx'] = self.dx
		o['dy'] = self.dy
		o['linked'] = self.linked
		return o

class magda_clip_auto_midiCCData:
	def __init__(self, indict=None):
		self.controller = 0
		self.beatPosition = 0
		self.value = 0
		self.curveType = 0
		self.tension = 0.0
		self.inHandle = magda_clip_auto_handle()
		self.outHandle = magda_clip_auto_handle()
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'controller' in indict: self.controller = indict['controller']
		if 'beatPosition' in indict: self.beatPosition = indict['beatPosition']
		if 'value' in indict: self.value = indict['value']
		if 'curveType' in indict: self.curveType = indict['curveType']
		if 'tension' in indict: self.tension = indict['tension']
		if 'inHandle' in indict: self.inHandle.read(indict['inHandle'])
		if 'outHandle' in indict: self.outHandle.read(indict['outHandle'])

	def write(self):
		o = {}
		o['controller'] = self.controller
		o['value'] = self.value
		o['beatPosition'] = self.beatPosition
		o['curveType'] = self.curveType
		o['tension'] = self.tension
		o['inHandle'] = self.inHandle.write()
		o['outHandle'] = self.outHandle.write()
		return o

class magda_clip_auto_midiPitchBendData:
	def __init__(self, indict=None):
		self.beatPosition = 0
		self.value = 0
		self.curveType = 0
		self.tension = 0.0
		self.inHandle = magda_clip_auto_handle()
		self.outHandle = magda_clip_auto_handle()
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'beatPosition' in indict: self.beatPosition = indict['beatPosition']
		if 'value' in indict: self.value = indict['value']
		if 'curveType' in indict: self.curveType = indict['curveType']
		if 'tension' in indict: self.tension = indict['tension']
		if 'inHandle' in indict: self.inHandle.read(indict['inHandle'])
		if 'outHandle' in indict: self.outHandle.read(indict['outHandle'])

	def write(self):
		o = {}
		o['value'] = self.value
		o['beatPosition'] = self.beatPosition
		o['curveType'] = self.curveType
		o['tension'] = self.tension
		o['inHandle'] = self.inHandle.write()
		o['outHandle'] = self.outHandle.write()
		return o

class magda_clip_audio_source:
	def __init__(self, indict=None):
		self.filePath = ''
		self.durationSeconds = 0
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'filePath' in indict: self.filePath = indict['filePath']
		if 'durationSeconds' in indict: self.durationSeconds = indict['durationSeconds']

	def write(self):
		o = {}
		o['filePath'] = self.filePath
		o['durationSeconds'] = self.durationSeconds
		return o

class magda_clip_audio_interpretation:
	def __init__(self, indict=None):
		self.bpm = 120
		self.totalBeats = 4
		self.totalBeatsLocked = False
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'bpm' in indict: self.bpm = indict['bpm']
		if 'totalBeats' in indict: self.totalBeats = indict['totalBeats']
		if 'totalBeatsLocked' in indict: self.totalBeatsLocked = indict['totalBeatsLocked']

	def write(self):
		o = {}
		o['bpm'] = self.bpm
		o['totalBeats'] = self.totalBeats
		o['totalBeatsLocked'] = self.totalBeatsLocked
		return o

class magda_clip_audio_playback:
	def __init__(self, indict=None):
		self.offsetSeconds = 0.0
		self.offsetBeats = 0.0
		self.loopStartSeconds = 0.0
		self.loopLengthSeconds = 1
		self.loopStartBeats = 0.0
		self.loopLengthBeats = 0.0
		self.speedRatio = 1.0
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'offsetSeconds' in indict: self.offsetSeconds = indict['offsetSeconds']
		if 'offsetBeats' in indict: self.offsetBeats = indict['offsetBeats']
		if 'loopStartSeconds' in indict: self.loopStartSeconds = indict['loopStartSeconds']
		if 'loopLengthSeconds' in indict: self.loopLengthSeconds = indict['loopLengthSeconds']
		if 'loopStartBeats' in indict: self.loopStartBeats = indict['loopStartBeats']
		if 'loopLengthBeats' in indict: self.loopLengthBeats = indict['loopLengthBeats']
		if 'speedRatio' in indict: self.speedRatio = indict['speedRatio']
	
	def write(self):
		o = {}
		o['offsetSeconds'] = self.offsetSeconds
		o['offsetBeats'] = self.offsetBeats
		o['loopStartSeconds'] = self.loopStartSeconds
		o['loopLengthSeconds'] = self.loopLengthSeconds
		o['loopStartBeats'] = self.loopStartBeats
		o['loopLengthBeats'] = self.loopLengthBeats
		o['speedRatio'] = self.speedRatio
		return o

class magda_clip_audio:
	def __init__(self, indict=None):
		self.source = magda_clip_audio_source()
		self.interpretation = magda_clip_audio_interpretation()
		self.playback = magda_clip_audio_playback()
		self.warpEnabled = False
		self.warpMarkers = {}
		self.timeStretchMode = 0
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'source' in indict: self.source.read(indict['source'])
		if 'interpretation' in indict: self.interpretation.read(indict['interpretation'])
		if 'playback' in indict: self.playback.read(indict['playback'])
		if 'warpEnabled' in indict: self.warpEnabled = indict['warpEnabled']
		if 'warpMarkers' in indict: self.warpMarkers = indict['warpMarkers']
		if 'timeStretchMode' in indict: self.timeStretchMode = indict['timeStretchMode']

	def write(self):
		o = {}
		o['source'] = self.source.write()
		o['interpretation'] = self.interpretation.write()
		o['playback'] = self.playback.write()
		if self.warpEnabled: o['warpEnabled'] = self.warpEnabled
		if self.warpMarkers: o['warpMarkers'] = self.warpMarkers
		if self.timeStretchMode: o['timeStretchMode'] = self.timeStretchMode
		return o

class magda_clip_midiNote:
	def __init__(self, indict=None):
		self.noteNumber = 60
		self.velocity = 100
		self.startBeat = 0
		self.lengthBeats = 1
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'noteNumber' in indict: self.noteNumber = indict['noteNumber']
		if 'velocity' in indict: self.velocity = indict['velocity']
		if 'startBeat' in indict: self.startBeat = indict['startBeat']
		if 'lengthBeats' in indict: self.lengthBeats = indict['lengthBeats']

	def write(self):
		o = {}
		o['noteNumber'] = self.noteNumber
		o['velocity'] = self.velocity
		o['startBeat'] = self.startBeat
		o['lengthBeats'] = self.lengthBeats
		return o

class magda_clip:
	def __init__(self, indict=None):
		self.id = 0
		self.trackId = 1
		self.name = ""
		self.colour = "FF5588AA"
		self.type = 1
		self.view = 0
		self.loopEnabled = False
		self.sceneIndex = -1
		self.launchMode = 0
		self.launchQuantize = 4
		self.followAction = 0
		self.followActionDelayBeats = 0.0
		self.followActionLoopCount = 1
		self.placement = {}
		self.gridAutoGrid = True
		self.gridNumerator = 1
		self.gridDenominator = 4
		self.gridSnapEnabled = True
		self.volumeDB = 0.0
		self.gainDB = 0.0
		self.pan = 0.0
		self.fadeIn = 0.0
		self.fadeOut = 0.0
		self.fadeInType = 1
		self.fadeOutType = 1
		self.fadeInBehaviour = 0
		self.fadeOutBehaviour = 0
		self.autoCrossfade = False
		self.launchFadeSamples = 256
		self.pitchChange = 0.0
		self.transpose = 0
		self.autoPitch = False
		self.autoPitchMode = 0
		self.isReversed = False
		self.autoDetectBeats = False
		self.beatSensitivity = 0.5
		self.leftChannelActive = True
		self.rightChannelActive = True
		self.autoTempo = False
		self.loopLengthBeats = 0
		self.midiNotes = []
		self.audio = None
		self.midiCCData = []
		self.midiPitchBendData = []
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'id' in indict: self.id = indict['id']
		if 'trackId' in indict: self.trackId = indict['trackId']
		if 'name' in indict: self.name = indict['name']
		if 'colour' in indict: self.colour = indict['colour']
		if 'type' in indict: self.type = indict['type']
		if 'view' in indict: self.view = indict['view']
		if 'loopEnabled' in indict: self.loopEnabled = indict['loopEnabled']
		if 'sceneIndex' in indict: self.sceneIndex = indict['sceneIndex']
		if 'launchMode' in indict: self.launchMode = indict['launchMode']
		if 'launchQuantize' in indict: self.launchQuantize = indict['launchQuantize']
		if 'followAction' in indict: self.followAction = indict['followAction']
		if 'followActionDelayBeats' in indict: self.followActionDelayBeats = indict['followActionDelayBeats']
		if 'followActionLoopCount' in indict: self.followActionLoopCount = indict['followActionLoopCount']
		if 'placement' in indict: self.placement = indict['placement']
		if 'gridAutoGrid' in indict: self.gridAutoGrid = indict['gridAutoGrid']
		if 'gridNumerator' in indict: self.gridNumerator = indict['gridNumerator']
		if 'gridDenominator' in indict: self.gridDenominator = indict['gridDenominator']
		if 'gridSnapEnabled' in indict: self.gridSnapEnabled = indict['gridSnapEnabled']
		if 'volumeDB' in indict: self.volumeDB = indict['volumeDB']
		if 'gainDB' in indict: self.gainDB = indict['gainDB']
		if 'pan' in indict: self.pan = indict['pan']
		if 'fadeIn' in indict: self.fadeIn = indict['fadeIn']
		if 'fadeOut' in indict: self.fadeOut = indict['fadeOut']
		if 'fadeInType' in indict: self.fadeInType = indict['fadeInType']
		if 'fadeOutType' in indict: self.fadeOutType = indict['fadeOutType']
		if 'fadeInBehaviour' in indict: self.fadeInBehaviour = indict['fadeInBehaviour']
		if 'fadeOutBehaviour' in indict: self.fadeOutBehaviour = indict['fadeOutBehaviour']
		if 'autoCrossfade' in indict: self.autoCrossfade = indict['autoCrossfade']
		if 'launchFadeSamples' in indict: self.launchFadeSamples = indict['launchFadeSamples']
		if 'pitchChange' in indict: self.pitchChange = indict['pitchChange']
		if 'transpose' in indict: self.transpose = indict['transpose']
		if 'autoPitch' in indict: self.autoPitch = indict['autoPitch']
		if 'autoPitchMode' in indict: self.autoPitchMode = indict['autoPitchMode']
		if 'isReversed' in indict: self.isReversed = indict['isReversed']
		if 'autoDetectBeats' in indict: self.autoDetectBeats = indict['autoDetectBeats']
		if 'beatSensitivity' in indict: self.beatSensitivity = indict['beatSensitivity']
		if 'leftChannelActive' in indict: self.leftChannelActive = indict['leftChannelActive']
		if 'rightChannelActive' in indict: self.rightChannelActive = indict['rightChannelActive']
		if 'autoTempo' in indict: self.autoTempo = indict['autoTempo']
		if 'loopLengthBeats' in indict: self.loopLengthBeats = indict['loopLengthBeats']
		if 'midiNotes' in indict: 
			self.midiNotes = []
			for x in indict['midiNotes']: 
				self.midiNotes.append(magda_clip_midiNote(x))
		if 'audio' in indict: 
			self.audio = magda_clip_audio(indict['audio'])
		if 'midiCCData' in indict: 
			self.midiCCData = []
			for x in indict['midiCCData']: 
				self.midiCCData.append(magda_clip_auto_midiCCData(x))
		if 'midiPitchBendData' in indict: 
			self.midiPitchBendData = []
			for x in indict['midiPitchBendData']:
				self.midiPitchBendData.append(magda_clip_auto_midiPitchBendData(x))

	def write(self):
		o = {}
		o['id'] = self.id
		o['trackId'] = self.trackId
		o['name'] = self.name
		o['colour'] = self.colour
		o['type'] = self.type
		o['view'] = self.view
		o['loopEnabled'] = self.loopEnabled
		o['sceneIndex'] = self.sceneIndex
		o['launchMode'] = self.launchMode
		o['launchQuantize'] = self.launchQuantize
		o['followAction'] = self.followAction
		o['followActionDelayBeats'] = self.followActionDelayBeats
		o['followActionLoopCount'] = self.followActionLoopCount
		o['placement'] = self.placement
		o['gridAutoGrid'] = self.gridAutoGrid
		o['gridNumerator'] = self.gridNumerator
		o['gridDenominator'] = self.gridDenominator
		o['gridSnapEnabled'] = self.gridSnapEnabled
		o['volumeDB'] = self.volumeDB
		o['gainDB'] = self.gainDB
		o['pan'] = self.pan
		o['fadeIn'] = self.fadeIn
		o['fadeOut'] = self.fadeOut
		o['fadeInType'] = self.fadeInType
		o['fadeOutType'] = self.fadeOutType
		o['fadeInBehaviour'] = self.fadeInBehaviour
		o['fadeOutBehaviour'] = self.fadeOutBehaviour
		o['autoCrossfade'] = self.autoCrossfade
		o['launchFadeSamples'] = self.launchFadeSamples
		o['pitchChange'] = self.pitchChange
		o['transpose'] = self.transpose
		o['autoPitch'] = self.autoPitch
		o['autoPitchMode'] = self.autoPitchMode
		o['isReversed'] = self.isReversed
		o['autoDetectBeats'] = self.autoDetectBeats
		o['beatSensitivity'] = self.beatSensitivity
		o['leftChannelActive'] = self.leftChannelActive
		o['rightChannelActive'] = self.rightChannelActive
		o['autoTempo'] = self.autoTempo
		if self.loopLengthBeats: o['loopLengthBeats'] = self.loopLengthBeats
		if self.audio: o['audio'] = self.audio.write()
		o['midiNotes'] = [x.write() for x in self.midiNotes]
		if self.midiCCData: o['midiCCData'] = [x.write() for x in self.midiCCData]
		if self.midiPitchBendData: o['midiPitchBendData'] = [x.write() for x in self.midiPitchBendData]
		return o

# =========================================== chainelement ===========================================

class magda_chainElement_rack_chain:
	def __init__(self, indict=None):
		self.id = 1
		self.name = ""
		self.outputIndex = 0
		self.muted = False
		self.solo = False
		self.bypassed = False
		self.volume = 0.0
		self.pan = 0.0
		self.expanded = True
		self.elements = []
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'id' in indict: self.id = indict['id']
		if 'name' in indict: self.name = indict['name']
		if 'outputIndex' in indict: self.outputIndex = indict['outputIndex']
		if 'muted' in indict: self.muted = indict['muted']
		if 'solo' in indict: self.solo = indict['solo']
		if 'bypassed' in indict: self.bypassed = indict['bypassed']
		if 'volume' in indict: self.volume = indict['volume']
		if 'pan' in indict: self.pan = indict['pan']
		if 'expanded' in indict: self.expanded = indict['expanded']
		if 'elements' in indict: self.elements = indict['elements']
	
	def write(self):
		o = {}
		o['id'] = self.id
		o['name'] = self.name
		o['outputIndex'] = self.outputIndex
		o['muted'] = self.muted
		o['solo'] = self.solo
		o['bypassed'] = self.bypassed
		o['volume'] = self.volume
		o['pan'] = self.pan
		o['expanded'] = self.expanded
		o['elements'] = self.elements
		return o

class magda_chainElement_rack:
	def __init__(self, indict=None):
		self.id = 0
		self.name = ""
		self.bypassed = False
		self.expanded = True
		self.modPanelOpen = False
		self.paramPanelOpen = False
		self.volume = 0.0
		self.pan = 0.0,
		self.chains = []
		self.macros = []
		self.mods = []
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'id' in indict: self.id = indict['id']
		if 'name' in indict: self.name = indict['name']
		if 'bypassed' in indict: self.bypassed = indict['bypassed']
		if 'expanded' in indict: self.expanded = indict['expanded']
		if 'modPanelOpen' in indict: self.modPanelOpen = indict['modPanelOpen']
		if 'paramPanelOpen' in indict: self.paramPanelOpen = indict['paramPanelOpen']
		if 'volume' in indict: self.volume = indict['volume']
		if 'pan' in indict: self.pan = indict['pan']
		if 'chains' in indict: 
			self.chains = []
			for x in indict['chains']:
				self.chains.append(magda_chainElement_rack_chain(x))
		if 'macros' in indict: 
			self.macros = []
			for x in indict['macros']:
				self.macros.append(magda_macros(x))
		if 'mods' in indict: self.mods = indict['mods']

	def write(self):
		o = {}
		o['id'] = self.id
		o['name'] = self.name
		o['bypassed'] = self.bypassed
		o['expanded'] = self.expanded
		o['modPanelOpen'] = self.modPanelOpen
		o['paramPanelOpen'] = self.paramPanelOpen
		o['volume'] = self.volume
		o['pan'] = self.pan
		o['chains'] = [x.write() for x in self.chains]
		o['macros'] = [x.write() for x in self.macros]
		o['mods'] = self.mods
		return o

class magda_chainElement_device_param:
	def __init__(self, indict=None):
		self.paramIndex = 0
		self.name = ""
		self.unit = ""
		self.minValue = 0.0
		self.maxValue = 1.0
		self.defaultValue = 0.0
		self.currentValue = 0.0
		self.teMinValue = 0.0
		self.teMaxValue = 1.0
		self.scale = 0
		self.skewFactor = 1.0
		self.scaleAnchor = 0.0
		self.displayFormat = 0
		self.modulatable = False
		self.bipolarModulation = False
		self.gateSlotIndex = -1
		self.gateNegated = False
		self.hidden = False
		self.choices = []
		self.labelTicks = []
		self.valueTable = []
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'paramIndex' in indict: self.paramIndex = indict['paramIndex']
		if 'name' in indict: self.name = indict['name']
		if 'unit' in indict: self.unit = indict['unit']
		if 'minValue' in indict: self.minValue = indict['minValue']
		if 'maxValue' in indict: self.maxValue = indict['maxValue']
		if 'defaultValue' in indict: self.defaultValue = indict['defaultValue']
		if 'currentValue' in indict: self.currentValue = indict['currentValue']
		if 'teMinValue' in indict: self.teMinValue = indict['teMinValue']
		if 'teMaxValue' in indict: self.teMaxValue = indict['teMaxValue']
		if 'scale' in indict: self.scale = indict['scale']
		if 'skewFactor' in indict: self.skewFactor = indict['skewFactor']
		if 'scaleAnchor' in indict: self.scaleAnchor = indict['scaleAnchor']
		if 'displayFormat' in indict: self.displayFormat = indict['displayFormat']
		if 'modulatable' in indict: self.modulatable = indict['modulatable']
		if 'bipolarModulation' in indict: self.bipolarModulation = indict['bipolarModulation']
		if 'gateSlotIndex' in indict: self.gateSlotIndex = indict['gateSlotIndex']
		if 'gateNegated' in indict: self.gateNegated = indict['gateNegated']
		if 'hidden' in indict: self.hidden = indict['hidden']
		if 'choices' in indict: self.choices = indict['choices']
		if 'labelTicks' in indict: self.labelTicks = indict['labelTicks']
		if 'valueTable' in indict: self.valueTable = indict['valueTable']
	
	def write(self):
		o = {}
		o['paramIndex'] = self.paramIndex
		o['name'] = self.name
		o['unit'] = self.unit
		o['minValue'] = self.minValue
		o['maxValue'] = self.maxValue
		o['defaultValue'] = self.defaultValue
		o['currentValue'] = self.currentValue
		o['teMinValue'] = self.teMinValue
		o['teMaxValue'] = self.teMaxValue
		o['scale'] = self.scale
		o['skewFactor'] = self.skewFactor
		o['scaleAnchor'] = self.scaleAnchor
		o['displayFormat'] = self.displayFormat
		o['modulatable'] = self.modulatable
		o['bipolarModulation'] = self.bipolarModulation
		o['gateSlotIndex'] = self.gateSlotIndex
		o['gateNegated'] = self.gateNegated
		o['hidden'] = self.hidden
		o['choices'] = self.choices
		o['labelTicks'] = self.labelTicks
		o['valueTable'] = self.valueTable
		return o

class magda_chainElement_device:
	def __init__(self, indict=None):
		self.id = 0
		self.name = ""
		self.pluginId = ""
		self.manufacturer = ""
		self.format = 0
		self.isInstrument = True
		self.deviceType = 0
		self.uniqueId = ""
		self.fileOrIdentifier = ""
		self.bypassed = False
		self.expanded = True
		self.modPanelOpen = False
		self.gainPanelOpen = False
		self.paramPanelOpen = False
		self.aiPanelOpen = False
		self.parameters = []
		self.visibleParameters = []
		self.gainValue = 1.0
		self.gainDb = 0.0
		self.macros = []
		self.mods = []
		self.currentParameterPage = 0
		self.pluginState = ""
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'id' in indict: self.id = indict['id']
		if 'name' in indict: self.name = indict['name']
		if 'pluginId' in indict: self.pluginId = indict['pluginId']
		if 'manufacturer' in indict: self.manufacturer = indict['manufacturer']
		if 'format' in indict: self.format = indict['format']
		if 'isInstrument' in indict: self.isInstrument = indict['isInstrument']
		if 'deviceType' in indict: self.deviceType = indict['deviceType']
		if 'uniqueId' in indict: self.uniqueId = indict['uniqueId']
		if 'fileOrIdentifier' in indict: self.fileOrIdentifier = indict['fileOrIdentifier']
		if 'bypassed' in indict: self.bypassed = indict['bypassed']
		if 'expanded' in indict: self.expanded = indict['expanded']
		if 'modPanelOpen' in indict: self.modPanelOpen = indict['modPanelOpen']
		if 'gainPanelOpen' in indict: self.gainPanelOpen = indict['gainPanelOpen']
		if 'paramPanelOpen' in indict: self.paramPanelOpen = indict['paramPanelOpen']
		if 'aiPanelOpen' in indict: self.aiPanelOpen = indict['aiPanelOpen']
		if 'parameters' in indict: 
			self.parameters = []
			for x in indict['parameters']:
				self.parameters.append(magda_chainElement_device_param(x))
		if 'visibleParameters' in indict: self.visibleParameters = indict['visibleParameters']
		if 'gainValue' in indict: self.gainValue = indict['gainValue']
		if 'gainDb' in indict: self.gainDb = indict['gainDb']
		if 'macros' in indict: 
			self.macros = []
			for x in indict['macros']:
				self.macros.append(magda_macros(x))
		if 'mods' in indict: self.mods = indict['mods']
		if 'currentParameterPage' in indict: self.currentParameterPage = indict['currentParameterPage']
		if 'pluginState' in indict: self.pluginState = indict['pluginState']

	def write(self):
		o = {}
		o['id'] = self.id
		o['name'] = self.name
		o['pluginId'] = self.pluginId
		o['manufacturer'] = self.manufacturer
		o['format'] = self.format
		o['isInstrument'] = self.isInstrument
		o['deviceType'] = self.deviceType
		o['uniqueId'] = self.uniqueId
		o['fileOrIdentifier'] = self.fileOrIdentifier
		o['bypassed'] = self.bypassed
		o['expanded'] = self.expanded
		o['modPanelOpen'] = self.modPanelOpen
		o['gainPanelOpen'] = self.gainPanelOpen
		o['paramPanelOpen'] = self.paramPanelOpen
		o['aiPanelOpen'] = self.aiPanelOpen
		o['parameters'] = [x.write() for x in self.parameters]
		o['visibleParameters'] = self.visibleParameters
		o['gainValue'] = self.gainValue
		o['gainDb'] = self.gainDb
		o['macros'] = [x.write() for x in self.macros]
		o['mods'] = self.mods
		o['currentParameterPage'] = self.currentParameterPage
		o['pluginState'] = self.pluginState
		return o

# =========================================== track ===========================================

class magda_track_mod_curvePoint:
	def __init__(self, indict=None):
		self.phase = 0
		self.value = 0
		self.tension = 0
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'phase' in indict: self.phase = indict['phase']
		if 'value' in indict: self.value = indict['value']
		if 'tension' in indict: self.tension = indict['tension']

	def write(self):
		o = {}
		o['phase'] = self.phase
		o['value'] = self.value
		o['tension'] = self.tension
		return o

class magda_track_mod_link:
	def __init__(self, indict=None):
		self.target = {}
		self.amount = 0
		self.bipolar = False
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'target' in indict: self.target = indict['target']
		if 'amount' in indict: self.amount = indict['amount']
		if 'bipolar' in indict: self.bipolar = indict['bipolar']

	def write(self):
		o = {}
		o['target'] = self.target
		o['amount'] = self.amount
		o['bipolar'] = self.bipolar
		return o

class magda_track_mod:
	def __init__(self, indict=None):
		self.id = 0
		self.name = ""
		self.type = 0
		self.enabled = True
		self.rate = 1.0
		self.waveform = 0
		self.phase = 0.0
		self.phaseOffset = 0.0
		self.value = 0.0
		self.tempoSync = False
		self.syncDivision = 4
		self.triggerMode = 0
		self.oneShot = False
		self.useLoopRegion = False
		self.loopStart = 0.0
		self.loopEnd = 1.0
		self.midiChannel = 0
		self.midiNote = -1
		self.audioAttackMs = 1.0
		self.audioReleaseMs = 100.0
		self.curvePreset = 0
		self.curvePoints = []
		self.links = []
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'id' in indict: self.id = indict['id']
		if 'name' in indict: self.name = indict['name']
		if 'type' in indict: self.type = indict['type']
		if 'enabled' in indict: self.enabled = indict['enabled']
		if 'rate' in indict: self.rate = indict['rate']
		if 'waveform' in indict: self.waveform = indict['waveform']
		if 'phase' in indict: self.phase = indict['phase']
		if 'phaseOffset' in indict: self.phaseOffset = indict['phaseOffset']
		if 'value' in indict: self.value = indict['value']
		if 'tempoSync' in indict: self.tempoSync = indict['tempoSync']
		if 'syncDivision' in indict: self.syncDivision = indict['syncDivision']
		if 'triggerMode' in indict: self.triggerMode = indict['triggerMode']
		if 'oneShot' in indict: self.oneShot = indict['oneShot']
		if 'useLoopRegion' in indict: self.useLoopRegion = indict['useLoopRegion']
		if 'loopStart' in indict: self.loopStart = indict['loopStart']
		if 'loopEnd' in indict: self.loopEnd = indict['loopEnd']
		if 'midiChannel' in indict: self.midiChannel = indict['midiChannel']
		if 'midiNote' in indict: self.midiNote = indict['midiNote']
		if 'audioAttackMs' in indict: self.audioAttackMs = indict['audioAttackMs']
		if 'audioReleaseMs' in indict: self.audioReleaseMs = indict['audioReleaseMs']
		if 'curvePreset' in indict: self.curvePreset = indict['curvePreset']
		if 'curvePoints' in indict: 
			self.curvePoints = []
			for x in indict['curvePoints']:
				self.curvePoints.append(magda_track_mod_curvePoint(x))
		if 'links' in indict: 
			self.links = []
			for x in indict['links']:
				self.links.append(magda_track_mod_link(x))
	
	def write(self):
		o = {}
		o['id'] = self.id
		o['name'] = self.name
		o['type'] = self.type
		o['enabled'] = self.enabled
		o['rate'] = self.rate
		o['waveform'] = self.waveform
		o['phase'] = self.phase
		o['phaseOffset'] = self.phaseOffset
		o['value'] = self.value
		o['tempoSync'] = self.tempoSync
		o['syncDivision'] = self.syncDivision
		o['triggerMode'] = self.triggerMode
		o['oneShot'] = self.oneShot
		o['useLoopRegion'] = self.useLoopRegion
		o['loopStart'] = self.loopStart
		o['loopEnd'] = self.loopEnd
		o['midiChannel'] = self.midiChannel
		o['midiNote'] = self.midiNote
		o['audioAttackMs'] = self.audioAttackMs
		o['audioReleaseMs'] = self.audioReleaseMs
		o['curvePreset'] = self.curvePreset
		o['curvePoints'] = [x.write() for x in self.curvePoints]
		o['links'] = [x.write() for x in self.links]
		return o

class magda_macros:
	def __init__(self, indict=None):
		self.id = 0
		self.name = ""
		self.value = 0.5
		self.links = []
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'id' in indict: self.id = indict['id']
		if 'name' in indict: self.name = indict['name']
		if 'value' in indict: self.value = indict['value']
		if 'links' in indict: self.links = indict['links']

	def write(self):
		o = {}
		o['id'] = self.id
		o['name'] = self.name
		o['value'] = self.value
		o['links'] = self.links
		return o

class magda_track_viewSetting:
	def __init__(self, indict=None):
		self.visible = True
		self.locked = False
		self.collapsed = False
		self.height = 80
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'visible' in indict: self.visible = indict['visible']
		if 'locked' in indict: self.locked = indict['locked']
		if 'collapsed' in indict: self.collapsed = indict['collapsed']
		if 'height' in indict: self.height = indict['height']

	def write(self):
		o = {}
		o['visible'] = self.visible
		o['locked'] = self.locked
		o['collapsed'] = self.collapsed
		o['height'] = self.height
		return o

class magda_track_send:
	def __init__(self, indict=None):
		self.busIndex = 0
		self.level = 1
		self.preFader = False
		self.destTrackId = 0
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'busIndex' in indict: self.busIndex = indict['busIndex']
		if 'level' in indict: self.level = indict['level']
		if 'preFader' in indict: self.preFader = indict['preFader']
		if 'destTrackId' in indict: self.destTrackId = indict['destTrackId']

	def write(self):
		o = {}
		o['busIndex'] = self.busIndex
		o['level'] = self.level
		o['preFader'] = self.preFader
		o['destTrackId'] = self.destTrackId
		return o

class magda_track:
	def __init__(self, indict=None):
		self.idnum = 1
		self.type = 0
		self.name = ""
		self.colour = "FF5588AA"
		self.parentId = -1
		self.childIds = []
		self.volume = 1.0
		self.pan = 0.0
		self.manualVolume = 1.0
		self.manualPan = 0.0
		self.muted = False
		self.soloed = False
		self.recordArmed = False
		self.inputMonitor = 0
		self.frozen = False
		self.playbackMode = 0
		self.viewSettings = {}
		self.midiInputDevice = ""
		self.midiOutputDevice = ""
		self.audioInputDevice = ""
		self.audioOutputDevice = "master"
		self.auxBusIndex = -1
		self.sends = []
		self.chainElements = []
		self.trackMods = []
		self.trackMacros = []
		self.globalModsPanelOpen = False
		self.globalMacrosPanelOpen = False
		self.selectedGlobalModIndex = -1
		self.selectedGlobalMacroIndex = -1
		for x in range(16):
			t = magda_macros()
			t.name = 'Macro '+str(x+1)
			t.id = x
			self.trackMacros.append(t)
		self.viewSettings['Live'] = magda_track_viewSetting()
		self.viewSettings['Arrange'] = magda_track_viewSetting()
		self.viewSettings['Mix'] = magda_track_viewSetting()
		self.viewSettings['Master'] = magda_track_viewSetting()
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'id' in indict: self.idnum = indict['id']
		if 'type' in indict: self.type = indict['type']
		if 'name' in indict: self.name = indict['name']
		if 'colour' in indict: self.colour = indict['colour']
		if 'parentId' in indict: self.parentId = indict['parentId']
		if 'childIds' in indict: self.childIds = indict['childIds']
		if 'volume' in indict: self.volume = indict['volume']
		if 'pan' in indict: self.pan = indict['pan']
		if 'manualVolume' in indict: self.manualVolume = indict['manualVolume']
		if 'manualPan' in indict: self.manualPan = indict['manualPan']
		if 'muted' in indict: self.muted = indict['muted']
		if 'soloed' in indict: self.soloed = indict['soloed']
		if 'recordArmed' in indict: self.recordArmed = indict['recordArmed']
		if 'inputMonitor' in indict: self.inputMonitor = indict['inputMonitor']
		if 'frozen' in indict: self.frozen = indict['frozen']
		if 'playbackMode' in indict: self.playbackMode = indict['playbackMode']
		if 'viewSettings' in indict: 
			self.viewSettings = {}
			for k, v in indict['viewSettings'].items():
				self.viewSettings[k] = magda_track_viewSetting(v)
		if 'midiInputDevice' in indict: self.midiInputDevice = indict['midiInputDevice']
		if 'midiOutputDevice' in indict: self.midiOutputDevice = indict['midiOutputDevice']
		if 'audioInputDevice' in indict: self.audioInputDevice = indict['audioInputDevice']
		if 'audioOutputDevice' in indict: self.audioOutputDevice = indict['audioOutputDevice']
		if 'auxBusIndex' in indict: self.auxBusIndex = indict['auxBusIndex']
		if 'sends' in indict: 
			self.sends = []
			for v in indict['sends']:
				self.sends.append(magda_track_send(v))
		if 'chainElements' in indict: 
			self.chainElements = []
			for x in indict['chainElements']:
				ctype = x['type']
				if ctype=='device':
					self.chainElements.append(magda_chainElement_device(x['device']))
				if ctype=='rack':
					self.chainElements.append(magda_chainElement_rack(x['rack']))
		if 'trackMods' in indict: 
			self.trackMods = []
			for x in indict['trackMods']:
				self.trackMods.append(magda_track_mod(x))
		if 'trackMacros' in indict: 
			self.trackMacros = []
			for x in indict['trackMacros']:
				self.trackMacros.append(magda_macros(x))
		if 'globalModsPanelOpen' in indict: self.globalModsPanelOpen = indict['globalModsPanelOpen']
		if 'globalMacrosPanelOpen' in indict: self.globalMacrosPanelOpen = indict['globalMacrosPanelOpen']
		if 'selectedGlobalModIndex' in indict: self.selectedGlobalModIndex = indict['selectedGlobalModIndex']
		if 'selectedGlobalMacroIndex' in indict: self.selectedGlobalMacroIndex = indict['selectedGlobalMacroIndex']

	def write(self):
		o = {}
		o['id'] = self.idnum
		o['type'] = self.type
		o['name'] = self.name
		o['colour'] = self.colour
		o['parentId'] = self.parentId
		o['childIds'] = self.childIds
		o['volume'] = self.volume
		o['pan'] = self.pan
		o['manualVolume'] = self.manualVolume
		o['manualPan'] = self.manualPan
		o['muted'] = self.muted
		o['soloed'] = self.soloed
		o['recordArmed'] = self.recordArmed
		o['inputMonitor'] = self.inputMonitor
		o['frozen'] = self.frozen
		o['playbackMode'] = self.playbackMode
		o['viewSettings'] = dict([[k, v.write()] for k, v in self.viewSettings.items()])
		o['midiInputDevice'] = self.midiInputDevice
		o['midiOutputDevice'] = self.midiOutputDevice
		o['audioInputDevice'] = self.audioInputDevice
		o['audioOutputDevice'] = self.audioOutputDevice
		o['auxBusIndex'] = self.auxBusIndex
		o['sends'] = [x.write() for x in self.sends]
		c = o['chainElements'] = []
		for x in self.chainElements:
			if isinstance(x, magda_chainElement_device):
				c.append({"type": "device", "device": x.write()})
			if isinstance(x, magda_chainElement_rack):
				c.append({"type": "rack", "rack": x.write()})
		o['trackMods'] = [x.write() for x in self.trackMods]
		o['trackMacros'] = [x.write() for x in self.trackMacros]
		o['globalModsPanelOpen'] = self.globalModsPanelOpen
		o['globalMacrosPanelOpen'] = self.globalMacrosPanelOpen
		o['selectedGlobalModIndex'] = self.selectedGlobalModIndex
		o['selectedGlobalMacroIndex'] = self.selectedGlobalMacroIndex
		return o

# =========================================== automation ===========================================

class magda_automation_Handle:
	def __init__(self, indict=None):
		self.beatOffset = 0
		self.value = 0
		self.linked = True
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'beatOffset' in indict: self.beatOffset = indict['beatOffset']
		if 'value' in indict: self.value = indict['value']
		if 'linked' in indict: self.linked = indict['linked']

	def write(self):
		o = {}
		o['beatOffset'] = self.beatOffset
		o['value'] = self.value
		o['linked'] = self.linked
		return o

class magda_automation_absolutePoint:
	def __init__(self, indict=None):
		self.id = 1
		self.beatPosition = 0
		self.value = 0
		self.curveType = 0
		self.tension = 0.0
		self.inHandle = magda_automation_Handle()
		self.outHandle = magda_automation_Handle()
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'id' in indict: self.id = indict['id']
		if 'beatPosition' in indict: self.beatPosition = indict['beatPosition']
		if 'value' in indict: self.value = indict['value']
		if 'curveType' in indict: self.curveType = indict['curveType']
		if 'tension' in indict: self.tension = indict['tension']
		if 'inHandle' in indict: self.inHandle.read(indict['inHandle'])
		if 'outHandle' in indict: self.outHandle.read(indict['outHandle'])

	def write(self):
		o = {}
		o['id'] = self.id
		o['beatPosition'] = self.beatPosition
		o['value'] = self.value
		o['curveType'] = self.curveType
		o['tension'] = self.tension
		o['inHandle'] = self.inHandle.write()
		o['outHandle'] = self.outHandle.write()
		return o

class magda_automation_lane_target:
	def __init__(self, indict=None):
		self.type = 0
		self.trackId = 0
		self.devicePath = {}
		self.paramIndex = -1
		self.modId = -1
		self.modParamIndex = -1
		self.sendBusIndex = -1
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'type' in indict: self.type = indict['type']
		if 'trackId' in indict: self.trackId = indict['trackId']
		if 'devicePath' in indict: self.devicePath = indict['devicePath']
		if 'paramIndex' in indict: self.paramIndex = indict['paramIndex']
		if 'modId' in indict: self.modId = indict['modId']
		if 'modParamIndex' in indict: self.modParamIndex = indict['modParamIndex']
		if 'sendBusIndex' in indict: self.sendBusIndex = indict['sendBusIndex']

	def write(self):
		o = {}
		o['type'] = self.type
		o['trackId'] = self.trackId
		o['devicePath'] = self.devicePath
		o['paramIndex'] = self.paramIndex
		o['modId'] = self.modId
		o['modParamIndex'] = self.modParamIndex
		o['sendBusIndex'] = self.sendBusIndex
		return o

class magda_automation_lane:
	def __init__(self, indict=None):
		self.id = 0
		self.target = magda_automation_lane_target()
		self.type = 0
		self.name = ""
		self.visible = True
		self.expanded = True
		self.bypass = False
		self.snapEditsToBeatGrid = True
		self.snapValue = False
		self.height = 60
		self.absolutePoints = []
		self.clipIds = []
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'id' in indict: self.id = indict['id']
		if 'target' in indict: self.target.read(indict['target'])
		if 'type' in indict: self.type = indict['type']
		if 'name' in indict: self.name = indict['name']
		if 'visible' in indict: self.visible = indict['visible']
		if 'expanded' in indict: self.expanded = indict['expanded']
		if 'bypass' in indict: self.bypass = indict['bypass']
		if 'snapEditsToBeatGrid' in indict: self.snapEditsToBeatGrid = indict['snapEditsToBeatGrid']
		if 'snapValue' in indict: self.snapValue = indict['snapValue']
		if 'height' in indict: self.height = indict['height']
		if 'absolutePoints' in indict: 
			self.absolutePoints = []
			for x in indict['absolutePoints']:
				self.absolutePoints.append(magda_automation_absolutePoint(x))
		if 'clipIds' in indict: self.clipIds = indict['clipIds']

	def write(self):
		o = {}
		o['id'] = self.id
		o['target'] = self.target.write()
		o['type'] = self.type
		o['name'] = self.name
		o['visible'] = self.visible
		o['expanded'] = self.expanded
		o['bypass'] = self.bypass
		o['snapEditsToBeatGrid'] = self.snapEditsToBeatGrid
		o['snapValue'] = self.snapValue
		o['height'] = self.height
		o['absolutePoints'] = [x.write for x in self.absolutePoints]
		o['clipIds'] = self.clipIds
		return o

class magda_automation:
	def __init__(self, indict=None):
		self.clips = []
		self.lanes = []
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'clips' in indict: self.clips = indict['clips']
		if 'lanes' in indict: 
			self.lanes = []
			for x in indict['lanes']:
				self.lanes.append(magda_automation_lane(x))

	def write(self):
		o = {}
		o['lanes'] = [x.write() for x in self.lanes]
		o['clips'] = self.clips
		return o

# =========================================== project ===========================================

class magda_project_loop:
	def __init__(self, indict=None):
		self.enabled = False
		self.startBeats = 0
		self.endBeats = 0
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'enabled' in indict: self.enabled = indict['enabled']
		if 'startBeats' in indict: self.startBeats = indict['startBeats']
		if 'endBeats' in indict: self.endBeats = indict['endBeats']

	def write(self):
		o = {}
		o['enabled'] = self.enabled
		o['startBeats'] = self.startBeats
		o['endBeats'] = self.endBeats
		return o

class magda_project_zoom:
	def __init__(self, indict=None):
		self.horizontalZoom = 5.0
		self.verticalZoom = 1.0
		self.scrollX = 0
		self.scrollY = 0
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'horizontalZoom' in indict: self.horizontalZoom = indict['horizontalZoom']
		if 'verticalZoom' in indict: self.verticalZoom = indict['verticalZoom']
		if 'scrollX' in indict: self.scrollX = indict['scrollX']
		if 'scrollY' in indict: self.scrollY = indict['scrollY']

	def write(self):
		o = {}
		o['horizontalZoom'] = self.horizontalZoom
		o['verticalZoom'] = self.verticalZoom
		o['scrollX'] = self.scrollX
		o['scrollY'] = self.scrollY
		return o

class magda_project:
	def __init__(self, indict=None):
		self.name = ''
		self.tempo = 120.0
		self.timeSignature = [4,4]
		self.projectLength = 240.0
		self.sampleRate = 44100.0
		self.keyRoot = -1
		self.keyQuality = 0
		self.loop = magda_project_loop()
		self.zoom = magda_project_zoom()
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'name' in indict: self.name = indict['name']
		if 'tempo' in indict: self.tempo = indict['tempo']
		if 'timeSignature' in indict: self.timeSignature = indict['timeSignature']
		if 'projectLength' in indict: self.projectLength = indict['projectLength']
		if 'sampleRate' in indict: self.sampleRate = indict['sampleRate']
		if 'keyRoot' in indict: self.keyRoot = indict['keyRoot']
		if 'keyQuality' in indict: self.keyQuality = indict['keyQuality']
		if 'loop' in indict: self.loop.read(indict['loop'])
		if 'zoom' in indict: self.zoom.read(indict['zoom'])

	def write(self):
		o = {}
		o['name'] = self.name
		o['tempo'] = self.tempo
		o['timeSignature'] = self.timeSignature
		o['projectLength'] = self.projectLength
		o['sampleRate'] = self.sampleRate
		o['keyRoot'] = self.keyRoot
		o['keyQuality'] = self.keyQuality
		o['loop'] = self.loop.write()
		o['zoom'] = self.zoom.write()
		return o

class magda_session:
	def __init__(self, indict=None):
		self.magdaVersion = ''
		self.lastModified = ''
		self.project = magda_project()
		self.tracks = []
		self.clips = []
		self.automation = magda_automation()
		self.projectBindings = []
		if indict is not None: self.read_json(indict)

	def load_from_file(self, input_file):
		f = open(input_file, 'rb')
		d = zlib.decompress(f.read())
		projectdata = json.loads(d)
		self.read_json(projectdata)
		return True

	def read_json(self, indict):
		if 'magdaVersion' in indict: self.magdaVersion = indict['magdaVersion']
		if 'lastModified' in indict: self.lastModified = indict['lastModified']
		if 'projectBindings' in indict: self.projectBindings = indict['projectBindings']
		if 'project' in indict: self.project.read(indict['project'])
		if 'tracks' in indict: 
			self.tracks = []
			for x in indict['tracks']: self.tracks.append(magda_track(x))
		if 'clips' in indict: 
			self.clips = []
			for x in indict['clips']: self.clips.append(magda_clip(x))
		if 'automation' in indict: self.automation.read(indict['automation'])

		if DEBUGSTUFF:
			f = open('magda_in.json', 'w')
			f.write(str(json.dumps(j, indent=4)))

	def write(self):
		o = {}
		o['magdaVersion'] = self.magdaVersion
		o['lastModified'] = self.lastModified
		o['project'] = self.project.write()
		o['tracks'] = [x.write() for x in self.tracks]
		o['clips'] = [x.write() for x in self.clips]
		o['automation'] = self.automation.write()
		o['projectBindings'] = self.projectBindings

		if DEBUGSTUFF:
			f = open('magda_out.json', 'w')
			f.write(str(json.dumps(o, indent=4)))

		return o

	def save_to_file(self, filename):
		outjsond = json.dumps(self.write()).encode()
		f = open(filename, 'wb')
		f.write(zlib.compress(outjsond))

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", default=None)
	parser.add_argument("-o", default=None)
	args = parser.parse_args()
	session_obj = magda_session()
	session_obj.load_from_file(args.i)
	f = open(args.o, 'w')
	f.write(str(json.dumps(session_obj.write(), indent=4)))