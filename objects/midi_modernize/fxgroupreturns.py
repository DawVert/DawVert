# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import objects.midi_modernize.ctrls as ctrls
import objects.midi_modernize.gfunc as gfunc
import objects.midi_modernize.fxchans_base as fxchans_base
calcval = ctrls.calcval
split_channum = gfunc.split_channum

class fxgroupreturns_maker(fxchans_base.fx_maker_base):
	def __init__(self, num_ports, num_channels):
		super().__init__(num_ports, num_channels)
		self.inst_track_id = []
		self.inst_track_obj = []
		self.autolocstart = {}
		self.chanport_groups = {}

	def generate(self, convproj_obj, used_inst):
		cvpj_groups = convproj_obj.groups
		track_master = convproj_obj.track_master

		for p in range(self.num_ports):
			curd_port = self.data_port[p]

			if np.any(self.data_channel[p]['fx__reverb__used']):
				return_obj = track_master.fx__return__add('%i_reverb' % p)
				self.add_reverb(p, convproj_obj, return_obj.plugslots)

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
				track_obj = self.inst_track_obj[instnum]
				self.autolocstart[chanport] = ['track', self.inst_track_id[instnum]]
				params_obj = track_obj.params
			else: 
				groupid = str(chanport)
				group_obj = cvpj_groups.add(groupid)
				self.autolocstart[chanport] = ['group', groupid]
				params_obj = group_obj.params
			self.out_params_std(portnum, channum, params_obj)
