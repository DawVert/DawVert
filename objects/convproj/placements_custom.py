# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects.convproj import time
from objects.convproj import placements_base
import copy

class cvpj_placement_custom(placements_base.cvpj_placement_base):
	__slots__ = ['custom']
	def __init__(self, time_ppq):
		super().__init__(time_ppq)
		self.custom = {}

class cvpj_placements_custom(placements_base.cvpj_placements_multi_base):
	__slots__ = ['custom']
	def __init__(self, time_ppq):
		super().__init__(time_ppq, cvpj_placement_custom)
		self.custom = {}