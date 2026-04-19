# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
import uuid

def make_uuid(): return uuid.uuid4().hex

DEBUG_IN_OUT = False

# =================================================== AUTOMATION ===================================================

class zenbeats_automation_point:
	def __init__(self, xml_data):
		self.position = 0.0
		self.value = 0.0
		self.type = 'line'
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		attrib = xml_data.attrib
		if 'position' in attrib: self.position = float(attrib['position'])
		if 'value' in attrib: self.value = float(attrib['value'])
		if 'type' in attrib: self.type = attrib['type']

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "point")
		tempxml.set('position', str(self.position))
		tempxml.set('value', str(self.value))
		tempxml.set('type', str(self.type))

class zenbeats_automation_curve:
	def __init__(self, xml_data):
		self.tag = 'automation_curve'
		self.version = zenbeats_version()
		self.visual = zenbeats_visual_info()
		self.uid = make_uuid()
		self.target_object = None 
		self.target = ""
		self.function = ""
		self.parameter = 0
		self.low_range = 0.0
		self.high_range = 1.0
		self.unlinked_parameter_name = "" 
		self.unlinked_internal_plugin_type = -1
		self.unlinked_plugin_file = "" 
		self.restore_value = None
		self.points = []
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		self.tag = xml_data.tag
		attrib = xml_data.attrib
		self.visual.read(xml_data)
		self.version.read(xml_data)
		if 'uid' in attrib: self.uid = attrib['uid']
		if 'target_object' in attrib: self.target_object = attrib['target_object']
		if 'target' in attrib: self.target = attrib['target']
		if 'function' in attrib: self.function = attrib['function']
		if 'parameter' in attrib: self.parameter = int(attrib['parameter'])
		if 'low_range' in attrib: self.low_range = float(attrib['low_range'])
		if 'high_range' in attrib: self.high_range = float(attrib['high_range'])
		if 'unlinked_parameter_name' in attrib: self.unlinked_parameter_name = attrib['unlinked_parameter_name']
		if 'unlinked_internal_plugin_type' in attrib: self.unlinked_internal_plugin_type = int(attrib['unlinked_internal_plugin_type'])
		if 'unlinked_plugin_file' in attrib: self.unlinked_plugin_file = attrib['unlinked_plugin_file']
		if 'restore_value' in attrib: self.restore_value = float(attrib['restore_value'])
		for x_part in xml_data:
			if x_part.tag == 'point': self.points.append(zenbeats_automation_point(x_part))

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, self.tag)
		self.version.write(tempxml)
		self.visual.write(tempxml)
		tempxml.set('uid', str(self.uid))
		if self.target_object is not None: tempxml.set('target_object', str(self.target_object))
		tempxml.set('target', str(self.target))
		tempxml.set('function', str(self.function))
		tempxml.set('parameter', str(self.parameter))
		tempxml.set('low_range', str(self.low_range))
		tempxml.set('high_range', str(self.high_range))
		tempxml.set('unlinked_parameter_name', str(self.unlinked_parameter_name))
		tempxml.set('unlinked_internal_plugin_type', str(self.unlinked_internal_plugin_type))
		tempxml.set('unlinked_plugin_file', str(self.unlinked_plugin_file))
		if self.restore_value is not None: tempxml.set('restore_value', str(self.restore_value))
		for point in self.points: point.write(tempxml)

class zenbeats_automation_set:
	def __init__(self, xml_data):
		self.version = zenbeats_version()
		self.visual = zenbeats_visual_info()
		self.uid = make_uuid()
		self.selected_child = -1
		self.target_uid = ""
		self.curves = []
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		attrib = xml_data.attrib
		self.visual.read(xml_data)
		self.version.read(xml_data)
		if 'uid' in attrib: self.uid = attrib['uid']
		if 'selected_child' in attrib: self.selected_child = int(attrib['selected_child'])
		if 'target_uid' in attrib: self.target_uid = attrib['target_uid']
		for x_part in xml_data:
			if x_part.tag == 'automation_curve': self.curves.append(zenbeats_automation_curve(x_part))

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "automation_set")
		self.version.write(tempxml)
		self.visual.write(tempxml)
		tempxml.set('uid', str(self.uid))
		tempxml.set('selected_child', str(self.selected_child))
		tempxml.set('target_uid', str(self.target_uid))
		for curve in self.curves: curve.write(tempxml)

# =================================================== BANK RACK ===================================================

class zenbeats_plugin:
	def __init__(self, xml_data):
		self.name = ""
		self.descriptiveName = None
		self.format = ""
		self.category = ""
		self.manufacturer = ""
		self.version = '1.0'
		self.file = ""
		self.uniqueId = 17
		self.isInstrument = 0
		self.isMidiEffect = 0
		self.fileTime = 0
		self.infoUpdateTime = 0
		self.numInputs = 2
		self.numOutputs = 2
		self.isShell = 0
		self.uid = 0
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		attrib = xml_data.attrib
		if 'name' in attrib: self.name = attrib['name']
		if 'descriptiveName' in attrib: self.descriptiveName = attrib['descriptiveName']
		if 'format' in attrib: self.format = attrib['format']
		if 'category' in attrib: self.category = attrib['category']
		if 'manufacturer' in attrib: self.manufacturer = attrib['manufacturer']
		if 'version' in attrib: self.version = attrib['version']
		if 'file' in attrib: self.file = attrib['file']
		if 'uniqueId' in attrib: self.uniqueId = attrib['uniqueId']
		if 'isInstrument' in attrib: self.isInstrument = int(attrib['isInstrument'])
		if 'isMidiEffect' in attrib: self.isMidiEffect = int(attrib['isMidiEffect'])
		if 'fileTime' in attrib: self.fileTime = int(attrib['fileTime'])
		if 'infoUpdateTime' in attrib: self.infoUpdateTime = int(attrib['infoUpdateTime'])
		if 'numInputs' in attrib: self.numInputs = int(attrib['numInputs'])
		if 'numOutputs' in attrib: self.numOutputs = int(attrib['numOutputs'])
		if 'isShell' in attrib: self.isShell = int(attrib['isShell'])
		if 'uid' in attrib: self.uid = int(attrib['uid'])

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "PLUGIN")
		tempxml.set('name', str(self.name))
		if self.descriptiveName is not None: tempxml.set('descriptiveName', str(self.descriptiveName))
		tempxml.set('format', str(self.format))
		tempxml.set('category', str(self.category))
		tempxml.set('manufacturer', str(self.manufacturer))
		tempxml.set('version', str(self.version))
		tempxml.set('file', str(self.file))
		tempxml.set('uniqueId', str(self.uniqueId))
		tempxml.set('isInstrument', str(self.isInstrument))
		tempxml.set('isMidiEffect', str(self.isMidiEffect))
		tempxml.set('fileTime', str(self.fileTime))
		tempxml.set('infoUpdateTime', str(self.infoUpdateTime))
		tempxml.set('numInputs', str(self.numInputs))
		tempxml.set('numOutputs', str(self.numOutputs))
		tempxml.set('isShell', str(self.isShell))
		tempxml.set('uid', str(self.uid))

class zenbeats_cached_parameter:
	def __init__(self, xml_data):
		self.index = 0
		self.name = ''
		self.type = 0.0
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		attrib = xml_data.attrib
		if 'index' in attrib: self.index = int(attrib['index'])
		if 'name' in attrib: self.name = attrib['name']
		if 'value' in attrib: self.value = float(attrib['value'])

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "parameter")
		tempxml.set('index', str(self.index))
		tempxml.set('name', str(self.name))
		tempxml.set('value', str(self.value))

