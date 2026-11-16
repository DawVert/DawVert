# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET

def getbool(v): return v=='true'

class easyamixr_EAM1_VideoInfo:
	__slots__ = ['BeatN','Value','ID','Selected']

	def __init__(self, xmldata=None):
		self.wVideoFile = ''
		self.wTotalSnapshots = 9
		self.wSnapshotsIntervalSecs = 2
		self.wSnapshotCurrentRatio = 0.75
		self.SnapshotPrefix = 'AAAA-'
		if xmldata is not None: self.read(xmldata)

	def read(self, xmldata):
		for xpart in xmldata:
			tagname = xpart.tag
			if tagname == 'wVideoFile': self.wVideoFile = xpart.text
			elif tagname == 'wTotalSnapshots': self.wTotalSnapshots = int(xpart.text)
			elif tagname == 'wSnapshotsIntervalSecs': self.wSnapshotsIntervalSecs = int(xpart.text)
			elif tagname == 'wSnapshotCurrentRatio': self.wSnapshotCurrentRatio = float(xpart.text)
			elif tagname == 'SnapshotPrefix': self.SnapshotPrefix = xpart.text

class easyamixr_EAM1_AutomationPointClass:
	__slots__ = ['BeatN','Value','ID','Selected']

	def __init__(self, xmldata=None):
		self.BeatN = 0
		self.Value = 0
		self.ID = 0
		self.Selected = False
		if xmldata is not None: self.read(xmldata)

	def read(self, xmldata):
		for xpart in xmldata:
			tagname = xpart.tag
			if tagname == 'BeatN': self.BeatN = float(xpart.text)
			elif tagname == 'Value': self.Value = float(xpart.text)
			elif tagname == 'ID': self.ID = int(xpart.text)
			elif tagname == 'Selected': self.Selected = getbool(xpart.text)

class easyamixr_EAM1_AutomationClass:
	__slots__ = [
		'ID',
		'DestinationID',
		'AutomationType',
		'OwnerISAudioChannel',
		'ParameterIndex',
		'MidiControllerNumber',
		'HTMLColor',
		'Visible',
		'DisplayMode',
		'Points'
	]

	def __init__(self, xmldata=None):
		self.ID = 0
		self.DestinationID = 0
		self.AutomationType = 'Volume'
		self.OwnerISAudioChannel = True
		self.ParameterIndex = 0
		self.MidiControllerNumber = 0
		self.HTMLColor = ''
		self.Visible = True
		self.DisplayMode = 'Lineal'
		self.Points = []
		if xmldata is not None: self.read(xmldata)

	def read(self, xmldata):
		for xpart in xmldata:
			tagname = xpart.tag
			if tagname == 'ID': self.ID = int(xpart.text)
			elif tagname == 'DestinationID': self.DestinationID = int(xpart.text)
			elif tagname == 'AutomationType': self.AutomationType = xpart.text
			elif tagname == 'OwnerISAudioChannel': self.OwnerISAudioChannel = getbool(xpart.text)
			elif tagname == 'ParameterIndex': self.ParameterIndex = int(xpart.text)
			elif tagname == 'MidiControllerNumber': self.MidiControllerNumber = int(xpart.text)
			elif tagname == 'HTMLColor': self.HTMLColor = xpart.text
			elif tagname == 'Visible': self.Visible = getbool(xpart.text)
			elif tagname == 'DisplayMode': self.DisplayMode = xpart.text
			elif tagname == 'Points':
				for t in xpart:
					if t.tag == 'AutomationPointClass':
						self.Points.append(easyamixr_EAM1_AutomationPointClass(t))

class easyamixr_EAM1_WaveEventClass:
	def __init__(self, xmldata=None):
		self.ID = 0
		self.FilePath = ''
		self.StartSampleMS = 0
		self.EndSampleMS = 0
		self.Title = ''
		self.BeatPos = 0
		self.FadeIN_LengthBeats = 0
		self.FadeOUT_LengthBeats = 0
		self.Muted = False
		self.Gain = 0
		if xmldata is not None: self.read(xmldata)

	def read(self, xmldata):
		for xpart in xmldata:
			tagname = xpart.tag
			if tagname == 'ID': self.ID = int(xpart.text)
			elif tagname == 'FilePath': self.FilePath = xpart.text
			elif tagname == 'StartSampleMS': self.StartSampleMS = float(xpart.text)
			elif tagname == 'EndSampleMS': self.EndSampleMS = float(xpart.text)
			elif tagname == 'Title': self.Title = xpart.text
			elif tagname == 'BeatPos': self.BeatPos = float(xpart.text)
			elif tagname == 'FadeIN_LengthBeats': self.FadeIN_LengthBeats = float(xpart.text)
			elif tagname == 'FadeOUT_LengthBeats': self.FadeOUT_LengthBeats = float(xpart.text)
			elif tagname == 'Muted': self.Muted = getbool(xpart.text)
			elif tagname == 'Gain': self.Gain = float(xpart.text)

class easyamixr_EAM1_FxInfo:
	def __init__(self, xmldata=None):
		self.bypass = False
		self.dllPath = ''
		self.displayName = ''
		self.effectVersion = 1
		self.effectType = 0
		self.ID = 0
		if xmldata is not None: self.read(xmldata)

	def read(self, xmldata):
		for xpart in xmldata:
			tagname = xpart.tag
			if tagname == 'bypass': self.bypass = getbool(xpart.text)
			elif tagname == 'dllPath': self.dllPath = xpart.text
			elif tagname == 'displayName': self.displayName = xpart.text
			elif tagname == 'effectVersion': self.effectVersion = int(xpart.text)
			elif tagname == 'effectType': self.effectType = int(xpart.text)
			elif tagname == 'ID': self.ID = int(xpart.text)

