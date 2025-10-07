# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from lxml import etree as ET
from objects.exceptions import ProjectFileParserException
DEBUG_IN_OUT = False

import logging
logger_projparse = logging.getLogger('projparse')

# =================================================== RACK ===================================================

class tracktion_rack_connection:
	def __init__(self):
		self.src = 0
		self.dst = 0
		self.srcPin = 0
		self.dstPin = 0

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'src': self.src = int(v)
			elif n == 'dst': self.dst = int(v)
			elif n == 'srcPin': self.srcPin = int(v)
			elif n == 'dstPin': self.dstPin = int(v)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "CONNECTION")
		tempxml.set('src', str(self.src))
		tempxml.set('dst', str(self.dst))
		tempxml.set('srcPin', str(self.srcPin))
		tempxml.set('dstPin', str(self.dstPin))

class tracktion_rack_plugininstance:
	def __init__(self):
		self.x = 0
		self.y = 0
		self.plugin = tracktion_plugin()

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'x': self.x = float(v)
			if n == 'y': self.y = float(v)
		for subxml in xmldata:
			if subxml.tag == 'PLUGIN': 
				self.plugin.load(subxml)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "PLUGININSTANCE")
		tempxml.set('x', str(self.x))
		tempxml.set('y', str(self.y))
		self.plugin.write(tempxml)

class tracktion_rack_output:
	def __init__(self):
		self.name = ''

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'name': self.name = v

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "OUTPUT")
		tempxml.set('name', str(self.name))

class tracktion_rack_input:
	def __init__(self):
		self.name = ''

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'name': self.name = v

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "INPUT")
		tempxml.set('name', str(self.name))

class tracktion_rack:
	def __init__(self):
		self.id_num = 0
		self.name = ''
		self.macroparameters = tracktion_macroparameters()
		self.outputs = []
		self.inputs = []
		self.connections = []
		self.modifiers = tracktion_modifiers()
		self.plugins = {}

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'id': self.id_num = int(v)
			if n == 'name': self.name = v

		for xmlpart in xmldata:
			if xmlpart.tag == 'MACROPARAMETERS': self.macroparameters.load(xmlpart)
			elif xmlpart.tag == 'OUTPUT': 
				x_out = tracktion_rack_output()
				x_out.load(xmlpart)
				self.outputs.append(x_out)
			elif xmlpart.tag == 'INPUT': 
				x_out = tracktion_rack_input()
				x_out.load(xmlpart)
				self.inputs.append(x_out)
			elif xmlpart.tag == 'MODIFIERS': self.modifiers.load(xmlpart)
			elif xmlpart.tag == 'PLUGININSTANCE': 
				x_out = tracktion_rack_plugininstance()
				x_out.load(xmlpart)
				self.plugins[int(x_out.plugin.id_num)] = x_out
			elif xmlpart.tag == 'CONNECTION': 
				x_out = tracktion_rack_connection()
				x_out.load(xmlpart)
				self.connections.append(x_out)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "RACK")
		tempxml.set('id', str(self.id_num))
		tempxml.set('name', str(self.name))
		self.macroparameters.write(tempxml)
		for x in self.outputs: x.write(tempxml)
		for x in self.inputs: x.write(tempxml)
		self.modifiers.write(tempxml)
		used_plugins = []
		for connection in self.connections:
			do_plugins = [connection.src, connection.dst]
			for plugid in do_plugins:
				if plugid and plugid not in used_plugins:
					self.plugins[plugid].write(tempxml)
					used_plugins.append(plugid)
			connection.write(tempxml)

# =================================================== OTHER ===================================================

class tracktion_auxbusname:
	def __init__(self):
		self.bus = 0
		self.name = ''

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'bus': self.bus = int(v)
			if n == 'name': self.name = v

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, 'NAME')
		tempxml.set('bus', str(self.bus))
		tempxml.set('name', self.name)

class tracktion_followactions:
	def __init__(self):
		pass

	def load(self, xmldata):
		pass

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "FOLLOWACTIONS")

# =================================================== MODIFIERS ===================================================

class tracktion_modifierassignment:
	def __init__(self):
		self.type = None
		self.source = 0
		self.paramID = None
		self.value = 1.0
		self.end = 1.0

	def load(self, xmldata):
		self.type = xmldata.tag
		for n, v in xmldata.attrib.items():
			if n == 'source': self.source = int(v)
			if n == 'paramID': self.paramID = v
			if n == 'value': self.value = float(v)
			if n == 'end': self.end = float(v)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, self.type)
		tempxml.set('source', str(self.source))
		tempxml.set('paramID', self.paramID)
		tempxml.set('value', str(self.value))
		tempxml.set('end', str(self.end))

class tracktion_modifierassignments:
	def __init__(self):
		self.modifierassignments = []

	def load(self, xmldata):
		for x in xmldata:
			m = tracktion_modifierassignment()
			m.load(x)
			self.modifierassignments.append(m)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "MODIFIERASSIGNMENTS")
		for m in self.modifierassignments: m.write(tempxml)

class tracktion_modifier_midinode:
	def __init__(self):
		self.midi = 60
		self.value = 0

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'midi': self.midi = int(v)
			if n == 'value': self.value = float(v)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, 'NODE')
		tempxml.set('midi', str(self.midi))
		tempxml.set('value', str(self.value))

class tracktion_modifier:
	def __init__(self):
		self.type = None
		self.remapOnTempoChange = 1
		self.id_num = 0
		self.colour = None
		self.modifierassignments = tracktion_modifierassignments()
		self.nodes = None
		self.params = {}

	def load(self, xmldata):
		self.type = xmldata.tag
		for n, v in xmldata.attrib.items():
			if n == 'id': self.id_num = int(v)
			elif n == 'remapOnTempoChange': self.remapOnTempoChange = int(v)
			elif n == 'colour': self.colour = v
			else: self.params[n] = v

		for xmlpart in xmldata:
			if xmlpart.tag == 'MODIFIERASSIGNMENTS': self.modifierassignments.load(xmlpart)
			if xmlpart.tag == 'NODES': 
				self.nodes = []
				for subinxml in xmlpart:
					if subinxml.tag == 'NODE':
						node = tracktion_modifier_midinode()
						node.load(subinxml)
						self.nodes.append(node)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, self.type)
		tempxml.set('id', str(self.id_num))
		tempxml.set('remapOnTempoChange', str(self.remapOnTempoChange))
		if self.colour: tempxml.set('colour', self.colour)
		for n, v in self.params.items(): tempxml.set(n, str(v))
		self.modifierassignments.write(tempxml)
		if self.nodes is not None:
			nodesxml = ET.SubElement(tempxml, 'NODES')
			for node in self.nodes: node.write(nodesxml)


class tracktion_modifiers:
	def __init__(self):
		self.modifiers = []

	def load(self, xmldata):
		for x in xmldata:
			m = tracktion_modifier()
			m.load(x)
			self.modifiers.append(m)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "MODIFIERS")
		for m in self.modifiers:
			m.write(tempxml)

# =================================================== AUTOMATION ===================================================

class tracktion_macroparameters:
	def __init__(self):
		self.id_num = 0
		self.used = False

	def load(self, xmldata):
		self.used = True
		id_num = xmldata.get('id')
		if id_num != None: self.id_num = int(id_num)

	def write(self, xmldata):
		if self.used:
			tempxml = ET.SubElement(xmldata, "MACROPARAMETERS")
			tempxml.set('id', str(self.id_num))

class tracktion_seq_pitch:
	def __init__(self):
		self.sequence = {}

	def load(self, xmldata):
		for subxml in xmldata:
			if subxml.tag == 'PITCH': 
				startpos = subxml.get('startBeat')
				if not startpos: startpos = subxml.get('start')
				if startpos: self.sequence[float(startpos)] = int(subxml.get('pitch'))

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "PITCHSEQUENCE")
		for pos, pitch in self.sequence.items():
			pxml = ET.SubElement(tempxml, "PITCH")
			pxml.set('startBeat', str(pos))
			pxml.set('pitch', str(pitch))

