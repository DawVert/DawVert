# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

from functions import xtramath
from external.easybinrw import easybinrw
from objects.file_proj._flp import plugin
import struct

class flp_env_lfo:
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
		self.el_env_attack_tension = ebrw_readstr.int_s32()/128
		self.el_env_decay_tension = ebrw_readstr.int_s32()/128
		self.el_env_release_tension = ebrw_readstr.int_s32()/128

	def write(self):
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
		ebrw_writestr.int_s32(el_env_attack_tension)
		ebrw_writestr.int_s32(el_env_decay_tension)
		ebrw_writestr.int_s32(el_env_release_tension)
		return ebrw_writestr.getvalue()

class flp_channel_params:
	def __init__(self):
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
		self.timegate = 1447
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
		ebrw_readstr.skip(8) # ffffffff 00000000
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
		self.timegate = ebrw_readstr.int_u16()
		ebrw_readstr.skip(2) # 05 00
		self.keyrange_min = ebrw_readstr.int_u32()
		self.keyrange_max = ebrw_readstr.int_u32()
		ebrw_readstr.skip(4) # 00 00 00 00
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

		if ebrw_readstr.remaining(): self.midi_chan_thru = ebrw_readstr.int_u32()
		if ebrw_readstr.remaining(): ebrw_readstr.skip(4)
		if ebrw_readstr.remaining(): ebrw_readstr.skip(4)
		if ebrw_readstr.remaining(): ebrw_readstr.skip(4)
		if ebrw_readstr.remaining(): self.start = ebrw_readstr.double()
		if ebrw_readstr.remaining(): self.length = ebrw_readstr.double()
		if ebrw_readstr.remaining(): self.start_offset = ebrw_readstr.double()
		if ebrw_readstr.remaining(): ebrw_readstr.skip(4)
		if ebrw_readstr.remaining(): ebrw_readstr.skip(4)
		if ebrw_readstr.remaining(): self.stretchingformant = (ebrw_readstr.double()-0.5)*24

	def write(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_s32(-1)
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
		ebrw_writestr.int_s8(self.arpslide)
		ebrw_writestr.raw(b'\x00')
		ebrw_writestr.int_s8(self.timefull_porta)
		ebrw_writestr.int_s8(self.addtokey)
		ebrw_writestr.int_s16(self.timegate)
		ebrw_writestr.raw(b'\x00\x00')
		ebrw_writestr.int_u32(self.keyrange_min)
		ebrw_writestr.int_u32(self.keyrange_max)
		ebrw_writestr.raw(b'\x00\x00\x00\x00')
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
		ebrw_writestr.int_s32(0)
		ebrw_writestr.double(self.start)
		ebrw_writestr.double(self.length)
		ebrw_writestr.double(self.start_offset)
		ebrw_writestr.raw(b'\xff\xff\xff\xff\x00\x01\x00\x00')
		ebrw_writestr.double((self.stretchingformant/24)+0.5)
		return ebrw_writestr.getvalue()

class flp_channel_basicparams:
	def __init__(self):
		self.pan = 0
		self.volume = 1
		self.pitch = 0
		self.mod_x = 256
		self.mod_y = 0
		self.mod_type = 0

	def read(self, event_data):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_data(event_data)
		self.pan = ((ebrw_readstr.int_u32()/12800)-0.5)*2
		self.volume = (ebrw_readstr.int_u32()/12800)
		self.pitch = ebrw_readstr.int_s32()
		self.mod_x = ebrw_readstr.int_u32()/256
		self.mod_y = ebrw_readstr.int_u32()/256
		self.mod_type = ebrw_readstr.int_u32()

	def write(self):
		basicp_pan = int(xtramath.clamp((self.pan/2)+0.5, 0, 1)*12800)
		basicp_volume = int(xtramath.clamp(self.volume, 0, 1)*12800)
		basicp_pitch = int(self.pitch)
		basicp_mod_x = int(xtramath.clamp(self.mod_x, 0, 1)*256)
		basicp_mod_y = int(xtramath.clamp(self.mod_y, 0, 1)*256)
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u32(basicp_pan)
		ebrw_writestr.int_u32(basicp_volume)
		ebrw_writestr.int_s32(basicp_pitch)
		ebrw_writestr.int_u32(basicp_mod_x)
		ebrw_writestr.int_u32(basicp_mod_y)
		ebrw_writestr.int_u32(self.mod_type)
		return ebrw_writestr.getvalue()

class flp_channel_poly:
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

class flp_channel_tracking:
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

class flp_channel_delay:
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

class flp_channel:
	def __init__(self):
		self.type = 0
		self.name = None
		self.icon = None
		self.color = None
		self.plugin = plugin.flp_plugin()
		self.enabled = 1
		self.env_lfo = []
		self.attack = 0
		self.cutcutby = 0
		self.cutoff = 1024
		self.decay = 0
		self.delay = flp_channel_delay()
		#self.delay = b'\x00\x00\x00\x00\x00\x19\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x90\x00\x00\x00'
		self.delayreso = 8388736
		self.fxflags = 0
		self.fx = 128
		self.fx3 = 256
		self.fxchannel = 0
		self.fxsine = 8388608
		self.layerflags = 0
		self.looptype = 0
		self.middlenote = 60
		self.ofslevels = b'\x00\x00\x00\x00\x002\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
		self.preamp = 0
		self.resonance = 0
		self.reverb = 65536
		self.sampleflags = 10
		self.shiftdelay = 0
		self.stdel = 2048
		self.basicparams = flp_channel_basicparams()
		self.poly = flp_channel_poly()
		self.params = flp_channel_params()
		self.cutcutby = 0
		self.layerflags = 0
		self.filtergroup = 0
		self.samplefilename = None
		self.tracking = []
		self.layer_chans = []
		self.autopoints = None