class zenbeats_stream_processor:
	def __init__(self, xml_data):
		self.version = zenbeats_version()
		self.visual = zenbeats_visual_info()
		self.uid = make_uuid()
		self.selected_child = -1
		self.index = 0
		self.block_ccs = 0
		self.bypass = 0
		self.wet_dry_mix = 1.0
		self.pre_gain = 1.0
		self.post_gain = 1.0
		self.mpe_enabled = 0
		self.stream_processor_type = 4
		self.program_index = -1
		self.show_editor_preference = 0
		self.plugin_window_x = -1
		self.plugin_window_y = -1
		self.preset_name = None
		self.cached_parameters = []
		self.plugin = None
		self.plugin_xml_data = None
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		self.visual.read(xml_data)
		self.version.read(xml_data)
		attrib = xml_data.attrib
		if 'uid' in attrib: self.uid = attrib['uid']
		if 'selected_child' in attrib: self.selected_child = int(attrib['selected_child'])
		if 'index' in attrib: self.index = int(attrib['index'])
		if 'block_ccs' in attrib: self.block_ccs = int(attrib['block_ccs'])
		if 'bypass' in attrib: self.bypass = int(attrib['bypass'])
		if 'wet_dry_mix' in attrib: self.wet_dry_mix = float(attrib['wet_dry_mix'])
		if 'pre_gain' in attrib: self.pre_gain = float(attrib['pre_gain'])
		if 'post_gain' in attrib: self.post_gain = float(attrib['post_gain'])
		if 'mpe_enabled' in attrib: self.mpe_enabled = int(attrib['mpe_enabled'])
		if 'stream_processor_type' in attrib: self.stream_processor_type = int(attrib['stream_processor_type'])
		if 'program_index' in attrib: self.program_index = int(attrib['program_index'])
		if 'preset_name' in attrib: self.preset_name = attrib['preset_name']
		if 'show_editor_preference' in attrib: self.show_editor_preference = int(attrib['show_editor_preference'])
		if 'plugin_window_x' in attrib: self.plugin_window_x = int(attrib['plugin_window_x'])
		if 'plugin_window_y' in attrib: self.plugin_window_y = int(attrib['plugin_window_y'])
		for x_part in xml_data:
			if x_part.tag == 'PLUGIN': self.plugin = zenbeats_plugin(x_part)
			if x_part.tag == 'plugin_xml_data': self.plugin_xml_data = x_part
			if x_part.tag == 'cached_parameters': 
				for inpart in x_part:
					if inpart.tag == 'parameter': self.cached_parameters.append(zenbeats_cached_parameter(inpart))

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "stream_processor")
		self.version.write(tempxml)
		self.visual.write(tempxml)
		tempxml.set('uid', str(self.uid))
		tempxml.set('selected_child', str(self.selected_child))
		tempxml.set('index', str(self.index))
		tempxml.set('block_ccs', str(self.block_ccs))
		tempxml.set('bypass', str(self.bypass))
		tempxml.set('wet_dry_mix', str(self.wet_dry_mix))
		tempxml.set('pre_gain', str(self.pre_gain))
		tempxml.set('post_gain', str(self.post_gain))
		tempxml.set('mpe_enabled', str(self.mpe_enabled))
		tempxml.set('stream_processor_type', str(self.stream_processor_type))
		tempxml.set('program_index', str(self.program_index))
		if self.preset_name is not None: tempxml.set('preset_name', str(self.preset_name))
		tempxml.set('show_editor_preference', str(self.show_editor_preference))
		tempxml.set('plugin_window_x', str(self.plugin_window_x))
		tempxml.set('plugin_window_y', str(self.plugin_window_y))
		paramtempxml = ET.SubElement(tempxml, "cached_parameters")
		for env in self.cached_parameters: env.write(paramtempxml)
		if self.plugin is not None: self.plugin.write(tempxml)
		if self.plugin_xml_data is not None: tempxml.append(self.plugin_xml_data)

class zenbeats_signal_chain:
	def __init__(self, xml_data):
		self.version = zenbeats_version()
		self.visual = zenbeats_visual_info()
		self.uid = make_uuid()
		self.selected_child = 0
		self.index = 0
		self.gain = 1.0
		self.pan = 0.0
		self.tranpose = 0
		self.solo = 0
		self.mute = 0
		self.low_key_range = 0
		self.high_key_range = 127
		self.input_midi_channel = 1088044720
		self.target_midi_channel = 0
		self.signal_chain_type = 2
		self.midi_compression_low = 0
		self.midi_compression_high = 127
		self.midi_compression_ratio = 1.0
		self.midi_compression_full_on = 0
		self.stream_processors = []
		self.sub_track_master_instrument = None
		self.sub_track_audio_ch1 = None
		self.sub_track_audio_ch2 = None
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		self.visual.read(xml_data)
		self.version.read(xml_data)
		attrib = xml_data.attrib
		if 'uid' in attrib: self.uid = attrib['uid']
		if 'selected_child' in attrib: self.selected_child = int(attrib['selected_child'])
		if 'index' in attrib: self.index = int(attrib['index'])
		if 'gain' in attrib: self.gain = float(attrib['gain'])
		if 'pan' in attrib: self.pan = float(attrib['pan'])
		if 'tranpose' in attrib: self.tranpose = int(attrib['tranpose'])
		if 'solo' in attrib: self.solo = int(attrib['solo'])
		if 'mute' in attrib: self.mute = int(attrib['mute'])
		if 'low_key_range' in attrib: self.low_key_range = int(attrib['low_key_range'])
		if 'high_key_range' in attrib: self.high_key_range = int(attrib['high_key_range'])
		if 'input_midi_channel' in attrib: self.input_midi_channel = int(attrib['input_midi_channel'])
		if 'target_midi_channel' in attrib: self.target_midi_channel = int(attrib['target_midi_channel'])
		if 'signal_chain_type' in attrib: self.signal_chain_type = int(attrib['signal_chain_type'])
		if 'midi_compression_low' in attrib: self.midi_compression_low = int(attrib['midi_compression_low'])
		if 'midi_compression_high' in attrib: self.midi_compression_high = int(attrib['midi_compression_high'])
		if 'midi_compression_ratio' in attrib: self.midi_compression_ratio = float(attrib['midi_compression_ratio'])
		if 'midi_compression_full_on' in attrib: self.midi_compression_full_on = int(attrib['midi_compression_full_on'])
		if 'sub_track_master_instrument' in attrib: self.sub_track_master_instrument = attrib['sub_track_master_instrument']
		if 'sub_track_audio_ch1' in attrib: self.sub_track_audio_ch1 = int(attrib['sub_track_audio_ch1'])
		if 'sub_track_audio_ch2' in attrib: self.sub_track_audio_ch2 = int(attrib['sub_track_audio_ch2'])

		for x_part in xml_data:
			if x_part.tag == 'stream_processor': self.stream_processors.append(zenbeats_stream_processor(x_part))

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "signal_chain")
		self.version.write(tempxml)
		self.visual.write(tempxml)
		tempxml.set('uid', str(self.uid))
		tempxml.set('selected_child', str(self.selected_child))
		tempxml.set('index', str(self.index))
		tempxml.set('gain', str(self.gain))
		tempxml.set('pan', str(self.pan))
		tempxml.set('tranpose', str(self.tranpose))
		tempxml.set('solo', str(self.solo))
		tempxml.set('mute', str(self.mute))
		tempxml.set('low_key_range', str(self.low_key_range))
		tempxml.set('high_key_range', str(self.high_key_range))
		tempxml.set('input_midi_channel', str(self.input_midi_channel))
		tempxml.set('target_midi_channel', str(self.target_midi_channel))
		tempxml.set('signal_chain_type', str(self.signal_chain_type))
		tempxml.set('midi_compression_low', str(self.midi_compression_low))
		tempxml.set('midi_compression_high', str(self.midi_compression_high))
		tempxml.set('midi_compression_ratio', str(self.midi_compression_ratio))
		tempxml.set('midi_compression_full_on', str(self.midi_compression_full_on))
		if self.sub_track_master_instrument is not None: tempxml.set('sub_track_master_instrument', str(self.sub_track_master_instrument))
		if self.sub_track_audio_ch1 is not None: tempxml.set('sub_track_audio_ch1', str(self.sub_track_audio_ch1))
		if self.sub_track_audio_ch2 is not None: tempxml.set('sub_track_audio_ch2', str(self.sub_track_audio_ch2))
		for stream_processor in self.stream_processors: stream_processor.write(tempxml)

