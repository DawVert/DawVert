# SPDX-FileCopyrightText: 2026 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json

class darwin_note:
	def __init__(self, indict=None):
		self.durationTicks = 0
		self.pitch = 60
		self.startTick = 0
		self.velocity = 100
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'durationTicks' in indict: self.durationTicks = indict['durationTicks']
		if 'pitch' in indict: self.pitch = indict['pitch']
		if 'startTick' in indict: self.startTick = indict['startTick']
		if 'velocity' in indict: self.velocity = indict['velocity']

	def write(self):
		outdict = {}
		outdict['durationTicks'] = self.durationTicks
		outdict['pitch'] = self.pitch
		outdict['startTick'] = self.startTick
		outdict['velocity'] = self.velocity
		return outdict

class darwin_clip:
	def __init__(self, indict=None):
		self.clipType = "midi"
		self.durationTicks = 128
		self.notes = []
		self.startTick = 0
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'clipType' in indict: self.clipType = indict['clipType']
		if 'durationTicks' in indict: self.durationTicks = indict['durationTicks']
		if 'startTick' in indict: self.startTick = indict['startTick']
		if 'notes' in indict: 
			for t in indict['notes']:
				note_obj = darwin_note()
				note_obj.read(t)
				self.notes.append(note_obj)

	def write(self):
		outdict = {}
		outdict['clipType'] = self.clipType
		outdict['durationTicks'] = self.durationTicks
		outdict['notes'] = [x.write() for x in self.notes]
		outdict['startTick'] = self.startTick
		return outdict

class darwin_track:
	def __init__(self, indict=None):
		self.clips = []
		self.color = "#888888"
		self.folderExpanded = True
		self.id = 0
		self.instrumentName = ""
		self.isFolder = False
		self.muted = False
		self.name = "Track"
		self.pan = 0
		self.parentFolderId = -1
		self.solo = False
		self.timingOffsetMs = 0
		self.visible = True
		self.volume = 1
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'clips' in indict: 
			for t in indict['clips']:
				clip_obj = darwin_clip()
				clip_obj.read(t)
				self.clips.append(clip_obj)
		if 'color' in indict: self.color = indict['color']
		if 'folderExpanded' in indict: self.folderExpanded = indict['folderExpanded']
		if 'id' in indict: self.id = indict['id']
		if 'instrumentName' in indict: self.instrumentName = indict['instrumentName']
		if 'isFolder' in indict: self.isFolder = indict['isFolder']
		if 'muted' in indict: self.muted = indict['muted']
		if 'name' in indict: self.name = indict['name']
		if 'pan' in indict: self.pan = indict['pan']
		if 'parentFolderId' in indict: self.parentFolderId = indict['parentFolderId']
		if 'solo' in indict: self.solo = indict['solo']
		if 'timingOffsetMs' in indict: self.timingOffsetMs = indict['timingOffsetMs']
		if 'visible' in indict: self.visible = indict['visible']
		if 'volume' in indict: self.volume = indict['volume']

	def write(self):
		outdict = {}
		outdict['clips'] = [x.write() for x in self.clips]
		outdict['color'] = self.color
		outdict['folderExpanded'] = self.folderExpanded
		outdict['id'] = self.id
		outdict['instrumentName'] = self.instrumentName
		outdict['isFolder'] = self.isFolder
		outdict['muted'] = self.muted
		outdict['name'] = self.name
		outdict['pan'] = self.pan
		outdict['parentFolderId'] = self.parentFolderId
		outdict['solo'] = self.solo
		outdict['timingOffsetMs'] = self.timingOffsetMs
		outdict['visible'] = self.visible
		outdict['volume'] = self.volume
		return outdict

class darwin_project:
	def __init__(self, indict=None):
		self.bpm = 128
		self.formatVersion = 1
		self.masterTrack = darwin_track()
		self.name = ""
		self.tracks = []

	def load_from_file(self, input_file):
		f = open(input_file, 'rb')
		projectdata = json.load(f)
		self.read(projectdata)
		return True
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'bpm' in indict: self.bpm = indict['bpm']
		if 'formatVersion' in indict: self.formatVersion = indict['formatVersion']
		if 'name' in indict: self.name = indict['name']
		if 'masterTrack' in indict: self.masterTrack.read(indict['masterTrack'])
		if 'tracks' in indict: 
			for t in indict['tracks']:
				track_obj = darwin_track()
				track_obj.read(t)
				self.tracks.append(track_obj)

	def write(self):
		outdict = {}
		outdict['bpm'] = self.bpm
		outdict['formatVersion'] = self.formatVersion
		outdict['name'] = self.name
		outdict['masterTrack'] = self.masterTrack.write()
		outdict['tracks'] = [x.write() for x in self.tracks]
		return outdict

	def save_to_file(self, output_file):
		f = open(output_file, 'w')
		f.write(json.dumps(self.write(), indent = 2))