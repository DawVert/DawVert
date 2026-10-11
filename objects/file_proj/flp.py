# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import struct
import zipfile
import logging
from io import BytesIO
from functions import data_bytes
from functions.dawspecific import format_flp_tlv
from external.easybinrw import easybinrw
from external.easybinrw import chunked

from objects.file_proj._flp import auto
from objects.file_proj._flp import arrangement
from objects.file_proj._flp import chunks
from objects.file_proj._flp import objs
from objects.exceptions import ProjectFileParserException

tlv_writer = format_flp_tlv.tlv_writer
tlv_reader = format_flp_tlv.tlv_reader
tlv_write_utf8 = format_flp_tlv.write_utf8
tlv_write_std = format_flp_tlv.write_tlv

flp_current_state = objs.flp_current_state
flp_fxchan = objs.flp_fxchan

decodetext = objs.decodetext
utf16encode = objs.utf16encode

logger_projparse = logging.getLogger('projparse')

DEBUG_IN_OUT = False

#FL_OUTPUT_MODE = 12

total_num_tracks = {
	25: 500, 24: 500, 23: 500, 22: 500, 21: 500, 20: 500,
	12: 199, 11: 199, 10: 199, 9: 199, 8: 199, 7: 199, 6: 199, 5: 199, 4: 199, 3: 199,
}

total_num_fx = {
	25: 126, 24: 126, 23: 126, 22: 126, 21: 126, 20: 126,
	12: 104, 11: 104, 10: 104, 9: 104, 8: 104, 7: 104, 6: 104, 5: 104, 4: 104,
	3: 21,
}

total_num_fx_routing = {
	25: 127, 24: 127, 23: 127, 22: 127, 21: 127,
	20: 126,
	12: 105, 11: 105, 10: 105, 9: 105, 8: 105, 7: 105, 6: 105, 5: 105, 4: 105,
	3: 21,
}

