# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

from objects.file_proj._flp import chunks
from objects.file_proj._flp import auto

def decodetext(version_split, event_data):
	if event_data.endswith(b'\x00\x00'):
		return event_data.decode('utf-16le').rstrip('\x00\x00')
	elif event_data.endswith(b'\x00'):
		return event_data.decode('utf-8').rstrip('\x00')
	else:
		return ''

def utf16encode(text):
	out_text = text if text != None else ''
	return out_text.encode('utf-16le') + b'\x00\x00'

class flp_patterns:
	def __init__(self):
		self.data = {}
		self.data[0] = objs.flp_pattern()

	def __getitem__(self, k): return self.data.__getitem__(k)

	def iter(self):
		for num in range(len(self.data)):
			if num in self.data: yield num, self.data[num]

class flp_channels:
	def __init__(self): self.data = {}

	def __getitem__(self, k): return self.data.__getitem__(k)

	def iter(self):
		for num in range(len(self.data)):
			if num in self.data: yield num, self.data[num]

class flp_mixer:
	def __init__(self): self.data = {}

	def __getitem__(self, k): return self.data.__getitem__(k)

	def setup_num(self, n): 
		self.data = {}
		for fxnum in range(n): self.data[fxnum] = flp_fxchan(fxnum)

	def iter(self):
		for num in range(len(self.data)):
			if num in self.data: yield num, self.data[num]

class flp_arrangements:
	def __init__(self):
		self.data = {}
		self.data[0] = arrangement.flp_arrangement(500)

	def __getitem__(self, k): return self.data.__getitem__(k)

	def iter(self):
		for num in range(len(self.data)):
			if num in self.data: yield num, self.data[num]

class flp_metadata:
	def __init__(self):
		self.title = ''
		self.genre = ''
		self.author = ''
		self.comment = ''
		self.comment_rtf = ''
		self.url = ''
		self.showinfo = 0
		self.projecttime = None

class flp_channel:
	def __init__(self):
		self.type = 0
		self.plugin = flp_plugin()
		#self.delay = b'\x00\x00\x00\x00\x00\x19\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x90\x00\x00\x00'
		self.attack = 0
		self.autopoints = None
		self.basicparams = chunks.chunk_channel_basicparams()
		self.cutcutby = 0
		self.cutoff = 1024
		self.decay = 0
		self.delay = chunks.chunk_channel_delay()
		self.delayreso = 8388736
		self.enabled = 1
		self.env_lfo = []
		self.filtergroup = 0
		self.fx = 128
		self.fx3 = 256
		self.fxchannel = 0
		self.fxflags = 0
		self.fxsine = 8388608
		self.layer_chans = []
		self.layerflags = 0
		self.looptype = 0
		self.loop_on = 0
		self.middlenote = 60
		self.ofslevels = b'\x00\x00\x00\x00\x002\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
		self.oldfilterparams = None
		self.params = chunks.chunk_channel_params()
		self.poly = chunks.chunk_channel_poly()
		self.preamp = 0
		self.resonance = 0
		self.reverb = 65536
		self.samplefilename = None
		self.sampleflags = 10
		self.shiftdelay = 0
		self.stdel = 2048
		self.stretchtime = 0
		self.tracking = []
		self.ts404params = None

	def make_tlv(self, tlvw, channum, version_split):
		plugin = self.plugin
		tlvw.out(  64, channum)
		tlvw.out(  21, self.type)
		self.plugin.make_tlv(tlvw)
		tlvw.out(   0, self.enabled)
		tlvw.out( 209, self.delay.write() )
		if self.ts404params: tlvw.out( 210, self.ts404params )
		tlvw.out( 138, self.delayreso)
		tlvw.out( 139, self.reverb)
		tlvw.out(  89, self.shiftdelay)
		tlvw.out(  69, self.fx)
		tlvw.out(  86, self.fx3)
		tlvw.out(  71, self.cutoff)
		tlvw.out(  83, self.resonance)
		tlvw.out(  74, self.preamp)
		tlvw.out(  75, self.decay)
		tlvw.out(  76, self.attack)
		tlvw.out(  85, self.stdel)
		tlvw.out( 131, self.fxsine)
		tlvw.out(  70, self.fxflags)
		tlvw.out( 140, self.stretchtime)
		tlvw.out(  22, self.fxchannel)
		tlvw.out( 219, self.basicparams.write() )
		tlvw.out( 229, self.ofslevels )
		tlvw.out( 221, self.poly.write() )
		tlvw.out( 215, self.params.write(3) )
		tlvw.out( 132, self.cutcutby)
		if self.layerflags: tlvw.out( 144, self.layerflags)
		if self.filtergroup: tlvw.out( 145, self.filtergroup)
		for x in self.tracking:
			tlvw.out( 228, x.write())
		for x in self.env_lfo:
			tlvw.out( 218, x.write(version_split))
		tlvw.out( 143, self.sampleflags)
		if self.loop_on: tlvw.out(  19, self.loop_on)
		tlvw.out(  20, self.looptype)
		if self.middlenote!=60: tlvw.out( 135, self.middlenote)
		if self.samplefilename: tlvw.str8(196, self.samplefilename)
		tlvw.str8(192, plugin.name)
		tlvw.out( 128, plugin.color)

