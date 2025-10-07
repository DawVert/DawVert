# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from lxml import etree as ET
DEBUG_IN_OUT = False

def set_value(xml_proj, name, val):
	tempxml = ET.SubElement(xml_proj, name)
	if val is not None: tempxml.text = str(val)
	return tempxml

class qtractor_connect:
	def __init__(self, xmldata):
		self.index = 0
		self.client = None
		self.port = None
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib
		if 'index' in trackattrib: self.index = int(trackattrib['index'])
		for xmlpart in xml_proj:
			if xmlpart.tag == 'client': self.client = xmlpart.text
			if xmlpart.tag == 'port': self.port = xmlpart.text

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'connect')
		tempxml.set('index', str(self.index))
		set_value(tempxml, 'client', self.client)
		set_value(tempxml, 'port', self.port)

# --------------------------------------------------------- MIDI MAP ---------------------------------------------------------

class qtractor_midi_patch:
	def __init__(self, xmldata):
		self.channel = 0
		self.midi_bank_sel_method = 0
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib
		if 'channel' in trackattrib: self.channel = int(trackattrib['channel'])
		for xmlpart in xml_proj:
			if xmlpart.tag == 'midi-bank-sel-method': self.midi_bank_sel_method = int(xmlpart.text)

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'midi-patch')
		tempxml.set('channel', str(self.channel))
		set_value(tempxml, 'midi-bank-sel-method', self.midi_bank_sel_method)

# --------------------------------------------------------- MIDI ENGINE ---------------------------------------------------------

class qtractor_midi_control:
	def __init__(self, xmldata):
		self.mmc_mode = 'duplex'
		self.mmc_device = 127
		self.spp_mode = 'duplex'
		self.clock_mode = 'none'
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		for xmlpart in xml_proj:
			if xmlpart.tag == 'mmc-mode': self.mmc_mode = xmlpart.text
			if xmlpart.tag == 'mmc-device': self.mmc_device = int(xmlpart.text)
			if xmlpart.tag == 'spp-mode': self.spp_mode = xmlpart.text
			if xmlpart.tag == 'clock-mode': self.clock_mode = xmlpart.text

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'midi-control')
		set_value(tempxml, 'mmc-mode', self.mmc_mode)
		set_value(tempxml, 'mmc-device', int(self.mmc_device))
		set_value(tempxml, 'spp-mode', self.spp_mode)
		set_value(tempxml, 'clock-mode', self.clock_mode)

class qtractor_midi_bus:
	def __init__(self, xmldata):
		self.mode = 'duplex'
		self.name = 'Master'
		self.monitor = 0
		self.input_gain = 1
		self.input_panning = 0
		self.input_controllers = []
		self.input_plugins = qtractor_plugins(None)
		self.input_connects = []

		self.output_gain = 1
		self.output_panning = 0
		self.output_controllers = []
		self.output_plugins = qtractor_plugins(None)
		self.output_connects = []

		self.plug_audio_output_bus = None
		self.audio_output_auto_connect = None
		self.midi_instrument_name = None

		self.midi_map = []

		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib
		if 'mode' in trackattrib: self.mode = trackattrib['mode']
		if 'name' in trackattrib: self.name = trackattrib['name']
		for xmlpart in xml_proj:
			if xmlpart.tag == 'monitor': self.monitor = int(xmlpart.text)
			if xmlpart.tag == 'input-gain': self.input_gain = float(xmlpart.text)
			if xmlpart.tag == 'input-panning': self.input_panning = float(xmlpart.text)
			if xmlpart.tag == 'input-controllers':
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'controller': self.input_controllers.append(qtractor_controller(xmlinpart))
			if xmlpart.tag == 'input-plugins': self.input_plugins.read(xmlpart)
			if xmlpart.tag == 'input-connects':
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'connect': self.input_connects.append(qtractor_connect(xmlinpart))
			if xmlpart.tag == 'output-gain': self.output_gain = float(xmlpart.text)
			if xmlpart.tag == 'output-panning': self.output_panning = float(xmlpart.text)
			if xmlpart.tag == 'output-controllers':
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'controller': self.output_controllers.append(qtractor_controller(xmlinpart))
			if xmlpart.tag == 'output-plugins': self.output_plugins.read(xmlpart)
			if xmlpart.tag == 'output-connects':
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'connect': self.output_connects.append(qtractor_connect(xmlinpart))
			if xmlpart.tag == 'midi-instrument-name': self.midi_instrument_name = xmlpart.text
			if xmlpart.tag == 'midi-map':
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'midi-patch': self.midi_map.append(qtractor_midi_patch(xmlinpart))

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'midi-bus')
		tempxml.set('mode', self.mode)
		tempxml.set('name', self.name)
		set_value(tempxml, 'monitor', int(self.monitor))
		set_value(tempxml, 'input-gain', float(self.input_gain))
		set_value(tempxml, 'input-panning', float(self.input_panning))
		controllerssxml = ET.SubElement(tempxml, 'input-controllers')
		for x in self.input_controllers: x.write(controllerssxml)
		self.input_plugins.write(tempxml, 'input-plugins')
		connectsxml = ET.SubElement(tempxml, 'input-connects')
		for x in self.input_connects: x.write(connectsxml)
		set_value(tempxml, 'output-gain', float(self.output_gain))
		set_value(tempxml, 'output-panning', float(self.output_panning))
		controllerssxml = ET.SubElement(tempxml, 'output-controllers')
		for x in self.output_controllers: x.write(controllerssxml)
		self.output_plugins.write(tempxml, 'output-plugins')
		connectsxml = ET.SubElement(tempxml, 'output-connects')
		for x in self.output_connects: x.write(connectsxml)
		if self.midi_instrument_name: set_value(tempxml, 'midi-instrument-name', self.midi_instrument_name)
		midi_mapxml = ET.SubElement(tempxml, 'midi-map')
		for x in self.midi_map: x.write(midi_mapxml)