class tracktion_seq_tempo:
	def __init__(self):
		self.tempo = {}
		self.timesig = {}

	def load(self, xmldata):
		for subxml in xmldata:
			if subxml.tag == 'TEMPO':
				curve = subxml.get('curve')
				self.tempo[float(subxml.get('startBeat'))] = [float(subxml.get('bpm')), str(curve) if curve != None else 1]
			if subxml.tag == 'TIMESIG':
				self.timesig[float(subxml.get('startBeat'))] = [int(subxml.get('numerator')), int(subxml.get('denominator'))]

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "TEMPOSEQUENCE")
		for pos, data in self.tempo.items():
			bpm, curve = data
			pxml = ET.SubElement(tempxml, "TEMPO")
			pxml.set('startBeat', str(pos))
			pxml.set('bpm', str(bpm))
			pxml.set('curve', str(curve))
		for pos, data in self.timesig.items():
			numerator, denominator = data
			pxml = ET.SubElement(tempxml, "TIMESIG")
			pxml.set('numerator', str(numerator))
			pxml.set('denominator', str(denominator))
			pxml.set('startBeat', str(pos))

class tracktion_automationcurve:
	def __init__(self):
		self.paramid = None
		self.points = []

	def load(self, xmldata):
		self.paramid = xmldata.get('paramID')
		for subxml in xmldata:
			if subxml.tag == 'POINT': 
				curve = float(subxml.get('c')) if 'c' in subxml.attrib else 0
				self.points.append([float(subxml.get('t')), float(subxml.get('v')), curve if curve else None])

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "AUTOMATIONCURVE")
		if self.paramid: tempxml.set('paramID', self.paramid)
		for t,v,c in self.points:
			pxml = ET.SubElement(tempxml, "POINT")
			pxml.set('t', str(t))
			pxml.set('v', str(v))
			if c: pxml.set('c', str(c))

# =================================================== PLUGIN ===================================================

class tracktion_plugin:
	def __init__(self):
		self.plugtype = ''
		self.windowLocked = 0
		self.id_num = 0
		self.enabled = 1
		self.presetDirty = 0
		self.windowX = 0
		self.windowY = 0
		self.width = 0
		self.height = 0
		self.quickParamName = ''
		self.params = {}
		self.macroparameters = tracktion_macroparameters()
		self.automationcurves = []
		self.modifierassignments = None
		self.base64_parameters = None
		self.rackType = 0
		self.other_elem = {}

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'type': self.plugtype = v
			elif n == 'windowLocked': self.windowLocked = int(v)
			elif n == 'id': self.id_num = v
			elif n == 'enabled': self.enabled = int(v)
			elif n == 'presetDirty': self.presetDirty = int(v)
			elif n == 'windowX': self.windowX = int(v)
			elif n == 'windowY': self.windowY = int(v)
			elif n == 'width': self.width = float(v)
			elif n == 'height': self.height = int(v)
			elif n == 'quickParamName': self.quickParamName = v
			elif n == 'base64:parameters': self.base64_parameters = v
			elif n == 'rackType': self.rackType = v
			else: self.params[n] = v
		for xmlpart in xmldata:
			if xmlpart.tag == 'MACROPARAMETERS': self.macroparameters.load(xmlpart)
			elif xmlpart.tag == 'AUTOMATIONCURVE': 
				autocurve_obj = tracktion_automationcurve()
				autocurve_obj.load(xmlpart)
				self.automationcurves.append(autocurve_obj)
			elif xmlpart.tag == 'MODIFIERASSIGNMENTS':
				self.modifierassignments = tracktion_modifierassignments()
				self.modifierassignments.load(xmlpart)
			else:
				self.other_elem[xmlpart.tag] = xmlpart

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "PLUGIN")
		if self.plugtype: tempxml.set('type', str(self.plugtype))
		if self.rackType: tempxml.set('rackType', str(self.rackType))
		if self.windowLocked: tempxml.set('windowLocked', str(self.windowLocked))
		if self.id_num: tempxml.set('id', str(self.id_num))
		if self.enabled: tempxml.set('enabled', str(self.enabled))
		if self.presetDirty: tempxml.set('presetDirty', str(self.presetDirty))
		if self.windowX: tempxml.set('windowX', str(self.windowX))
		if self.windowY: tempxml.set('windowY', str(self.windowY))
		if self.width: tempxml.set('width', str(self.width))
		if self.height: tempxml.set('height', str(self.height))
		for n, v in self.params.items():
			if ':' not in n:
				tempxml.set(n, str(v))
		for c in self.automationcurves:
			c.write(tempxml)
		self.macroparameters.write(tempxml)
		for k, v in self.other_elem.items():
			tempxml.append(v)
		if self.modifierassignments: self.modifierassignments.write(tempxml)

# =================================================== MIDI CLIP ===================================================

class tracktion_control:
	def __init__(self):
		self.pos = 0
		self.ctype = 0
		self.val = 0
		self.metadata = 0

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'b': self.pos = float(v)
			if n == 'type': self.ctype = int(v)
			if n == 'val': self.val = int(v)
			if n == 'metadata': self.metadata = int(v)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "CONTROL")
		tempxml.set('b', str(self.pos))
		tempxml.set('type', str(self.ctype))
		tempxml.set('val', str(self.val))
		tempxml.set('metadata', str(self.metadata))

class tracktion_note:
	def __init__(self):
		self.pos = 0
		self.key = 0
		self.dur = 0
		self.vel = 0
		self.chan = 0
		self.auto = {}

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'p': self.key = int(v)
			if n == 'b': self.pos = float(v)
			if n == 'l': self.dur = float(v)
			if n == 'v': self.vel = int(v)
			if n == 'c': self.chan = int(v)

		for subxml in xmldata:
			if subxml.tag not in self.auto:
				self.auto[subxml.tag] = {}
			if subxml.attrib:
				self.auto[subxml.tag][float(subxml.attrib['b'])] = float(subxml.attrib['v'])


	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "NOTE")
		tempxml.set('p', str(self.key))
		tempxml.set('b', str(self.pos))
		tempxml.set('l', str(self.dur))
		tempxml.set('v', str(self.vel))
		tempxml.set('c', str(self.chan))

		for a_name, a_val in self.auto.items():
			for c_pos, c_val in a_val.items():
				a_xml = ET.SubElement(tempxml, a_name)
				a_xml.set('p', str(c_pos))
				a_xml.set('v', str(c_val))

class tracktion_sequence:
	def __init__(self):
		self.notes = []
		self.controls = []

	def load(self, xmldata):
		for subxml in xmldata:
			if subxml.tag == 'NOTE':
				note_obj = tracktion_note()
				note_obj.load(subxml)
				self.notes.append(note_obj)
			if subxml.tag == 'CONTROL':
				control_obj = tracktion_control()
				control_obj.load(subxml)
				self.controls.append(control_obj)

	def write(self, xmldata):
		seq_xml = ET.SubElement(xmldata, "SEQUENCE")
		seq_xml.set('ver', '1')
		seq_xml.set('channelNumber', '1')
		for note_obj in self.notes:
			note_obj.write(seq_xml)
		for control_obj in self.controls:
			control_obj.write(seq_xml)

