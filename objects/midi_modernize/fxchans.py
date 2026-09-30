# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import objects.midi_modernize.automation as automation
import objects.midi_modernize.ctrls as ctrls
import objects.midi_modernize.fxchans_base as fxchans_base
calcval = ctrls.calcval
import numpy as np

class fxchans_maker(fxchans_base.fx_maker_base):
	def __init__(self, num_ports, num_channels):
		super().__init__(num_ports, num_channels)

	def generate(self, convproj_obj):
		fxrack_obj = convproj_obj.fxrack
		
		fxchannel_obj = fxrack_obj.add(0)
		fxchannel_obj.visual.name = "Master"
		fxchannel_obj.visual.color.set_float([0.3, 0.3, 0.3])

		fxnum = 1
		for p in range(self.num_ports):
			curd_port = self.data_port[p]

			for c in range(self.num_channels):
				curd_channel = self.data_channel[p][c]
				fxchannel_obj = fxrack_obj.add(fxnum)
				self.out_params_std(p, c, fxchannel_obj.params)
				self.out_params_cc(p, c, fxchannel_obj.params)
				self.add_obj(curd_channel['idstor'], fxnum, fxchannel_obj)
				fxnum += 1
				if curd_channel['fx__chorus__used']:
					self.add_chorus(p, c, convproj_obj, fxchannel_obj.plugslots)

			if np.any(self.data_channel[p]['fx__reverb__used']):
				reverb_fxchannel_obj = fxrack_obj.add(fxnum)
				reverb_fxchannel_obj.visual.name = 'Reverb'
				reverb_fxchannel_obj.visual_ui.other['docked'] = 1
				self.add_obj(curd_port['reverb_idstor'], fxnum, reverb_fxchannel_obj)
				self.add_reverb(p, convproj_obj, reverb_fxchannel_obj.plugslots)

				for c in range(self.num_channels):
					curd_channel = self.data_channel[p][c]
					chan_cc = curd_channel['val_cc']
					fxchannel_obj = self.get_obj(self.data_channel[p][c]['idstor'])
					if fxchannel_obj: fxchannel_obj.sends.add(fxnum, '_'.join([str(p), str(c), 'reverb']), calcval(chan_cc[91], 91))
				fxnum += 1

	def make_autoloc(self, convproj_obj, autoloc_store):
		for p in range(self.num_ports):
			curd_port = self.data_port[p]
			for c in range(self.num_channels):
				curd_channel = self.data_channel[p][c]
				autoloc_store.setup_fxchan(p, curd_port, c, curd_channel)