class qtractor_midi_engine:
	def __init__(self, xmldata):
		self.midi_control = qtractor_midi_control(None)
		self.midi_bus = qtractor_midi_bus(None)
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		for xmlpart in xml_proj:
			if xmlpart.tag == 'midi-control': self.midi_control.read(xmlpart)
			if xmlpart.tag == 'midi-bus': self.midi_bus.read(xmlpart)

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'midi-engine')
		self.midi_control.write(tempxml)
		self.midi_bus.write(tempxml)

# --------------------------------------------------------- AUDIO ENGINE ---------------------------------------------------------

class qtractor_audio_control:
	def __init__(self, xmldata):
		self.transport_mode = 'duplex'
		self.timebase = 1
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		for xmlpart in xml_proj:
			if xmlpart.tag == 'transport-mode': self.transport_mode = xmlpart.text
			if xmlpart.tag == 'timebase': self.timebase = float(xmlpart.text)

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'audio-control')
		set_value(tempxml, 'transport-mode', self.transport_mode)
		set_value(tempxml, 'timebase', self.timebase)

class qtractor_audio_bus:
	def __init__(self, xmldata):
		self.mode = 'duplex'
		self.name = 'Master'
		self.monitor = 0
		self.channels = 2
		self.auto_connect = 1
		self.input_gain = 1
		self.input_panning = 0
		self.input_controllers = []
		self.input_plugins = qtractor_plugins(None)
		self.input_connects = []

		self.output_gain = 1
		self.output_panning = 0
		self.output_controllers = []
		self.output_plugins = qtractor_plugins(None)
		self.output_connects = []
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib
		if 'mode' in trackattrib: self.mode = trackattrib['mode']
		if 'name' in trackattrib: self.name = trackattrib['name']
		for xmlpart in xml_proj:
			if xmlpart.tag == 'monitor': self.monitor = int(xmlpart.text)
			if xmlpart.tag == 'channels': self.channels = int(xmlpart.text)
			if xmlpart.tag == 'auto-connect': self.auto_connect = int(xmlpart.text)
			if xmlpart.tag == 'input-gain': self.input_gain = float(xmlpart.text)
			if xmlpart.tag == 'input-panning': self.input_panning = float(xmlpart.text)
			if xmlpart.tag == 'input-controllers':
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'controller': self.input_controllers.append(qtractor_controller(xmlinpart))
			if xmlpart.tag == 'input-plugins': self.input_plugins.read(xmlpart)
			if xmlpart.tag == 'input-connects':
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'connect': self.input_connects.append(qtractor_connect(xmlinpart))
			if xmlpart.tag == 'output-gain': self.output_gain = float(xmlpart.text)
			if xmlpart.tag == 'output-panning': self.output_panning = float(xmlpart.text)
			if xmlpart.tag == 'output-controllers':
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'controller': self.output_controllers.append(qtractor_controller(xmlinpart))
			if xmlpart.tag == 'output-plugins': self.output_plugins.read(xmlpart)
			if xmlpart.tag == 'output-connects':
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'connect': self.output_connects.append(qtractor_connect(xmlinpart))

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'audio-bus')
		tempxml.set('mode', self.mode)
		tempxml.set('name', self.name)
		set_value(tempxml, 'monitor', int(self.monitor))
		set_value(tempxml, 'channels', int(self.channels))
		set_value(tempxml, 'auto-connect', int(self.auto_connect))
		set_value(tempxml, 'input-gain', float(self.input_gain))
		set_value(tempxml, 'input-panning', float(self.input_panning))
		controllerssxml = ET.SubElement(tempxml, 'input-controllers')
		for x in self.input_controllers: x.write(controllerssxml)
		self.input_plugins.write(tempxml, 'input-plugins')
		connectsxml = ET.SubElement(tempxml, 'input-connects')
		for x in self.input_connects: x.write(connectsxml)
		set_value(tempxml, 'output-gain', float(self.output_gain))
		set_value(tempxml, 'output-panning', float(self.output_panning))
		controllerssxml = ET.SubElement(tempxml, 'output-controllers')
		for x in self.output_controllers: x.write(controllerssxml)
		self.output_plugins.write(tempxml, 'output-plugins')
		connectsxml = ET.SubElement(tempxml, 'output-connects')
		for x in self.output_connects: x.write(connectsxml)