class zenbeats_send_track:
	def __init__(self, xml_data):
		self.send_track_uid = ''
		self.send_amount = ''
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		attrib = xml_data.attrib
		if 'send_track_uid' in attrib: self.send_track_uid = attrib['send_track_uid']
		if 'send_amount' in attrib: self.send_amount = attrib['send_amount']

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "send_track")
		tempxml.set('send_track_uid', str(self.send_track_uid))
		tempxml.set('send_amount', str(self.send_amount))

class zenbeats_rack:
	def __init__(self, xml_data):
		self.version = zenbeats_version()
		self.visual = zenbeats_visual_info()
		self.uid = make_uuid()
		self.selected_child = -1
		self.gain = 0.5011872336272722
		self.force_mono = 0
		self.filter_low_cut = 0.0
		self.filter_high_cut = 1.0
		self.transpose = 0
		self.solo = 0
		self.mute_by_solo = 0
		self.mute = 0
		self.audio_output_left = 0
		self.audio_output_right = 1
		self.audio_output_aux1_left = -1
		self.audio_output_aux1_right = -1
		self.rack_type = 2
		self.phase_invert_audio_output = 0
		self.post_send = 1
		self.automation_set = zenbeats_automation_set(None)
		self.signal_chain = zenbeats_signal_chain(None)
		self.audio_output_channel_left = None
		self.audio_output_channel_right = None
		self.send_tracks = []
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		self.visual.read(xml_data)
		self.version.read(xml_data)
		attrib = xml_data.attrib
		if 'uid' in attrib: self.uid = attrib['uid']
		if 'selected_child' in attrib: self.selected_child = int(attrib['selected_child'])
		if 'gain' in attrib: self.gain = float(attrib['gain'])
		if 'force_mono' in attrib: self.force_mono = int(attrib['force_mono'])
		if 'filter_low_cut' in attrib: self.filter_low_cut = float(attrib['filter_low_cut'])
		if 'filter_high_cut' in attrib: self.filter_high_cut = float(attrib['filter_high_cut'])
		if 'transpose' in attrib: self.transpose = int(attrib['transpose'])
		if 'solo' in attrib: self.solo = int(attrib['solo'])
		if 'mute_by_solo' in attrib: self.mute_by_solo = int(attrib['mute_by_solo'])
		if 'mute' in attrib: self.mute = int(attrib['mute'])
		if 'audio_output_left' in attrib: self.audio_output_left = int(attrib['audio_output_left'])
		if 'audio_output_right' in attrib: self.audio_output_right = int(attrib['audio_output_right'])
		if 'audio_output_aux1_left' in attrib: self.audio_output_aux1_left = int(attrib['audio_output_aux1_left'])
		if 'audio_output_aux1_right' in attrib: self.audio_output_aux1_right = int(attrib['audio_output_aux1_right'])
		if 'rack_type' in attrib: self.rack_type = int(attrib['rack_type'])
		if 'phase_invert_audio_output' in attrib: self.phase_invert_audio_output = int(attrib['phase_invert_audio_output'])
		if 'post_send' in attrib: self.post_send = int(attrib['post_send'])
		if 'audio_output_channel_left' in attrib: self.audio_output_channel_left = int(attrib['audio_output_channel_left'])
		if 'audio_output_channel_right' in attrib: self.audio_output_channel_right = int(attrib['audio_output_channel_right'])
		for x_part in xml_data:
			if x_part.tag == 'automation_set': self.automation_set.read(x_part)
			if x_part.tag == 'signal_chain': self.signal_chain.read(x_part)
			if x_part.tag == 'send_track': self.send_tracks.append(zenbeats_send_track(x_part))

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "rack")
		self.version.write(tempxml)
		self.visual.write(tempxml)
		tempxml.set('uid', str(self.uid))
		tempxml.set('selected_child', str(self.selected_child))
		tempxml.set('gain', str(self.gain))
		tempxml.set('force_mono', str(self.force_mono))
		tempxml.set('filter_low_cut', str(self.filter_low_cut))
		tempxml.set('filter_high_cut', str(self.filter_high_cut))
		tempxml.set('transpose', str(self.transpose))
		tempxml.set('solo', str(self.solo))
		tempxml.set('mute_by_solo', str(self.mute_by_solo))
		tempxml.set('mute', str(self.mute))
		if self.audio_output_channel_left is not None: tempxml.set('audio_output_channel_left', str(self.audio_output_channel_left))
		if self.audio_output_channel_right is not None: tempxml.set('audio_output_channel_right', str(self.audio_output_channel_right))
		tempxml.set('audio_output_left', str(self.audio_output_left))
		tempxml.set('audio_output_right', str(self.audio_output_right))
		tempxml.set('audio_output_aux1_left', str(self.audio_output_aux1_left))
		tempxml.set('audio_output_aux1_right', str(self.audio_output_aux1_right))
		tempxml.set('rack_type', str(self.rack_type))
		tempxml.set('phase_invert_audio_output', str(self.phase_invert_audio_output))
		tempxml.set('post_send', str(self.post_send))
		for send_track in self.send_tracks: send_write(tempxml)
		self.signal_chain.write(tempxml)
		self.automation_set.write(tempxml)

class zenbeats_bank:
	def __init__(self, xml_data):
		self.version = 6
		self.selected_child = 0
		self.uid = ''
		self.racks = []
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		attrib = xml_data.attrib
		if 'version' in attrib: self.version = int(attrib['version'])
		if 'selected_child' in attrib: self.selected_child = int(attrib['selected_child'])
		if 'uid' in attrib: self.uid = attrib['uid']
		for x_part in xml_data:
			if x_part.tag == 'rack': self.racks.append(zenbeats_rack(x_part))

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "bank")
		tempxml.set('version', str(self.version))
		tempxml.set('selected_child', str(self.selected_child))
		tempxml.set('uid', str(self.uid))
		for rack in self.racks: rack.write(tempxml)

# =================================================== MISC ===================================================

class zenbeats_version:
	def __init__(self):
		self.version = 6
		self.build_number = 9399

	def read(self, xml_proj):
		attrib = xml_proj.attrib
		if 'version' in attrib: self.version = int(attrib['version'])
		if 'build_number' in attrib: self.build_number = int(attrib['build_number'])

	def write(self, tempxml):
		tempxml.set('version', str(self.version))
		tempxml.set('build_number', str(self.build_number))

