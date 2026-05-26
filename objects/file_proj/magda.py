
import json, zlib

DEBUGSTUFF = True

# =========================================== clip ===========================================

class magda_clip_auto_handle:
	def __init__(self):
		self.dx = 0
		self.dy = 0
		self.linked = True

	def read(self, j):
		if 'dx' in j: self.dx = j['dx']
		if 'dy' in j: self.dy = j['dy']
		if 'linked' in j: self.linked = j['linked']

	def write(self):
		o = {}
		o['dx'] = self.dx
		o['dy'] = self.dy
		o['linked'] = self.linked
		return o

class magda_clip_auto_midiCCData:
	def __init__(self):
		self.controller = 0
		self.beatPosition = 0
		self.value = 0
		self.curveType = 0
		self.tension = 0.0
		self.inHandle = magda_clip_auto_handle()
		self.outHandle = magda_clip_auto_handle()

	def read(self, j):
		if 'controller' in j: self.controller = j['controller']
		if 'beatPosition' in j: self.beatPosition = j['beatPosition']
		if 'value' in j: self.value = j['value']
		if 'curveType' in j: self.curveType = j['curveType']
		if 'tension' in j: self.tension = j['tension']
		if 'inHandle' in j: self.inHandle.read(j['inHandle'])
		if 'outHandle' in j: self.outHandle.read(j['outHandle'])

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
	def __init__(self):
		self.beatPosition = 0
		self.value = 0
		self.curveType = 0
		self.tension = 0.0
		self.inHandle = magda_clip_auto_handle()
		self.outHandle = magda_clip_auto_handle()

	def read(self, j):
		if 'beatPosition' in j: self.beatPosition = j['beatPosition']
		if 'value' in j: self.value = j['value']
		if 'curveType' in j: self.curveType = j['curveType']
		if 'tension' in j: self.tension = j['tension']
		if 'inHandle' in j: self.inHandle.read(j['inHandle'])
		if 'outHandle' in j: self.outHandle.read(j['outHandle'])

	def write(self):
		o = {}
		o['value'] = self.value
		o['beatPosition'] = self.beatPosition
		o['curveType'] = self.curveType
		o['tension'] = self.tension
		o['inHandle'] = self.inHandle.write()
		o['outHandle'] = self.outHandle.write()
		return o

class magda_clip_audio:
	def __init__(self):
		self.source = {}
		self.interpretation = {}
		self.playback = {}
		self.warpEnabled = False
		self.warpMarkers = {}

	def read(self, j):
		if 'source' in j: self.source = j['source']
		if 'interpretation' in j: self.interpretation = j['interpretation']
		if 'playback' in j: self.playback = j['playback']
		if 'warpEnabled' in j: self.warpEnabled = j['warpEnabled']
		if 'warpMarkers' in j: self.warpMarkers = j['warpMarkers']

	def write(self):
		o = {}
		o['source'] = self.source
		o['interpretation'] = self.interpretation
		o['playback'] = self.playback
		o['warpEnabled'] = self.warpEnabled
		o['warpMarkers'] = self.warpMarkers
		return o

class magda_clip_midiNotes:
	def __init__(self):
		self.noteNumber = 60
		self.velocity = 100
		self.startBeat = 0
		self.lengthBeats = 1

	def read(self, j):
		if 'noteNumber' in j: self.noteNumber = j['noteNumber']
		if 'velocity' in j: self.velocity = j['velocity']
		if 'startBeat' in j: self.startBeat = j['startBeat']
		if 'lengthBeats' in j: self.lengthBeats = j['lengthBeats']

	def write(self):
		o = {}
		o['noteNumber'] = self.noteNumber
		o['velocity'] = self.velocity
		o['startBeat'] = self.startBeat
		o['lengthBeats'] = self.lengthBeats
		return o

