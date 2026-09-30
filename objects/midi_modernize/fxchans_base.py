# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import objects.midi_modernize.ctrls as ctrls
import objects.midi_modernize.gfunc as gfunc
calcval = ctrls.calcval
split_channum = gfunc.split_channum

import numpy as np

fxmaker_idstor = np.dtype([
	('used', np.int8),
	('chanid', np.int32),
	('mem', np.uintp),
	])

fxmaker_port = np.dtype([
	('reverb_idstor', fxmaker_idstor),
	])

fxmaker_channel = np.dtype([
	('fx__reverb__used', np.int8),
	('fx__chorus__used', np.int8),
	('fx__filter__used', np.int8),
	('fx__detune__used', np.int8),
	('fx__tremolo__used', np.int8),
	('fx__phaser__used', np.int8),
	('idstor', fxmaker_idstor),
	('val_cc', np.uint8, 128),
	('val_pressure', np.uint8),
	('val_pitch', np.int32),
	])

class fx_maker_base:
	def __init__(self, num_ports, num_channels):
		import objects.midi_modernize.ctrls as ctrls
		self.num_channels = num_channels
		self.num_ports = num_ports
		self.data_port = np.zeros((num_ports), dtype=fxmaker_port)
		self.data_channel = np.zeros((num_ports, num_channels), dtype=fxmaker_channel)
		self.data_channel['val_cc'][0:128] = ctrls.cc_defualtvals
		self.data_objs = {}

	def add_fx(self, p, c, t):
		d = self.data_channel[p][c]
		if 'reverb' in t: d['fx__reverb__used'] = 1
		if 'tremolo' in t: d['fx__tremolo__used'] = 1
		if 'chorus' in t: d['fx__chorus__used'] = 1
		if 'detune' in t: d['fx__detune__used'] = 1
		if 'phaser' in t: d['fx__phaser__used'] = 1
		if 'filter' in t: d['fx__filter__used'] = 1

	def add_obj(self, idstor, fxnum, objdata):
		idval = id(objdata)
		idstor['mem'] = idval
		idstor['chanid'] = fxnum
		idstor['used'] = 1
		self.data_objs[idval] = objdata

	def get_obj(self, idstor):
		return self.data_objs[idstor['mem']] if idstor['mem'] else None

	def out_params_std(self, p, c, param_obj):
		curd_channel = self.data_channel[p][c]
		chan_cc = curd_channel['val_cc']

		param_obj.add('enabled', True, 'float')
		param_obj.add('vol', calcval(chan_cc[7], 7), 'float')
		if chan_cc[10] != 64: param_obj.add('pan', calcval(chan_cc[10], 10), 'float')

	def out_params_cc(self, p, c, param_obj):
		curd_channel = self.data_channel[p][c]
		chan_cc = curd_channel['val_cc']
		
		param_obj.add('modulation', calcval(chan_cc[1], 1), 'float')
		param_obj.add('breath', calcval(chan_cc[2], 2), 'float')
		param_obj.add('expression', calcval(chan_cc[11], 11), 'float')
		param_obj.add('sustain', calcval(chan_cc[64], 64), 'float')
		param_obj.add('portamento', calcval(chan_cc[65], 65), 'float')
		param_obj.add('sostenuto', calcval(chan_cc[66], 66), 'float')
		param_obj.add('soft_pedal', calcval(chan_cc[67], 67), 'float')
		param_obj.add('legato', calcval(chan_cc[68], 68), 'float')

	def add_chorus(self, p, c, convproj_obj, plugslots):
		curd_channel = self.data_channel[p][c]
		chan_cc = curd_channel['val_cc']
		chorus_pluginid = '_'.join([str(p), str(c), 'chorus'])
		plugin_obj = convproj_obj.plugin__add(chorus_pluginid, 'simple', 'chorus', None)
		plugin_obj.visual.name = 'Chorus'
		plugin_obj.params.add('amount', calcval(chan_cc[93], 93), 'float')
		plugslots.slots_audio.append(chorus_pluginid)

	def add_reverb(self, p, convproj_obj, plugslots):
		reverb_pluginid = str(p)+'_reverb'
		plugin_obj = convproj_obj.plugin__add(reverb_pluginid, 'simple', 'reverb', None)
		plugin_obj.visual.name = 'Reverb'
		plugin_obj.fxdata_add(1, 0.5)
		plugslots.slots_audio.append(reverb_pluginid)

	def add_cc_vals(self, p, c, s, v):
		self.data_channel[p][c]['val_cc'][s] = v

	def get_fxid(self, po, ch):
		return self.data_channel[po][ch]['idstor']['chanid']

	def get_fxobj(self, po, ch):
		return self.get_obj(self.data_channel[po][ch]['idstor'])

	def split_channum(self, chanport):
		return split_channum(chanport, self.num_channels)