class tracktion_midiclip:
	def __init__(self):
		self.name = 'New MIDI Clip'
		self.start = 0
		self.length = 0
		self.offset = 0
		self.id_num = 0
		self.sync = 0
		self.colour = 'ff4cff4c'
		self.currentTake = 0
		self.mute = 0
		self.speed = 1.0
		self.volDb = 0.0
		self.originalLength = 0
		self.loopStartBeats = 0.0
		self.loopLengthBeats = 0.0
		self.groupID = -1
		self.sequence = tracktion_sequence()
		self.proxyAllowed = 1
		self.patterngenerator = None
		self.followactions = None
		self.linkID = None
		self.source = None
		self.showingTakes = None
		self.mpeMode = None
		self.sendProgramChange = None
		self.sendBankChange = None
		self.grooveStrength = None

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'id': self.id_num = v
			elif n == 'name': self.name = v
			elif n == 'start': self.start = float(v)
			elif n == 'length': self.length = float(v)
			elif n == 'offset': self.offset = float(v)
			elif n == 'id_num': self.id_num = float(v)
			elif n == 'sync': self.sync = int(v)
			elif n == 'colour': self.colour = v
			elif n == 'mute': self.mute = int(v)
			elif n == 'currentTake': self.currentTake = int(v)
			elif n == 'speed': self.speed = float(v)
			elif n == 'volDb': self.volDb = float(v)
			elif n == 'originalLength': self.originalLength = float(v)
			elif n == 'loopStartBeats': self.loopStartBeats = float(v)
			elif n == 'loopLengthBeats': self.loopLengthBeats = float(v)
			elif n == 'groupID': self.groupID = int(v)
			elif n == 'proxyAllowed': self.proxyAllowed = int(v)
			elif n == 'linkID': self.linkID = v
			elif n == 'source': self.source = v
			elif n == 'showingTakes': self.showingTakes = v
			elif n == 'mpeMode': self.mpeMode = v
			elif n == 'sendProgramChange': self.sendProgramChange = v
			elif n == 'sendBankChange': self.sendBankChange = v
			elif n == 'grooveStrength': self.grooveStrength = v
			else: logger_projparse.warning('tracktion_edit: midiclip: unimplemented attrib: '+n)

		for subxml in xmldata:
			if subxml.tag == 'SEQUENCE': self.sequence.load(subxml)
			elif subxml.tag == 'PATTERNGENERATOR':
				self.patterngenerator = tracktion_patterngenerator()
				self.patterngenerator.load(subxml)
			elif subxml.tag == 'FOLLOWACTIONS':
				self.followactions = tracktion_followactions()
				self.followactions.load(subxml)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "MIDICLIP")
		tempxml.set('name', self.name)
		tempxml.set('start', str(self.start))
		tempxml.set('length', str(self.length))
		tempxml.set('offset', str(self.offset))
		tempxml.set('id', str(self.id_num))
		tempxml.set('sync', str(self.sync))
		tempxml.set('colour', self.colour)
		tempxml.set('currentTake', str(self.currentTake))
		tempxml.set('speed', str(self.speed))
		if self.volDb: tempxml.set('volDb', str(self.volDb))
		if self.linkID: tempxml.set('linkID', self.linkID)
		if self.source: tempxml.set('source', self.source)
		if self.showingTakes: tempxml.set('showingTakes', self.showingTakes)
		if self.mpeMode: tempxml.set('mpeMode', self.mpeMode)
		if self.sendProgramChange: tempxml.set('sendProgramChange', self.sendProgramChange)
		if self.sendBankChange: tempxml.set('sendBankChange', self.sendBankChange)
		if self.grooveStrength: tempxml.set('grooveStrength', self.grooveStrength)
		if self.mute: tempxml.set('mute', str(self.mute))
		tempxml.set('proxyAllowed', str(self.proxyAllowed))
		tempxml.set('originalLength', str(self.originalLength))
		tempxml.set('loopStartBeats', str(self.loopStartBeats))
		tempxml.set('loopLengthBeats', str(self.loopLengthBeats))
		if self.groupID != -1: tempxml.set('groupID', str(self.groupID))
		ET.SubElement(tempxml, "QUANTISATION")
		ET.SubElement(tempxml, "GROOVE")
		self.sequence.write(tempxml)
		if self.patterngenerator: self.patterngenerator.write(tempxml)
		if self.followactions: self.followactions.write(tempxml)

# =================================================== AUDIO CLIP ===================================================

class tracktion_loopinfo:
	def __init__(self):
		self.rootNote = -1
		self.numBeats = 0.0
		self.oneShot = 0
		self.denominator = 4
		self.numerator = 4
		self.bpm = 0.0
		self.inMarker = 0
		self.outMarker = -1

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'rootNote': self.rootNote = int(v)
			elif n == 'numBeats': self.numBeats = float(v)
			elif n == 'oneShot': self.oneShot = int(v)
			elif n == 'denominator': self.denominator = int(v)
			elif n == 'numerator': self.numerator = int(v)
			elif n == 'bpm': self.bpm = float(v)
			elif n == 'inMarker': self.inMarker = int(v)
			elif n == 'outMarker': self.outMarker = int(v)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "LOOPINFO")
		tempxml.set('rootNote', str(self.rootNote))
		tempxml.set('numBeats', str(self.numBeats))
		tempxml.set('oneShot', str(self.oneShot))
		tempxml.set('denominator', str(self.denominator))
		tempxml.set('numerator', str(self.numerator))
		tempxml.set('bpm', str(self.bpm))
		tempxml.set('inMarker', str(self.inMarker))
		tempxml.set('outMarker', str(self.outMarker))

class tracktion_warpmarker:
	def __init__(self):
		self.sourceTime = 0
		self.warpTime = 0

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'sourceTime': self.sourceTime = float(v)
			if n == 'warpTime': self.warpTime = float(v)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "WARPMARKER")
		tempxml.set('sourceTime', str(self.sourceTime))
		tempxml.set('warpTime', str(self.warpTime))

class tracktion_warptime:
	def __init__(self):
		self.warpEndMarkerTime = 0
		self.warpmarkers = []

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'warpEndMarkerTime': self.warpEndMarkerTime = float(v)
		for xpart in xmldata:
			if xpart.tag == 'WARPMARKERS':
				for xwarp in xpart:
					warpmarker = tracktion_warpmarker()
					warpmarker.load(xwarp)
					self.warpmarkers.append(warpmarker)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "WARPTIME")
		tempxml.set('warpEndMarkerTime', str(self.warpEndMarkerTime))
		if self.warpmarkers:
			warpmarkers = ET.SubElement(tempxml, "WARPMARKERS")
			for warpmarker in self.warpmarkers:
				warpmarker.write(warpmarkers)

class tracktion_audioclip_fx:
	def __init__(self):
		self.fx_type = ''
		self.plugin = tracktion_plugin()
		self.warptime = None

	def load(self, xmldata):
		fx_type = xmldata.get('type')
		if fx_type: self.fx_type = fx_type
		for subxml in xmldata:
			if subxml.tag in ['PLUGIN', 'FILTER']:
				self.plugin.load(subxml)
			if subxml.tag == 'WARPTIME': 
				self.warptime = tracktion_warptime()
				self.warptime.load(subxml)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "EFFECT")
		tempxml.set('type', str(self.fx_type))
		if self.plugin.plugtype: self.plugin.write(tempxml)
		if self.warptime: self.warptime.write(tempxml)

