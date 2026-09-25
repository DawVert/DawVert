# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import numpy as np
from objects.exceptions import ProjectFileParserException

vl_dtype = np.dtype([('n', np.int16),('t', np.int16),('v', np.int16),('f', np.int16),('id', np.int32),('x', np.int16),('p', np.int16),('e', np.int16)])

class LCSound:
	def __init__(self, indict=None):
		self.play_notes = 32
		self.play_speed = 30
		self.vl = None
		self.voicelist = np.zeros(self.play_notes, dtype=vl_dtype)
		self.voicelist.fill(-1)
		self.voicelist['x'] = 14
		self.voicelist['p'] = 8
		if indict is not None: self.read(indict)

	def read(self, indict):
		if '__LCSound__' in indict:
			self.vl = indict['vl']
			if 'play_notes' in indict: self.play_notes = indict['play_notes']
			if 'play_speed' in indict: self.play_speed = indict['play_speed']

		if self.vl:
			for num in range(min(len(self.voicelist), len(self.vl))):
				dat = self.vl[num]
				vlp = self.voicelist[num]
				if 'n' in dat:
					if dat['n'] != None: vlp['n'] = dat['n']
				if 't' in dat:
					if dat['t'] != None: vlp['t'] = dat['t']
				if 'v' in dat:
					if dat['v'] != None: vlp['v'] = dat['v']
				if 'f' in dat:
					if dat['f'] != None: vlp['f'] = dat['f']
				if 'id' in dat:
					if dat['id'] != None: vlp['id'] = dat['id']
				if 'x' in dat:
					if dat['x'] != None: vlp['x'] = dat['x']
				if 'p' in dat:
					if dat['p'] != None: vlp['p'] = dat['p']
				if 'e' in dat:
					if dat['e'] != None: vlp['e'] = dat['e']

class LCSoundList:
	def __init__(self, indict=None):
		self.sl = []
		if indict is not None: self.read(indict)

	def read(self, indict):
		if '__LCSoundList__' in indict:
			for ch in indict['sl']:
				self.sl.append(LCSound(ch))

class LCChannelList:
	def __init__(self):
		self.ch = []

	def load(self, indict):
		if '__LCChannelList__' in indict:
			for ch in indict['channels']:
				self.ch.append(LCSoundList(ch))

class LCRhythm:
	def __init__(self, indict=None):
		self.enable_drum = True
		self.enable_base = True
		self.enable_melody = True
		self.bar_rhythm_rate = 3
		self.bar_arpeggio_rate = 3
		self.arpeggio = 0
		self.arpeggio_octave = 1
		self.arpeggio_length = 3
		self.arpeggio_reverse = False
		self.pattern = 3
		self.sub_pattern = 2
		self.enable_chordpart = True
		if indict is not None: self.read(indict)

	def read(self, indict):
		if '__LCRhythm__' in indict:
			if 'enable_drum' in indict: self.enable_drum = indict['enable_drum']
			if 'enable_base' in indict: self.enable_base = indict['enable_base']
			if 'enable_melody' in indict: self.enable_melody = indict['enable_melody']
			if 'bar_rhythm_rate' in indict: self.bar_rhythm_rate = indict['bar_rhythm_rate']
			if 'bar_arpeggio_rate' in indict: self.bar_arpeggio_rate = indict['bar_arpeggio_rate']
			if 'arpeggio' in indict: self.arpeggio = indict['arpeggio']
			if 'arpeggio_octave' in indict: self.arpeggio_octave = indict['arpeggio_octave']
			if 'arpeggio_length' in indict: self.arpeggio_length = indict['arpeggio_length']
			if 'arpeggio_reverse' in indict: self.arpeggio_reverse = indict['arpeggio_reverse']
			if 'pattern' in indict: self.pattern = indict['pattern']
			if 'sub_pattern' in indict: self.sub_pattern = indict['sub_pattern']
			if 'enable_chordpart' in indict: self.enable_chordpart = indict['enable_chordpart']

class LCRhythmList:
	def __init__(self):
		self.ry = []

	def load(self, indict):
		if '__LCRhythmList__' in indict:
			for ch in indict['rhythms']:
				self.ry.append(LCRhythm(ch))