class zenbeats_visual_info:
	def __init__(self):
		self.name = ""
		self.name_set_by_user = 0
		self.description = ""
		self.color = "ffffffff"

	def read(self, xml_proj):
		attrib = xml_proj.attrib
		if 'name' in attrib: self.name = attrib['name']
		if 'name_set_by_user' in attrib: self.name_set_by_user = int(attrib['name_set_by_user'])
		if 'description' in attrib: self.description = attrib['description']
		if 'color' in attrib: self.color = attrib['color']

	def write(self, tempxml):
		tempxml.set('name', str(self.name))
		tempxml.set('name_set_by_user', str(self.name_set_by_user))
		tempxml.set('description', str(self.description))
		tempxml.set('color', str(self.color))

class zenbeats_scale_lock:
	def __init__(self, xml_proj):
		self.active = 0
		self.key = 0
		self.mode = 0
		if xml_proj is not None: self.read(xml_proj)

	def read(self, xml_proj):
		attrib = xml_proj.attrib
		if 'active' in attrib: self.active = int(attrib['active'])
		if 'key' in attrib: self.key = int(attrib['key'])
		if 'mode' in attrib: self.mode = int(attrib['mode'])

	def write(self, xml_proj):
		tempxml = ET.SubElement(xml_proj, "scale_lock")
		tempxml.set('active', str(self.active))
		tempxml.set('key', str(self.key))
		tempxml.set('mode', str(self.mode))

# =================================================== PATTERN ===================================================

class zenbeats_envelope:
	def __init__(self, xml_data):
		self.name = ''
		self.x = 0
		self.y = 0
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		attrib = xml_data.attrib
		if 'name' in attrib: self.name = attrib['name']
		if 'x' in attrib: self.x = float(attrib['x'])
		if 'y' in attrib: self.y = float(attrib['y'])

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "point")
		tempxml.set('name', str(self.name))
		tempxml.set('x', str(self.x))
		tempxml.set('y', str(self.y))

class zenbeats_key_change:
	def __init__(self, xml_data):
		self.key = 0
		self.mode = 0
		self.beat = 0
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		attrib = xml_data.attrib
		if 'key' in attrib: self.key = int(attrib['key'])
		if 'mode' in attrib: self.mode = int(attrib['mode'])
		if 'beat' in attrib: self.beat = float(attrib['beat'])

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "key_change")
		tempxml.set('key', str(self.key))
		tempxml.set('mode', str(self.mode))
		tempxml.set('beat', str(self.beat))

class zenbeats_note:
	def __init__(self, xml_data):
		self.version = zenbeats_version()
		self.visual = zenbeats_visual_info()
		self.uid = make_uuid()
		self.start = 0
		self.end = 1
		self.velocity = 100
		self.semitone = 60
		self.active = 1
		self.probability = 1.0
		self.velocity_jitter = None
		self.pan_jitter = None
		self.filter_high_cut = None
		self.reverse = 0
		self.pan_linear = 0.5
		self.pitch_offset = 0
		self.mpe = {}
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		attrib = xml_data.attrib
		self.visual.read(xml_data)
		self.version.read(xml_data)
		if 'uid' in attrib: self.uid = attrib['uid']
		if 'start' in attrib: self.start = float(attrib['start'])
		if 'end' in attrib: self.end = float(attrib['end'])
		if 'velocity' in attrib: self.velocity = int(attrib['velocity'])
		if 'semitone' in attrib: self.semitone = int(attrib['semitone'])
		if 'active' in attrib: self.active = int(attrib['active'])
		if 'probability' in attrib: self.probability = float(attrib['probability'])
		if 'velocity_jitter' in attrib: self.velocity_jitter = float(attrib['velocity_jitter'])
		if 'pan_jitter' in attrib: self.pan_jitter = float(attrib['pan_jitter'])
		if 'filter_high_cut' in attrib: self.filter_high_cut = float(attrib['filter_high_cut'])
		if 'reverse' in attrib: self.reverse = float(attrib['reverse'])
		if 'pan_linear' in attrib: self.pan_linear = float(attrib['pan_linear'])
		if 'pitch_offset' in attrib: self.pitch_offset = float(attrib['pitch_offset'])*100
		for x_part in xml_data:
			if x_part.tag in 'MPE_Pressure':
				self.mpe['pressure'] = zenbeats_automation_curve(x_part)
			if x_part.tag in 'MPE_Pitch':
				self.mpe['pitch'] = zenbeats_automation_curve(x_part)
			if x_part.tag in 'MPE_Timbre':
				self.mpe['timbre'] = zenbeats_automation_curve(x_part)

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "note")
		self.version.write(tempxml)
		self.visual.write(tempxml)
		tempxml.set('uid', str(self.uid))
		tempxml.set('start', str(self.start))
		tempxml.set('end', str(self.end))
		tempxml.set('velocity', str(self.velocity))
		tempxml.set('semitone', str(self.semitone))
		tempxml.set('active', str(self.active))
		if self.velocity_jitter is not None: tempxml.set('velocity_jitter', str(self.velocity_jitter))
		tempxml.set('probability', str(self.probability))
		if self.filter_high_cut is not None: tempxml.set('filter_high_cut', str(self.filter_high_cut))
		if 'pressure' in self.mpe:
			self.mpe['pressure'].tag = 'MPE_Pressure'
			self.mpe['pressure'].write(tempxml)
		if 'pitch' in self.mpe:
			self.mpe['pitch'].tag = 'MPE_Pitch'
			self.mpe['pitch'].write(tempxml)
		if 'timbre' in self.mpe:
			self.mpe['timbre'].tag = 'MPE_Timbre'
			self.mpe['timbre'].write(tempxml)