class tracktion_audioclip:
	def __init__(self):
		self.name = "qd - sleep"
		self.start = 0
		self.length = 0
		self.offset = 0.0
		self.id_num = 0
		self.source = ""
		self.sync = 0
		self.elastiqueMode = 0
		self.pan = 0.0
		self.colour = "ff00ff00"
		self.proxyAllowed = 1
		self.resamplingQuality = "lagrange"
		self.autoTempo = 1

		self.fadeIn = 0.0
		self.fadeOut = 0.0
		self.speed = 1.0
		self.showingTakes = 0
		self.gain = 0.0
		self.mute = 0
		self.channels = "L R"
		self.fadeInType = 1
		self.fadeOutType = 1
		self.autoCrossfade = 0
		self.fadeInBehaviour = 0
		self.fadeOutBehaviour = 0
		self.loopStart = 0.0
		self.loopLength = 0.0
		self.loopStartBeats = 0.0
		self.loopLengthBeats = 0.0
		self.transpose = 0
		self.pitchChange = 0.0
		self.beatSensitivity = 0.5
		self.elastiqueOptions = "1/0/0/0/64"
		self.autoPitch = 0
		self.autoPitchMode = 0
		self.isReversed = 0
		self.autoDetectBeats = 0
		self.warpTime = 0
		self.groupID = -1
		self.effectsVisible = 1
		self.linkID = None

		self.video = None
		self.srcVideo = None
		self.videoEnabled = -1
		self.srcVideoX = -1
		self.srcVideoY = -1
		self.videoX = -1

		self.loopinfo = tracktion_loopinfo()
		self.effects = []

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'id': self.id_num = v
			elif n == 'name': self.name = str(v)
			elif n == 'start': self.start = float(v)
			elif n == 'length': self.length = float(v)
			elif n == 'offset': self.offset = float(v)
			elif n == 'source': self.source = str(v)
			elif n == 'mediaId': self.source = str(v)
			elif n == 'sync': self.sync = int(v)
			elif n == 'elastiqueMode': self.elastiqueMode = int(v)
			elif n == 'pan': self.pan = float(v)
			elif n == 'colour': self.colour = str(v)
			elif n == 'proxyAllowed': self.proxyAllowed = int(v)
			elif n == 'resamplingQuality': self.resamplingQuality = str(v)
			elif n == 'autoTempo': self.autoTempo = int(v)

			elif n == 'fadeIn': self.fadeIn = float(v)
			elif n == 'fadeOut': self.fadeOut = float(v)
			elif n == 'speed': self.speed = float(v)
			elif n == 'showingTakes': self.showingTakes = int(v)
			elif n == 'gain': self.gain = float(v)
			elif n == 'mute': self.mute = int(v)
			elif n == 'channels': self.channels = str(v)
			elif n == 'fadeInType': self.fadeInType = int(v)
			elif n == 'fadeOutType': self.fadeOutType = int(v)
			elif n == 'autoCrossfade': self.autoCrossfade = int(v)
			elif n == 'fadeInBehaviour': self.fadeInBehaviour = int(v)
			elif n == 'fadeOutBehaviour': self.fadeOutBehaviour = int(v)
			elif n == 'loopStart': self.loopStart = float(v)
			elif n == 'loopLength': self.loopLength = float(v)
			elif n == 'loopStartBeats': self.loopStartBeats = float(v)
			elif n == 'loopLengthBeats': self.loopLengthBeats = float(v)
			elif n == 'transpose': self.transpose = int(v)
			elif n == 'pitchChange': self.pitchChange = float(v)
			elif n == 'beatSensitivity': self.beatSensitivity = float(v)
			elif n == 'elastiqueOptions': self.elastiqueOptions = str(v)
			elif n == 'autoPitch': self.autoPitch = int(v)
			elif n == 'autoPitchMode': self.autoPitchMode = int(v)
			elif n == 'isReversed': self.isReversed = int(v)
			elif n == 'autoDetectBeats': self.autoDetectBeats = int(v)
			elif n == 'warpTime': self.warpTime = int(v)
			elif n == 'effectsVisible': self.effectsVisible = int(v)
			elif n == 'groupID': self.groupID = int(v)
			elif n == 'linkID': self.linkID = v

			elif n == 'video': self.video = v
			elif n == 'srcVideo': self.srcVideo = v
			elif n == 'videoEnabled': self.videoEnabled = int(v)
			elif n == 'srcVideoX': self.srcVideoX = int(v)
			elif n == 'srcVideoY': self.srcVideoY = int(v)
			elif n == 'videoX': self.videoX = int(v)

			else: logger_projparse.warning('tracktion_edit: audioclip: unimplemented attrib: '+n)

		for subxml in xmldata:
			if subxml.tag == 'LOOPINFO': self.loopinfo.load(subxml)
			if subxml.tag == 'EFFECTS': 
				for fxxml in subxml:
					afx_obj = tracktion_audioclip_fx()
					afx_obj.load(fxxml)
					self.effects.append(afx_obj)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "AUDIOCLIP")
		tempxml.set('name', str(self.name))
		tempxml.set('start', str(self.start))
		tempxml.set('length', str(self.length))
		tempxml.set('offset', str(self.offset))
		tempxml.set('id', str(self.id_num))
		tempxml.set('source', str(self.source))
		tempxml.set('sync', str(self.sync))
		tempxml.set('elastiqueMode', str(self.elastiqueMode))
		tempxml.set('pan', str(self.pan))
		tempxml.set('colour', str(self.colour))
		tempxml.set('proxyAllowed', str(self.proxyAllowed))
		tempxml.set('resamplingQuality', str(self.resamplingQuality))
		if self.linkID: tempxml.set('linkID', self.linkID)
		tempxml.set('autoTempo', str(self.autoTempo))

		if self.fadeIn != 0: tempxml.set('fadeIn', str(self.fadeIn))
		if self.fadeOut != 0: tempxml.set('fadeOut', str(self.fadeOut))
		if self.speed != 1: tempxml.set('speed', str(self.speed))
		if self.showingTakes != 0: tempxml.set('showingTakes', str(self.showingTakes))
		if self.gain != 0: tempxml.set('gain', str(self.gain))
		if self.mute != 0: tempxml.set('mute', str(self.mute))
		if self.channels != "L R": tempxml.set('channels', str(self.channels))
		if self.fadeInType != 1: tempxml.set('fadeInType', str(self.fadeInType))
		if self.fadeOutType != 1: tempxml.set('fadeOutType', str(self.fadeOutType))
		if self.autoCrossfade != 0: tempxml.set('autoCrossfade', str(self.autoCrossfade))
		if self.fadeInBehaviour != 0: tempxml.set('fadeInBehaviour', str(self.fadeInBehaviour))
		if self.fadeOutBehaviour != 0: tempxml.set('fadeOutBehaviour', str(self.fadeOutBehaviour))
		if self.loopStart != 0: tempxml.set('loopStart', str(self.loopStart))
		if self.loopLength != 0: tempxml.set('loopLength', str(self.loopLength))
		if self.loopStartBeats != 0: tempxml.set('loopStartBeats', str(self.loopStartBeats))
		if self.loopLengthBeats != 0: tempxml.set('loopLengthBeats', str(self.loopLengthBeats))
		if self.transpose != 0: tempxml.set('transpose', str(self.transpose))
		if self.pitchChange != 0: tempxml.set('pitchChange', str(self.pitchChange))
		if self.beatSensitivity != 0.5: tempxml.set('beatSensitivity', str(self.beatSensitivity))
		if self.elastiqueOptions != "1/0/0/0/64": tempxml.set('elastiqueOptions', str(self.elastiqueOptions))
		if self.autoPitch != 0: tempxml.set('autoPitch', str(self.autoPitch))
		if self.autoPitchMode != 0: tempxml.set('autoPitchMode', str(self.autoPitchMode))
		if self.isReversed != 0: tempxml.set('isReversed', str(self.isReversed))
		if self.autoDetectBeats != 0: tempxml.set('autoDetectBeats', str(self.autoDetectBeats))
		if self.warpTime != 0: tempxml.set('warpTime', str(self.warpTime))
		if self.effectsVisible != 1: tempxml.set('effectsVisible', str(self.effectsVisible))
		if self.groupID != -1: tempxml.set('groupID', str(self.groupID))

		if self.video: tempxml.set('video', str(self.video))
		if self.srcVideo: tempxml.set('srcVideo', str(self.srcVideo))
		if self.videoEnabled != -1: tempxml.set('videoEnabled', str(self.videoEnabled))
		if self.srcVideoX != -1: tempxml.set('srcVideoX', str(self.srcVideoX))
		if self.srcVideoY != -1: tempxml.set('srcVideoY', str(self.srcVideoY))
		if self.videoX != -1: tempxml.set('videoX', str(self.videoX))

		self.loopinfo.write(tempxml)

		if self.effects:
			effects = ET.SubElement(tempxml, "EFFECTS")
			for afx_obj in self.effects:
				afx_obj.write(effects)