class easyamixr_EAM1_AudioChannel:
	def __init__(self, xmldata=None):
		self.ID = 0
		self.Name = ''
		self.OutputID = 0
		self.InputID = -1
		self.OutputName = ''
		self.InputName = ''
		self.Type = ''
		self.Pan = 0.0
		self.Trim = 0.0
		self.Volume = 0.0
		self.VoiceRemoval = 0
		self.ChannelHeight = 100
		self.EventsColorRGB = None
		self.TitleColorIndex = 1
		self.Muted = False
		self.Solo = False
		self.Record = False
		self.MonitorInput = False
		self.IsMusicChannel = True
		self.IsVideoAudio = False
		self.FXList = []
		self.EventsList = []
		self.AutomationList = []
		if xmldata is not None: self.read(xmldata)

	def read(self, xmldata):
		for xpart in xmldata:
			tagname = xpart.tag
			if tagname == 'ID': self.ID = int(xpart.text)
			elif tagname == 'Name': self.Name = xpart.text
			elif tagname == 'OutputID': self.OutputID = int(xpart.text)
			elif tagname == 'InputID': self.InputID = int(xpart.text)
			elif tagname == 'OutputName': self.OutputName = xpart.text
			elif tagname == 'InputName': self.InputName = xpart.text
			elif tagname == 'Type': self.Type = xpart.text
			elif tagname == 'Pan': self.Pan = float(xpart.text)
			elif tagname == 'Trim': self.Trim = float(xpart.text)
			elif tagname == 'Volume': self.Volume = float(xpart.text)
			elif tagname == 'VoiceRemoval': self.VoiceRemoval = int(xpart.text)
			elif tagname == 'ChannelHeight': self.ChannelHeight = int(xpart.text)
			elif tagname == 'EventsColorRGB': self.EventsColorRGB = int(xpart.text)
			elif tagname == 'TitleColorIndex': self.TitleColorIndex = int(xpart.text)
			elif tagname == 'Muted': self.Muted = getbool(xpart.text)
			elif tagname == 'Solo': self.Solo = getbool(xpart.text)
			elif tagname == 'Record': self.Record = getbool(xpart.text)
			elif tagname == 'MonitorInput': self.MonitorInput = getbool(xpart.text)
			elif tagname == 'IsMusicChannel': self.IsMusicChannel = getbool(xpart.text)
			elif tagname == 'IsVideoAudio': self.IsVideoAudio = getbool(xpart.text)
			elif tagname == 'FXList':
				for t in xpart:
					if t.tag == 'FxInfo':
						self.FXList.append(easyamixr_EAM1_FxInfo(t))
			elif tagname == 'EventsList':
				for t in xpart:
					if t.tag == 'WaveEventClass':
						self.EventsList.append(easyamixr_EAM1_WaveEventClass(t))
			elif tagname == 'AutomationList':
				for t in xpart:
					if t.tag == 'AutomationClass':
						self.AutomationList.append(easyamixr_EAM1_AutomationClass(t))

class easyamixr_EAMFormat1:
	def __init__(self, xmldata=None):
		self.VideoInfo = None
		self.MinorVersion = 2
		self.ChannelsOrder = []
		self.IDCounter = 112
		self.BPM = 60
		self.TimeSignature = 5
		self.AudioChannelsList = []
		self.ProjectSettings = None
		self.SavePath = ''
		self.ExportTagSettings = {}
		self.TrackEditorAlign = 1
		self.SaveFileDPI = 96
		if xmldata is not None: self.read(xmldata)

	def read(self, xmldata):
		for xpart in xmldata:
			tagname = xpart.tag
			if tagname == 'ExportTagSettings': 
				self.ExportTagSettings = {}
				for inpart in xpart:
					if inpart.text: self.ExportTagSettings[inpart.tag] = inpart.text
			elif tagname == 'MinorVersion': self.MinorVersion = int(xpart.text)
			elif tagname == 'IDCounter': self.IDCounter = int(xpart.text)
			elif tagname == 'BPM': self.BPM = int(xpart.text)
			elif tagname == 'TimeSignature': self.TimeSignature = int(xpart.text)
			elif tagname == 'SavePath': self.SavePath = xpart.text
			elif tagname == 'TrackEditorAlign': self.TrackEditorAlign = int(xpart.text)
			elif tagname == 'SaveFileDPI': self.SaveFileDPI = int(xpart.text)
			elif tagname == 'ChannelsOrder': self.ChannelsOrder = [int(x.text) for x in xpart if x.tag == 'long']
			elif tagname == 'AudioChannelsList':
				for t in xpart:
					if t.tag == 'AudioChannel':
						self.AudioChannelsList.append(easyamixr_EAM1_AudioChannel(t))

class easyamixr_proj:
	def __init__(self):
		self.Format = None
		self.EAMFormat1 = None

	def load_from_file(self, input_file):
		x_root = ET.parse(input_file).getroot()
		for xpart in x_root:
			if xpart.tag == 'Format': self.Format = xpart.text
			elif xpart.tag == 'EAMFormat1': self.EAMFormat1 = easyamixr_EAMFormat1(xpart)
		return True