class zenbeats_pattern:
	def __init__(self, xml_data):
		self.type = 'pattern'
		self.version = zenbeats_version()
		self.visual = zenbeats_visual_info()
		self.uid = make_uuid()
		self.color_index = 2
		self.low_note = 0
		self.high_note = 127
		self.time_signature_numerator = 4
		self.time_signature_denominator = 4
		self.default_note_size = -1.0
		self.start_beat = 0
		self.end_beat = 4
		self.loop = 1
		self.start_playing_on_transport = 0
		self.loop_start_beat = 0
		self.loop_end_beat = 4
		self.loop_play_start = 0
		self.active = 1
		self.play_mutual_exclusive = 1
		self.pattern_type = 1
		self.play_back_ratio = 1.0
		self.original_file_bpm = 0.0
		self.viewport_start = 0
		self.viewport_end = 4
		self.viewport_lower_bound = 0.0
		self.viewport_upper_bound = 6.99999
		self.grid_size = 0.25
		self.snap_to_grid = 1
		self.show_step_sequencer = 0
		self.loop_xfade_length = 0.0
		self.use_adaptive_grid = 0
		self.use_triplets = 0
		self.locked = 0
		self.scale_lock = zenbeats_scale_lock(None)
		self.pattern_envelope = []
		self.timeline_envelope = []
		self.key_change_list = []
		self.notes = []
		self.automation_set = zenbeats_automation_set(None)

		self.default_file_bpm = None
		self.audio_file = None
		self.audio_file_original_bpm = None
		self.timestretching = None
		self.preserve_pitch = None
		self.audio_pitch = None
		self.fine_audio_pitch_offset = None
		self.audio_gain = None
		self.audio_pan = None
		self.reverse_audio = None
		self.icon_name = None
		self.key_string = None
		self.scene_index = -1
		self.accent = None
		self.last_note_automation_function = None

		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		self.type = xml_data.tag
		self.visual.read(xml_data)
		self.version.read(xml_data)
		attrib = xml_data.attrib
		if 'uid' in attrib: self.uid = attrib['uid']
		if 'color_index' in attrib: self.color_index = int(attrib['color_index'])
		if 'low_note' in attrib: self.low_note = int(attrib['low_note'])
		if 'high_note' in attrib: self.high_note = int(attrib['high_note'])
		if 'time_signature_numerator' in attrib: self.time_signature_numerator = int(attrib['time_signature_numerator'])
		if 'time_signature_denominator' in attrib: self.time_signature_denominator = int(attrib['time_signature_denominator'])
		if 'default_note_size' in attrib: self.default_note_size = float(attrib['default_note_size'])
		if 'start_beat' in attrib: self.start_beat = float(attrib['start_beat'])
		if 'end_beat' in attrib: self.end_beat = float(attrib['end_beat'])
		if 'loop' in attrib: self.loop = int(attrib['loop'])
		if 'start_playing_on_transport' in attrib: self.start_playing_on_transport = int(attrib['start_playing_on_transport'])
		if 'loop_start_beat' in attrib: self.loop_start_beat = float(attrib['loop_start_beat'])
		if 'loop_end_beat' in attrib: self.loop_end_beat = float(attrib['loop_end_beat'])
		if 'loop_play_start' in attrib: self.loop_play_start = float(attrib['loop_play_start'])
		if 'active' in attrib: self.active = int(attrib['active'])
		if 'play_mutual_exclusive' in attrib: self.play_mutual_exclusive = int(attrib['play_mutual_exclusive'])
		if 'pattern_type' in attrib: self.pattern_type = int(attrib['pattern_type'])
		if 'play_back_ratio' in attrib: self.play_back_ratio = float(attrib['play_back_ratio'])
		if 'original_file_bpm' in attrib: self.original_file_bpm = float(attrib['original_file_bpm'])
		if 'viewport_start' in attrib: self.viewport_start = float(attrib['viewport_start'])
		if 'viewport_end' in attrib: self.viewport_end = float(attrib['viewport_end'])
		if 'viewport_lower_bound' in attrib: self.viewport_lower_bound = float(attrib['viewport_lower_bound'])
		if 'viewport_upper_bound' in attrib: self.viewport_upper_bound = float(attrib['viewport_upper_bound'])
		if 'grid_size' in attrib: self.grid_size = float(attrib['grid_size'])
		if 'snap_to_grid' in attrib: self.snap_to_grid = int(attrib['snap_to_grid'])
		if 'show_step_sequencer' in attrib: self.show_step_sequencer = int(attrib['show_step_sequencer'])
		if 'last_note_automation_function' in attrib: self.last_note_automation_function = attrib['last_note_automation_function']
		if 'loop_xfade_length' in attrib: self.loop_xfade_length = float(attrib['loop_xfade_length'])
		if 'use_adaptive_grid' in attrib: self.use_adaptive_grid = int(attrib['use_adaptive_grid'])
		if 'use_triplets' in attrib: self.use_triplets = int(attrib['use_triplets'])
		if 'locked' in attrib: self.locked = int(attrib['locked'])
		if 'accent' in attrib: self.accent = attrib['accent']
		if 'scene_index' in attrib: self.scene_index = int(attrib['scene_index'])
		if 'last_note_automation_function' in attrib: self.last_note_automation_function = attrib['last_note_automation_function']

		if 'default_file_bpm' in attrib: self.default_file_bpm = float(attrib['default_file_bpm'])
		if 'audio_file' in attrib: self.audio_file = attrib['audio_file']
		if 'audio_file_original_bpm' in attrib: self.audio_file_original_bpm = float(attrib['audio_file_original_bpm'])
		if 'timestretching' in attrib: self.timestretching = int(attrib['timestretching'])
		if 'preserve_pitch' in attrib: self.preserve_pitch = int(attrib['preserve_pitch'])
		if 'audio_pitch' in attrib: self.audio_pitch = float(attrib['audio_pitch'])
		if 'fine_audio_pitch_offset' in attrib: self.fine_audio_pitch_offset = float(attrib['fine_audio_pitch_offset'])
		if 'audio_gain' in attrib: self.audio_gain = float(attrib['audio_gain'])
		if 'audio_pan' in attrib: self.audio_pan = float(attrib['audio_pan'])
		if 'reverse_audio' in attrib: self.reverse_audio = int(attrib['reverse_audio'])
		if 'icon_name' in attrib: self.icon_name = attrib['icon_name']
		if 'key_string' in attrib: self.key_string = attrib['key_string']
		if 'accent' in attrib: self.accent = attrib['accent']

		for x_part in xml_data:
			if x_part.tag == 'note': self.notes.append(zenbeats_note(x_part))
			if x_part.tag == 'scale_lock': self.scale_lock.read(x_part)
			if x_part.tag == 'pattern_envelope': 
				for inpart in x_part:
					if inpart.tag == 'point': self.pattern_envelope.append(zenbeats_envelope(inpart))
			if x_part.tag == 'timeline_envelope': 
				for inpart in x_part:
					if inpart.tag == 'point': self.timeline_envelope.append(zenbeats_envelope(inpart))
			if x_part.tag == 'key_change_list': 
				for inpart in x_part:
					if inpart.tag == 'key_change': self.key_change_list.append(zenbeats_key_change(inpart))
			if x_part.tag == 'automation_set': self.automation_set.read(x_part)

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, self.type)
		self.version.write(tempxml)
		self.visual.write(tempxml)
		tempxml.set('uid', str(self.uid))
		tempxml.set('color_index', str(self.color_index))
		tempxml.set('low_note', str(self.low_note))
		tempxml.set('high_note', str(self.high_note))
		tempxml.set('time_signature_numerator', str(self.time_signature_numerator))
		tempxml.set('time_signature_denominator', str(self.time_signature_denominator))
		tempxml.set('default_note_size', str(self.default_note_size))
		tempxml.set('start_beat', str(self.start_beat))
		tempxml.set('end_beat', str(self.end_beat))
		tempxml.set('loop', str(self.loop))
		tempxml.set('start_playing_on_transport', str(self.start_playing_on_transport))
		tempxml.set('loop_start_beat', str(self.loop_start_beat))
		tempxml.set('loop_end_beat', str(self.loop_end_beat))
		tempxml.set('loop_play_start', str(self.loop_play_start))
		tempxml.set('active', str(self.active))
		tempxml.set('play_mutual_exclusive', str(self.play_mutual_exclusive))
		tempxml.set('pattern_type', str(self.pattern_type))
		tempxml.set('play_back_ratio', str(self.play_back_ratio))
		tempxml.set('original_file_bpm', str(self.original_file_bpm))
		tempxml.set('viewport_start', str(self.viewport_start))
		tempxml.set('viewport_end', str(self.viewport_end))
		tempxml.set('viewport_lower_bound', str(self.viewport_lower_bound))
		tempxml.set('viewport_upper_bound', str(self.viewport_upper_bound))
		tempxml.set('grid_size', str(self.grid_size))
		tempxml.set('snap_to_grid', str(self.snap_to_grid))
		tempxml.set('show_step_sequencer', str(self.show_step_sequencer))
		if self.last_note_automation_function != None: tempxml.set('last_note_automation_function', str(self.last_note_automation_function))
		tempxml.set('loop_xfade_length', str(self.loop_xfade_length))
		tempxml.set('use_adaptive_grid', str(self.use_adaptive_grid))
		tempxml.set('use_triplets', str(self.use_triplets))
		tempxml.set('locked', str(self.locked))
		if self.accent != None: tempxml.set('accent', str(self.accent))
		if self.scene_index != -1: tempxml.set('scene_index', str(self.scene_index))
		self.scale_lock.write(tempxml)

		if self.default_file_bpm != None: tempxml.set('default_file_bpm', str(self.default_file_bpm))
		if self.audio_file != None: tempxml.set('audio_file', str(self.audio_file))
		if self.audio_file_original_bpm != None: tempxml.set('audio_file_original_bpm', str(self.audio_file_original_bpm))
		if self.timestretching != None: tempxml.set('timestretching', str(self.timestretching))
		if self.preserve_pitch != None: tempxml.set('preserve_pitch', str(self.preserve_pitch))
		if self.audio_pitch != None: tempxml.set('audio_pitch', str(self.audio_pitch))
		if self.fine_audio_pitch_offset != None: tempxml.set('fine_audio_pitch_offset', str(self.fine_audio_pitch_offset))
		if self.audio_gain != None: tempxml.set('audio_gain', str(self.audio_gain))
		if self.audio_pan != None: tempxml.set('audio_pan', str(self.audio_pan))
		if self.reverse_audio != None: tempxml.set('reverse_audio', str(self.reverse_audio))
		if self.icon_name != None: tempxml.set('icon_name', str(self.icon_name))
		if self.key_string != None: tempxml.set('key_string', str(self.key_string))
		if self.accent != None: tempxml.set('accent', str(self.accent))
		
		envtempxml = ET.SubElement(tempxml, "pattern_envelope")
		for env in self.pattern_envelope: env.write(envtempxml)
		envtempxml = ET.SubElement(tempxml, "timeline_envelope")
		for env in self.timeline_envelope: env.write(envtempxml)
		kcxml = ET.SubElement(tempxml, "key_change_list")
		for env in self.key_change_list: env.write(kcxml)
		for note in self.notes: note.write(tempxml)
		self.automation_set.write(tempxml)
	