# =================================================== STEP CLIP ===================================================

class tracktion_stepclip_channel:
	def __init__(self):
		self.channel = 1
		self.note = 36
		self.velocity = 96
		self.name = ''

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'channel': self.channel = int(v)
			if n == 'note': self.note = int(v)
			if n == 'velocity': self.velocity = int(v)
			if n == 'name': self.name = v

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "CHANNEL")
		tempxml.set('channel', str(self.channel))
		tempxml.set('note', str(self.note))
		tempxml.set('velocity', str(self.velocity))
		tempxml.set('name', str(self.name))

class tracktion_stepclip_pattern:
	def __init__(self):
		self.numNotes = 16
		self.noteLength = 0.25
		self.data = {}

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'numNotes': self.numNotes = int(v)
			if n == 'noteLength': self.noteLength = float(v)

		channum = 0
		for subxml in xmldata:
			if subxml.tag == 'CHANNEL':
				patdata = subxml.get('pattern')
				if patdata not in ['0', None]:
					self.data[channum] = patdata
				channum += 1

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "PATTERN")
		tempxml.set('numNotes', str(self.numNotes))
		tempxml.set('noteLength', str(self.noteLength))

		if self.data:
			for n in range(max(self.data.keys())+1):
				chanxml = ET.SubElement(tempxml, "CHANNEL")
				if n in self.data: chanxml.set('pattern', self.data[n])
				else: chanxml.set('pattern', '0')

class tracktion_stepclip:
	def __init__(self):
		self.id_num = 0
		self.name = ''
		self.start = 0
		self.length = 0
		self.offset = 0
		self.sequence = 0
		self.colour = 'ffff0000'
		self.repeatSequence = 0
		self.volDb = None
		self.speed = 1
		self.source = ''
		self.sync = 0
		self.showingTakes = 0
		self.mute = 0
		self.channels = []
		self.patterns = []
		self.groupID = -1
		self.originalLength = 0
		self.loopStartBeats = 0.0
		self.loopLengthBeats = 0.0
		self.followactions = None
		self.linkID = None

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'id': self.id_num = v
			elif n == 'name': self.name = str(v)
			elif n == 'start': self.start = float(v)
			elif n == 'length': self.length = float(v)
			elif n == 'offset': self.offset = float(v)
			elif n == 'sequence': self.sequence = [int(x) for x in v.split(',')]
			elif n == 'colour': self.colour = str(v)
			elif n == 'repeatSequence': self.repeatSequence = int(v)
			elif n == 'volDb': self.volDb = float(v)
			elif n == 'speed': self.speed = float(v)
			elif n == 'source': self.source = str(v)
			elif n == 'sync': self.sync = int(v)
			elif n == 'showingTakes': self.showingTakes = int(v)
			elif n == 'mute': self.mute = int(v)
			elif n == 'groupID': self.groupID = int(v)
			elif n == 'originalLength': self.originalLength = float(v)
			elif n == 'loopStartBeats': self.loopStartBeats = float(v)
			elif n == 'loopLengthBeats': self.loopLengthBeats = float(v)
			elif n == 'linkID': self.linkID = v
			else: logger_projparse.warning('tracktion_edit: stepclip: unimplemented attrib: '+n)

		for subxml in xmldata:
			if subxml.tag == 'CHANNELS':
				for chanxml in subxml:
					if chanxml.tag == 'CHANNEL':
						chan_obj = tracktion_stepclip_channel()
						chan_obj.load(chanxml)
						self.channels.append(chan_obj)
			elif subxml.tag == 'PATTERNS':
				for chanxml in subxml:
					if chanxml.tag == 'PATTERN':
						pat_obj = tracktion_stepclip_pattern()
						pat_obj.load(chanxml)
						self.patterns.append(pat_obj)
			elif subxml.tag == 'FOLLOWACTIONS':
				self.followactions = tracktion_followactions()
				self.followactions.load(subxml)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "STEPCLIP")
		if self.name: tempxml.set('name', str(self.name))
		tempxml.set('start', str(self.start))
		tempxml.set('length', str(self.length))
		tempxml.set('offset', str(self.offset))
		tempxml.set('id', str(self.id_num))
		tempxml.set('sequence', ','.join([str(x) for x in self.sequence]))
		tempxml.set('colour', str(self.colour))
		if self.repeatSequence: tempxml.set('repeatSequence', str(self.repeatSequence))
		if self.speed!=1: tempxml.set('speed', str(self.speed))
		if self.source: tempxml.set('source', str(self.source))
		if self.sync: tempxml.set('sync', str(self.sync))
		if self.showingTakes: tempxml.set('showingTakes', str(self.showingTakes))
		if self.mute: tempxml.set('mute', str(self.mute))
		if self.originalLength: tempxml.set('originalLength', str(self.originalLength))
		tempxml.set('loopStartBeats', str(self.loopStartBeats))
		if self.loopLengthBeats: tempxml.set('loopLengthBeats', str(self.loopLengthBeats))
		if self.volDb is not None: tempxml.set('volDb', str(self.volDb))
		if self.linkID: tempxml.set('linkID', self.linkID)
		if self.channels:
			chanxml = ET.SubElement(tempxml, "CHANNELS")
			for chan_obj in self.channels:
				chan_obj.write(chanxml)
		if self.patterns:
			patxml = ET.SubElement(tempxml, "PATTERNS")
			for chan_obj in self.patterns:
				chan_obj.write(patxml)
		if self.groupID != -1: tempxml.set('groupID', str(self.groupID))
		if self.followactions: self.followactions.write(tempxml)

# =================================================== TRACK ===================================================

class tracktion_inputdevicedestination:
	def __init__(self):
		self.targetID = None
		self.targetIndex = None

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'targetID': self.targetID = int(v)
			if n == 'targetIndex': self.targetIndex = int(v)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "INPUTDEVICEDESTINATION")
		if self.targetID is not None: tempxml.set('targetID', str(self.targetID))
		if self.targetIndex is not None: tempxml.set('targetIndex', str(self.targetIndex))

class tracktion_inputdevice:
	def __init__(self):
		self.name = None
		self.destinations = []

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'name': self.name = v

		for subxml in xmldata:
			if subxml.tag == 'INPUTDEVICEDESTINATION': 
				inputdevicedestination = tracktion_inputdevicedestination()
				inputdevicedestination.load(subxml)
				self.destinations.append(inputdevicedestination)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "INPUTDEVICE")
		if self.name: tempxml.set('name', str(self.name))
		for destination in self.destinations: destination.write(tempxml)

class tracktion_inputdevices:
	def __init__(self):
		self.devices = []

	def load(self, xmldata):
		for subxml in xmldata:
			if subxml.tag == 'INPUTDEVICE':
				imputdevice = tracktion_inputdevice()
				imputdevice.load(subxml)
				self.devices.append(imputdevice)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "INPUTDEVICES")
		for device in self.devices: device.write(tempxml)

class tracktion_outputdevices:
	def __init__(self):
		self.devices = []

	def load(self, xmldata):
		for subxml in xmldata:
			if subxml.tag == 'DEVICE': self.devices.append(subxml.attrib)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "OUTPUTDEVICES")
		for device in self.devices:
			devxml = ET.SubElement(tempxml, "DEVICE")
			for n, v in device.items(): devxml.set(n, str(v))