class flp_plugin:
	__slots__ = ['plugname', 'params', 'chunk', 'icon', 'color', 'name']
	def __init__(self):
		self.plugname = None
		self.params = None
		self.chunk = chunks.chunk_plugin()
		self.icon = None
		self.color = None
		self.name = None

	def make_tlv(self, tlvw):
		if self.plugname:
			tlvw.str8(201, self.plugname)
			tlvw.out(212, self.chunk.write() )
			if self.params: tlvw.out(213, self.params)

class flp_fxslot:
	__slots__ = ['plugin', 'icon', 'color', 'name', 'used']
	def __init__(self, fxnum):
		self.plugin = flp_plugin()
		self.plugin.chunk.fxnum = fxnum
		self.used = False

class flp_fxchan:
	def __init__(self, fxnum):
		self.name = ''
		self.color = None
		self.slots = [flp_fxslot(fxnum) for x in range(10)]
		self.data = None
		self.routing = []
		self.inchannum = 4294967295
		self.outchannum = 4294967295
		self.chunk = chunks.chunk_fxchan()

class flp_current_state:
	def __init__(self, project):
		self.project = project
		self.version_split = [20]
		self.fx_make_mode = 0

		self.arrangement_num = 0
		self.arrangement_obj = self.project.arrangements[0]

		self.pattern_num = 0
		self.pattern_obj = self.project.patterns[0]

		self.channel_num = 0
		self.channel_obj = None

		self.track_num = 0
		self.track_obj = None

		self.control_num = 0
		self.control_obj = None

		self.timemarkers_obj = self.arrangement_obj.timemarkers
		self.timemarker_single_obj = None

		self.plugin_obj = None

		self.fx_obj = None
		self.fx_num = -1
		self.fx_name = None
		self.fx_color = None
		self.fx_icon = None

		self.slot_obj = None

		self.make_plugin_name = None

	def set_version(self, version_split): 
		self.version_split = version_split
		self.fx_make_mode = 0

	# ----------------------------------------- fxchannel -----------------------------------------
	def fxchan_color(self, event_data): self.fx_color = event_data
	def fxchan_icon(self, event_data): self.fx_icon = event_data
	def fxchan_name(self, event_data): 
		self.fx_name = decodetext(self.version_split, event_data)
	def fxchan_create(self): 
		self.fx_num += 1
		self.fx_obj = self.project.mixer[self.fx_num]
	def fxchan_add(self, event_data): 
		self.fxchan_create()
		self.fx_obj.name = self.fx_name
		self.fx_obj.color = self.fx_color
		self.fx_obj.icon = self.fx_icon
		self.fx_obj.chunk.read(event_data)
		self.fx_color = None
		self.fx_icon = None
		self.fx_name = None
	def fxchan_inchannum(self, event_data): self.fx_obj.inchannum = event_data
	def fxchan_outchannum(self, event_data):
		if self.fx_make_mode==0:
			self.fxchan_create()
			self.fx_obj.name = self.fx_name
			self.fx_name = None
		self.fx_obj.outchannum = event_data
	def fxchan_routing(self, event_data): 
		for num, on in enumerate(event_data):
			if on: self.fx_obj.routing.append(num)

	# ----------------------------------------- channel -----------------------------------------
	def channel_new(self, event_data):
		channels = self.project.channels
		self.channel_num = event_data
		if self.channel_num not in channels: channels[self.channel_num] = flp_channel()
		self.channel_obj = channels[self.channel_num]
		self.plugin_obj = self.channel_obj.plugin

	def channel_enabled(self, event_data): self.channel_obj.enabled = event_data
	def channel_type(self, event_data): self.channel_obj.type = event_data
	def channel_delayreso(self, event_data): self.channel_obj.delayreso = event_data
	def channel_reverb(self, event_data): self.channel_obj.reverb = event_data
	def channel_shiftdelay(self, event_data): self.channel_obj.shiftdelay = event_data
	def channel_fx(self, event_data): self.channel_obj.fx = event_data
	def channel_fx3(self, event_data): self.channel_obj.fx3 = event_data
	def channel_cutoff(self, event_data): self.channel_obj.cutoff = event_data
	def channel_resonance(self, event_data): self.channel_obj.resonance = event_data
	def channel_preamp(self, event_data): self.channel_obj.preamp = event_data
	def channel_decay(self, event_data): self.channel_obj.decay = event_data
	def channel_attack(self, event_data): self.channel_obj.attack = event_data
	def channel_stdel(self, event_data): self.channel_obj.stdel = event_data
	def channel_fxsine(self, event_data): self.channel_obj.fxsine = event_data
	def channel_fxflags(self, event_data): self.channel_obj.fxflags = event_data
	def channel_fxchannel(self, event_data): self.channel_obj.fxchannel = event_data
	def channel_layer_chans(self, event_data): self.channel_obj.layer_chans.append(event_data)
	def channel_params(self, event_data): self.channel_obj.params.read(event_data)
	def channel_ofslevels(self, event_data): self.channel_obj.ofslevels = event_data
	def channel_cutcutby(self, event_data): self.channel_obj.cutcutby = event_data
	def channel_layerflags(self, event_data): self.channel_obj.layerflags = event_data
	def channel_filtergroup(self, event_data): self.channel_obj.filtergroup = event_data
	def channel_sampleflags(self, event_data): self.channel_obj.sampleflags = event_data
	def channel_looptype(self, event_data): self.channel_obj.looptype = event_data
	def channel_middlenote(self, event_data): self.channel_obj.middlenote = event_data
	def channel_samplefilename(self, event_data): self.channel_obj.samplefilename = decodetext(self.version_split, event_data)
	def channel_delay(self, event_data): self.channel_obj.delay.read(event_data)
	def channel_basicparams(self, event_data): self.channel_obj.basicparams.read(event_data)
	def channel_oldfilterparams(self, event_data): self.channel_obj.basicparams.read_filterparams(event_data)
	def channel_poly(self, event_data): self.channel_obj.poly.read(event_data)
	def channel_ts404params(self, event_data): self.channel_obj.ts404params = event_data
	def channel_stretchtime(self, event_data): self.channel_obj.stretchtime = event_data
	def channel_name(self, event_data): self.plugin_obj.name = decodetext(self.version_split, event_data)

	def channel_uselooppoints(self, event_data):
		if event_data:
			if not bool(self.channel_obj.sampleflags & 8): self.channel_obj.sampleflags += 8
		self.channel_obj.loop_on = event_data

	def channel_env_lfo(self, event_data): 
		envlfo_obj = chunks.chunk_env_lfo()
		envlfo_obj.read(event_data)
		self.channel_obj.env_lfo.append(envlfo_obj)
			
	def channel_tracking(self, event_data): 
		trk_obj = chunks.chunk_channel_tracking()
		trk_obj.read(event_data)
		self.channel_obj.tracking.append(trk_obj)

	def channel_autopoints(self, event_data): 
		auto_obj = auto.flp_autopoints()
		auto_obj.read(event_data)
		self.current_ch_obj.autopoints = auto_obj

	# ----------------------------------------- pattern -----------------------------------------
	def pattern_create(self):
		project = self.project
		if self.pattern_num not in project.patterns: project.patterns[self.pattern_num] = flp_pattern()
		self.pattern_obj = project.patterns[self.pattern_num] 

	def pattern_new(self, event_data):
		self.pattern_num = event_data
		self.pattern_create()
		self.timemarkers_obj = self.pattern_obj.timemarkers

	def pattern_notes(self, event_data):
		self.pattern_obj.notes.read_data(event_data, self.version_split)

	def pattern_color(self, event_data):
		self.pattern_obj.color = event_data

	def pattern_name(self, event_data):
		self.pattern_obj.name = decodetext(self.version_split, event_data)

	def pattern_automation(self, event_data):
		self.pattern_obj.automation.read_data(event_data)

	def pattern_dot(self, event_data, itype):
		pos = event_data%256
		val = event_data>>8
		self.pattern_obj.add_dot(pos, self.channel_num)[itype] = val

	# ----------------------------------------- arrangement -----------------------------------------
	def arrangement_new(self, event_data):
		arrangements = self.project.arrangements
		self.arrangement_num = event_data
		if self.arrangement_num not in arrangements: 
			arrangements[self.arrangement_num] = arrangement.flp_arrangement(self.num_tracks)
		self.arrangement_obj = arrangements[self.arrangement_num]
		self.timemarkers_obj = self.arrangement_obj.timemarkers

	def arrangement_name(self, event_data):
		self.arrangement_obj.name = decodetext(self.version_split, event_data)

	def arrangement_items(self, event_data):
		arritems = self.arrangement_obj.items
		arritems.add_data(event_data, self.version_split)
		arritems.postprocess_input()
		self.timemarkers_obj = self.arrangement_obj.timemarkers

	# ----------------------------------------- timemarker -----------------------------------------
	def timemarker_new(self, event_data):
		timemarker_obj = arrangement.flp_timemarker()
		timemarker_obj.type = event_data >> 24
		timemarker_obj.pos = event_data & 0x00ffffff
		self.timemarkers_obj.append(timemarker_obj)
		self.timemarker_single_obj = timemarker_obj

	def timemarker_name(self, event_data): 
		self.timemarker_single_obj.name = decodetext(self.version_split, event_data)

	def timemarker_numerator(self, event_data): 
		self.timemarker_single_obj.numerator = event_data

	def timemarker_denominator(self, event_data): 
		self.timemarker_single_obj.denominator = event_data

	# ----------------------------------------- track -----------------------------------------
	def track_new(self, event_data):
		ebrw_readstr = BytesIO(event_data)
		flp_track_obj = arrangement.flp_track()
		flp_track_obj.read(ebrw_readstr, len(event_data), self.version_split)
		self.track_num = flp_track_obj.id
		self.track_obj = flp_track_obj
		self.arrangement_obj.tracks[self.track_num] = flp_track_obj

	def track_name(self, event_data):
		self.track_obj.name = decodetext(self.version_split, event_data)

	# ----------------------------------------- plugin -----------------------------------------
	def plugin_visname(self, event_data): 
		self.plugin_obj.name = decodetext(self.version_split, event_data)

	def plugin_icon(self, event_data): 
		self.plugin_obj.icon = event_data

	def plugin_color(self, event_data): 
		self.plugin_obj.color = event_data

	def plugin_params(self, event_data): 
		self.plugin_obj.params = event_data

	def plugin_name(self, event_data):
		self.make_plugin_name = decodetext(self.version_split, event_data)

	def plugin_chunk(self, event_data): 
		self.plugin_obj = flp_plugin()
		self.plugin_obj.plugname = self.make_plugin_name
		chunk = self.plugin_obj.chunk
		chunk.read(event_data)
		if chunk.generator:
			channels = self.project.channels
			channels[self.channel_num].plugin = self.plugin_obj
		else:
			self.slot_obj = flp_fxslot(chunk.fxnum)
			self.slot_obj.plugin = self.plugin_obj
			slotnum = chunk.slotnum
			if slotnum<10: 
				self.project.mixer[chunk.fxnum].slots[slotnum] = self.slot_obj

	# ----------------------------------------- control -----------------------------------------
	def control_new(self, event_data):
		self.control_obj = flp_auto = auto.flp_remotecontrol()
		flp_auto.read(event_data)
		remote_assoc = self.project.remote_assoc
		if flp_auto.channel not in remote_assoc: remote_assoc[flp_auto.channel] = []
		remote_assoc[flp_auto.channel].append(flp_auto)

	def control_formula(self, event_data):
		if self.control_obj:
			self.control_obj.formula = decodetext(self.version_split, event_data)