class magda_clip:
	def __init__(self):
		self.id = 0
		self.trackId = 1
		self.name = ""
		self.colour = "FF5588AA"
		self.type = 1
		self.view = 0
		self.loopEnabled = True
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

	def read(self, j):
		if 'id' in j: self.id = j['id']
		if 'trackId' in j: self.trackId = j['trackId']
		if 'name' in j: self.name = j['name']
		if 'colour' in j: self.colour = j['colour']
		if 'type' in j: self.type = j['type']
		if 'view' in j: self.view = j['view']
		if 'loopEnabled' in j: self.loopEnabled = j['loopEnabled']
		if 'sceneIndex' in j: self.sceneIndex = j['sceneIndex']
		if 'launchMode' in j: self.launchMode = j['launchMode']
		if 'launchQuantize' in j: self.launchQuantize = j['launchQuantize']
		if 'followAction' in j: self.followAction = j['followAction']
		if 'followActionDelayBeats' in j: self.followActionDelayBeats = j['followActionDelayBeats']
		if 'followActionLoopCount' in j: self.followActionLoopCount = j['followActionLoopCount']
		if 'placement' in j: self.placement = j['placement']
		if 'gridAutoGrid' in j: self.gridAutoGrid = j['gridAutoGrid']
		if 'gridNumerator' in j: self.gridNumerator = j['gridNumerator']
		if 'gridDenominator' in j: self.gridDenominator = j['gridDenominator']
		if 'gridSnapEnabled' in j: self.gridSnapEnabled = j['gridSnapEnabled']
		if 'volumeDB' in j: self.volumeDB = j['volumeDB']
		if 'gainDB' in j: self.gainDB = j['gainDB']
		if 'pan' in j: self.pan = j['pan']
		if 'fadeIn' in j: self.fadeIn = j['fadeIn']
		if 'fadeOut' in j: self.fadeOut = j['fadeOut']
		if 'fadeInType' in j: self.fadeInType = j['fadeInType']
		if 'fadeOutType' in j: self.fadeOutType = j['fadeOutType']
		if 'fadeInBehaviour' in j: self.fadeInBehaviour = j['fadeInBehaviour']
		if 'fadeOutBehaviour' in j: self.fadeOutBehaviour = j['fadeOutBehaviour']
		if 'autoCrossfade' in j: self.autoCrossfade = j['autoCrossfade']
		if 'launchFadeSamples' in j: self.launchFadeSamples = j['launchFadeSamples']
		if 'pitchChange' in j: self.pitchChange = j['pitchChange']
		if 'transpose' in j: self.transpose = j['transpose']
		if 'autoPitch' in j: self.autoPitch = j['autoPitch']
		if 'autoPitchMode' in j: self.autoPitchMode = j['autoPitchMode']
		if 'isReversed' in j: self.isReversed = j['isReversed']
		if 'autoDetectBeats' in j: self.autoDetectBeats = j['autoDetectBeats']
		if 'beatSensitivity' in j: self.beatSensitivity = j['beatSensitivity']
		if 'leftChannelActive' in j: self.leftChannelActive = j['leftChannelActive']
		if 'rightChannelActive' in j: self.rightChannelActive = j['rightChannelActive']
		if 'autoTempo' in j: self.autoTempo = j['autoTempo']
		if 'loopLengthBeats' in j: self.loopLengthBeats = j['loopLengthBeats']
		if 'midiNotes' in j: 
			self.midiNotes = []
			for x in j['midiNotes']:
				t = magda_clip_midiNotes()
				t.read(x)
				self.midiNotes.append(t)
		if 'audio' in j: 
			self.audio = magda_clip_audio()
			self.audio.read(j['audio'])
		if 'midiCCData' in j: 
			self.midiCCData = []
			for x in j['midiCCData']:
				t = magda_clip_auto_midiCCData()
				t.read(x)
				self.midiCCData.append(t)
		if 'midiPitchBendData' in j: 
			self.midiPitchBendData = []
			for x in j['midiPitchBendData']:
				t = magda_clip_auto_midiPitchBendData()
				t.read(x)
				self.midiPitchBendData.append(t)

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
	def __init__(self):
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
	
	def read(self, j):
		if 'id' in j: self.id = j['id']
		if 'name' in j: self.name = j['name']
		if 'outputIndex' in j: self.outputIndex = j['outputIndex']
		if 'muted' in j: self.muted = j['muted']
		if 'solo' in j: self.solo = j['solo']
		if 'bypassed' in j: self.bypassed = j['bypassed']
		if 'volume' in j: self.volume = j['volume']
		if 'pan' in j: self.pan = j['pan']
		if 'expanded' in j: self.expanded = j['expanded']
		if 'elements' in j: self.elements = j['elements']
	
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
	def __init__(self):
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

	def read(self, j):
		if 'id' in j: self.id = j['id']
		if 'name' in j: self.name = j['name']
		if 'bypassed' in j: self.bypassed = j['bypassed']
		if 'expanded' in j: self.expanded = j['expanded']
		if 'modPanelOpen' in j: self.modPanelOpen = j['modPanelOpen']
		if 'paramPanelOpen' in j: self.paramPanelOpen = j['paramPanelOpen']
		if 'volume' in j: self.volume = j['volume']
		if 'pan' in j: self.pan = j['pan']
		if 'chains' in j: 
			self.chains = []
			for x in j['chains']:
				t = magda_chainElement_rack_chain()
				t.read(x)
				self.chains.append(t)
		if 'macros' in j: 
			self.macros = []
			for x in j['macros']:
				t = magda_macros()
				t.read(x)
				self.macros.append(t)
		if 'mods' in j: self.mods = j['mods']

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
	def __init__(self):
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
	
	def read(self, j):
		if 'paramIndex' in j: self.paramIndex = j['paramIndex']
		if 'name' in j: self.name = j['name']
		if 'unit' in j: self.unit = j['unit']
		if 'minValue' in j: self.minValue = j['minValue']
		if 'maxValue' in j: self.maxValue = j['maxValue']
		if 'defaultValue' in j: self.defaultValue = j['defaultValue']
		if 'currentValue' in j: self.currentValue = j['currentValue']
		if 'teMinValue' in j: self.teMinValue = j['teMinValue']
		if 'teMaxValue' in j: self.teMaxValue = j['teMaxValue']
		if 'scale' in j: self.scale = j['scale']
		if 'skewFactor' in j: self.skewFactor = j['skewFactor']
		if 'scaleAnchor' in j: self.scaleAnchor = j['scaleAnchor']
		if 'displayFormat' in j: self.displayFormat = j['displayFormat']
		if 'modulatable' in j: self.modulatable = j['modulatable']
		if 'bipolarModulation' in j: self.bipolarModulation = j['bipolarModulation']
		if 'gateSlotIndex' in j: self.gateSlotIndex = j['gateSlotIndex']
		if 'gateNegated' in j: self.gateNegated = j['gateNegated']
		if 'hidden' in j: self.hidden = j['hidden']
		if 'choices' in j: self.choices = j['choices']
		if 'labelTicks' in j: self.labelTicks = j['labelTicks']
		if 'valueTable' in j: self.valueTable = j['valueTable']
	
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
	def __init__(self):
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

	def read(self, j):
		if 'id' in j: self.id = j['id']
		if 'name' in j: self.name = j['name']
		if 'pluginId' in j: self.pluginId = j['pluginId']
		if 'manufacturer' in j: self.manufacturer = j['manufacturer']
		if 'format' in j: self.format = j['format']
		if 'isInstrument' in j: self.isInstrument = j['isInstrument']
		if 'deviceType' in j: self.deviceType = j['deviceType']
		if 'uniqueId' in j: self.uniqueId = j['uniqueId']
		if 'fileOrIdentifier' in j: self.fileOrIdentifier = j['fileOrIdentifier']
		if 'bypassed' in j: self.bypassed = j['bypassed']
		if 'expanded' in j: self.expanded = j['expanded']
		if 'modPanelOpen' in j: self.modPanelOpen = j['modPanelOpen']
		if 'gainPanelOpen' in j: self.gainPanelOpen = j['gainPanelOpen']
		if 'paramPanelOpen' in j: self.paramPanelOpen = j['paramPanelOpen']
		if 'aiPanelOpen' in j: self.aiPanelOpen = j['aiPanelOpen']
		if 'parameters' in j: 
			self.parameters = []
			for x in j['parameters']:
				t = magda_chainElement_device_param()
				t.read(x)
				self.parameters.append(t)
		if 'visibleParameters' in j: self.visibleParameters = j['visibleParameters']
		if 'gainValue' in j: self.gainValue = j['gainValue']
		if 'gainDb' in j: self.gainDb = j['gainDb']
		if 'macros' in j: 
			self.macros = []
			for x in j['macros']:
				t = magda_macros()
				t.read(x)
				self.macros.append(t)
		if 'mods' in j: self.mods = j['mods']
		if 'currentParameterPage' in j: self.currentParameterPage = j['currentParameterPage']
		if 'pluginState' in j: self.pluginState = j['pluginState']

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
	def __init__(self):
		self.phase = 0
		self.value = 0
		self.tension = 0

	def read(self, j):
		if 'phase' in j: self.phase = j['phase']
		if 'value' in j: self.value = j['value']
		if 'tension' in j: self.tension = j['tension']

	def write(self):
		o = {}
		o['phase'] = self.phase
		o['value'] = self.value
		o['tension'] = self.tension
		return o