class tracktion_foldertrack:
	def __init__(self):
		self.id_num = 0
		self.height = 35.41053828354546
		self.expanded = 0
		self.tracks = []
		self.plugins = []
		self.macroparameters = tracktion_macroparameters()
		self.name = None
		self.colour = None
		self.mute = 0
		self.solo = 0
		self.modifiers = tracktion_modifiers()

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'id': self.id_num = v
			elif n == 'height': self.height = float(v)
			elif n == 'expanded': self.expanded = int(v)
			elif n == 'name': self.name = v
			elif n == 'colour': self.colour = v
			elif n == 'mute': self.mute = int(v)
			elif n == 'solo': self.solo = int(v)

		for subxml in xmldata:
			if subxml.tag == 'MACROPARAMETERS': self.macroparameters.load(subxml)
			elif subxml.tag == 'TRACK':
				track_obj = tracktion_track()
				track_obj.load(subxml)
				self.tracks.append(track_obj)
			elif subxml.tag in ['PLUGIN', 'FILTER']:
				plugin_obj = tracktion_plugin()
				plugin_obj.load(subxml)
				self.plugins.append(plugin_obj)
			elif subxml.tag == 'MODIFIERS': self.modifiers.load(subxml)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "FOLDERTRACK")
		tempxml.set('id', str(self.id_num))
		tempxml.set('height', str(self.height))
		if self.expanded: tempxml.set('expanded', str(self.expanded))
		if self.mute: tempxml.set('mute', str(self.mute))
		if self.solo: tempxml.set('solo', str(self.solo))
		self.macroparameters.write(tempxml)
		self.modifiers.write(tempxml)
		for track_obj in self.tracks:
			track_obj.write(tempxml)
		for plugin_obj in self.plugins:
			plugin_obj.write(tempxml)
		if self.name: tempxml.set('name', self.name)
		if self.colour: tempxml.set('colour', self.colour)

class tracktion_clipslot:
	def __init__(self):
		self.id_num = 0
		self.clip = None

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'id': self.id_num = v

		for subxml in xmldata:
			if subxml.tag == 'MIDICLIP':
				self.clip = tracktion_midiclip()
				self.clip.load(subxml)
			if subxml.tag == 'STEPCLIP':
				self.clip = tracktion_stepclip()
				self.clip.load(subxml)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "CLIPSLOT")
		tempxml.set('id', str(self.id_num))
		if self.clip:
			self.clip.write(tempxml)

class tracktion_track:
	def __init__(self):
		self.name = ''
		self.id_num = 0
		self.mute = 0
		self.solo = 0
		self.midiVProp = 0.28125
		self.midiVOffset = 0.359375
		self.colour = 'ffffaa00'
		self.height = 35.41053828354546
		self.plugins = []
		self.macroparameters = tracktion_macroparameters()
		self.outputdevices = tracktion_outputdevices()
		self.midiclips = []
		self.audioclips = []
		self.stepclips = []
		self.clipslots = []
		self.modifiers = tracktion_modifiers()

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'id': self.id_num = v
			elif n == 'midiVProp': self.midiVProp = float(v)
			elif n == 'midiVOffset': self.midiVOffset = float(v)
			elif n == 'colour': self.colour = v
			elif n == 'name': self.name = v
			elif n == 'height': self.height = float(v)
			elif n == 'mute': self.mute = int(v)
			elif n == 'solo': self.solo = int(v)

		for subxml in xmldata:
			if subxml.tag == 'MACROPARAMETERS': self.macroparameters.load(subxml)
			elif subxml.tag in ['PLUGIN', 'FILTER']:
				plugin_obj = tracktion_plugin()
				plugin_obj.load(subxml)
				self.plugins.append(plugin_obj)
			elif subxml.tag == 'OUTPUTDEVICES':
				self.outputdevices.load(subxml)
			elif subxml.tag == 'MIDICLIP':
				midiclip_obj = tracktion_midiclip()
				midiclip_obj.load(subxml)
				self.midiclips.append(midiclip_obj)
			elif subxml.tag == 'AUDIOCLIP':
				audioclip_obj = tracktion_audioclip()
				audioclip_obj.load(subxml)
				self.audioclips.append(audioclip_obj)
			elif subxml.tag == 'STEPCLIP':
				stepclip_obj = tracktion_stepclip()
				stepclip_obj.load(subxml)
				self.stepclips.append(stepclip_obj)
			elif subxml.tag == 'CLIP':
				if 'type' in subxml.attrib:
					cliptype = subxml.attrib['type']
					if cliptype == 'wave': 
						audioclip_obj = tracktion_audioclip()
						audioclip_obj.load(subxml)
						self.audioclips.append(audioclip_obj)
			elif subxml.tag == 'CLIPSLOTS':
				for subinxml in subxml:
					clipslot = tracktion_clipslot()
					clipslot.load(subinxml)
					self.clipslots.append(clipslot)
			elif subxml.tag == 'MODIFIERS': self.modifiers.load(subxml)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "TRACK")
		tempxml.set('id', str(self.id_num))
		tempxml.set('midiVProp', str(self.midiVProp))
		tempxml.set('midiVOffset', str(self.midiVOffset))
		tempxml.set('colour', str(self.colour))
		tempxml.set('height', str(self.height))
		if self.name: tempxml.set('name', str(self.name))
		if self.mute: tempxml.set('mute', str(self.mute))
		if self.solo: tempxml.set('solo', str(self.solo))
		self.macroparameters.write(tempxml)
		self.modifiers.write(tempxml)
		if self.clipslots is not None:
			x_clipslots = ET.SubElement(tempxml, "CLIPSLOTS")
			for clipslot in self.clipslots: clipslot.write(x_clipslots)
		for audioclip_obj in self.audioclips: audioclip_obj.write(tempxml)
		for stepclip_obj in self.stepclips: stepclip_obj.write(tempxml)
		for plugin_obj in self.plugins: plugin_obj.write(tempxml)
		for midiclip_obj in self.midiclips: midiclip_obj.write(tempxml)
		self.outputdevices.write(tempxml)

# =================================================== PROJECT OTHER TRACKS ===================================================

class tracktion_arrangerclip:
	def __init__(self):
		self.name = 'New Arranger'
		self.start = 0
		self.length = 0
		self.offset = 0
		self.id_num = 0
		self.colour = 'ffaa00ff'

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'id': self.id_num = v
			elif n == 'name': self.name = v
			elif n == 'start': self.start = float(v)
			elif n == 'length': self.length = float(v)
			elif n == 'offset': self.offset = float(v)
			elif n == 'colour': self.colour = v
			else: logger_projparse.warning('tracktion_edit: arrangerclip: unimplemented attrib: '+n)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "ARRANGERCLIP")
		tempxml.set('name', self.name)
		tempxml.set('start', str(self.start))
		tempxml.set('length', str(self.length))
		tempxml.set('offset', str(self.offset))
		tempxml.set('id', str(self.id_num))
		tempxml.set('colour', self.colour)

class tracktion_arrangertrack:
	def __init__(self):
		self.clips = []
		self.name = 'Arranger'
		self.id_num = 0
		self.height = 0
		self.macroparameters = tracktion_macroparameters()
		self.modifiers = tracktion_modifiers()

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'id': self.id_num = v
			elif n == 'name': self.name = v
			elif n == 'height': self.height = float(v)

		for subxml in xmldata:
			if subxml.tag == 'ARRANGERCLIP': 
				arrc_obj = tracktion_arrangerclip()
				arrc_obj.load(subxml)
				self.clips.append(arrc_obj)
			elif subxml.tag == 'MACROPARAMETERS': self.macroparameters.load(subxml)
			elif subxml.tag == 'MODIFIERS': self.modifiers.load(subxml)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "ARRANGERTRACK")
		if self.name: tempxml.set('name', str(self.name))
		tempxml.set('id', str(self.id_num))
		if self.height: tempxml.set('height', str(self.height))
		self.macroparameters.write(tempxml)
		self.modifiers.write(tempxml)
		for clip_obj in self.clips: clip_obj.write(tempxml)

