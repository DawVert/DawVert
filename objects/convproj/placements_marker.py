# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects.convproj import time
from objects.convproj import visual
from objects.convproj import placements_base
import copy

class cvpj_placement_marker(placements_base.cvpj_placement_base):
	__slots__ = ['type','data','special']
	def __init__(self, time_ppq):
		super().__init__(time_ppq)
		self.type = ''
		self.data = None
		self.special = False

class cvpj_placements_marker(placements_base.cvpj_placements_multi_base):
	__slots__ = ['data','time_ppq']
	def __init__(self, time_ppq):
		super().__init__(time_ppq, cvpj_placement_marker)

	def add_key(self, key):
		timemarker_obj = self.add()
		timemarker_obj.type = 'key_single'
		timemarker_obj.visual.name = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'][key%12]
		timemarker_obj.data = key
		timemarker_obj.special = True
		return timemarker_obj