class qtractor_audio_engine:
	def __init__(self, xmldata):
		self.audio_control = qtractor_audio_control(None)
		self.audio_bus = qtractor_audio_bus(None)
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		for xmlpart in xml_proj:
			if xmlpart.tag == 'audio-control': self.audio_control.read(xmlpart)
			if xmlpart.tag == 'audio-bus': self.audio_bus.read(xmlpart)

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'audio-engine')
		self.audio_control.write(tempxml)
		self.audio_bus.write(tempxml)

# --------------------------------------------------------- CONTROLLER ---------------------------------------------------------

class qtractor_controller:
	def __init__(self, xmldata):
		self.index = 0
		self.name = ""
		self.type = ""

		self.channel = 0
		self.param = 0
		self.logarithmic = 0
		self.feedback = 0
		self.invert = 0
		self.hook = 0
		self.latch = 0
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib
		if 'index' in trackattrib: self.index = trackattrib['index']
		if 'name' in trackattrib: self.name = trackattrib['name']
		if 'type' in trackattrib: self.type = trackattrib['type']

		for xmlpart in xml_proj:
			if xmlpart.tag == 'channel': self.channel = int(xmlpart.text)
			if xmlpart.tag == 'param': self.param = int(xmlpart.text)
			if xmlpart.tag == 'logarithmic': self.logarithmic = int(xmlpart.text)
			if xmlpart.tag == 'feedback': self.feedback = int(xmlpart.text)
			if xmlpart.tag == 'invert': self.invert = int(xmlpart.text)
			if xmlpart.tag == 'hook': self.hook = float(xmlpart.text)
			if xmlpart.tag == 'latch': self.latch = int(xmlpart.text)

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'controller')
		tempxml.set('index', str(self.index))
		tempxml.set('name', self.name)
		tempxml.set('type', self.type)
		set_value(tempxml, 'channel', self.channel)
		set_value(tempxml, 'param', self.param)
		set_value(tempxml, 'logarithmic', self.logarithmic)
		set_value(tempxml, 'feedback', self.feedback)
		set_value(tempxml, 'invert', self.invert)
		set_value(tempxml, 'hook', self.hook)
		set_value(tempxml, 'latch', self.latch)

# --------------------------------------------------------- CLIP ---------------------------------------------------------

class qtractor_clip_properties:
	def __init__(self, xmldata):
		self.name = ''
		self.start = 0
		self.offset = 0
		self.length = 0
		self.gain = 1
		self.panning = 0
		self.mute = 0
		self.fade_in = 0
		self.fade_out = 0
		self.fade_in_type = ''
		self.fade_out_type = ''
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		for xmlpart in xml_proj:
			if xmlpart.tag == 'name': self.name = xmlpart.text
			if xmlpart.tag == 'start': self.start = int(xmlpart.text)
			if xmlpart.tag == 'offset': self.offset = int(xmlpart.text)
			if xmlpart.tag == 'length': self.length = int(xmlpart.text)
			if xmlpart.tag == 'gain': self.gain = float(xmlpart.text)
			if xmlpart.tag == 'panning': self.panning = float(xmlpart.text)
			if xmlpart.tag == 'fade-in': 
				self.fade_in = int(xmlpart.text)
				self.fade_in_type = xmlpart.get('type')
			if xmlpart.tag == 'fade-out': 
				self.fade_out = int(xmlpart.text)
				self.fade_out_type = xmlpart.get('type')

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'properties')
		set_value(tempxml, 'name', self.name)
		set_value(tempxml, 'start', self.start)
		set_value(tempxml, 'offset', self.offset)
		set_value(tempxml, 'length', self.length)
		set_value(tempxml, 'gain', self.gain)
		set_value(tempxml, 'panning', self.panning)
		set_value(tempxml, 'mute', self.mute)
		fade_in = set_value(tempxml, 'fade-in', self.fade_in)
		if self.fade_in_type: fade_in.set('type', self.fade_in_type)
		fade_out = set_value(tempxml, 'fade-out', self.fade_out)
		if self.fade_out_type: fade_out.set('type', self.fade_out_type)

