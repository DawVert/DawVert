# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json

class hsm_pattern:
	def __init__(self):
		self.header = []
		self.trackparams = []
		self.notes = []

class hsm_sample:
	def __init__(self):
		self.path = None
		self.retrigger = 0
		self.attack = 0
		self.sustain = 0
		self.decay = 0

class hsm_song:
	def __init__(self):
		self.patterns = [hsm_pattern() for x in range(27)]
		self.samples = [hsm_sample() for x in range(37)]
		self.patternorder = []
		self.title = None
		self.artist = None

	def load_from_file(self, input_file):
		f = open(input_file, 'rb')
		hsmdata = json.load(f)

		vsize = len(hsmdata['data'][0])
		hsize = len(hsmdata['data'])
 
		tracks = []

		rotdata = []
		num = 0
		while True:
			try: 
				rotdata.append([x[num] for x in hsmdata['data']])
				num += 1
			except:
				break

		firstdata = rotdata[0][0]
		self.title = firstdata[0]
		self.artist = firstdata[1]

		for n, x in enumerate(rotdata[0][1:]):
			sample_obj = self.samples[n]
			sample_obj.path = x[0]
			sample_obj.retrigger = x[1]
			sample_obj.attack = x[2]
			sample_obj.sustain = x[3]
			sample_obj.decay = x[4]
			self.patternorder.append(x[10])

		for patnum, pattern_obj in enumerate(self.patterns):
			fadd = patnum*5
			for n, d in enumerate(rotdata[1+fadd:6+fadd]):
				if n==0: pattern_obj.header = d[0][0:4]
				pattern_obj.trackparams.append(d[0][4:])
				pattern_obj.notes.append(d[1:])

		return True