class tracktion_markerclip:
	def __init__(self):
		self.name = 'Marker'
		self.start = 0
		self.length = 0
		self.offset = 0
		self.id_num = 0
		self.colour = 'ffaa00ff'
		self.markerID = 0
		self.speed = 1.0
		self.sync = 0

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'id': self.id_num = v
			elif n == 'name': self.name = v
			elif n == 'start': self.start = float(v)
			elif n == 'length': self.length = float(v)
			elif n == 'offset': self.offset = float(v)
			elif n == 'colour': self.colour = v
			elif n == 'markerID': self.markerID = int(v)
			elif n == 'speed': self.speed = float(v)
			elif n == 'sync': self.sync = int(v)
			else: logger_projparse.warning('tracktion_edit: markerclip: unimplemented attrib: '+n)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "MARKERCLIP")
		tempxml.set('name', self.name)
		tempxml.set('start', str(self.start))
		tempxml.set('length', str(self.length))
		tempxml.set('offset', str(self.offset))
		tempxml.set('id', str(self.id_num))
		tempxml.set('colour', self.colour)
		tempxml.set('markerID', str(self.markerID))
		tempxml.set('speed', str(self.speed))
		tempxml.set('sync', str(self.sync))

class tracktion_markertrack:
	def __init__(self):
		self.clips = []
		self.name = 'Marker'
		self.id_num = 0
		self.height = 0
		self.macroparameters = tracktion_macroparameters()
		self.modifiers = tracktion_modifiers()

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'id': self.id_num = v
			elif n == 'name': self.name = v
			elif n == 'height': self.height = float(v)

		for subxml in xmldata:
			if subxml.tag == 'MARKERCLIP': 
				arrc_obj = tracktion_markerclip()
				arrc_obj.load(subxml)
				self.clips.append(arrc_obj)
			elif subxml.tag == 'MACROPARAMETERS': self.macroparameters.load(subxml)
			elif subxml.tag == 'MODIFIERS': self.modifiers.load(subxml)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "MARKERTRACK")
		tempxml.set('id', str(self.id_num))
		if self.name: tempxml.set('name', str(self.name))
		if self.height: tempxml.set('height', str(self.height))
		self.macroparameters.write(tempxml)
		self.modifiers.write(tempxml)
		for clip_obj in self.clips:
			clip_obj.write(tempxml)

class tracktion_progression_item:
	def __init__(self):
		self.chordName = ''
		self.pitches = ''
		self.octave = 0

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'chordName': self.chordName = v
			elif n == 'pitches': self.pitches = v
			elif n == 'octave': self.octave = int(v)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "PROGRESSIONITEM")
		tempxml.set('chordName', self.chordName)
		tempxml.set('pitches', self.pitches)
		if self.octave: tempxml.set('octave', str(self.octave))

class tracktion_patterngenerator:
	def __init__(self):
		self.progression_items = []

	def load(self, xmldata):
		for subxml in xmldata:
			if subxml.tag == 'PROGRESSION':
				for subinxml in subxml:
					if subinxml.tag == 'PROGRESSIONITEM':
						pitem = tracktion_progression_item()
						pitem.load(subinxml)
						self.progression_items.append(pitem)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "PATTERNGENERATOR")
		x_progression = ET.SubElement(tempxml, "PROGRESSION")
		for progression_item in self.progression_items:
			progression_item.write(x_progression)

class tracktion_chordclip:
	def __init__(self):
		self.name = 'Chord'
		self.start = 0
		self.length = 0
		self.offset = 0
		self.id_num = 0
		self.colour = 'ffaa00ff'
		self.speed = 1.0
		self.groupID = 0
		self.patterngenerator = tracktion_patterngenerator()

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'id': self.id_num = v
			elif n == 'name': self.name = v
			elif n == 'start': self.start = float(v)
			elif n == 'length': self.length = float(v)
			elif n == 'offset': self.offset = float(v)
			elif n == 'colour': self.colour = v
			elif n == 'speed': self.speed = float(v)
			elif n == 'groupID': self.groupID = int(v)
			else: logger_projparse.warning('tracktion_edit: chordclip: unimplemented attrib: '+n)

		for subxml in xmldata:
			if subxml.tag == 'PATTERNGENERATOR': self.patterngenerator.load(subxml)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "CHORDCLIP")
		tempxml.set('name', self.name)
		tempxml.set('start', str(self.start))
		tempxml.set('length', str(self.length))
		tempxml.set('offset', str(self.offset))
		tempxml.set('id', str(self.id_num))
		tempxml.set('colour', self.colour)
		tempxml.set('speed', str(self.speed))
		if self.groupID: tempxml.set('groupID', str(self.groupID))
		self.patterngenerator.write(tempxml)

class tracktion_chordtrack:
	def __init__(self):
		self.clips = []
		self.name = 'Marker'
		self.id_num = 0
		self.height = 0
		self.macroparameters = tracktion_macroparameters()
		self.modifiers = tracktion_modifiers()

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'id': self.id_num = v
			elif n == 'name': self.name = v
			elif n == 'height': self.height = float(v)

		for subxml in xmldata:
			if subxml.tag == 'CHORDCLIP': 
				chord_obj = tracktion_chordclip()
				chord_obj.load(subxml)
				self.clips.append(chord_obj)
			elif subxml.tag == 'MACROPARAMETERS': self.macroparameters.load(subxml)
			elif subxml.tag == 'MODIFIERS': self.modifiers.load(subxml)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "CHORDTRACK")
		if self.name: tempxml.set('name', str(self.name))
		tempxml.set('id', str(self.id_num))
		if self.height: tempxml.set('height', str(self.height))
		self.macroparameters.write(tempxml)
		self.modifiers.write(tempxml)
		for clip_obj in self.clips:
			clip_obj.write(tempxml)

class tracktion_tempotrack:
	def __init__(self):
		self.clips = []
		self.name = 'Global'
		self.id_num = 0
		self.height = 0
		self.macroparameters = tracktion_macroparameters()
		self.modifiers = tracktion_modifiers()

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'id': self.id_num = v
			elif n == 'name': self.name = v
			elif n == 'height': self.height = float(v)

		for subxml in xmldata:
			if subxml.tag == 'MACROPARAMETERS': self.macroparameters.load(subxml)
			elif subxml.tag == 'MODIFIERS': self.modifiers.load(subxml)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "TEMPOTRACK")
		if self.name: tempxml.set('name', str(self.name))
		tempxml.set('id', str(self.id_num))
		if self.height: tempxml.set('height', str(self.height))
		self.macroparameters.write(tempxml)
		self.modifiers.write(tempxml)

class tracktion_mastertrack:
	def __init__(self):
		self.clips = []
		self.name = 'Master'
		self.id_num = 0
		self.height = 0
		self.macroparameters = tracktion_macroparameters()
		self.modifiers = tracktion_modifiers()

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'id': self.id_num = v
			elif n == 'name': self.name = v
			elif n == 'height': self.height = float(v)

		for subxml in xmldata:
			if subxml.tag == 'MACROPARAMETERS': self.macroparameters.load(subxml)
			elif subxml.tag == 'MODIFIERS': self.modifiers.load(subxml)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "MASTERTRACK")
		if self.name: tempxml.set('name', str(self.name))
		tempxml.set('id', str(self.id_num))
		if self.height: tempxml.set('height', str(self.height))
		self.macroparameters.write(tempxml)
		self.modifiers.write(tempxml)

# =================================================== PROJECT ===================================================