class magda_track_mod_link:
	def __init__(self):
		self.target = {}
		self.amount = 0
		self.bipolar = False

	def read(self, j):
		if 'target' in j: self.target = j['target']
		if 'amount' in j: self.amount = j['amount']
		if 'bipolar' in j: self.bipolar = j['bipolar']

	def write(self):
		o = {}
		o['target'] = self.target
		o['amount'] = self.amount
		o['bipolar'] = self.bipolar
		return o

class magda_track_mod:
	def __init__(self):
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
	
	def read(self, j):
		if 'id' in j: self.id = j['id']
		if 'name' in j: self.name = j['name']
		if 'type' in j: self.type = j['type']
		if 'enabled' in j: self.enabled = j['enabled']
		if 'rate' in j: self.rate = j['rate']
		if 'waveform' in j: self.waveform = j['waveform']
		if 'phase' in j: self.phase = j['phase']
		if 'phaseOffset' in j: self.phaseOffset = j['phaseOffset']
		if 'value' in j: self.value = j['value']
		if 'tempoSync' in j: self.tempoSync = j['tempoSync']
		if 'syncDivision' in j: self.syncDivision = j['syncDivision']
		if 'triggerMode' in j: self.triggerMode = j['triggerMode']
		if 'oneShot' in j: self.oneShot = j['oneShot']
		if 'useLoopRegion' in j: self.useLoopRegion = j['useLoopRegion']
		if 'loopStart' in j: self.loopStart = j['loopStart']
		if 'loopEnd' in j: self.loopEnd = j['loopEnd']
		if 'midiChannel' in j: self.midiChannel = j['midiChannel']
		if 'midiNote' in j: self.midiNote = j['midiNote']
		if 'audioAttackMs' in j: self.audioAttackMs = j['audioAttackMs']
		if 'audioReleaseMs' in j: self.audioReleaseMs = j['audioReleaseMs']
		if 'curvePreset' in j: self.curvePreset = j['curvePreset']
		if 'curvePoints' in j: 
			self.curvePoints = []
			for x in j['curvePoints']:
				t = magda_track_mod_curvePoint()
				t.read(x)
				self.curvePoints.append(t)
		if 'links' in j: 
			self.links = []
			for x in j['links']:
				t = magda_track_mod_link()
				t.read(x)
				self.links.append(t)
	
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
	def __init__(self):
		self.id = 0
		self.name = ""
		self.value = 0.5
		self.links = []

	def read(self, j):
		if 'id' in j: self.id = j['id']
		if 'name' in j: self.name = j['name']
		if 'value' in j: self.value = j['value']
		if 'links' in j: self.links = j['links']

	def write(self):
		o = {}
		o['id'] = self.id
		o['name'] = self.name
		o['value'] = self.value
		o['links'] = self.links
		return o