# =================================================== TRACK ===================================================

class zenbeats_track:
	def __init__(self, xml_data):
		self.version = zenbeats_version()
		self.visual = zenbeats_visual_info()
		self.uid = make_uuid()
		self.selected_child = -1
		self.type = 1
		self.color_index = 3
		self.sub_track_master_track_uid = None
		self.show_sub_tracks = 0
		self.track_icon_index = -1
		self.arm_record = 0
		self.mute = 0
		self.solo = 0
		self.mute_by_solo = 0
		self.monitor = 0
		self.monitor_by_arm = 0
		self.transpose = 0
		self.input_channel_flags = 0
		self.output_channel = 0
		self.input_device_slot = -1
		self.output_device_slot = -2
		self.output_rack_uid = ""
		self.audio_input_channel_left = 0
		self.audio_input_channel_right = 1
		self.onscreen_midi_input_type = 200
		self.onscreen_midi_start_semitone = 36.0
		self.onscreen_keys_pitch_bend_on_drag = 0
		self.onscreen_midi_end_semitone = 67.0
		self.onscreen_note_pad_count = 24
		self.onscreen_drum_pad_count = 16
		self.onscreen_note_pad_columns = 12
		self.onscreen_drum_pad_columns = 8
		self.onscreen_midi_scale_lock = 1
		self.onscreen_midi_grid_invert = 0
		self.pattern_pre_midi_effects = 1
		self.track_tuner_active = 1
		self.visualizer_array_file = ""
		self.is_sub_track_master = -1
		self.patterns = []
		self.clip_patterns = []
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		self.visual.read(xml_data)
		self.version.read(xml_data)
		attrib = xml_data.attrib
		if 'name' in attrib: self.name = attrib['name']
		if 'name_set_by_user' in attrib: self.name_set_by_user = int(attrib['name_set_by_user'])
		if 'description' in attrib: self.description = attrib['description']
		if 'color' in attrib: self.color = attrib['color']
		if 'uid' in attrib: self.uid = attrib['uid']
		if 'selected_child' in attrib: self.selected_child = int(attrib['selected_child'])
		if 'type' in attrib: self.type = int(attrib['type'])
		if 'color_index' in attrib: self.color_index = int(attrib['color_index'])
		if 'show_sub_tracks' in attrib: self.show_sub_tracks = int(attrib['show_sub_tracks'])
		if 'track_icon_index' in attrib: self.track_icon_index = int(attrib['track_icon_index'])
		if 'arm_record' in attrib: self.arm_record = int(attrib['arm_record'])
		if 'mute' in attrib: self.mute = int(attrib['mute'])
		if 'solo' in attrib: self.solo = int(attrib['solo'])
		if 'mute_by_solo' in attrib: self.mute_by_solo = int(attrib['mute_by_solo'])
		if 'monitor' in attrib: self.monitor = int(attrib['monitor'])
		if 'monitor_by_arm' in attrib: self.monitor_by_arm = int(attrib['monitor_by_arm'])
		if 'transpose' in attrib: self.transpose = int(attrib['transpose'])
		if 'input_channel_flags' in attrib: self.input_channel_flags = int(attrib['input_channel_flags'])
		if 'output_channel' in attrib: self.output_channel = int(attrib['output_channel'])
		if 'input_device_slot' in attrib: self.input_device_slot = int(attrib['input_device_slot'])
		if 'output_device_slot' in attrib: self.output_device_slot = int(attrib['output_device_slot'])
		if 'output_rack_uid' in attrib: self.output_rack_uid = attrib['output_rack_uid']
		if 'audio_input_channel_left' in attrib: self.audio_input_channel_left = int(attrib['audio_input_channel_left'])
		if 'audio_input_channel_right' in attrib: self.audio_input_channel_right = int(attrib['audio_input_channel_right'])
		if 'onscreen_midi_input_type' in attrib: self.onscreen_midi_input_type = int(attrib['onscreen_midi_input_type'])
		if 'onscreen_midi_start_semitone' in attrib: self.onscreen_midi_start_semitone = float(attrib['onscreen_midi_start_semitone'])
		if 'onscreen_keys_pitch_bend_on_drag' in attrib: self.onscreen_keys_pitch_bend_on_drag = int(attrib['onscreen_keys_pitch_bend_on_drag'])
		if 'onscreen_midi_end_semitone' in attrib: self.onscreen_midi_end_semitone = float(attrib['onscreen_midi_end_semitone'])
		if 'onscreen_note_pad_count' in attrib: self.onscreen_note_pad_count = int(attrib['onscreen_note_pad_count'])
		if 'onscreen_drum_pad_count' in attrib: self.onscreen_drum_pad_count = int(attrib['onscreen_drum_pad_count'])
		if 'onscreen_note_pad_columns' in attrib: self.onscreen_note_pad_columns = int(attrib['onscreen_note_pad_columns'])
		if 'onscreen_drum_pad_columns' in attrib: self.onscreen_drum_pad_columns = int(attrib['onscreen_drum_pad_columns'])
		if 'onscreen_midi_scale_lock' in attrib: self.onscreen_midi_scale_lock = int(attrib['onscreen_midi_scale_lock'])
		if 'onscreen_midi_grid_invert' in attrib: self.onscreen_midi_grid_invert = int(attrib['onscreen_midi_grid_invert'])
		if 'pattern_pre_midi_effects' in attrib: self.pattern_pre_midi_effects = int(attrib['pattern_pre_midi_effects'])
		if 'track_tuner_active' in attrib: self.track_tuner_active = int(attrib['track_tuner_active'])
		if 'visualizer_array_file' in attrib: self.visualizer_array_file = attrib['visualizer_array_file']
		if 'is_sub_track_master' in attrib: self.is_sub_track_master = int(attrib['is_sub_track_master'])
		if 'sub_track_master_track_uid' in attrib: self.sub_track_master_track_uid = attrib['sub_track_master_track_uid']
		for x_part in xml_data:
			if x_part.tag == 'pattern': self.patterns.append(zenbeats_pattern(x_part))
		for x_part in xml_data:
			if x_part.tag == 'clip_pattern': self.clip_patterns.append(zenbeats_pattern(x_part))

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "track")
		self.version.write(tempxml)
		self.visual.write(tempxml)
		tempxml.set('uid', str(self.uid))
		tempxml.set('selected_child', str(self.selected_child))
		tempxml.set('type', str(self.type))
		tempxml.set('color_index', str(self.color_index))
		if self.is_sub_track_master != -1: tempxml.set('is_sub_track_master', str(self.is_sub_track_master))
		if self.sub_track_master_track_uid is not None: tempxml.set('sub_track_master_track_uid', str(self.sub_track_master_track_uid))
		tempxml.set('show_sub_tracks', str(self.show_sub_tracks))
		tempxml.set('track_icon_index', str(self.track_icon_index))
		tempxml.set('arm_record', str(self.arm_record))
		tempxml.set('mute', str(self.mute))
		tempxml.set('solo', str(self.solo))
		tempxml.set('mute_by_solo', str(self.mute_by_solo))
		tempxml.set('monitor', str(self.monitor))
		tempxml.set('monitor_by_arm', str(self.monitor_by_arm))
		tempxml.set('transpose', str(self.transpose))
		tempxml.set('input_channel_flags', str(self.input_channel_flags))
		tempxml.set('output_channel', str(self.output_channel))
		tempxml.set('input_device_slot', str(self.input_device_slot))
		tempxml.set('output_device_slot', str(self.output_device_slot))
		tempxml.set('output_rack_uid', str(self.output_rack_uid))
		tempxml.set('audio_input_channel_left', str(self.audio_input_channel_left))
		tempxml.set('audio_input_channel_right', str(self.audio_input_channel_right))
		tempxml.set('onscreen_midi_input_type', str(self.onscreen_midi_input_type))
		tempxml.set('onscreen_midi_start_semitone', str(self.onscreen_midi_start_semitone))
		tempxml.set('onscreen_keys_pitch_bend_on_drag', str(self.onscreen_keys_pitch_bend_on_drag))
		tempxml.set('onscreen_midi_end_semitone', str(self.onscreen_midi_end_semitone))
		tempxml.set('onscreen_note_pad_count', str(self.onscreen_note_pad_count))
		tempxml.set('onscreen_drum_pad_count', str(self.onscreen_drum_pad_count))
		tempxml.set('onscreen_note_pad_columns', str(self.onscreen_note_pad_columns))
		tempxml.set('onscreen_drum_pad_columns', str(self.onscreen_drum_pad_columns))
		tempxml.set('onscreen_midi_scale_lock', str(self.onscreen_midi_scale_lock))
		tempxml.set('onscreen_midi_grid_invert', str(self.onscreen_midi_grid_invert))
		tempxml.set('pattern_pre_midi_effects', str(self.pattern_pre_midi_effects))
		tempxml.set('track_tuner_active', str(self.track_tuner_active))
		tempxml.set('visualizer_array_file', str(self.visualizer_array_file))
		for pattern in self.patterns: write(tempxml)
		for clip_pattern in self.clip_patterns: clip_write(tempxml)

