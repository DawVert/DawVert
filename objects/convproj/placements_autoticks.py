# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects.convproj import autoticks
from objects.convproj import visual
from objects.convproj import time
from objects.convproj import placements_base

class cvpj_placements_autoticks(placements_base.cvpj_placements_multi_auto_base):
	__slots__ = ['data','time_ppq','val_type']
	def __init__(self, time_ppq, val_type):
		super().__init__(time_ppq, cvpj_placement_autoticks)

	def sort(self):
		self.data = placements_base.internal_sort(self.data)

	def remove_cut(self):
		for x in self.data: 
			if x.cut_type == 'cut':
				x.data.edit_trimmove(x.time.get_offset(), x.time.get_dur())
				x.cut_start = 0
				x.cut_type = None

class cvpj_placement_autoticks:
	__slots__ = ['time','muted','visual','data']

	def __init__(self, time_ppq, val_type):
		self.time = placements_base.cvpj_placement_timing(time_ppq)
		self.data = autoticks.cvpj_autoticks(time_ppq, val_type)
		self.muted = False
		self.visual = visual.cvpj_visual()