class magda_track_viewSetting:
	def __init__(self):
		self.visible = True
		self.locked = False
		self.collapsed = False
		self.height = 60

	def read(self, j):
		if 'visible' in j: self.visible = j['visible']
		if 'locked' in j: self.locked = j['locked']
		if 'collapsed' in j: self.collapsed = j['collapsed']
		if 'height' in j: self.height = j['height']

	def write(self):
		o = {}
		o['visible'] = self.visible
		o['locked'] = self.locked
		o['collapsed'] = self.collapsed
		o['height'] = self.height
		return o

class magda_track_send:
	def __init__(self):
		self.busIndex = 0
		self.level = 1
		self.preFader = False
		self.destTrackId = 0

	def read(self, j):
		if 'busIndex' in j: self.busIndex = j['busIndex']
		if 'level' in j: self.level = j['level']
		if 'preFader' in j: self.preFader = j['preFader']
		if 'destTrackId' in j: self.destTrackId = j['destTrackId']

	def write(self):
		o = {}
		o['busIndex'] = self.busIndex
		o['level'] = self.level
		o['preFader'] = self.preFader
		o['destTrackId'] = self.destTrackId
		return o

class magda_track:
	def __init__(self):
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
		self.midiInputDevice = "all"
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

	def read(self, j):
		if 'id' in j: self.idnum = j['id']
		if 'type' in j: self.type = j['type']
		if 'name' in j: self.name = j['name']
		if 'colour' in j: self.colour = j['colour']
		if 'parentId' in j: self.parentId = j['parentId']
		if 'childIds' in j: self.childIds = j['childIds']
		if 'volume' in j: self.volume = j['volume']
		if 'pan' in j: self.pan = j['pan']
		if 'manualVolume' in j: self.manualVolume = j['manualVolume']
		if 'manualPan' in j: self.manualPan = j['manualPan']
		if 'muted' in j: self.muted = j['muted']
		if 'soloed' in j: self.soloed = j['soloed']
		if 'recordArmed' in j: self.recordArmed = j['recordArmed']
		if 'inputMonitor' in j: self.inputMonitor = j['inputMonitor']
		if 'frozen' in j: self.frozen = j['frozen']
		if 'playbackMode' in j: self.playbackMode = j['playbackMode']
		if 'viewSettings' in j: 
			self.viewSettings = {}
			for k, v in j['viewSettings'].items():
				vs = magda_track_viewSetting()
				vs.read(v)
				self.viewSettings[k] = vs
		if 'midiInputDevice' in j: self.midiInputDevice = j['midiInputDevice']
		if 'midiOutputDevice' in j: self.midiOutputDevice = j['midiOutputDevice']
		if 'audioInputDevice' in j: self.audioInputDevice = j['audioInputDevice']
		if 'audioOutputDevice' in j: self.audioOutputDevice = j['audioOutputDevice']
		if 'auxBusIndex' in j: self.auxBusIndex = j['auxBusIndex']
		if 'sends' in j: 
			self.sends = []
			for v in j['sends']:
				vs = magda_track_send()
				vs.read(v)
				self.sends.append(vs)
		if 'chainElements' in j: 
			self.chainElements = []
			for x in j['chainElements']:
				ctype = x['type']
				if ctype=='device':
					dev = magda_chainElement_device()
					dev.read(x['device'])
					self.chainElements.append(dev)
				if ctype=='rack':
					dev = magda_chainElement_rack()
					dev.read(x['rack'])
					self.chainElements.append(dev)
		if 'trackMods' in j: 
			self.trackMods = []
			for x in j['trackMods']:
				t = magda_track_mod()
				t.read(x)
				self.trackMods.append(t)
		if 'trackMacros' in j: 
			self.trackMacros = []
			for x in j['trackMacros']:
				t = magda_macros()
				t.read(x)
				self.trackMacros.append(t)
		if 'globalModsPanelOpen' in j: self.globalModsPanelOpen = j['globalModsPanelOpen']
		if 'globalMacrosPanelOpen' in j: self.globalMacrosPanelOpen = j['globalMacrosPanelOpen']
		if 'selectedGlobalModIndex' in j: self.selectedGlobalModIndex = j['selectedGlobalModIndex']
		if 'selectedGlobalMacroIndex' in j: self.selectedGlobalMacroIndex = j['selectedGlobalMacroIndex']

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
	def __init__(self):
		self.beatOffset = 0
		self.value = 0
		self.linked = True

	def read(self, j):
		if 'beatOffset' in j: self.beatOffset = j['beatOffset']
		if 'value' in j: self.value = j['value']
		if 'linked' in j: self.linked = j['linked']

	def write(self):
		o = {}
		o['beatOffset'] = self.beatOffset
		o['value'] = self.value
		o['linked'] = self.linked
		return o

