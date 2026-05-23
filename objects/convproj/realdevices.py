# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.convproj import visual

class cvpj_realdevice_audio:
	def __init__(self):
		self.visual = visual.cvpj_visual()

class cvpj_realdevice_midi:
	def __init__(self):
		self.visual = visual.cvpj_visual()

class cvpj_realdevicelist:
	def __init__(self):
		self.audio_in = {}
		self.audio_out = {}
		self.midi = {}

	def add_audio_in(self, idt):
		outd = self.audio_in[idt] = cvpj_realdevice_audio()
		return outd

	def add_audio_out(self, idt):
		outd = self.audio_out[idt] = cvpj_realdevice_audio()
		return outd

	def add_midi(self, idt):
		outd = self.midi[idt] = cvpj_realdevice_midi()
		return outd