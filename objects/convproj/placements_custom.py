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

	def eq_content(self, pl, prev):
		if prev:
			isvalid_a = pl.custom==prev.custom
			isvalid_b = internal_eq_content(pl, prev)
			return isvalid_a & isvalid_b
		else:
			return False

	def eq_connect(self, pl, prev, loopcompat):
		if prev:
			isvalid_a = self.eq_content(pl, prev)
			isvalid_b = internal_eq_connect(pl, prev, loopcompat)
			return isvalid_a & isvalid_b
		else:
			return False
