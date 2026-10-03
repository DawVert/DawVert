# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
import logging

class meteor_aux:
	def __init__(self):
		self.volume = 32
		self.enabled = 0
		self.effect = meteor_effect()

class meteor_effect:
	def __init__(self):
		self.typeid = 0
		self.inputlevel = 0
		self.mix = 0
		self.params = {}

	def read(self, xmldata):
		attrib = xmldata.attrib
		for n, v in xmldata.attrib.items():
			if n=='ID': self.typeid = int(v)
			elif n=='InputLevel': self.inputlevel = int(v)
			elif n=='Mix': self.mix = int(v)
			else: self.params[n] = int(v)

class meteor_track:
	def __init__(self):
		self.clips = []
		self.color = 0
		self.volume = 30
		self.auxsend = {}
		self.auxsendenable = {}
		self.effects = {}

class meteor_clip:
	def __init__(self, xmldata=None):
		self.sampleid = 0
		self.flags = 0
		self.ticks = 0
		self.ticklength = 0
		if xmldata is not None: self.read(xmldata)

	def read(self, xmldata):
		attrib = xmldata.attrib
		if 'SampleID' in attrib: self.sampleid = int(attrib['SampleID'])
		if 'Flags' in attrib: self.flags = int(attrib['Flags'])
		if 'Ticks' in attrib: self.ticks = int(attrib['Ticks'])
		if 'TickLength' in attrib: self.ticklength = int(attrib['TickLength'])

# ============================================= main ============================================= 

class meteor_metronome:
	def __init__(self, xmldata=None):
		self.volume = 31
		self.countinbars = 4
		self.metronomeenabled = 0
		self.countinenabled = 0
		self.metrotype = 0
		if xmldata is not None: self.read(xmldata)

	def read(self, xmldata):
		attrib = xmldata.attrib
		if 'Volume' in attrib: self.volume = int(attrib['Volume'])
		if 'CountInBars' in attrib: self.countinbars = int(attrib['CountInBars'])
		if 'MetronomeEnabled' in attrib: self.metronomeenabled = int(attrib['MetronomeEnabled'])
		if 'CountInEnabled' in attrib: self.countinenabled = int(attrib['CountInEnabled'])
		if 'MetroType' in attrib: self.metrotype = int(attrib['MetroType'])

class meteor_info:
	def __init__(self, xmldata=None):
		self.beatsizepixels = 8
		self.tempo = 120
		self.loopstart = 0
		self.loopend = 0
		if xmldata is not None: self.read(xmldata)

	def read(self, xmldata):
		attrib = xmldata.attrib
		if 'BeatSizePixels' in attrib: self.beatsizepixels = int(attrib['BeatSizePixels'])
		if 'Tempo' in attrib: self.tempo = int(attrib['Tempo'])
		if 'LoopStart' in attrib: self.loopstart = int(attrib['LoopStart'])
		if 'LoopEnd' in attrib: self.loopend = int(attrib['LoopEnd'])

class meteor_about:
	def __init__(self, xmldata=None):
		self.author = ''
		self.title = ''
		self.information = ''
		if xmldata is not None: self.read(xmldata)

	def read(self, xmldata):
		attrib = xmldata.attrib
		if 'Author' in attrib: self.author = attrib['Author']
		if 'Title' in attrib: self.title = attrib['Title']
		if 'Information' in attrib: self.information = attrib['Information']

def decode_vals(attribs, letter):
	out = {}
	for n, v in attribs.items():
		if n.startswith(letter):
			tracknum = int(n[1:])-1
			out[tracknum] = int(v)
	return out

class meteor_project:
	def __init__(self):
		self.num_tracks = 12
		self.num_aux_busses = 3
		self.num_samples = 0
		self.project_length = 0
		self.about = meteor_about()
		self.trackinfo = meteor_info()
		self.editinfo = meteor_info()
		self.metronome = meteor_metronome()
		self.tracks = []
		self.aux_returns = []
		self.audiopool_path = None

	def load_from_file(self, input_file):
		x_root = ET.parse(input_file).getroot()
		self.read(x_root)
		return True

	def read_score(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'SampleCnt': self.num_samples = int(v)
			elif n == 'ProjectLength': self.project_length = int(v)

		for x_part in xmldata:
			name = x_part.tag
			if name == 'AudioPool': 
				attrib = x_part.attrib
				if 'Path' in attrib: self.audiopool_path = attrib['Path']
			if name == 'TrackColorIndex': 
				for n, v in decode_vals(x_part.attrib, 'T').items():
					self.tracks[n].color = int(v)
			if name == 'SampleData': 
				for sampdat in x_part:
					tracknum = int(sampdat.attrib['Track'])
					self.tracks[tracknum].clips.append(meteor_clip(sampdat))

	def read_mixer(self, xmldata):
		for x_part in xmldata:
			name = x_part.tag
			if name == 'Volume': 
				for n, v in decode_vals(x_part.attrib, 'V').items():
					self.tracks[n].volume = int(v)
			elif name == 'Pan': 
				for n, v in decode_vals(x_part.attrib, 'P').items():
					self.tracks[n].pan = int(v)
			elif name.startswith('AuxSend'): 
				is_enable = name[7:13]=='Enable'
				startnum = 13 if is_enable else 7
				auxnum = int(name[startnum:])-1
				if is_enable:
					for n, v in decode_vals(x_part.attrib, 'E').items():
						self.tracks[n].auxsendenable[auxnum] = int(v)
				else:
					for n, v in decode_vals(x_part.attrib, 'V').items():
						self.tracks[n].auxsend[auxnum] = int(v)
			elif name == 'AuxReturns': 
				for n, v in decode_vals(x_part.attrib, 'V').items():
					self.aux_returns[n].volume = int(v)
			elif name == 'AuxReturnsEnable': 
				for n, v in decode_vals(x_part.attrib, 'E').items():
					self.aux_returns[n].enabled = int(v)

	def read_auxsendeffects(self, xmldata):
		for x_part in xmldata:
			name = x_part.tag
			if name.startswith('Effect'): 
				fxnum = int(name[6:])-1
				self.aux_returns[fxnum].effect.read(x_part)

	def read_inserteffects(self, xmldata):
		for x_part in xmldata:
			name = x_part.tag
			if name.startswith('Track'): 
				tracknum = int(name[5:])-1

				for x_inpart in x_part:
					inname = x_inpart.tag
					if inname.startswith('Effect'): 
						fxnum = int(inname[6:])-1
						effect = meteor_effect()
						effect.read(x_inpart)
						self.tracks[tracknum].effects[fxnum] = effect

	def read(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'Tracks': 
				self.num_tracks = int(v)
				self.tracks = [meteor_track() for _ in range(self.num_tracks)]
			elif n == 'AuxBusses': 
				self.num_aux_busses = int(v)
				self.aux_returns = [meteor_aux() for _ in range(self.num_aux_busses)]

		for x_part in xmldata:
			name = x_part.tag
			if name == 'About': self.about.read(x_part)
			elif name == 'TrackInfo': self.trackinfo.read(x_part)
			elif name == 'EditInfo': self.editinfo.read(x_part)
			elif name == 'Metronome': self.metronome.read(x_part)
			elif name == 'Score': self.read_score(x_part)
			elif name == 'Mixer': self.read_mixer(x_part)
			elif name == 'AuxSendEffects': self.read_auxsendeffects(x_part)
			elif name == 'InsertEffects': self.read_inserteffects(x_part)