class LCMusic:
	def __init__(self):
		self.abrepeat_a = None
		self.abrepeat_b = None
		self.bars_number_per_page = 4
		self.channels = LCChannelList()
		self.chord_channels = LCChannelList()
		self.code_channels = LCChannelList()
		self.compatibility_mode = 0
		self.enable_loop = True
		self.ex_filename = ''
		self.loop_end_bar = 9
		self.loop_start_bar = 0
		self.mixer_channel_switch_list = [0,0,0,0,0]
		self.mixer_expression_list = [0,0,0,0,0]
		self.mixer_output_channel_list = [0,0,0,0,0]
		self.mixer_transpose = 0
		self.notes_by_page = True
		self.pages = 20
		self.pan_law_type = 0
		self.pianoroll_display_mode = 0
		self.play_notes = 32
		self.pro_mode = 0
		self.rhythms = LCRhythmList()
		self.sel_scale_id = 0
		self.sel_scale_key = 0
		self.speed = 15
		self.tempo_by_page = True
		self.ui_mixer_expression_list = [0,0,0,0,0]
		self.ui_mixer_output_channel_list = [0,0,0,0,0]
		self.wave_memory_effect_list = []
		self.wave_memory_table_list = []
		self.wave_memory_type_list = []

		self.title = None
		self.editor = None

	def get_channel(self, num):
		voi_notes = self.channels.ch[num].sl
		voi_chord = self.chord_channels.ch[num].sl
		return voi_notes, voi_chord

	def load(self, indict):
		if '__LCMusic__' in indict:
			if 'speed' in indict: self.speed = indict['speed']
			if 'loop_start_bar' in indict: self.loop_start_bar = indict['loop_start_bar']
			if 'loop_end_bar' in indict: self.loop_end_bar = indict['loop_end_bar']
			if 'enable_loop' in indict: self.enable_loop = indict['enable_loop']
			if 'bars_number_per_page' in indict: self.bars_number_per_page = indict['bars_number_per_page']
			if 'pages' in indict: self.pages = indict['pages']
			if 'notes_by_page' in indict: self.notes_by_page = indict['notes_by_page']
			if 'tempo_by_page' in indict: self.tempo_by_page = indict['tempo_by_page']
			if 'play_notes' in indict: self.play_notes = indict['play_notes']
			if 'abrepeat_a' in indict: self.abrepeat_a = indict['abrepeat_a']
			if 'abrepeat_b' in indict: self.abrepeat_b = indict['abrepeat_b']
			if 'sel_scale_id' in indict: self.sel_scale_id = indict['sel_scale_id']
			if 'pianoroll_display_mode' in indict: self.pianoroll_display_mode = indict['pianoroll_display_mode']
			if 'channels' in indict: self.channels.load(indict['channels'])
			if 'chord_channels' in indict: self.chord_channels.load(indict['chord_channels'])
			if 'code_channels' in indict: self.code_channels.load(indict['code_channels'])
			if 'rhythms' in indict: self.rhythms.load(indict['rhythms'])
			if 'pro_mode' in indict: self.pro_mode = indict['pro_mode']
			if 'mixer_expression_list' in indict: self.mixer_expression_list = indict['mixer_expression_list']
			if 'mixer_output_channel_list' in indict: self.mixer_output_channel_list = indict['mixer_output_channel_list']
			if 'mixer_channel_switch_list' in indict: self.mixer_channel_switch_list = indict['mixer_channel_switch_list']
			if 'ui_mixer_expression_list' in indict: self.ui_mixer_expression_list = indict['ui_mixer_expression_list']
			if 'ui_mixer_output_channel_list' in indict: self.ui_mixer_output_channel_list = indict['ui_mixer_output_channel_list']
			if 'mixer_transpose' in indict: self.mixer_transpose = indict['mixer_transpose']
			if 'pan_law_type' in indict: self.pan_law_type = indict['pan_law_type']
			if 'compatibility_mode' in indict: self.compatibility_mode = indict['compatibility_mode']
			if 'sel_scale_key' in indict: self.sel_scale_key = indict['sel_scale_key']
			if 'title' in indict: self.title = indict['title']
			if 'editor' in indict: self.editor = indict['editor']
			if 'ex_filename' in indict: self.ex_filename = indict['ex_filename']
			if 'abrepeat_a' in indict: self.abrepeat_a = indict['abrepeat_a']
			if 'abrepeat_b' in indict: self.abrepeat_b = indict['abrepeat_b']
			if 'pianoroll_display_mode' in indict: self.pianoroll_display_mode = indict['pianoroll_display_mode']
			if 'wave_memory_table_list' in indict: self.wave_memory_table_list = indict['wave_memory_table_list']
			if 'wave_memory_type_list' in indict: self.wave_memory_type_list = indict['wave_memory_type_list']
			if 'wave_memory_effect_list' in indict: self.wave_memory_effect_list = indict['wave_memory_effect_list']

	def load_from_file(self, input_file):
		try:
			song_file = open(input_file, 'r')
			for num, lined in enumerate(song_file.readlines()):
				if num == 0: 
					metadata = json.loads(lined)
					if 'title' in metadata: self.title = metadata['title']
					if 'editor' in metadata: self.editor = metadata['editor']
				if num == 1: self.load(json.loads(lined))
		except UnicodeDecodeError:
			raise ProjectFileParserException('famistudio_txt: File is not text')

		return True

