# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import objects.midi_modernize.ctrls as ctrls
import objects.midi_modernize.gfunc as gfunc
calcval = ctrls.calcval
split_channum = gfunc.split_channum

import numpy as np

#fxmaker_port = np.dtype([
#	('reverb_idstor', fxmaker_idstor),
#	])

fxmaker_channel = np.dtype([
	('fx__reverb__used', np.int8),
	('fx__chorus__used', np.int8),
	('fx__filter__used', np.int8),
	('fx__detune__used', np.int8),
	('fx__tremolo__used', np.int8),
	('fx__phaser__used', np.int8),
	('val_cc', np.uint8, 128),
	('val_pressure', np.uint8),
	('val_pitch', np.int32),
	])

class midicvpj_fx_assoc:
	def __init__(self):
		self.used = False
		self.object = None
		self.chanid = None

class fx_maker_base:
	def __init__(self, num_ports, num_channels):
		import objects.midi_modernize.ctrls as ctrls
		self.num_channels = num_channels
		self.num_ports = num_ports
		#self.data_port = np.zeros((num_ports), dtype=fxmaker_port)
		self.data_channel = np.zeros((num_ports, num_channels), dtype=fxmaker_channel)
		self.data_channel['val_cc'][0:128] = ctrls.cc_defualtvals

		self.cvpj_assoc = [[midicvpj_fx_assoc() for c in range(num_channels)] for p in range(num_ports)]
		self.cvpj_fx_assoc = [{} for p in range(num_ports)]

	def add_fx(self, p, c, t):
		d = self.data_channel[p][c]
		if 'reverb' in t: d['fx__reverb__used'] = 1
		if 'tremolo' in t: d['fx__tremolo__used'] = 1
		if 'chorus' in t: d['fx__chorus__used'] = 1
		if 'detune' in t: d['fx__detune__used'] = 1
		if 'phaser' in t: d['fx__phaser__used'] = 1
		if 'filter' in t: d['fx__filter__used'] = 1

	def add_obj_chan(self, p, c, fxnum, objdata):
		assoc_obj = self.cvpj_assoc[p][c]
		assoc_obj.used = True
		assoc_obj.object = objdata
		assoc_obj.chanid = fxnum

	def get_obj_chan(self, p, c):
		return self.cvpj_assoc[p][c]

	def add_obj_fx_chan(self, p, fxtype, fxnum, objdata):
		assoc_d = self.cvpj_fx_assoc[p]
		if fxtype not in assoc_d: assoc_d[fxtype] = midicvpj_fx_assoc()
		assoc_obj = assoc_d[fxtype]
		assoc_obj.used = True
		assoc_obj.object = objdata
		assoc_obj.chanid = fxnum

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
		return self.cvpj_assoc[po][ch]

	def split_channum(self, chanport):
		return split_channum(chanport, self.num_channels)