# =================================================== CLIP SCENE ===================================================

class zenbeats_clip_scene:
	def __init__(self, xml_data):
		self.version = zenbeats_version()
		self.visual = zenbeats_visual_info()
		self.uid = make_uuid()
		self.selected_child = -1
		self.follow_active = 0
		self.follow_loop_count = 1
		self.color_index = 0
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		self.visual.read(xml_data)
		self.version.read(xml_data)
		attrib = xml_data.attrib
		if 'uid' in attrib: self.uid = attrib['uid']
		if 'selected_child' in attrib: self.selected_child = int(attrib['selected_child'])
		if 'follow_active' in attrib: self.follow_active = int(attrib['follow_active'])
		if 'follow_loop_count' in attrib: self.follow_loop_count = int(attrib['follow_loop_count'])
		if 'color_index' in attrib: self.color_index = int(attrib['color_index'])

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "clip_scene")
		self.version.write(tempxml)
		self.visual.write(tempxml)
		tempxml.set('uid', str(self.uid))
		tempxml.set('selected_child', str(self.selected_child))
		tempxml.set('follow_active', str(self.follow_active))
		tempxml.set('follow_loop_count', str(self.follow_loop_count))
		tempxml.set('color_index', str(self.color_index))

class zenbeats_clip_scene_list:
	def __init__(self, xml_data):
		self.version = zenbeats_version()
		self.visual = zenbeats_visual_info()
		self.uid = make_uuid()
		self.selected_child = 0
		self.clip_scenes = []
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		self.visual.read(xml_data)
		self.version.read(xml_data)
		attrib = xml_data.attrib
		if 'uid' in attrib: self.uid = attrib['uid']
		if 'selected_child' in attrib: self.selected_child = int(attrib['selected_child'])
		for x_part in xml_data:
			if x_part.tag == 'clip_scene': self.clip_scenes.append(zenbeats_clip_scene(x_part))

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "clip_scene_list")
		self.version.write(tempxml)
		self.visual.write(tempxml)
		tempxml.set('uid', str(self.uid))
		tempxml.set('selected_child', str(self.selected_child))
		for clip_scene in self.clip_scenes: clip_scene.write(tempxml)

# =================================================== MAIN ===================================================