def make_dot(pos, val): return pos+(val<<8)

class flp_pattern:
	__slots__ = ['color', 'automation', 'notes', 'name', 'timemarkers', 'dotmode', 'dots']
	def __init__(self):
		self.name = None
		self.color = None
		self.automation = chunks.autoeventdata()
		self.notes = chunks.notedata()
		self.timemarkers = []
		self.dotmode = False
		self.dots = {}

	def add_dot(self, n, channum):
		self.dotmode = True
		if channum not in self.dots: self.dots[channum] = {}
		if n not in self.dots[channum]: self.dots[channum][n] = {}
		return self.dots[channum][n]

	def make_tlv(self, tlvw, patnum):
		outauto = self.automation.make()
		outnotes = self.notes.make_old()
		if outauto or outnotes:
			tlvw.out(65, patnum)
			if outauto: tlvw.out(223, outauto)
			if outnotes: tlvw.out(224, outnotes)

	def make_tlv_name(self, tlvw, patnum):
		if self.name:
			tlvw.out(65, patnum)
			tlvw.str8(193, self.name)

	def make_tlv_dots(self, tlvw, patnum, channum):
		if channum in self.dots:
			chandots = self.dots[channum]
			tlvw.out(65, patnum)
			for pos, dots in chandots.items():
				if 'vol' in dots: tlvw.out(72, make_dot(pos, dots['vol']) )
				if 'note' in dots: tlvw.out(77, make_dot(pos, dots['note']) )
				if 'pan' in dots: tlvw.out(73, make_dot(pos, dots['pan']) )
				if 'pitch' in dots: tlvw.out(78, make_dot(pos, dots['pitch']) )
				if 'mix' in dots: tlvw.out(79, make_dot(pos, dots['mix']) )
				if 'reso' in dots: tlvw.out(87, make_dot(pos, dots['reso']) )
				if 'cutoff' in dots: tlvw.out(88, make_dot(pos, dots['cutoff']) )
				if 'shift' in dots: tlvw.out(92, make_dot(pos, dots['shift']) )
				if 'on' in dots: tlvw.out(91, make_dot(pos, dots['on']) )