class qtractor_clip_audioclip:
	def __init__(self, xmldata):
		self.filename = ''
		self.time_stretch = 1
		self.pitch_shift = 1
		self.wsola_time_stretch = 1
		self.wsola_quick_seek = 0
		self.rubberband_formant = 0
		self.rubberband_finer_r3 = 0
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		for xmlpart in xml_proj:
			if xmlpart.tag == 'filename': self.filename = xmlpart.text
			if xmlpart.tag == 'time-stretch': self.time_stretch = float(xmlpart.text)
			if xmlpart.tag == 'pitch-shift': self.pitch_shift = float(xmlpart.text)
			if xmlpart.tag == 'wsola-time-stretch': self.wsola_time_stretch = xmlpart.text
			if xmlpart.tag == 'wsola-quick-seek': self.wsola_quick_seek = xmlpart.text
			if xmlpart.tag == 'rubberband-formant': self.rubberband_formant = xmlpart.text
			if xmlpart.tag == 'rubberband-finer-r3': self.rubberband_finer_r3 = xmlpart.text

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'audio-clip')
		set_value(tempxml, 'filename', self.filename)
		set_value(tempxml, 'time-stretch', self.time_stretch)
		set_value(tempxml, 'pitch-shift', self.pitch_shift)
		set_value(tempxml, 'wsola-time-stretch', self.wsola_time_stretch)
		set_value(tempxml, 'wsola-quick-seek', self.wsola_quick_seek)
		set_value(tempxml, 'rubberband-formant', self.rubberband_formant)
		set_value(tempxml, 'rubberband-finer-r3', self.rubberband_finer_r3)

class qtractor_clip_midiclip:
	def __init__(self, xmldata):
		self.filename = ''
		self.track_channel = 1
		self.revision = 2
		self.editor_pos = ''
		self.editor_size = ''
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		for xmlpart in xml_proj:
			if xmlpart.tag == 'filename': self.filename = xmlpart.text
			if xmlpart.tag == 'track-channel': self.track_channel = xmlpart.text
			if xmlpart.tag == 'revision': self.revision = xmlpart.text
			if xmlpart.tag == 'editor-pos': self.editor_pos = xmlpart.text
			if xmlpart.tag == 'editor-size': self.editor_size = xmlpart.text

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'midi-clip')
		if self.filename: set_value(tempxml, 'filename', self.filename)
		set_value(tempxml, 'track-channel', self.track_channel)
		set_value(tempxml, 'revision', self.revision)
		if self.editor_pos: set_value(tempxml, 'editor-pos', self.editor_pos)
		if self.editor_size: set_value(tempxml, 'editor-size', self.editor_size)

class qtractor_clip:
	def __init__(self, xmldata):
		self.name = ''
		self.properties = qtractor_clip_properties(None)
		self.audioclip = None
		self.midiclip = None
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib

		if 'name' in trackattrib: self.name = trackattrib['name']

		for xmlpart in xml_proj:
			if xmlpart.tag == 'properties': self.properties.read(xmlpart)
			if xmlpart.tag == 'audio-clip': self.audioclip = qtractor_clip_audioclip(xmlpart)
			if xmlpart.tag == 'midi-clip': self.midiclip = qtractor_clip_midiclip(xmlpart)

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'clip')
		tempxml.set('name', self.name)
		self.properties.write(tempxml)
		if self.audioclip: self.audioclip.write(tempxml)
		if self.midiclip: self.midiclip.write(tempxml)

# --------------------------------------------------------- PLUGINS ---------------------------------------------------------

class qtractor_plugins:
	def __init__(self, xmldata):
		self.plugins = []
		self.plug_audio_output_bus = None
		self.audio_output_auto_connect = None

	def __iter__(self):
		return self.plugins.__iter__()

	def read(self, xml_proj):
		for xmlpart in xml_proj:
			if xmlpart.tag == 'plugin': self.plugins.append(qtractor_plugin(xmlpart))
			if xmlpart.tag == 'audio-output-bus': self.plug_audio_output_bus = xmlpart.text
			if xmlpart.tag == 'audio-output-auto-connect': self.audio_output_auto_connect = xmlpart.text

	def write(self, in_xml, tagname):
		tempxml = ET.SubElement(in_xml, tagname)
		for x in self.plugins: x.write(tempxml)
		if self.plug_audio_output_bus is not None: set_value(tempxml, 'audio-output-bus', self.plug_audio_output_bus)
		if self.audio_output_auto_connect is not None: set_value(tempxml, 'audio-output-auto-connect', self.audio_output_auto_connect)

class qtractor_plugin_param:
	def __init__(self, xmldata):
		self.index = ''
		self.name = ''
		self.value = '0'
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib
		if 'index' in trackattrib: self.index = trackattrib['index']
		if 'name' in trackattrib: self.name = trackattrib['name']
		self.value = xml_proj.text

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'param')
		tempxml.set('index', self.index)
		tempxml.set('name', self.name)
		tempxml.text = str(self.value)

