# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects.convproj import autopoints
from objects.convproj import visual
from objects.convproj import placements_base
import copy

class cvpj_placements_autopoints(placements_base.cvpj_placements_multi_auto_base):
	__slots__ = ['data','time_ppq','val_type']
	def __init__(self, time_ppq, val_type):
		super().__init__(time_ppq, val_type, cvpj_placement_autopoints)

	def sort(self):
		ta_bsort = {}
		ta_sorted = {}
		new_a = []
		for n in self.data:
			if n.time.position not in ta_bsort: ta_bsort[n.time.position] = []
			ta_bsort[n.time.position].append(n)
		ta_sorted = dict(sorted(ta_bsort.items(), key=lambda item: item[0]))
		for p in ta_sorted:
			for note in ta_sorted[p]: new_a.append(note)
		self.data = new_a

	def remove_cut(self):
		for x in self.data: 
			if x.cut_type == 'cut':
				x.data.edit_trimmove(x.time.get_offset(), x.time.get_dur())
				x.cut_start = 0
				x.cut_type = None

	def remove_unused(self):
		for x in self.data: 
			if x.cut_type == 'cut':
				x.data.edit_trimmove(x.time.get_offset(), x.time.get_dur())
			else:
				x.data.edit_trimmove(0, x.time.get_dur())

	def merge_crop(self, npl_obj, pos, dur):
		for n in npl_obj.data:
			if n.time.get_pos() < dur:
				copy_npl_obj = copy.deepcopy(n)
				copytime_obj = copy_npl_obj.time
				plend = copytime_obj.get_end()
				numval = copytime_obj.get_dur()+min(0, dur-plend)
				copytime_obj.calc_pos_add(pos)
				copytime_obj.set_dur(numval)
				self.data.append(copy_npl_obj)

class cvpj_placement_autopoints:
	__slots__ = ['time','muted','visual','data']

	def __init__(self, time_ppq, val_type):
		self.time = placements_base.cvpj_placement_timing(time_ppq)
		self.data = autopoints.cvpj_autopoints(time_ppq, val_type)
		self.muted = False
		self.visual = visual.cvpj_visual()

	def remove_cut(self):
		if self.time.cut_type == 'cut':
			offset = self.time.get_offset()
			self.data.edit_trimmove(offset, self.time.get_dur()+offset)
		if self.time.cut_type == 'none':
			self.data.edit_trimmove(0, self.time.get_dur())

	def change_seconds(self, is_seconds, bpm):
		self.time.change_seconds(is_seconds, bpm, ppq)