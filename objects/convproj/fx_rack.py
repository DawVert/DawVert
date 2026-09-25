# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.convproj import params
from objects.convproj import tracks
from objects.convproj import visual
from objects.convproj import sends
import logging

logger_project = logging.getLogger('project')

class cvpj_fxchannel:
	def __init__(self):
		self.visual = visual.cvpj_visual()
		self.visual_ui = visual.cvpj_visual_ui()
		self.params = params.cvpj_paramset()
		self.plugslots = tracks.cvpj_plugslots()
		self.sends = sends.cvpj_sends()
		self.latency_offset = 0

class cvpj_fxrack:
	def __init__(self):
		self.channels = {}

	def __contains__(self, v):
		return self.channels.__contains__(v)

	def __getitem__(self, v):
		return self.channels.__getitem__(v)

	def __iter__(self):
		return self.channels.__iter__()

	def __bool__(self):
		return self.channels.__bool__()

	def items(self):
		return self.channels.items()

	def add(self, fxnum):
		logger_project.info('FX Channel - '+str(fxnum))
		if fxnum not in self.channels: self.channels[fxnum] = cvpj_fxchannel()
		return self.channels[fxnum]

	def get(self, fxnum):
		return self.channels[fxnum] if fxnum in self.channels else None

	def remove(self, fxnum):
		if fxnum in self.channels:
			del self.channels[fxnum]
			return True
		else:
			return False

	def iter(self):
		for num, fxchannel_obj in self.channels.items():
			yield num, fxchannel_obj

	def clear(self):
		self.channels = {}

	def removeloopcrash(self):
		targalredy = {}
		crashfounds = []
		for fx_num, fxchannel_obj in self.channels.items():
			sendtargs = [x[0] for x in fxchannel_obj.sends.iter()]
			for target in sendtargs:
				if target not in targalredy: targalredy[target] = []
				targalredy[target].append(fx_num)
				iscrash = False
				if fx_num in targalredy:
					if target in targalredy[fx_num]: 
						crashfounds.append([target,fx_num])
		for target,fx_num in crashfounds:
			del self.channels[target].sends.data[fx_num]

	def remove_unused(self):
		unused_fx = list(self.channels)
		for trackid, track_obj in self.track_data.items():
			if track_obj.fxrack_channel in unused_fx: unused_fx.remove(track_obj.fxrack_channel)

		for n, d in self.channels.items():
			if d.visual or d.visual_ui or d.plugslots.slots_audio or d.plugslots.slots_mixer:
				if n in unused_fx: unused_fx.remove(n)
			if d.sends.to_master_active:
				if 0 in unused_fx: unused_fx.remove(0)
			for i in list(d.sends.data):
				if i in unused_fx: unused_fx.remove(i)

		for x in unused_fx: del self.channels[x]
		logger_project.info('Removed '+str(len(unused_fx))+' FX Channels')