class qtractor_plugin:
	def __init__(self, xmldata):
		self.type = ''
		self.alias = ''
		self.filename = ''
		self.index = ''
		self.label = ''
		self.preset = ''
		self.direct_access_param = ''
		self.activated = ''
		self.params = []
		self.editor_pos = ''
		self.form_pos = ''
		self.configs = []
		self.curve_file = qtractor_track_curve_file(None)
		self.controllers = []
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib

		if 'type' in trackattrib: self.type = trackattrib['type']

		for xmlpart in xml_proj:
			if xmlpart.tag == 'filename': self.filename = xmlpart.text
			if xmlpart.tag == 'index': self.index = xmlpart.text
			if xmlpart.tag == 'label': self.label = xmlpart.text
			if xmlpart.tag == 'preset': self.preset = xmlpart.text
			if xmlpart.tag == 'direct-access-param': self.direct_access_param = xmlpart.text
			if xmlpart.tag == 'activated': self.activated = int(xmlpart.text)
			if xmlpart.tag == 'alias': self.alias = xmlpart.text
			if xmlpart.tag == 'params':
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'param': 
						self.params.append(qtractor_plugin_param(xmlinpart))
			if xmlpart.tag == 'configs':
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'config': 
						self.configs.append([xmlinpart.get('key'), xmlinpart.get('type'), xmlinpart.text])
			if xmlpart.tag == 'controllers':
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'controller': 
						self.controllers.append(qtractor_controller(xmlinpart))
			if xmlpart.tag == 'editor-pos': self.editor_pos = xmlpart.text
			if xmlpart.tag == 'form-pos': self.form_pos = xmlpart.text
			if xmlpart.tag == 'curve-file': self.curve_file.read(xmlpart)

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'plugin')
		tempxml.set('type', self.type)
		set_value(tempxml, 'filename', self.filename)
		set_value(tempxml, 'index', self.index)
		set_value(tempxml, 'label', self.label)
		if self.alias: set_value(tempxml, 'alias', self.alias)
		if self.preset: set_value(tempxml, 'preset', self.preset)
		if self.direct_access_param: set_value(tempxml, 'direct-access-param', self.direct_access_param)
		set_value(tempxml, 'activated', self.activated)
		configsxml = ET.SubElement(tempxml, 'configs')
		for c_key, c_type, c_value in self.configs:
			configxml = ET.SubElement(configsxml, 'config')
			configxml.set('key', str(c_key))
			if c_type: configxml.set('type', str(c_type))
			configxml.text = str(c_value)
		paramsxml = ET.SubElement(tempxml, 'params')
		for x in self.params: x.write(paramsxml)
		controllerssxml = ET.SubElement(tempxml, 'controllers')
		for x in self.controllers: x.write(controllerssxml)
		self.curve_file.write(tempxml)
		set_value(tempxml, 'editor-pos', self.editor_pos)
		set_value(tempxml, 'form-pos', self.form_pos)

# --------------------------------------------------------- CURVE ---------------------------------------------------------

class qtractor_track_curve_item:
	def __init__(self, xmldata):
		self.index = 0
		self.mode = ''
		self.name = ''
		self.curve_item = []

		self.p_type = "CONTROLLER"
		self.p_channel = 0
		self.p_param = 0
		self.p_mode = ""
		self.p_process = 0
		self.p_capture = 0
		self.p_locked = 0
		self.p_logarithmic = 0
		self.p_color = "#800000"

		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		self.used = True
		trackattrib = xml_proj.attrib

		if 'index' in trackattrib: self.index = int(trackattrib['index'])
		if 'mode' in trackattrib: self.mode = trackattrib['mode']
		if 'name' in trackattrib: self.name = trackattrib['name']

		for xmlpart in xml_proj:
			if xmlpart.tag == 'type': self.p_type = xmlpart.text
			if xmlpart.tag == 'channel': self.p_channel = int(xmlpart.text)
			if xmlpart.tag == 'param': self.p_param = int(xmlpart.text)
			if xmlpart.tag == 'mode': self.p_mode = xmlpart.text
			if xmlpart.tag == 'process': self.p_process = int(xmlpart.text)
			if xmlpart.tag == 'capture': self.p_capture = int(xmlpart.text)
			if xmlpart.tag == 'locked': self.p_locked = int(xmlpart.text)
			if xmlpart.tag == 'logarithmic': self.p_logarithmic = int(xmlpart.text)
			if xmlpart.tag == 'color': self.p_color = xmlpart.text

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'curve-item')
		tempxml.set('index', str(self.index))
		tempxml.set('mode', str(self.mode))
		tempxml.set('name', str(self.name))
		set_value(tempxml, 'type', str(self.p_type))
		set_value(tempxml, 'channel', str(self.p_channel))
		set_value(tempxml, 'param', str(self.p_param))
		set_value(tempxml, 'mode', str(self.p_mode))
		set_value(tempxml, 'process', str(self.p_process))
		set_value(tempxml, 'capture', str(self.p_capture))
		set_value(tempxml, 'locked', str(self.p_locked))
		set_value(tempxml, 'logarithmic', str(self.p_logarithmic))
		set_value(tempxml, 'color', str(self.p_color))


