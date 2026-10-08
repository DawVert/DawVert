# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
import objects.midi_modernize.ctrls as ctrls
import objects.midi_modernize.gfunc as gfunc
import objects.midi_modernize.fxchans_base as fxchans_base
calcval = ctrls.calcval
split_channum = gfunc.split_channum

class fxgroupreturns_maker(fxchans_base.fx_maker_base):
	__slots__ = ['inst_track_id','inst_track_obj','autolocstart','chanport_groups']
	
	def __init__(self, num_ports, num_channels):
		super().__init__(num_ports, num_channels)
		self.inst_track_id = []
		self.inst_track_obj = []
		self.autolocstart = {}
		self.chanport_groups = {}

	def generate(self, convproj_obj, used_inst, visstore_data):
		cvpj_groups = convproj_obj.groups
		track_master = convproj_obj.track_master

		for p in range(self.num_ports):
			if np.any(self.data_channel[p]['fx__reverb__used']):
				returnid = '%i_reverb' % p
				return_obj = track_master.fx__return__add(returnid)
				return_obj.visual.name = 'Reverb'
				self.add_reverb(p, convproj_obj, return_obj.plugslots)
				self.add_obj_fx_chan(p, 'reverb', ['return', returnid], return_obj)

		for instnum, inst in enumerate(used_inst):
			chanport = int(inst['chanport'])
			portnum, channum = self.split_channum(chanport)
			track_obj = self.inst_track_obj[instnum]
			if chanport not in self.chanport_groups: self.chanport_groups[chanport] = []
			self.chanport_groups[chanport].append(instnum)
			self.out_params_cc(portnum, channum, track_obj.params)

		for chanport, insts in self.chanport_groups.items():
			portnum, channum = self.split_channum(chanport)
			if len(insts)==1: 
				trackid = self.inst_track_id[insts[0]]
				track_obj = self.inst_track_obj[insts[0]]
				self.autolocstart[chanport] = ['track', trackid]
				params_obj = track_obj.params
				self.add_obj_chan(portnum, channum, ['track', trackid], track_obj)
			else: 
				groupid = str(chanport)
				group_obj = cvpj_groups.add(groupid)
				self.autolocstart[chanport] = ['group', groupid]
				params_obj = group_obj.params
				self.add_obj_chan(portnum, channum, ['group', groupid], group_obj)
				visstore_data.vis_fxchan[portnum][channum].to_cvpj_visual(group_obj.visual)
			self.out_params_std(portnum, channum, params_obj)

		for p in range(self.num_ports):
			if np.any(self.data_channel[p]['fx__reverb__used']):
				for c in range(self.num_channels):
					curd_channel = self.data_channel[p][c]
					assoc_d = self.get_obj_chan(p, c)
					fxchannel_obj = assoc_d.object
					returnid = '%i_reverb' % p
					chan_cc = curd_channel['val_cc']
					if fxchannel_obj: 
						fxchannel_obj.sends.add(returnid, '_'.join([str(p), str(c), 'reverb']), calcval(chan_cc[91], 91))

	def make_autoloc(self, convproj_obj, autoloc_store):
		for p in range(self.num_ports):
			for c in range(self.num_channels):
				autoloc_store.setup_groupreturn(p, c, self)