class tracktion_transport:
	def __init__(self):
		self.looping = 0
		self.endToEnd = 1
		self.position = 0.5
		self.scrubInterval = 0.1581309034119588
		self.loopPoint1 = -1
		self.loopPoint2 = -1
		self.start = -1

	def load(self, xmldata):
		looping = xmldata.get('looping')
		endToEnd = xmldata.get('endToEnd')
		position = xmldata.get('position')
		scrubInterval = xmldata.get('scrubInterval')
		start = xmldata.get('start')
		loopPoint1 = xmldata.get('loopPoint1')
		loopPoint2 = xmldata.get('loopPoint2')
		if endToEnd != None: self.endToEnd = int(endToEnd)
		if position != None: self.position = float(position)
		if scrubInterval != None: self.scrubInterval = float(scrubInterval)
		if start != None: self.start = float(start)
		if looping != None: self.looping = float(looping)
		if loopPoint1 != None: self.loopPoint1 = float(loopPoint1)
		if loopPoint2 != None: self.loopPoint2 = float(loopPoint2)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "TRANSPORT")
		tempxml.set('endToEnd', str(self.endToEnd))
		tempxml.set('position', str(self.position))
		tempxml.set('scrubInterval', str(self.scrubInterval))
		if self.looping: tempxml.set('looping', str(int(self.looping)))
		if self.start >= 0: tempxml.set('start', str(self.start))
		if self.loopPoint1 >= 0: tempxml.set('loopPoint1', str(self.loopPoint1))
		if self.loopPoint2 >= 0: tempxml.set('loopPoint2', str(self.loopPoint2))

class tracktion_edit:
	def __init__(self):
		self.appVersion = None
		self.projectID = None
		self.creationTime = None
		self.lastSignificantChange = None
		self.modifiedBy = None
		self.transport = tracktion_transport()
		self.macroparameters = tracktion_macroparameters()
		self.pitchsequence = tracktion_seq_pitch()
		self.temposequence = tracktion_seq_tempo()
		self.clicktrack = 0.6
		self.id3vorbismetadata = {}
		self.mastervolume = tracktion_plugin()
		self.arrangertrack = tracktion_arrangertrack()
		self.markertrack = tracktion_markertrack()
		self.chordtrack = tracktion_chordtrack()
		self.tempotrack = tracktion_tempotrack()
		self.mastertrack = tracktion_mastertrack()
		self.masterplugins = []
		self.tracks = []
		self.inputdevices = tracktion_inputdevices()
		self.racks = []
		self.auxbusnames = []

	def load_from_file(self, input_file):
		parser = ET.XMLParser(recover=True, encoding='utf-8')
		xml_data = ET.parse(input_file, parser)

		x_EDIT = xml_data.getroot()
		if x_EDIT == None: raise ProjectFileParserException('tracktion_edit: no XML root found')
		e = self.load_from_elementdata(x_EDIT)

		if DEBUG_IN_OUT:
			outfile = ET.ElementTree(x_EDIT)
			ET.indent(outfile)
			outfile.write('debug_in.xml', xml_declaration = True)
			self.save_to_file('debug_out.xml')
		return e

	def load_from_elementdata(self, x_EDIT):
		self.appVersion = x_EDIT.get('appVersion')
		self.projectID = x_EDIT.get('projectID')
		self.creationTime = x_EDIT.get('creationTime')
		self.lastSignificantChange = x_EDIT.get('lastSignificantChange')
		self.modifiedBy = x_EDIT.get('modifiedBy')

		for xmlpart in x_EDIT:
			#print(xmlpart.tag)

			if xmlpart.tag == 'TRANSPORT': self.transport.load(xmlpart)
			elif xmlpart.tag == 'MACROPARAMETERS': self.macroparameters.load(xmlpart)
			elif xmlpart.tag == 'PITCHSEQUENCE': self.pitchsequence.load(xmlpart)
			elif xmlpart.tag == 'TEMPOSEQUENCE': self.temposequence.load(xmlpart)
			elif xmlpart.tag == 'CLICKTRACK':
				level = xmlpart.get('level')
				if level: self.clicktrack = float(level)
			elif xmlpart.tag == 'ARRANGERTRACK': self.arrangertrack.load(xmlpart)
			elif xmlpart.tag == 'MARKERTRACK': self.markertrack.load(xmlpart)
			elif xmlpart.tag == 'CHORDTRACK': self.chordtrack.load(xmlpart)
			elif xmlpart.tag == 'TEMPOTRACK': self.tempotrack.load(xmlpart)
			elif xmlpart.tag == 'MASTERTRACK': self.mastertrack.load(xmlpart)
			elif xmlpart.tag == 'INPUTDEVICES': self.inputdevices.load(xmlpart)
			elif xmlpart.tag == 'ID3VORBISMETADATA': self.id3vorbismetadata = xmlpart.attrib
			elif xmlpart.tag == 'MASTERVOLUME':
				for subxml in xmlpart:
					if subxml.tag in ['PLUGIN', 'FILTER']:
						self.mastervolume.load(subxml)
			elif xmlpart.tag == 'MASTERPLUGINS':
				for subxml in xmlpart:
					if subxml.tag in ['PLUGIN', 'FILTER']:
						t_plug = tracktion_plugin()
						t_plug.load(subxml)
						self.masterplugins.append(t_plug)
			elif xmlpart.tag == 'TRACK':
				track_obj = tracktion_track()
				track_obj.load(xmlpart)
				self.tracks.append(track_obj)
			elif xmlpart.tag == 'FOLDERTRACK':
				track_obj = tracktion_foldertrack()
				track_obj.load(xmlpart)
				self.tracks.append(track_obj)
			elif xmlpart.tag == 'RACKS':
				for subxml in xmlpart:
					if subxml.tag == 'RACK':
						rack_obj = tracktion_rack()
						rack_obj.load(subxml)
						self.racks.append(rack_obj)
			elif xmlpart.tag == 'AUXBUSNAMES':
				for subxml in xmlpart:
					if subxml.tag == 'NAME':
						name_obj = tracktion_auxbusname()
						name_obj.load(subxml)
						self.auxbusnames.append(name_obj)
			#else:
			#	print(xmlpart.tag)
		return True

	def save_to_file(self, output_file):
		wf_proj = ET.Element("EDIT")
		if self.appVersion: wf_proj.set('appVersion', self.appVersion)
		if self.projectID: wf_proj.set('projectID', self.projectID)
		if self.creationTime: wf_proj.set('creationTime', self.creationTime)
		if self.lastSignificantChange: wf_proj.set('lastSignificantChange', self.lastSignificantChange)
		if self.modifiedBy: wf_proj.set('modifiedBy', self.modifiedBy)

		self.transport.write(wf_proj)
		self.macroparameters.write(wf_proj)
		self.pitchsequence.write(wf_proj)
		self.temposequence.write(wf_proj)
		ET.SubElement(wf_proj, "VIDEO")
		ET.SubElement(wf_proj, "AUTOMAPXML")
		wf_click = ET.SubElement(wf_proj, "CLICKTRACK")
		wf_click.set('level', str(self.clicktrack))
		id3_xml = ET.SubElement(wf_proj, "ID3VORBISMETADATA")
		for n, v in self.id3vorbismetadata.items(): id3_xml.set(n, str(v))
		wf_mv = ET.SubElement(wf_proj, "MASTERVOLUME")
		self.mastervolume.write(wf_mv)
		wf_racks = ET.SubElement(wf_proj, "RACKS")
		for plugin_obj in self.racks:
			plugin_obj.write(wf_racks)
		wf_mp = ET.SubElement(wf_proj, "MASTERPLUGINS")
		for plugin_obj in self.masterplugins:
			plugin_obj.write(wf_mp)
		abn = ET.SubElement(wf_proj, "AUXBUSNAMES")
		for x in self.auxbusnames: x.write(abn)
		self.inputdevices.write(wf_proj)
		ET.SubElement(wf_proj, "TRACKCOMPS")
		ET.SubElement(wf_proj, "ARADOCUMENT")
		ET.SubElement(wf_proj, "CONTROLLERMAPPINGS")

		self.arrangertrack.write(wf_proj)
		self.chordtrack.write(wf_proj)
		self.markertrack.write(wf_proj)
		self.tempotrack.write(wf_proj)
		self.mastertrack.write(wf_proj)

		for track_obj in self.tracks:
			track_obj.write(wf_proj)

		outfile = ET.ElementTree(wf_proj)
		ET.indent(outfile)
		outfile.write(output_file, encoding='utf-8', xml_declaration = True)