class magda_automation_absolutePoint:
	def __init__(self):
		self.id = 1
		self.beatPosition = 0
		self.value = 0
		self.curveType = 0
		self.tension = 0.0
		self.inHandle = magda_automation_Handle()
		self.outHandle = magda_automation_Handle()

	def read(self, j):
		if 'id' in j: self.id = j['id']
		if 'beatPosition' in j: self.beatPosition = j['beatPosition']
		if 'value' in j: self.value = j['value']
		if 'curveType' in j: self.curveType = j['curveType']
		if 'tension' in j: self.tension = j['tension']
		if 'inHandle' in j: self.inHandle.read(j['inHandle'])
		if 'outHandle' in j: self.outHandle.read(j['outHandle'])

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
	def __init__(self):
		self.type = 0
		self.trackId = 0
		self.devicePath = {}
		self.paramIndex = -1
		self.modId = -1
		self.modParamIndex = -1
		self.sendBusIndex = -1

	def read(self, j):
		if 'type' in j: self.type = j['type']
		if 'trackId' in j: self.trackId = j['trackId']
		if 'devicePath' in j: self.devicePath = j['devicePath']
		if 'paramIndex' in j: self.paramIndex = j['paramIndex']
		if 'modId' in j: self.modId = j['modId']
		if 'modParamIndex' in j: self.modParamIndex = j['modParamIndex']
		if 'sendBusIndex' in j: self.sendBusIndex = j['sendBusIndex']

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
	def __init__(self):
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

	def read(self, j):
		if 'id' in j: self.id = j['id']
		if 'target' in j: self.target.read(j['target'])
		if 'type' in j: self.type = j['type']
		if 'name' in j: self.name = j['name']
		if 'visible' in j: self.visible = j['visible']
		if 'expanded' in j: self.expanded = j['expanded']
		if 'bypass' in j: self.bypass = j['bypass']
		if 'snapEditsToBeatGrid' in j: self.snapEditsToBeatGrid = j['snapEditsToBeatGrid']
		if 'snapValue' in j: self.snapValue = j['snapValue']
		if 'height' in j: self.height = j['height']
		if 'absolutePoints' in j: 
			self.absolutePoints = []
			for x in j['absolutePoints']:
				t = magda_automation_absolutePoint()
				t.read(x)
				self.absolutePoints.append(t)
		if 'clipIds' in j: self.clipIds = j['clipIds']

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
		o['absolutePoints'] = [x.write() for x in self.absolutePoints]
		o['clipIds'] = self.clipIds
		return o

