# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects.convproj import placements_base
from objects.convproj import time
from objects.convproj import visual
import copy

class cvpj_placement_video(placements_base.cvpj_placement_base):
	__slots__ = ['videoref','looped']
	def __init__(self, time_ppq):
		super().__init__(time_ppq)
		self.videoref = ''
		self.looped = False

class cvpj_placements_video(placements_base.cvpj_placements_multi_base):
	__slots__ = ['data','videoref','time_ppq']
	def __init__(self, time_ppq):
		super().__init__(time_ppq, cvpj_placement_video)
		self.time_ppq = time_ppq
		self.videoref = ''
		self.data = []

	def __bool__(self):
		return bool(self.data) or bool(self.videoref)