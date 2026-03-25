# SPDX-FileCopyrightText: 2026 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json

class darwin_note:
	def __init__(self):
		self.durationTicks = 0
		self.pitch = 60
		self.startTick = 0
		self.velocity = 100

	def read(self, trackdata):
		if 'durationTicks' in trackdata: self.durationTicks = trackdata['durationTicks']
		if 'pitch' in trackdata: self.pitch = trackdata['pitch']
		if 'startTick' in trackdata: self.startTick = trackdata['startTick']
		if 'velocity' in trackdata: self.velocity = trackdata['velocity']

	def write(self):
		out = {}
		out['durationTicks'] = self.durationTicks
		out['pitch'] = self.pitch
		out['startTick'] = self.startTick
		out['velocity'] = self.velocity
		return out

class darwin_clip:
	def __init__(self):
		self.clipType = "midi"
		self.durationTicks = 128
		self.notes = []
		self.startTick = 0

	def read(self, trackdata):
		if 'clipType' in trackdata: self.clipType = trackdata['clipType']
		if 'durationTicks' in trackdata: self.durationTicks = trackdata['durationTicks']
		if 'startTick' in trackdata: self.startTick = trackdata['startTick']
		if 'notes' in trackdata: 
			for t in trackdata['notes']:
				note_obj = darwin_note()
				note_obj.read(t)
				self.notes.append(note_obj)

	def write(self):
		out = {}
		out['clipType'] = self.clipType
		out['durationTicks'] = self.durationTicks
		out['notes'] = [x.write() for x in self.notes]
		out['startTick'] = self.startTick
		return out

class darwin_track:
	def __init__(self):
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

	def read(self, trackdata):
		if 'clips' in trackdata: 
			for t in trackdata['clips']:
				clip_obj = darwin_clip()
				clip_obj.read(t)
				self.clips.append(clip_obj)
		if 'color' in trackdata: self.color = trackdata['color']
		if 'folderExpanded' in trackdata: self.folderExpanded = trackdata['folderExpanded']
		if 'id' in trackdata: self.id = trackdata['id']
		if 'instrumentName' in trackdata: self.instrumentName = trackdata['instrumentName']
		if 'isFolder' in trackdata: self.isFolder = trackdata['isFolder']
		if 'muted' in trackdata: self.muted = trackdata['muted']
		if 'name' in trackdata: self.name = trackdata['name']
		if 'pan' in trackdata: self.pan = trackdata['pan']
		if 'parentFolderId' in trackdata: self.parentFolderId = trackdata['parentFolderId']
		if 'solo' in trackdata: self.solo = trackdata['solo']
		if 'timingOffsetMs' in trackdata: self.timingOffsetMs = trackdata['timingOffsetMs']
		if 'visible' in trackdata: self.visible = trackdata['visible']
		if 'volume' in trackdata: self.volume = trackdata['volume']

	def write(self):
		out = {}
		out['clips'] = [x.write() for x in self.clips]
		out['color'] = self.color
		out['folderExpanded'] = self.folderExpanded
		out['id'] = self.id
		out['instrumentName'] = self.instrumentName
		out['isFolder'] = self.isFolder
		out['muted'] = self.muted
		out['name'] = self.name
		out['pan'] = self.pan
		out['parentFolderId'] = self.parentFolderId
		out['solo'] = self.solo
		out['timingOffsetMs'] = self.timingOffsetMs
		out['visible'] = self.visible
		out['volume'] = self.volume
		return out

class darwin_project:
	def __init__(self):
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

	def read(self, projectdata):
		if 'bpm' in projectdata: self.bpm = projectdata['bpm']
		if 'formatVersion' in projectdata: self.formatVersion = projectdata['formatVersion']
		if 'name' in projectdata: self.name = projectdata['name']
		if 'masterTrack' in projectdata: self.masterTrack.read(projectdata['masterTrack'])
		if 'tracks' in projectdata: 
			for t in projectdata['tracks']:
				track_obj = darwin_track()
				track_obj.read(t)
				self.tracks.append(track_obj)

	def write(self):
		out = {}
		out['bpm'] = self.bpm
		out['formatVersion'] = self.formatVersion
		out['name'] = self.name
		out['masterTrack'] = self.masterTrack.write()
		out['tracks'] = [x.write() for x in self.tracks]
		return out

	def save_to_file(self, output_file):
		f = open(output_file, 'w')
		f.write(json.dumps(self.write(), indent = 2))