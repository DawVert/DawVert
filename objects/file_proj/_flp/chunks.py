# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

from external.easybinrw import easybinrw
from functions import xtramath
from io import BytesIO
from objects.data_bytes import dynbytearr
import numpy as np
import struct

flnote_dtype = [
	('pos', np.uint32),
	('flags', np.uint16),
	('rack', np.uint16),
	('dur', np.uint32),
	('key', np.uint16),
	('group', np.uint16),
	('finep', np.uint8),
	('u1', np.uint8),
	('rel', np.uint8),
	('midich', np.uint8),
	('pan', np.uint8),
	('velocity', np.uint8),
	('mod_x', np.uint8),
	('mod_y', np.uint8)
]

flnote_old_dtype = [
	('pos', np.uint32),
	('flags', np.uint16),
	('rack', np.uint16),
	('dur', np.uint32),
	('key', np.uint8),
	('finep', np.uint8),
	('u1', np.uint8),
	('midich', np.uint8),
	('pan', np.uint8),
	('velocity', np.uint8),
	('mod_x', np.uint8),
	('mod_y', np.uint8)
]

flnote_premake = dynbytearr.dynbytearr_premake(flnote_dtype)

class notedata:
	def __init__(self):
		self.data = flnote_premake.create()

	def read_data(self, event_data, version_split):
		if 5>=version_split[0]:
			self.add_old(event_data)
		elif 24>=version_split[0]:
			self.add_24(event_data)

	def add_old(self, event_data):
		datasize = len(event_data)
		self.data.alloc(datasize//20)
		innotes = np.frombuffer(event_data, flnote_old_dtype)

		nd = self.data.data
		nd['used'] = 1
		nd['pos'] = innotes['pos']
		nd['flags'] = innotes['flags']
		nd['rack'] = innotes['rack']
		nd['dur'] = innotes['dur']
		nd['key'] = innotes['key']
		nd['finep'] = innotes['finep']
		nd['u1'] = innotes['u1']
		nd['midich'] = innotes['midich']
		nd['pan'] = innotes['pan']
		nd['velocity'] = innotes['velocity']
		nd['mod_x'] = innotes['mod_x']
		nd['mod_y'] = innotes['mod_y']

	def add_24(self, event_data):
		datasize = len(event_data)
		self.data.alloc(datasize//24)
		innotes = np.frombuffer(event_data, flnote_dtype)
		
		nd = self.data.data
		nd['pos'] = innotes['pos']
		nd['flags'] = innotes['flags']
		nd['rack'] = innotes['rack']
		nd['dur'] = innotes['dur']
		nd['key'] = innotes['key']
		nd['group'] = innotes['group']
		nd['finep'] = innotes['finep']
		nd['u1'] = innotes['u1']
		nd['rel'] = innotes['rel']
		nd['midich'] = innotes['midich']
		nd['pan'] = innotes['pan']
		nd['velocity'] = innotes['velocity']
		nd['mod_x'] = innotes['mod_x']
		nd['mod_y'] = innotes['mod_y']

	def make_old(self):
		out_notes = self.data.get_used()
		usedd = np.zeros(len(out_notes), flnote_old_dtype)
		usedd['pos'] = out_notes['pos']
		usedd['flags'] = out_notes['flags']
		usedd['rack'] = out_notes['rack']
		usedd['dur'] = out_notes['dur']
		usedd['key'] = out_notes['key']
		usedd['finep'] = out_notes['finep']
		usedd['u1'] = out_notes['u1']
		usedd['midich'] = out_notes['midich']
		usedd['pan'] = out_notes['pan']
		usedd['velocity'] = out_notes['velocity']
		usedd['mod_x'] = out_notes['mod_x']
		usedd['mod_y'] = out_notes['mod_y']
		return usedd.tobytes()

flarr_premake = dynbytearr.dynbytearr_premake([
	('real_isaudio', np.uint8),
	('real_patnum', np.int32),
	('real_tracknum', np.int32),

	('position', np.uint32),
	('length', np.uint32),
	('flags', np.uint16),

	('startoffset', np.uint32),
	('endoffset', np.uint32),
	('real_startoffset_audio', float),
	('real_endoffset_audio', float),

	('id', np.uint32),
	('fade_in_dur', float),
	('fade_in_tens', float),
	('fade_out_dur', float),
	('fade_out_tens', float),
	('vol', float),
	('fade_flags', np.uint32),
	('stretch_mul', float),

	('unknown1', np.uint16),
	('unknown2', np.uint32),
	('unknown3', np.uint32),
	('unknown4', np.uint32),
	('unknown5', np.uint32),

	('native_patternbase', np.uint16),
	('native_itemindex', np.uint16),
	('native_trackindex', np.uint32),

	('is_native', np.uint8),

	])

class arrdata:
	def __init__(self, num_tracks):
		self.data = flarr_premake.create()
		self.cursor = self.data.create_cursor()
		self.num_tracks = num_tracks

	def add_data(self, event_data, version_split):
		mode = 0
		if (version_split[0] == 20 and version_split[1] >= 99) or (version_split[0] > 20): 
			mode = 1
		if (version_split[0] >= 25): 
			mode = 2

		datasize = len(event_data)
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_data(event_data)
		while ebrw_readstr.tell() < datasize:
			self.add_part(ebrw_readstr)
			self.add_partdata(ebrw_readstr)
			if mode>0: self.add_partdata_20(ebrw_readstr)
			if mode>1: self.add_partdata_25(ebrw_readstr)

	def add_part(self, ebrw_readstr):
		self.cursor.add()

	def add_partdata(self, ebrw_readstr):
		cursor = self.cursor
		cursor['position'] = ebrw_readstr.int_u32()
		cursor['native_patternbase'] = ebrw_readstr.int_u16()
		cursor['native_itemindex'] = ebrw_readstr.int_u16()
		cursor['length'] = ebrw_readstr.int_u32()
		cursor['native_trackindex'] = ebrw_readstr.int_u32()
		cursor['unknown1'] = ebrw_readstr.int_u16()
		cursor['flags'] = ebrw_readstr.int_u16()
		cursor['unknown2'] = ebrw_readstr.int_u32()
		cursor['startoffset'] = ebrw_readstr.int_u32()
		cursor['endoffset'] = ebrw_readstr.int_u32()

		cursor['vol'] = 1
		cursor['stretch_mul'] = 1

		cursor['is_native'] = 1

	def add_partdata_20(self, ebrw_readstr):
		cursor = self.cursor
		cursor['id'] = ebrw_readstr.int_u32()
		cursor['fade_in_dur'] = ebrw_readstr.float()
		cursor['fade_in_tens'] = ebrw_readstr.float()
		cursor['fade_out_dur'] = ebrw_readstr.float()
		cursor['fade_out_tens'] = ebrw_readstr.float()
		cursor['vol'] = ebrw_readstr.float()
		cursor['fade_flags'] = ebrw_readstr.int_u32()

	def add_partdata_25(self, ebrw_readstr):
		cursor = self.cursor
		cursor['unknown3'] = ebrw_readstr.int_u32()
		cursor['stretch_mul'] = ebrw_readstr.double()
		cursor['unknown4'] = ebrw_readstr.int_u32()
		cursor['unknown5'] = ebrw_readstr.int_u32()

	def postprocess_input(self):
		rd = self.data.data
		rd['real_patnum'] = rd['native_itemindex']
		rd['real_patnum'] -= rd['native_patternbase']
		rd['real_isaudio'] = rd['real_patnum']<0
		rd['real_patnum'] += rd['real_isaudio']*rd['native_patternbase']
		rd['real_tracknum'] = (self.num_tracks-rd['native_trackindex'])-1
		rd['real_startoffset_audio'] = np.frombuffer(rd['startoffset'].tobytes(), np.float32)
		rd['real_endoffset_audio'] = np.frombuffer(rd['endoffset'].tobytes(), np.float32)
		rd['is_native'] = 0
		#print(self.data.get_used())
		#exit()

autoevent_dtype = [
	('pos', np.uint32),
	('param', np.uint32),
	('val', np.uint32),
]

autoevent_premake = dynbytearr.dynbytearr_premake(autoevent_dtype)

class autoeventdata:
	def __init__(self):
		self.data = autoevent_premake.create()

	def read_data(self, event_data):
		datasize = len(event_data)
		self.data.alloc(datasize//12)
		innotes = np.frombuffer(event_data, autoevent_dtype)

		nd = self.data.data
		nd['used'] = 1
		nd['pos'] = innotes['pos']
		nd['param'] = innotes['param']
		nd['val'] = innotes['val']

	def make(self):
		out_evt = self.data.get_used()
		usedd = np.zeros(len(out_evt), autoevent_dtype)
		usedd['pos'] = out_evt['pos']
		usedd['param'] = out_evt['param']
		usedd['val'] = out_evt['val']
		return usedd.tobytes()

class chunk_fxchan:
	def __init__(self):
		self.latency = 0
		self.reversepolarity = False
		self.swap_lr = False
		self.fx_enabled = True
		self.docked_center = True
		self.docked_pos = False
		self.enabled = True
		self.disable_threaded_proc = False
		self.seperator = False
		self.solo = False

	def read(self, event_data):
		if 8<=len(event_data):
			ebrw_readstr = easybinrw.binread()
			ebrw_readstr.load_data(event_data)
			self.latency = ebrw_readstr.float()
			flags = ebrw_readstr.int_u32()
	
			self.reversepolarity = bool(flags&1)
			self.swap_lr = bool(flags&2)
			self.fx_enabled = bool(flags&4)
			self.enabled = bool(flags&8)
			self.disable_threaded_proc = bool(flags&16)
			self.docked_center = bool(flags&64)
			self.docked_pos = bool(flags&128)
			self.seperator = bool(flags&1024)
			self.solo = bool(flags&4096)

	def write(self, versionnum):
		outflags = 0
		outflags += int(self.reversepolarity)*1
		outflags += int(self.swap_lr)*2
		outflags += int(self.fx_enabled)*4
		outflags += int(self.enabled)*8
		outflags += int(self.disable_threaded_proc)*16
		outflags += int(self.docked_center)*64
		#outflags += 32
		outflags += int(self.docked_pos)*128
		outflags += int(self.seperator)*1024
		outflags += int(self.solo)*4096
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.float(self.latency)
		ebrw_writestr.int_u32(outflags)
		if versionnum>=20: ebrw_writestr.int_u32(0)
		return ebrw_writestr.getvalue()

class chunk_env_lfo:
	def __init__(self):
		self.envlfo_flags = 0
		self.el_env_enabled = 0
		self.el_env_predelay = 100
		self.el_env_attack = 20000
		self.el_env_hold = 20000
		self.el_env_decay = 30000
		self.el_env_sustain = 50
		self.el_env_release = 20000
		self.el_env_aomunt = 0
		self.envlfo_lfo_predelay = 100
		self.envlfo_lfo_attack = 20000
		self.envlfo_lfo_amount = 0
		self.envlfo_lfo_speed = 32950
		self.envlfo_lfo_shape = 0
		self.el_env_attack_tension = 0.0
		self.el_env_decay_tension = 0.0
		self.el_env_release_tension = 0.0

	def read(self, event_data):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_data(event_data)
		self.envlfo_flags = ebrw_readstr.int_u32()
		self.el_env_enabled = ebrw_readstr.int_u32()
		self.el_env_predelay = ebrw_readstr.int_u32()
		self.el_env_attack = ebrw_readstr.int_u32()
		self.el_env_hold = ebrw_readstr.int_u32()
		self.el_env_decay = ebrw_readstr.int_u32()
		self.el_env_sustain = ebrw_readstr.int_u32()
		self.el_env_release = ebrw_readstr.int_u32()
		self.el_env_aomunt = ebrw_readstr.int_s32()
		self.envlfo_lfo_predelay = ebrw_readstr.int_u32()
		self.envlfo_lfo_attack = ebrw_readstr.int_u32()
		self.envlfo_lfo_amount = ebrw_readstr.int_u32()
		self.envlfo_lfo_speed = ebrw_readstr.int_u32()
		self.envlfo_lfo_shape = ebrw_readstr.int_u32()
		if ebrw_readstr.remaining(): # over FL 3
			self.el_env_attack_tension = ebrw_readstr.int_s32()/128
			self.el_env_decay_tension = ebrw_readstr.int_s32()/128
			self.el_env_release_tension = ebrw_readstr.int_s32()/128

	def write(self, version_split):
		el_env_attack_tension = int(self.el_env_attack_tension*128)
		el_env_decay_tension = int(self.el_env_decay_tension*128)
		el_env_release_tension = int(self.el_env_release_tension*128)

		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u32(self.envlfo_flags)
		ebrw_writestr.int_u32(self.el_env_enabled)
		ebrw_writestr.int_u32(self.el_env_predelay)
		ebrw_writestr.int_u32(self.el_env_attack)
		ebrw_writestr.int_u32(self.el_env_hold)
		ebrw_writestr.int_u32(self.el_env_decay)
		ebrw_writestr.int_u32(self.el_env_sustain)
		ebrw_writestr.int_u32(self.el_env_release)
		ebrw_writestr.int_s32(self.el_env_aomunt)
		ebrw_writestr.int_u32(self.envlfo_lfo_predelay)
		ebrw_writestr.int_u32(self.envlfo_lfo_attack)
		ebrw_writestr.int_u32(self.envlfo_lfo_amount)
		ebrw_writestr.int_u32(self.envlfo_lfo_speed)
		ebrw_writestr.int_u32(self.envlfo_lfo_shape)
		if version_split[0]>3: # over FL 3
			ebrw_writestr.int_s32(el_env_attack_tension)
			ebrw_writestr.int_s32(el_env_decay_tension)
			ebrw_writestr.int_s32(el_env_release_tension)
		return ebrw_writestr.getvalue()


class chunk_channel_params:
	def __init__(self):
		self.unk0 = 0
		self.addtokey = 0
		self.arpchord = 4294967295
		self.arpdirection = 0
		self.arpgate = 48
		self.arprange = 1
		self.arprepeat = 1
		self.arpslide = 0
		self.arptime = 1024
		self.crossfade = 0
		self.declickmode = 0
		self.delayflags = 0
		self.fix_trim = 1
		self.keyrange_max = 256
		self.keyrange_min = 0
		self.length = 1
		self.main_pitch = 1
		self.normalize = 0
		self.pan = 0
		self.remove_dc = 0
		self.reversepolarity = 0
		self.start = 0
		self.start_offset = 0
		self.stretchingmode = 0
		self.stretchingmultiplier = 0
		self.stretchingpitch = 0
		self.stretchingtime = 0
		self.stretchingformant = 0
		self.timefull_porta = 1
		self.timegate = 193
		self.trim = 0
		self.midi_chan_thru = 0
		self.unkflag1 = 0
		self.ds_tone = 1.0
		self.ds_over = 1.0
		self.ds_noise = 1.0
		self.ds_band = 1.0
		self.ds_time = 1.0

	def read(self, event_data):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_data(event_data)
		self.unk0 = ebrw_readstr.int_s32()
		ebrw_readstr.skip(4) # 00000000
		self.unkflag1 = ebrw_readstr.int_u8()
		self.remove_dc = ebrw_readstr.int_u8()
		self.delayflags = ebrw_readstr.int_u8()
		self.main_pitch = ebrw_readstr.int_u8()
		ebrw_readstr.skip(8) # ffffffff3c000000
		self.ds_tone = ebrw_readstr.float()
		self.ds_over = ebrw_readstr.float()
		self.ds_noise = ebrw_readstr.float()
		self.ds_band = ebrw_readstr.float()
		self.ds_time = ebrw_readstr.float()
		self.arpdirection = ebrw_readstr.int_u32()
		self.arprange = ebrw_readstr.int_u32()
		self.arpchord = ebrw_readstr.int_u32()
		self.arptime = ebrw_readstr.int_u32()
		self.arpgate = ebrw_readstr.int_u32()
		self.arpslide = ebrw_readstr.int_u8()
		ebrw_readstr.skip(1) # 00
		self.timefull_porta = ebrw_readstr.int_u8()
		self.addtokey = ebrw_readstr.int_u8()
		if ebrw_readstr.remaining():
			self.timegate = ebrw_readstr.int_u16()
			ebrw_readstr.skip(2) # 05 00

		if ebrw_readstr.remaining():
			self.keyrange_min = ebrw_readstr.int_u32()
			self.keyrange_max = ebrw_readstr.int_u32()
			ebrw_readstr.skip(4) # 00 00 00 00

		if ebrw_readstr.remaining():
			self.normalize = ebrw_readstr.int_u8()
			self.reversepolarity = ebrw_readstr.int_u8()
			ebrw_readstr.skip(1) # 00
			self.declickmode = ebrw_readstr.int_u8()
			self.crossfade = ebrw_readstr.int_u32()
			self.trim = ebrw_readstr.int_u32()
			self.arprepeat = ebrw_readstr.int_u32()
			self.stretchingtime = ebrw_readstr.int_u32()
			self.stretchingpitch = ebrw_readstr.int_s32()
			self.stretchingmultiplier = ebrw_readstr.int_s32()
			self.stretchingmode = ebrw_readstr.int_s32()

		if ebrw_readstr.remaining():
			self.midi_chan_thru = ebrw_readstr.int_u32()
			ebrw_readstr.skip(4)
			ebrw_readstr.skip(4)
			ebrw_readstr.skip(4)

		if ebrw_readstr.remaining():
			self.start = ebrw_readstr.double()
			self.length = ebrw_readstr.double()
			self.start_offset = ebrw_readstr.double()
			ebrw_readstr.skip(4)
			ebrw_readstr.skip(4)
			self.stretchingformant = (ebrw_readstr.double()-0.5)*24

	def write(self, versionnum):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_s32(self.unk0)
		ebrw_writestr.int_s32(0)
		ebrw_writestr.int_s8(self.unkflag1)
		ebrw_writestr.int_s8(self.remove_dc)
		ebrw_writestr.int_s8(self.delayflags)
		ebrw_writestr.int_s8(self.main_pitch)
		ebrw_writestr.int_s32(-1)
		ebrw_writestr.int_s32(60)
		ebrw_writestr.float(self.ds_tone)
		ebrw_writestr.float(self.ds_over)
		ebrw_writestr.float(self.ds_noise)
		ebrw_writestr.float(self.ds_band)
		ebrw_writestr.float(self.ds_time)

		ebrw_writestr.int_u32(self.arpdirection)
		ebrw_writestr.int_u32(self.arprange)
		ebrw_writestr.int_u32(self.arpchord)
		ebrw_writestr.int_u32(self.arptime)
		ebrw_writestr.int_u32(self.arpgate)
		ebrw_writestr.int_u8(self.arpslide)
		ebrw_writestr.raw(b'\x00')
		ebrw_writestr.int_u8(self.timefull_porta)
		ebrw_writestr.int_u8(self.addtokey)
		ebrw_writestr.int_u16(self.timegate)
		ebrw_writestr.raw(b'\x00\x00')
		if versionnum>=4:
			ebrw_writestr.int_u32(self.keyrange_min)
			ebrw_writestr.int_u32(self.keyrange_max)
			ebrw_writestr.raw(b'\x00\x00\x00\x00')
		if versionnum>=4:
			ebrw_writestr.int_s8(self.normalize)
			ebrw_writestr.int_s8(self.reversepolarity)
			ebrw_writestr.raw(b'\x00')
			ebrw_writestr.int_s8(self.declickmode)
			ebrw_writestr.int_u32(self.crossfade)
			ebrw_writestr.int_u32(self.trim)
			ebrw_writestr.int_u32(self.arprepeat)
			ebrw_writestr.int_u32(self.stretchingtime)
			ebrw_writestr.int_s32(self.stretchingpitch)
			ebrw_writestr.int_s32(self.stretchingmultiplier)
			ebrw_writestr.int_s32(self.stretchingmode)
			ebrw_writestr.int_u32(self.midi_chan_thru)
			ebrw_writestr.int_s32(-2)
			ebrw_writestr.int_s32(-1)
		if versionnum>=12:
			ebrw_writestr.int_s8(0)
		if versionnum>=20:
			ebrw_writestr.int_s32(0)
			ebrw_writestr.double(self.start)
			ebrw_writestr.double(self.length)
			ebrw_writestr.double(self.start_offset)
			ebrw_writestr.raw(b'\xff\xff\xff\xff\x00\x01\x00\x00')
			ebrw_writestr.double((self.stretchingformant/24)+0.5)
		return ebrw_writestr.getvalue()


class chunk_channel_basicparams:
	def __init__(self):
		self.pan = 0
		self.volume = 1
		self.pitch = 0
		self.mod_x = 256
		self.mod_y = 0
		self.mod_type = 0

	def get_pan(self): return ((self.pan/12800)-0.5)*2
	def set_pan(self, v): self.pan = int(xtramath.clamp((v/2)+0.5, 0, 1)*12800)

	def read_filterparams(self, event_data):
		try:
			ebrw_readstr = easybinrw.binread()
			ebrw_readstr.load_data(event_data)
			self.mod_x = ebrw_readstr.int_u32()/256
			self.mod_y = ebrw_readstr.int_u32()/256
			self.mod_type = ebrw_readstr.int_u32()
		except:
			pass

	def read(self, event_data):
		try:
			ebrw_readstr = easybinrw.binread()
			ebrw_readstr.load_data(event_data)
			self.pan = ebrw_readstr.int_u32()
			self.volume = ebrw_readstr.int_u32()/12800
			self.pitch = ebrw_readstr.int_s32()
			self.mod_x = ebrw_readstr.int_u32()/256
			self.mod_y = ebrw_readstr.int_u32()/256
			self.mod_type = ebrw_readstr.int_u32()
		except:
			pass

	def write(self):
		basicp_volume = int(xtramath.clamp(self.volume, 0, 1)*12800)
		basicp_pitch = int(self.pitch)
		basicp_mod_x = int(xtramath.clamp(self.mod_x, 0, 1)*256)
		basicp_mod_y = int(xtramath.clamp(self.mod_y, 0, 1)*256)
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u32(self.pan)
		ebrw_writestr.int_u32(basicp_volume)
		ebrw_writestr.int_s32(basicp_pitch)
		ebrw_writestr.int_u32(basicp_mod_x)
		ebrw_writestr.int_u32(basicp_mod_y)
		ebrw_writestr.int_u32(self.mod_type)
		return ebrw_writestr.getvalue()


class chunk_channel_poly:
	def __init__(self):
		self.max = 0
		self.slide = 500
		self.flags = 0

	def read(self, event_data):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_data(event_data)
		self.max = ebrw_readstr.int_u32()
		self.slide = ebrw_readstr.int_u32()
		self.flags = ebrw_readstr.int_u8()

	def write(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u32(self.max)
		ebrw_writestr.int_u32(self.slide)
		ebrw_writestr.int_u8(self.flags)
		return ebrw_writestr.getvalue()

class chunk_channel_tracking:
	def __init__(self):
		self.mid = 0
		self.pan = 0
		self.mod_x = 0
		self.mod_y = 0

	def read(self, event_data):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_data(event_data)
		self.mid = ebrw_readstr.int_s32()
		self.pan = ebrw_readstr.int_s32()
		self.mod_x = ebrw_readstr.int_s32()
		self.mod_y = ebrw_readstr.int_s32()

	def write(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_s32(self.mid)
		ebrw_writestr.int_s32(self.pan)
		ebrw_writestr.int_s32(self.mod_x)
		ebrw_writestr.int_s32(self.mod_y)
		return ebrw_writestr.getvalue()

class chunk_channel_delay:
	def __init__(self):
		self.feedback = 0
		self.pan = 0
		self.pitch = 0
		self.echoes = 4
		self.time = 3

	def read(self, event_data):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_data(event_data)
		self.feedback = ebrw_readstr.int_u32()/12800
		self.pan = ebrw_readstr.int_u32()/19200
		self.pitch = ebrw_readstr.int_u32()
		self.echoes = ebrw_readstr.int_u32()
		self.time = ebrw_readstr.int_u32()/48

	def write(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u32(int(self.feedback*12800))
		ebrw_writestr.int_u32(int(self.pan*19200))
		ebrw_writestr.int_u32(self.pitch)
		ebrw_writestr.int_u32(self.echoes)
		ebrw_writestr.int_u32(int(self.time*48))
		return ebrw_writestr.getvalue()


class chunk_plugin:
	def __init__(self):
		self.fxnum = 0
		self.slotnum = 0
		self.window_p_x = 0
		self.window_p_y = 0
		self.window_s_x = 0
		self.window_s_y = 0
		self.visible = False
		self.detached = False
		self.generator = False
		self.smart_disable = False
		self.threaded_processing = True
		self.hide_settings = False
		self.minimized = False
		self.unk1 = 2
		self.unk2 = 0
		self.unk3 = 0
		self.unk4 = 0
		self.unk5 = 0
		self.unk6 = 0

	def read(self, event_data):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_data(event_data)
		self.fxnum = ebrw_readstr.int_u32()
		self.slotnum = ebrw_readstr.int_u32()
		self.unk1 = ebrw_readstr.int_s32()
		self.unk2 = ebrw_readstr.int_u32()
		flags = ebrw_readstr.int_u32()
		self.unk3 = ebrw_readstr.int_u32()
		self.unk4 = ebrw_readstr.int_u32()
		self.unk5 = ebrw_readstr.int_u32()
		self.unk6 = ebrw_readstr.int_u32()
		self.window_p_x = ebrw_readstr.int_u32()
		self.window_p_y = ebrw_readstr.int_u32()
		self.window_s_x = ebrw_readstr.int_u32()
		self.window_s_y = ebrw_readstr.int_u32()

		self.visible = bool(flags&1)
		self.detached = bool(flags&4)
		self.generator = bool(flags&16)
		self.smart_disable = bool(flags&32)
		self.threaded_processing = bool(flags&64)
		#flags&128
		self.hide_settings = bool(flags&256)
		self.minimized = bool(flags&512)

		#print(self.unk1, self.unk2, flags, self.unk3, self.unk4, self.unk5, self.unk6)

	def write(self):
		outflags = 0
		outflags += int(self.visible)<<0
		outflags += int(self.detached)<<2
		outflags += int(self.generator)<<4
		outflags += int(self.smart_disable)<<5
		outflags += int(self.threaded_processing)<<6
		#outflags += 128
		outflags += int(self.hide_settings)<<8
		#outflags += int(self.minimized)<<9

		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u32(self.fxnum)
		ebrw_writestr.int_u32(self.slotnum)
		ebrw_writestr.int_s32(self.unk1)
		ebrw_writestr.int_u32(self.unk2)
		ebrw_writestr.int_u32(outflags)
		ebrw_writestr.int_u32(self.unk3)
		ebrw_writestr.int_u32(self.unk4)
		ebrw_writestr.int_u32(self.unk5)
		ebrw_writestr.int_u32(self.unk6)
		ebrw_writestr.int_u32(self.window_p_x)
		ebrw_writestr.int_u32(self.window_p_y)
		ebrw_writestr.int_u32(self.window_s_x)
		ebrw_writestr.int_u32(self.window_s_y)
		return ebrw_writestr.getvalue()