class flp_project:
	def __init__(self):
		self.main = {}
		self.channels = {}
		self.patterns = {}
		self.patterns[0] = objs.flp_pattern()
		self.mixer = {}
		#for fxnum in range(127): self.mixer[fxnum] = flp_fxchan(fxnum)
		self.initfxvals = auto.flp_initvals()
		self.startvals = auto.flp_initvals()
		self.arrangements = {}
		self.arrangements[0] = arrangement.flp_arrangement(500)
		self.timemarkers = []
		self.changroupname = []
		self.nonsong_patnum = 1
		self.truncate_clip_notes = 1
		self.loop_active = 1
		self.automatic_crossfades = 0
		self.panning_law = 0
		self.ppq = 96
		self.num_channels = 0
		self.main_vol = 128
		self.num_steps_shown = 32
		self.current_filternum = 4294967295
		self.remotectrl_midi = []

		self.fx_color = None
		self.fx_icon = None
		self.fxcreationmode = 0
		self.def_pluginname = ''
		self.delayline = None

		self.current_ctrl = None

		self.slotstore = None

		self.tempo = 120
		self.tempofine = 0

		self.mainpitch = 0
		self.numerator = 4
		self.denominator = 4
		self.shuffle = 0
		self.title = ''
		self.genre = ''
		self.author = ''
		self.projectdatapath = ''
		self.comment = ''
		self.comment_rtf = ''
		self.url = ''
		self.projecttime = None
		self.showinfo = 0
		self.version = ''
		self.version_split = [0]

		self.remote_assoc = {}
		self.fx_name = ''

		self.zipped = False
		self.zipfile = None
		#with open('flp_eventname.txt') as f:
		#	self.lines = f.readlines()

		self.playlistblock = {}
		self.playlistblock_looppos = 0

		self.plsel = None

	def init_set_version(self, FLVersion, cur_state):
		self.version = FLVersion
		self.version_split = [int(x) for x in FLVersion.split('.')]
		self.num_fx = total_num_fx[self.version_split[0]]
		self.num_fx_routing = total_num_fx_routing[self.version_split[0]]
		self.num_tracks = total_num_tracks[self.version_split[0]]
		for fxnum in range(self.num_fx): self.mixer[fxnum] = flp_fxchan(fxnum)
		self.arrangements[0] = arrangement.flp_arrangement(self.num_tracks)
		cur_state.set_version(self.version_split)

	def add_old_playlistblock(self, event_data):
		pos = event_data&0xFF
		patnum = event_data>>16
		if pos not in self.playlistblock: self.playlistblock[pos] = []
		self.playlistblock[pos].append(patnum)

	def do_event(self, event_id, event_data, cur_state):
		#print(event_id)
		if event_id == 199: 
			FLVersion = event_data.decode('utf-8').rstrip('\x00')
			logger_projparse.info('FL: Version: ' + FLVersion)
			self.init_set_version(FLVersion, cur_state)
		elif event_id ==   9: self.loop_active = event_data
		elif event_id ==  10: self.showinfo = event_data
		elif event_id ==  11: self.shuffle = event_data
		elif event_id ==  17: self.numerator = event_data
		elif event_id ==  18: self.denominator = event_data
		elif event_id ==  23: self.panning_law = event_data
		elif event_id ==  30: self.truncate_clip_notes = event_data
		elif event_id ==  44: self.automatic_crossfades = event_data
		elif event_id ==  67: self.nonsong_patnum = event_data
		elif event_id ==  80: self.mainpitch = struct.unpack('h', struct.pack('H', event_data))[0]
		elif event_id == 194: self.title = decodetext(self.version_split, event_data)
		elif event_id == 195: self.comment = decodetext(self.version_split, event_data)
		elif event_id == 198: self.comment_rtf = decodetext(self.version_split, event_data)
		elif event_id == 197: self.url = decodetext(self.version_split, event_data)
		elif event_id == 202: self.projectdatapath = decodetext(self.version_split, event_data)
		elif event_id == 206: self.genre = decodetext(self.version_split, event_data)
		elif event_id == 207: self.author = decodetext(self.version_split, event_data)
		elif event_id == 231: self.changroupname.append(decodetext(self.version_split, event_data))
		elif event_id == 237: self.projecttime = event_data
		elif event_id == 216: self.startvals.read(event_data)
		elif event_id == 225: self.initfxvals.read(event_data)
		elif event_id ==  12: self.main_vol = event_data
		elif event_id ==  24: self.num_steps_shown = event_data
		elif event_id == 146: self.current_filternum = event_data
		elif event_id == 226: self.remotectrl_midi.append(event_data)
		elif event_id ==  84: self.playlistblock_looppos = event_data
		elif event_id == 211: self.delayline = event_data

		elif event_id ==  93: self.tempofine = event_data
		elif event_id ==  66: self.tempo = event_data

		elif event_id == 200: pass # RegName
		elif event_id == 217: self.plsel = event_data
		elif event_id == 133: pass # WindowH

		elif event_id == 156: 
			self.tempo = event_data//1000
			self.tempofine = event_data%1000

		elif event_id ==   0: cur_state.channel_enabled(event_data)
		elif event_id ==  19: cur_state.channel_uselooppoints(event_data)
		elif event_id ==  20: cur_state.channel_looptype(event_data)
		elif event_id ==  21: cur_state.channel_type(event_data)
		elif event_id ==  22: cur_state.channel_fxchannel(event_data)
		elif event_id ==  64: cur_state.channel_new(event_data)
		elif event_id ==  69: cur_state.channel_fx(event_data)
		elif event_id ==  70: cur_state.channel_fxflags(event_data)
		elif event_id ==  71: cur_state.channel_cutoff(event_data)
		elif event_id ==  74: cur_state.channel_preamp(event_data)
		elif event_id ==  75: cur_state.channel_decay(event_data)
		elif event_id ==  76: cur_state.channel_attack(event_data)
		elif event_id ==  83: cur_state.channel_resonance(event_data)
		elif event_id ==  85: cur_state.channel_stdel(event_data)
		elif event_id ==  86: cur_state.channel_fx3(event_data)
		elif event_id ==  89: cur_state.channel_shiftdelay(event_data)
		elif event_id ==  94: cur_state.channel_layer_chans(event_data)
		elif event_id == 131: cur_state.channel_fxsine(event_data)
		elif event_id == 132: cur_state.channel_cutcutby(event_data)
		elif event_id == 135: cur_state.channel_middlenote(event_data)
		elif event_id == 138: cur_state.channel_delayreso(event_data)
		elif event_id == 139: cur_state.channel_reverb(event_data)
		elif event_id == 140: cur_state.channel_stretchtime(event_data)
		elif event_id == 143: cur_state.channel_sampleflags(event_data)
		elif event_id == 144: cur_state.channel_layerflags(event_data)
		elif event_id == 145: cur_state.channel_filtergroup(event_data)
		elif event_id == 192: cur_state.channel_name(event_data)
		elif event_id == 196: cur_state.channel_samplefilename(event_data)
		elif event_id == 209: cur_state.channel_delay(event_data)
		elif event_id == 210: cur_state.channel_ts404params(event_data)
		elif event_id == 215: cur_state.channel_params(event_data)
		elif event_id == 218: cur_state.channel_env_lfo(event_data)
		elif event_id == 219: cur_state.channel_basicparams(event_data)
		elif event_id == 220: cur_state.channel_oldfilterparams(event_data)
		elif event_id == 221: cur_state.channel_poly(event_data)
		elif event_id == 228: cur_state.channel_tracking(event_data)
		elif event_id == 229: cur_state.channel_ofslevels(event_data)
		#elif event_id == 234: cur_state.channel_autopoints(event_data)

		elif event_id ==  99: cur_state.arrangement_new(event_data)

		elif event_id ==  33: cur_state.timemarker_numerator(event_data)
		elif event_id ==  34: cur_state.timemarker_denominator(event_data)
		elif event_id == 148: cur_state.timemarker_new(event_data)
		elif event_id == 205: cur_state.timemarker_name(event_data)

		elif event_id ==  65: cur_state.pattern_new(event_data)
		elif event_id == 223: cur_state.pattern_automation(event_data)
		elif event_id == 224: cur_state.pattern_notes(event_data)
		elif event_id == 150: cur_state.pattern_color(event_data)
		elif event_id == 193: cur_state.pattern_name(event_data)

		elif event_id == 241: cur_state.arrangement_name(event_data)
		#elif event_id == 233: cur_state.arrangement_items(event_data)

		elif event_id == 238: cur_state.track_new(event_data)
		elif event_id == 239: cur_state.track_name(event_data)

		elif event_id == 227: cur_state.control_new(event_data)
		elif event_id == 230: cur_state.control_formula(event_data)

		elif event_id == 201: cur_state.plugin_name(event_data)
		elif event_id == 203: cur_state.plugin_visname(event_data)
		elif event_id == 155: cur_state.plugin_icon(event_data)
		elif event_id == 128: cur_state.plugin_color(event_data)
		elif event_id == 213: cur_state.plugin_params(event_data)

		elif event_id == 236: cur_state.fxchan_add(event_data)
		elif event_id == 149: cur_state.fxchan_color(event_data)
		elif event_id ==  95: cur_state.fxchan_icon(event_data)
		elif event_id == 204: cur_state.fxchan_name(event_data)
		elif event_id == 154: cur_state.fxchan_inchannum(event_data)
		elif event_id == 147: cur_state.fxchan_outchannum(event_data)
		elif event_id == 235: cur_state.fxchan_routing(event_data)

		elif event_id == 212: cur_state.plugin_chunk(event_data)

		elif event_id ==  91: cur_state.pattern_dot(event_data, 'on')
		elif event_id ==  72: cur_state.pattern_dot(event_data, 'vol')
		elif event_id ==  77: cur_state.pattern_dot(event_data, 'note')
		elif event_id ==  73: cur_state.pattern_dot(event_data, 'pan')
		elif event_id ==  78: cur_state.pattern_dot(event_data, 'pitch')
		elif event_id ==  79: cur_state.pattern_dot(event_data, 'mix')
		elif event_id ==  87: cur_state.pattern_dot(event_data, 'reso')
		elif event_id ==  88: cur_state.pattern_dot(event_data, 'cutoff')
		elif event_id ==  92: cur_state.pattern_dot(event_data, 'shift')

		elif event_id == 129: self.add_old_playlistblock(event_data)

		else: print('unknown eventid', event_id)

	def view_tlv(self, inputfile):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(inputfile)
		for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, None):
			if chunk_obj.id == b'FLdt':
				tlvr = tlv_reader(ebrw_readstr)
				tlvr.debug_load()
				while ebrw_readstr.remaining(): tlvr.view_event()

	def to_flp_debtxt(self, inputfile, outputfile):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(inputfile)
		f = open(outputfile, 'w')
		for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, None):
			if chunk_obj.id == b'FLdt':
				tlvr = tlv_reader(ebrw_readstr)
				tlvr.debug_load()
				while ebrw_readstr.remaining(): f.write(tlvr.debugtxt_event())

	def read_chunk_FLhd(self, ebrw_readstr):
		ebrw_readstr.skip(2)
		self.num_channels = ebrw_readstr.int_u16()
		self.ppq = ebrw_readstr.int_u16()

	def read(self, inputfile):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(inputfile)

		if ebrw_readstr.read(2) == b'PK':
			self.zipped = True
			self.zipfile = zipfile.ZipFile(inputfile, 'r')
			flpfound = False
			for filename in self.zipfile.namelist():
				if filename.endswith('.flp'):
					flpdata = self.zipfile.read(filename)
					ebrw_readstr = easybinrw.binread()
					ebrw_readstr.load_data(flpdata)
					flpfound = True
			if not flpfound:
				raise ProjectFileParserException('FL: FLP file not found in zip')

		ebrw_readstr.seek(0)

		current_state = objs.flp_current_state(self)

		tlvfound = False
		for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, None):
			if chunk_obj.id == b'FLhd': self.read_chunk_FLhd(ebrw_readstr)
			if chunk_obj.id == b'FLdt':
				tlvfound = True
				tlvr = tlv_reader(ebrw_readstr)
				tlvr.debug_load()
				while ebrw_readstr.remaining(): 
					event_id, event_data = tlvr.read_event()
					self.do_event(event_id, event_data, current_state)

		if not tlvfound:
			raise ProjectFileParserException('FL: TLV data not found')

		if DEBUG_IN_OUT:
			import shutil
			shutil.copy(inputfile, 'debug_in.flp')
			self.to_flp_debtxt('debug_in.flp', 'debug_in.flps')


	def make_fl3(self, ebrw_writestr):
		tlvw = tlv_writer(ebrw_writestr)
		tlvw.str8( 199, '3.5.6')
		tlvw.out(  200, b'')
		tlvw.out(   93, self.tempofine)
		tlvw.out(   66, self.tempo)
		tlvw.out(   67, self.nonsong_patnum)
		tlvw.out(    9, self.loop_active)
		tlvw.out(   11, self.shuffle)
		tlvw.out(   12, self.main_vol)
		tlvw.out(   80, self.mainpitch)
		tlvw.out(   17, self.numerator)
		tlvw.out(   24, self.num_steps_shown)
		tlvw.out(   18, self.denominator)
		if self.delayline: tlvw.out(  211, self.delayline)
		if self.plsel: tlvw.out(  217, self.plsel)
		tlvw.out(   23, self.panning_law)
		tlvw.out(   10, self.showinfo)
		tlvw.str8( 194, self.title)
		tlvw.str8( 198, self.comment_rtf)
		tlvw.str8( 197, self.url)
		tlvw.out(  146, self.current_filternum)
		tlvw.out(  216, self.startvals.write())
		for patnum, patdat in self.patterns.items(): patdat.make_tlv(tlvw, patnum)
		for x in self.remotectrl_midi: tlvw.out(226, x)

		#for renum, redat in self.remote_assoc.items():
		#	for x in redat: 
		#		tlvw.out(227, x.write())
		#		if x.formula: tlvw.str8(230, x.formula)

		for channum, chandata in self.channels.items():
			chandata.make_tlv(tlvw, channum, self.version_split)
			for patnum, patdat in self.patterns.items():
				patdat.make_tlv_dots(tlvw, patnum, channum)

		for pos, patnum in self.playlistblock.items():
			for x in patnum: tlvw.out(129, pos+(x<<16))

		tlvw.out(84, self.playlistblock_looppos)
		tlvw.out(225, self.initfxvals.write())

		for num, mixchan in self.mixer.items():
			tlvw.str8(204, mixchan.name)
			tlvw.out(147, mixchan.outchannum)

		tlvw.out(133, 480)

	def make_chunk_header(self, ebrw_writestr, name, data):
		ebrw_writestr.raw(name)
		ebrw_writestr.int_u32(len(data))
		ebrw_writestr.raw(data)

	def make_chunk_FLhd(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.raw(self.num_channels.to_bytes(3, 'big'))
		ebrw_writestr.raw(b'\x00')
		ebrw_writestr.raw(self.ppq.to_bytes(2, 'little'))
		return ebrw_writestr.getvalue()

	def make_chunk_FLdt(self, FL_OUTPUT_MODE):
		ebrw_writestr = easybinrw.binwrite()
		if FL_OUTPUT_MODE==3: self.make_fl3(ebrw_writestr)
		return ebrw_writestr.getvalue()

	def make(self, outputfile, FL_OUTPUT_MODE):
		num_fx = total_num_fx[FL_OUTPUT_MODE]
		num_fx_routing = total_num_fx_routing[FL_OUTPUT_MODE]
		num_tracks = total_num_tracks[FL_OUTPUT_MODE]

		flpout = open(outputfile, 'wb')
		ebrw_writestr = easybinrw.binwrite()
		self.make_chunk_header(ebrw_writestr, b'FLhd', self.make_chunk_FLhd())
		self.make_chunk_header(ebrw_writestr, b'FLdt', self.make_chunk_FLdt(FL_OUTPUT_MODE))
		flpout.write(ebrw_writestr.getvalue())
		flpout.close()

		if DEBUG_IN_OUT:
			import shutil
			shutil.copy(outputfile, 'debug_out.flp')
			self.to_flp_debtxt('debug_out.flp', 'debug_out.flps')


