class qtractor_track_curve_file:
	def __init__(self, xmldata):
		self.used = False
		self.filename = ''
		self.current = -1
		self.curve_items = []
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		self.used = True
		for xmlpart in xml_proj:
			if xmlpart.tag == 'filename': self.filename = xmlpart.text
			if xmlpart.tag == 'current': self.current = int(xmlpart.text)
			if xmlpart.tag == 'curve-items': 
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'curve-item': 
						self.curve_items.append(qtractor_track_curve_item(xmlinpart))

	def write(self, in_xml):
		if self.used:
			tempxml = ET.SubElement(in_xml, 'curve-file')
			if self.curve_items:
				curveitemsxml = ET.SubElement(tempxml, 'curve-items')
				for curve_item in self.curve_items: curve_item.write(curveitemsxml)
			if self.filename: set_value(tempxml, 'filename', self.filename)
			if self.current!=-1: set_value(tempxml, 'current', self.current)

# --------------------------------------------------------- TRACK ---------------------------------------------------------

class qtractor_track_properties:
	def __init__(self, xmldata):
		self.input_bus = ''
		self.output_bus = ''
		self.midi_omni = None
		self.midi_channel = None
		self.midi_bank_sel_method = None
		self.midi_drums = None
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		for xmlpart in xml_proj:
			if xmlpart.tag == 'input-bus': self.input_bus = xmlpart.text
			if xmlpart.tag == 'output-bus': self.output_bus = xmlpart.text
			if xmlpart.tag == 'midi-omni': self.midi_omni = xmlpart.text
			if xmlpart.tag == 'midi-channel': self.midi_channel = xmlpart.text
			if xmlpart.tag == 'midi-bank-sel-method': self.midi_bank_sel_method = xmlpart.text
			if xmlpart.tag == 'midi-drums': self.midi_drums = xmlpart.text

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'properties')
		set_value(tempxml, 'input-bus', self.input_bus)
		set_value(tempxml, 'output-bus', self.output_bus)
		if self.midi_omni is not None: set_value(tempxml, 'midi-omni', str(self.midi_omni))
		if self.midi_channel is not None: set_value(tempxml, 'midi-channel', str(self.midi_channel))
		if self.midi_bank_sel_method is not None: set_value(tempxml, 'midi-bank-sel-method', str(self.midi_bank_sel_method))
		if self.midi_drums is not None: set_value(tempxml, 'midi-drums', str(self.midi_drums))

class qtractor_track_state:
	def __init__(self, xmldata):
		self.mute = 0
		self.solo = 0
		self.record = 0
		self.monitor = 0
		self.gain = 1
		self.panning = 0
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		for xmlpart in xml_proj:
			if xmlpart.tag == 'mute': self.mute = int(xmlpart.text)
			if xmlpart.tag == 'solo': self.solo = int(xmlpart.text)
			if xmlpart.tag == 'record': self.record = int(xmlpart.text)
			if xmlpart.tag == 'monitor': self.monitor = int(xmlpart.text)
			if xmlpart.tag == 'gain': self.gain = float(xmlpart.text)
			if xmlpart.tag == 'panning': self.panning = float(xmlpart.text)

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'state')
		set_value(tempxml, 'mute', str(self.mute))
		set_value(tempxml, 'solo', str(self.solo))
		set_value(tempxml, 'record', str(self.record))
		set_value(tempxml, 'monitor', str(self.monitor))
		set_value(tempxml, 'gain', str(self.gain))
		set_value(tempxml, 'panning', str(self.panning))

class qtractor_track_view:
	def __init__(self, xmldata):
		self.height = 96
		self.background_color = None
		self.foreground_color = None
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		for xmlpart in xml_proj:
			if xmlpart.tag == 'height': self.height = int(xmlpart.text)
			if xmlpart.tag == 'background-color': self.background_color = xmlpart.text
			if xmlpart.tag == 'foreground-color': self.foreground_color = xmlpart.text

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'view')
		set_value(tempxml, 'height', str(self.height))
		if self.background_color: set_value(tempxml, 'background-color', str(self.background_color))
		if self.foreground_color: set_value(tempxml, 'foreground-color', str(self.foreground_color))