class zenbeats_song:
	def __init__(self):
		self.version = zenbeats_version()
		self.visual = zenbeats_visual_info()
		self.uid = make_uuid()
		self.selected_child = 0
		self.read_only = 0
		self.grid_size = 0.0
		self.track_view_state = "TIMELINE_VIEW"
		self.show_mixer_view = 0
		self.show_track_inspector = 1
		self.show_pattern_inspector = 0
		self.show_onscreen_midi_input = 0
		self.show_track_header_wide = 1
		self.show_track_header_wide_track_inpector_open = 0
		self.gain = 1.0
		self.bpm = 120.0
		self.x = 0
		self.y = 0
		self.show_curve_editor = 0
		self.loop = 0
		self.loop_start = 0.0
		self.loop_end = 16.0
		self.viewport_start = 0.0
		self.viewport_end = 24.0
		self.viewport_lower_bound = 0.0
		self.viewport_upper_bound = 600.0
		self.input_program_change = -1
		self.input_program_change_channel = 0
		self.output_program_change = -1
		self.output_program_change_channel = 1
		self.play_start_marker = 5.0
		self.show_beat_time = 1
		self.time_signature_numerator = 4
		self.time_signature_denominator = 4
		self.default_pattern_size = 1
		self.pattern_launch_beat = 1
		self.swing_active = 0
		self.track_height_index = 1
		self.scale_lock = zenbeats_scale_lock(None)
		self.bank = zenbeats_bank(None)
		self.clip_scene_list = zenbeats_clip_scene_list(None)
		self.tracks = []

		self.storeid__rack = {}

	def read(self, xml_data):
		self.__init__()
		self.visual.read(xml_data)
		self.version.read(xml_data)
		attrib = xml_data.attrib
		if 'uid' in attrib: self.uid = attrib['uid']
		if 'selected_child' in attrib: self.selected_child = int(attrib['selected_child'])
		if 'read_only' in attrib: self.read_only = int(attrib['read_only'])
		if 'grid_size' in attrib: self.grid_size = float(attrib['grid_size'])
		if 'track_view_state' in attrib: self.track_view_state = attrib['track_view_state']
		if 'show_mixer_view' in attrib: self.show_mixer_view = int(attrib['show_mixer_view'])
		if 'show_track_inspector' in attrib: self.show_track_inspector = int(attrib['show_track_inspector'])
		if 'show_pattern_inspector' in attrib: self.show_pattern_inspector = int(attrib['show_pattern_inspector'])
		if 'show_onscreen_midi_input' in attrib: self.show_onscreen_midi_input = int(attrib['show_onscreen_midi_input'])
		if 'show_track_header_wide' in attrib: self.show_track_header_wide = int(attrib['show_track_header_wide'])
		if 'show_track_header_wide_track_inpector_open' in attrib: self.show_track_header_wide_track_inpector_open = int(attrib['show_track_header_wide_track_inpector_open'])
		if 'gain' in attrib: self.gain = float(attrib['gain'])
		if 'bpm' in attrib: self.bpm = float(attrib['bpm'])
		if 'x' in attrib: self.x = int(attrib['x'])
		if 'y' in attrib: self.y = int(attrib['y'])
		if 'show_curve_editor' in attrib: self.show_curve_editor = int(attrib['show_curve_editor'])
		if 'loop' in attrib: self.loop = int(attrib['loop'])
		if 'loop_start' in attrib: self.loop_start = float(attrib['loop_start'])
		if 'loop_end' in attrib: self.loop_end = float(attrib['loop_end'])
		if 'viewport_start' in attrib: self.viewport_start = float(attrib['viewport_start'])
		if 'viewport_end' in attrib: self.viewport_end = float(attrib['viewport_end'])
		if 'viewport_lower_bound' in attrib: self.viewport_lower_bound = float(attrib['viewport_lower_bound'])
		if 'viewport_upper_bound' in attrib: self.viewport_upper_bound = float(attrib['viewport_upper_bound'])
		if 'input_program_change' in attrib: self.input_program_change = int(attrib['input_program_change'])
		if 'input_program_change_channel' in attrib: self.input_program_change_channel = int(attrib['input_program_change_channel'])
		if 'output_program_change' in attrib: self.output_program_change = int(attrib['output_program_change'])
		if 'output_program_change_channel' in attrib: self.output_program_change_channel = int(attrib['output_program_change_channel'])
		if 'play_start_marker' in attrib: self.play_start_marker = float(attrib['play_start_marker'])
		if 'show_beat_time' in attrib: self.show_beat_time = int(attrib['show_beat_time'])
		if 'time_signature_numerator' in attrib: self.time_signature_numerator = int(attrib['time_signature_numerator'])
		if 'time_signature_denominator' in attrib: self.time_signature_denominator = int(attrib['time_signature_denominator'])
		if 'default_pattern_size' in attrib: self.default_pattern_size = int(attrib['default_pattern_size'])
		if 'pattern_launch_beat' in attrib: self.pattern_launch_beat = int(attrib['pattern_launch_beat'])
		if 'swing_active' in attrib: self.swing_active = int(attrib['swing_active'])
		if 'track_height_index' in attrib: self.track_height_index = int(attrib['track_height_index'])

		for x_part in xml_data:
			if x_part.tag == 'scale_lock': self.scale_lock.read(x_part)
			if x_part.tag == 'track': self.tracks.append(zenbeats_track(x_part))
			if x_part.tag == 'bank': self.bank.read(x_part)
			if x_part.tag == 'clip_scene_list': self.clip_scene_list.read(x_part)

		for rack in self.bank.racks: self.storeid__rack[rack.uid] = rack

	def write(self, tempxml):
		self.version.write(tempxml)
		self.visual.write(tempxml)
		tempxml.set('uid', str(self.uid))
		tempxml.set('selected_child', str(self.selected_child))
		tempxml.set('read_only', str(self.read_only))
		tempxml.set('grid_size', str(self.grid_size))
		tempxml.set('track_view_state', str(self.track_view_state))
		tempxml.set('show_mixer_view', str(self.show_mixer_view))
		tempxml.set('show_track_inspector', str(self.show_track_inspector))
		tempxml.set('show_pattern_inspector', str(self.show_pattern_inspector))
		tempxml.set('show_onscreen_midi_input', str(self.show_onscreen_midi_input))
		tempxml.set('show_track_header_wide', str(self.show_track_header_wide))
		tempxml.set('show_track_header_wide_track_inpector_open', str(self.show_track_header_wide_track_inpector_open))
		tempxml.set('gain', str(self.gain))
		tempxml.set('bpm', str(self.bpm))
		tempxml.set('x', str(self.x))
		tempxml.set('y', str(self.y))
		tempxml.set('show_curve_editor', str(self.show_curve_editor))
		tempxml.set('loop', str(self.loop))
		tempxml.set('loop_start', str(self.loop_start))
		tempxml.set('loop_end', str(self.loop_end))
		tempxml.set('viewport_start', str(self.viewport_start))
		tempxml.set('viewport_end', str(self.viewport_end))
		tempxml.set('viewport_lower_bound', str(self.viewport_lower_bound))
		tempxml.set('viewport_upper_bound', str(self.viewport_upper_bound))
		tempxml.set('input_program_change', str(self.input_program_change))
		tempxml.set('input_program_change_channel', str(self.input_program_change_channel))
		tempxml.set('output_program_change', str(self.output_program_change))
		tempxml.set('output_program_change_channel', str(self.output_program_change_channel))
		tempxml.set('play_start_marker', str(self.play_start_marker))
		tempxml.set('show_beat_time', str(self.show_beat_time))
		tempxml.set('time_signature_numerator', str(self.time_signature_numerator))
		tempxml.set('time_signature_denominator', str(self.time_signature_denominator))
		tempxml.set('default_pattern_size', str(self.default_pattern_size))
		tempxml.set('pattern_launch_beat', str(self.pattern_launch_beat))
		tempxml.set('swing_active', str(self.swing_active))
		tempxml.set('track_height_index', str(self.track_height_index))
		self.scale_lock.write(tempxml)
		for track in self.tracks: write(tempxml)
		self.bank.write(tempxml)
		self.clip_scene_list.write(tempxml)

	def load_from_file(self, input_file):
		x_root = ET.parse(input_file).getroot()
		self.read(x_root)
		if DEBUG_IN_OUT:
			outfile = ET.ElementTree(x_root)
			ET.indent(outfile)
			outfile.write('debug_in.song', xml_declaration = True)
		return True

	def save_to_file(self, out_file):
		zenbeats_proj = ET.Element("song")
		self.write(zenbeats_proj)
		if DEBUG_IN_OUT:
			outfile = ET.ElementTree(zenbeats_proj)
			ET.indent(outfile)
			outfile.write('debug_out.song', xml_declaration = True)
		outfile = ET.ElementTree(zenbeats_proj)
		ET.indent(outfile)
		outfile.write(out_file, xml_declaration = True)