class magda_automation:
	def __init__(self):
		self.clips = {}
		self.lanes = []

	def read(self, j):
		if 'clips' in j: self.clips = j['clips']
		if 'lanes' in j: 
			self.lanes = []
			for x in j['lanes']:
				t = magda_automation_lane()
				t.read(x)
				self.lanes.append(t)

	def write(self):
		o = {}
		o['lanes'] = [x.write() for x in self.lanes]
		o['clips'] = self.clips
		return o

# =========================================== project ===========================================

class magda_project_loop:
	def __init__(self):
		self.enabled = False
		self.startBeats = 0
		self.endBeats = 0

	def read(self, j):
		if 'enabled' in j: self.enabled = j['enabled']
		if 'startBeats' in j: self.startBeats = j['startBeats']
		if 'endBeats' in j: self.endBeats = j['endBeats']

	def write(self):
		o = {}
		o['enabled'] = self.enabled
		o['startBeats'] = self.startBeats
		o['endBeats'] = self.endBeats
		return o

class magda_project_zoom:
	def __init__(self):
		self.horizontalZoom = 5.0
		self.verticalZoom = 1.0
		self.scrollX = 0
		self.scrollY = 0

	def read(self, j):
		if 'horizontalZoom' in j: self.horizontalZoom = j['horizontalZoom']
		if 'verticalZoom' in j: self.verticalZoom = j['verticalZoom']
		if 'scrollX' in j: self.scrollX = j['scrollX']
		if 'scrollY' in j: self.scrollY = j['scrollY']

	def write(self):
		o = {}
		o['horizontalZoom'] = self.horizontalZoom
		o['verticalZoom'] = self.verticalZoom
		o['scrollX'] = self.scrollX
		o['scrollY'] = self.scrollY
		return o