class qtractor_track:
	def __init__(self, xmldata):
		self.name = ''
		self.type = ''
		self.properties = qtractor_track_properties(None)
		self.state = qtractor_track_state(None)
		self.view = qtractor_track_view(None)
		self.curve_file = qtractor_track_curve_file(None)
		self.clips = []
		self.plugins = qtractor_plugins(None)
		self.plug_audio_output_bus = None
		self.audio_output_auto_connect = None
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib

		if 'name' in trackattrib: self.name = trackattrib['name']
		if 'type' in trackattrib: self.type = trackattrib['type']

		for xmlpart in xml_proj:
			if xmlpart.tag == 'properties': self.properties.read(xmlpart)
			if xmlpart.tag == 'state': self.state.read(xmlpart)
			if xmlpart.tag == 'view': self.view.read(xmlpart)
			if xmlpart.tag == 'curve-file': self.curve_file.read(xmlpart)
			if xmlpart.tag == 'clips':
				for xmlinpart in xmlpart:
					self.clips.append(qtractor_clip(xmlinpart))
			if xmlpart.tag == 'plugins': self.plugins.read(xmlpart)

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'track')
		tempxml.set('name', self.name)
		tempxml.set('type', self.type)
		self.properties.write(tempxml)
		self.state.write(tempxml)
		self.view.write(tempxml)
		ET.SubElement(tempxml, 'controllers')
		self.curve_file.write(tempxml)
		clipsxml = ET.SubElement(tempxml, 'clips')
		for x in self.clips: x.write(clipsxml)
		self.plugins.write(tempxml, 'plugins')
		if self.plug_audio_output_bus is not None: 
			set_value(pluginsxml, 'audio-output-bus', self.plug_audio_output_bus)
		if self.audio_output_auto_connect is not None: 
			set_value(pluginsxml, 'audio-output-auto-connect', self.audio_output_auto_connect)

# --------------------------------------------------------- PROJECT ---------------------------------------------------------

class qtractor_proj_properties:
	def __init__(self, xmldata):
		self.directory = ''
		self.description = ''
		self.sample_rate = 48000
		self.tempo = 110
		self.ticks_per_beat = 960
		self.beats_per_bar = 4
		self.beat_divisor = 2
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		for xmlpart in xml_proj:
			if xmlpart.tag == 'directory': self.directory = xmlpart.text
			if xmlpart.tag == 'description': self.description = xmlpart.text
			if xmlpart.tag == 'sample-rate': self.sample_rate = int(xmlpart.text)
			if xmlpart.tag == 'tempo': self.tempo = float(xmlpart.text)
			if xmlpart.tag == 'ticks-per-beat': self.ticks_per_beat = int(xmlpart.text)
			if xmlpart.tag == 'beats-per-bar': self.beats_per_bar = int(xmlpart.text)
			if xmlpart.tag == 'beat-divisor': self.beat_divisor = int(xmlpart.text)

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'properties')
		set_value(tempxml, 'directory', self.directory)
		set_value(tempxml, 'description', self.description)
		set_value(tempxml, 'sample-rate', self.sample_rate)
		set_value(tempxml, 'tempo', str(self.tempo))
		set_value(tempxml, 'ticks-per-beat', self.ticks_per_beat)
		set_value(tempxml, 'beats-per-bar', self.beats_per_bar)
		set_value(tempxml, 'beat-divisor', self.beat_divisor)

class qtractor_proj_state:
	def __init__(self, xmldata):
		self.loop_start = 0
		self.loop_end = 0
		self.punch_in = 0
		self.punch_out = 0
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		for xmlpart in xml_proj:
			if xmlpart.tag == 'loop-start': self.loop_start = int(xmlpart.text)
			if xmlpart.tag == 'loop-end': self.loop_end = int(xmlpart.text)
			if xmlpart.tag == 'punch-in': self.punch_in = int(xmlpart.text)
			if xmlpart.tag == 'punch-out': self.punch_out = int(xmlpart.text)

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'state')
		set_value(tempxml, 'loop-start', self.loop_start)
		set_value(tempxml, 'loop-end', self.loop_end)
		set_value(tempxml, 'punch-in', self.punch_in)
		set_value(tempxml, 'punch-out', self.punch_out)

class qtractor_proj_files:
	def __init__(self, xmldata):
		self.audio_list = {}
		self.midi_list = {}
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		for xmlpart in xml_proj:
			if xmlpart.tag == 'audio-list': 
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'file': 
						self.audio_list[xmlinpart.get('name')] = xmlinpart.text

			if xmlpart.tag == 'midi-list': 
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'file': 
						self.midi_list[xmlinpart.get('name')] = xmlinpart.text


	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'files')
		audio_list = ET.SubElement(tempxml, 'audio-list')
		for name, filename in self.audio_list.items():
			xmlfile = ET.SubElement(audio_list, 'file')
			xmlfile.set('name', name)
			xmlfile.text = filename

		midi_list = ET.SubElement(tempxml, 'midi-list')
		for name, filename in self.midi_list.items():
			xmlfile = ET.SubElement(midi_list, 'file')
			xmlfile.set('name', name)
			xmlfile.text = filename