class magda_project:
	def __init__(self):
		self.name = ''
		self.tempo = 120.0
		self.timeSignature = [4,4]
		self.projectLength = 240.0
		self.sampleRate = 44100.0
		self.keyRoot = -1
		self.keyQuality = 0
		self.loop = magda_project_loop()
		self.zoom = magda_project_zoom()

	def read(self, j):
		if 'name' in j: self.name = j['name']
		if 'tempo' in j: self.tempo = j['tempo']
		if 'timeSignature' in j: self.timeSignature = j['timeSignature']
		if 'projectLength' in j: self.projectLength = j['projectLength']
		if 'sampleRate' in j: self.sampleRate = j['sampleRate']
		if 'keyRoot' in j: self.keyRoot = j['keyRoot']
		if 'keyQuality' in j: self.keyQuality = j['keyQuality']
		if 'loop' in j: self.loop.read(j['loop'])
		if 'zoom' in j: self.zoom.read(j['zoom'])

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
	def __init__(self):
		self.magdaVersion = ''
		self.lastModified = ''
		self.project = magda_project()
		self.tracks = []
		self.clips = []
		self.automation = magda_automation()
		self.projectBindings = []

	def load_from_file(self, input_file):
		f = open(input_file, 'rb')
		d = zlib.decompress(f.read())
		projectdata = json.loads(d)
		self.read_json(projectdata)
		return True

	def read_json(self, j):
		if 'magdaVersion' in j: self.magdaVersion = j['magdaVersion']
		if 'lastModified' in j: self.lastModified = j['lastModified']
		if 'projectBindings' in j: self.projectBindings = j['projectBindings']
		if 'project' in j: self.project.read(j['project'])
		if 'tracks' in j: 
			self.tracks = []
			for x in j['tracks']:
				t = magda_track()
				t.read(x)
				self.tracks.append(t)
		if 'clips' in j: 
			self.clips = []
			for x in j['clips']:
				t = magda_clip()
				t.read(x)
				self.clips.append(t)
		if 'automation' in j: self.automation.read(j['automation'])

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