class qtractor_tempo_map:
	def __init__(self, xmldata):
		self.bar = 0
		self.frame = 0
		self.tempo = 120
		self.beat_type = 0
		self.beats_per_bar = 0
		self.beat_divisor = 0
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib
		if 'bar' in trackattrib: self.bar = int(trackattrib['bar'])
		if 'frame' in trackattrib: self.frame = int(trackattrib['frame'])

		for xmlpart in xml_proj:
			if xmlpart.tag == 'tempo': self.tempo = float(xmlpart.text)
			if xmlpart.tag == 'beat-type': self.beat_type = int(xmlpart.text)
			if xmlpart.tag == 'beats-per-bar': self.beats_per_bar = int(xmlpart.text)
			if xmlpart.tag == 'beat-divisor': self.beat_divisor = int(xmlpart.text)

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'tempo-node')
		tempxml.set('bar', str(self.bar))
		tempxml.set('frame', str(self.frame))
		set_value(tempxml, 'tempo', str(self.tempo))
		set_value(tempxml, 'beat-type', str(self.beat_type))
		set_value(tempxml, 'beats-per-bar', str(self.beats_per_bar))
		set_value(tempxml, 'beat-divisor', str(self.beat_divisor))

class qtractor_marker:
	def __init__(self, xmldata):
		self.accidentals = 0
		self.mode = 0
		self.frame = 0
		self.text = ''
		self.color = ''

		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib
		if 'frame' in trackattrib: self.frame = int(trackattrib['frame'])

		for xmlpart in xml_proj:
			if xmlpart.tag == 'accidentals': self.accidentals = int(xmlpart.text)
			if xmlpart.tag == 'mode': self.mode = int(xmlpart.text)
			if xmlpart.tag == 'text': self.text = xmlpart.text
			if xmlpart.tag == 'color': self.color = xmlpart.text

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'marker')
		tempxml.set('frame', str(self.frame))
		if self.text: set_value(tempxml, 'text', self.text)
		if self.color: set_value(tempxml, 'color', self.color)
		set_value(tempxml, 'accidentals', str(self.accidentals))
		set_value(tempxml, 'mode', str(self.mode))

class qtractor_project:
	def __init__(self):
		self.properties = qtractor_proj_properties(None)
		self.state = qtractor_proj_state(None)
		self.files = qtractor_proj_files(None)
		self.devices = []
		self.tempo_map = []
		self.markers = []
		self.tracks = []
		self.name = ''
		self.version = ''

	def load_from_file(self, input_file):
		self.metadata = {}
		parser = ET.XMLParser()
		xml_data = ET.parse(input_file, parser)
		xml_proj = xml_data.getroot()
		if xml_proj == None: raise ProjectFileParserException('qtractor: no XML root found')

		trackattrib = xml_proj.attrib
		if 'name' in trackattrib: self.name = trackattrib['name']
		if 'version' in trackattrib: self.version = trackattrib['version']

		for xmlpart in xml_proj:
			if xmlpart.tag == 'devices': 
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'audio-engine': self.devices.append(qtractor_audio_engine(xmlinpart))
					if xmlinpart.tag == 'midi-engine': self.devices.append(qtractor_midi_engine(xmlinpart))
			if xmlpart.tag == 'properties': self.properties.read(xmlpart)
			if xmlpart.tag == 'state': self.state.read(xmlpart)
			if xmlpart.tag == 'files': self.files.read(xmlpart)
			if xmlpart.tag == 'tempo-map': 
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'tempo-node':
						self.tempo_map.append(qtractor_tempo_map(xmlinpart))
			if xmlpart.tag == 'markers': 
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'marker':
						self.markers.append(qtractor_marker(xmlinpart))
				#self.tempo_map.read(xmlpart)
			if xmlpart.tag == 'tracks':
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'track':
						self.tracks.append(qtractor_track(xmlinpart))

		if DEBUG_IN_OUT:
			outfile = ET.ElementTree(xml_proj)
			outfile.write('debug_in.xml', xml_declaration = True)
			self.write_to_file('debug_out.xml')

		return True

	def write_to_file(self, output_file):
		xml_proj = ET.Element("session")

		xml_proj.set('name', self.name)
		xml_proj.set('version', self.version)
		self.properties.write(xml_proj)
		self.state.write(xml_proj)
		self.files.write(xml_proj)
		if self.devices:
			devicesxml = ET.SubElement(xml_proj, 'devices')
			for x in self.devices: x.write(devicesxml)
		if self.tempo_map:
			tempo_mapxml = ET.SubElement(xml_proj, 'tempo-map')
			for x in self.tempo_map: x.write(tempo_mapxml)
		if self.markers:
			markersxml = ET.SubElement(xml_proj, 'markers')
			for x in self.markers: x.write(markersxml)
		tracksxml = ET.SubElement(xml_proj, 'tracks')
		for x in self.tracks: x.write(tracksxml)

		outfile = ET.ElementTree(xml_proj)
		ET.indent(outfile, space=" ", level=0)
		outfile.write(output_file, doctype="<!DOCTYPE qtractorSession>")
