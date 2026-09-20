# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import dataclasses
from dataclasses import dataclass
from dataclasses import dataclass, field

from objects.file_proj._cubasexml.func import *

class_FNPath = globalstate.classes['FNPath']
class_MListNode = globalstate.classes['MListNode']
class_MAutomationNode = globalstate.classes['MAutomationNode']
class_MAutoFadeSetting = globalstate.classes['MAutoFadeSetting']

@dataclass
class class_MAudioTrack:
	idnum: int = 0
	connection_type: int = 0
	device_name: str = ''
	channel_id: int = 0
	deviceattributes: dict = field(default_factory=dict)
	flags: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Connection Type' in obj_data: self.connection_type = obj_data['Connection Type']
		if 'Device Name' in obj_data: self.device_name = obj_data['Device Name']
		if 'Channel ID' in obj_data: self.channel_id = obj_data['Channel ID']
		if 'DeviceAttributes' in obj_data: self.deviceattributes = obj_data['DeviceAttributes']
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'Connection Type', self.connection_type)
		makeval__string(xmlobj, 'Device Name', self.device_name, 0)
		makeval__int(xmlobj, 'Channel ID', self.channel_id)
		makeval__dict(xmlobj, 'DeviceAttributes', self.deviceattributes)
		makeval__int(xmlobj, 'Flags', self.flags)
globalstate.classes['MAudioTrack'] = class_MAudioTrack

@dataclass
class class_MAudioTrackEvent:
	idnum: int = 0
	flags: int = 0.0
	start: float = 0.0
	length: float = 1007999.9899864197
	node: class_MListNode = field(default_factory=class_MListNode)
	additional_attributes: dict = field(default_factory=dict)
	track_device: class_MAudioTrack = field(default_factory=class_MAudioTrack)
	height: int = 0
	automation: class_MAutomationNode = field(default_factory=class_MAutomationNode)
	autofade_settings: class_MAutoFadeSetting = field(default_factory=class_MAutoFadeSetting)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Node' in obj_data: self.node = obj_data['Node']
		if 'Additional Attributes' in obj_data: self.additional_attributes = obj_data['Additional Attributes']
		if 'Track Device' in obj_data: self.track_device = obj_data['Track Device']
		if 'Height' in obj_data: self.height = obj_data['Height']
		if 'Automation' in obj_data: self.automation = obj_data['Automation']
		if 'Autofade Settings' in obj_data: self.autofade_settings = obj_data['Autofade Settings']
	def spread_counter(self, counter_obj):
		self.idnum = counter_obj.get()
		self.node.idnum = counter_obj.get()
		self.track_device.idnum = counter_obj.get()
		self.automation.idnum = counter_obj.get()
		self.autofade_settings.idnum = counter_obj.get()
	def make_xml(self, xmlobj):
		if self.flags: makeval__int(xmlobj, 'Flags', self.flags)
		makeval__float(xmlobj, 'Start', self.start)
		makeval__float(xmlobj, 'Length', self.length)
		makeval__obj(xmlobj, 'Node', self.node)
		makeval__dict(xmlobj, 'Additional Attributes', self.additional_attributes)
		makeval__obj(xmlobj, 'Track Device', self.track_device)
		if self.height: makeval__int(xmlobj, 'Height', self.height)
		makeval__obj(xmlobj, 'Automation', self.automation)
		makeval__obj(xmlobj, 'Autofade Settings', self.autofade_settings)
globalstate.classes['MAudioTrackEvent'] = class_MAudioTrackEvent

@dataclass
class class_AudioCluster:
	idnum: int = 0
	substreams: cubasexml_list_obj = field(default_factory=cubasexml_list_obj)
	segments: cubasexml_list_dict = field(default_factory=cubasexml_list_dict)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Substreams' in obj_data: self.substreams.setvals(obj_data['Substreams'])
		if 'Segments' in obj_data: self.segments.setvals(obj_data['Segments'])
	def make_xml(self, xmlobj):
		makeval__list(xmlobj, 'Substreams', self.substreams)
		makeval__list(xmlobj, 'Segments', self.segments)
globalstate.classes['AudioCluster'] = class_AudioCluster

@dataclass
class class_AudioFile:
	idnum: int = 0
	fpath: class_FNPath = field(default_factory=class_FNPath)
	speakerarr: dict = field(default_factory=dict)
	framecount: int = 0
	sample_size: int = 0
	frame_size: int = 0
	channels: int = 0
	rate: float = 0
	format: int = 0
	byteorder: int = 0
	dataoffset: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'FPath' in obj_data: self.fpath = obj_data['FPath']
		if 'FrameCount' in obj_data: self.framecount = obj_data['FrameCount']
		if 'Sample Size' in obj_data: self.sample_size = obj_data['Sample Size']
		if 'Frame Size' in obj_data: self.frame_size = obj_data['Frame Size']
		if 'SpeakerArr' in obj_data: self.speakerarr = obj_data['SpeakerArr']
		if 'Channels' in obj_data: self.channels = obj_data['Channels']
		if 'Rate' in obj_data: self.rate = obj_data['Rate']
		if 'Format' in obj_data: self.format = obj_data['Format']
		if 'ByteOrder' in obj_data: self.byteorder = obj_data['ByteOrder']
		if 'DataOffset' in obj_data: self.dataoffset = obj_data['DataOffset']
	def make_xml(self, xmlobj):
		makeval__obj(xmlobj, 'FPath', self.fpath)
		makeval__int(xmlobj, 'FrameCount', self.framecount)
		makeval__int(xmlobj, 'Sample Size', self.sample_size)
		makeval__int(xmlobj, 'Frame Size', self.frame_size)
		if self.speakerarr: makeval__dict(xmlobj, 'SpeakerArr', self.speakerarr)
		if self.channels: makeval__int(xmlobj, 'Channels', self.channels)
		makeval__float(xmlobj, 'Rate', self.rate)
		makeval__int(xmlobj, 'Format', self.format)
		makeval__int(xmlobj, 'ByteOrder', self.byteorder)
		makeval__int(xmlobj, 'DataOffset', self.dataoffset)
globalstate.classes['AudioFile'] = class_AudioFile

@dataclass
class class_MAudioEvent:
	idnum: int = 0
	clip_idnum: int = -1
	start: float = 0
	length: float = 0
	priority: int = 1
	offset: float = 0
	volume: float = 1
	flags: int = 0
	additional_attributes: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Offset' in obj_data: self.offset = obj_data['Offset']
		if 'Priority' in obj_data: self.priority = obj_data['Priority']
		if 'Volume' in obj_data: self.volume = obj_data['Volume']
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
		if 'AudioClip' in obj_data: self.clip_idnum = obj_data['AudioClip'].idnum
		if 'Additional Attributes' in obj_data: self.additional_attributes = obj_data['Additional Attributes']
	def make_xml(self, xmlobj):
		makeval__float(xmlobj, 'Start', self.start)
		makeval__float(xmlobj, 'Length', self.length)
		if self.offset: makeval__float(xmlobj, 'Offset', self.offset)
		makeval__int(xmlobj, 'Priority', self.priority)
		if self.volume != 1: makeval__float(xmlobj, 'Volume', self.volume)
		makeval__pointer(xmlobj, 'AudioClip', self.clip_idnum)
		if self.flags: makeval__int(xmlobj, 'Flags', self.flags)
		if self.additional_attributes: makeval__dict(xmlobj, 'Additional Attributes', self.additional_attributes)
globalstate.classes['MAudioEvent'] = class_MAudioEvent

@dataclass
class class_PAudioClip:
	idnum: int = 0
	name: str = ''
	assetoid: str = ''
	history_number: int = 0
	origin_time: float = 0
	path: class_FNPath = field(default_factory=class_FNPath)
	uid: cubasexml_list_string = field(default_factory=cubasexml_list_string)
	additional_attributes: dict = field(default_factory=dict)
	cluster: class_AudioCluster = field(default_factory=class_AudioCluster)
	events: cubasexml_list_obj = field(default_factory=cubasexml_list_obj)
	domain: seq_domain = field(default_factory=seq_domain)

	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'AssetOID' in obj_data: self.assetoid = obj_data['AssetOID']
		if 'Cluster' in obj_data: self.cluster = obj_data['Cluster']
		if 'Domain' in obj_data: self.domain.from_dict(obj_data['Domain'])
		if 'Events' in obj_data: self.events = obj_data['Events']
		if 'History Number' in obj_data: self.history_number = obj_data['History Number']
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'Origin Time' in obj_data: self.origin_time = obj_data['Origin Time']
		if 'Path' in obj_data: self.path = obj_data['Path']
		if 'UID' in obj_data: self.uid.setvals(obj_data['UID'])
		if 'Additional Attributes' in obj_data: self.additional_attributes = obj_data['Additional Attributes']
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 'Name', self.name, 1)
		makeval__dict(xmlobj, 'Domain', self.domain.to_dict())
		if self.events: makeval__list(xmlobj, 'Events', self.events)
		makeval__obj(xmlobj, 'Path', self.path)
		if self.history_number: makeval__int(xmlobj, 'History Number', self.history_number)
		if self.origin_time: makeval__float(xmlobj, 'Origin Time', self.origin_time)
		if self.assetoid: makeval__string(xmlobj, 'AssetOID', self.assetoid, 1)
		makeval__dict(xmlobj, 'Additional Attributes', self.additional_attributes)
		makeval__obj(xmlobj, 'Cluster', self.cluster)
		if self.uid: makeval__list(xmlobj, 'UID', self.uid)
globalstate.classes['PAudioClip'] = class_PAudioClip

@dataclass
class class_PAudioWarpScale:
	idnum: int = 0
	warptab: cubasexml_list_obj = field(default_factory=cubasexml_list_obj)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'WarpTab' in obj_data: self.warptab.setvals(obj_data['WarpTab'])
	def make_xml(self, xmlobj):
		makeval__list(xmlobj, 'WarpTab', self.warptab)
globalstate.classes['PAudioWarpScale'] = class_PAudioWarpScale

@dataclass
class class_PWarpTab:
	idnum: int = 0
	position: float = 0.0
	warped: float = 0.0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Position' in obj_data: self.position = obj_data['Position']
		if 'Warped' in obj_data: self.warped = obj_data['Warped']
	def make_xml(self, xmlobj):
		makeval__float(xmlobj, 'Position', self.position)
		makeval__float(xmlobj, 'Warped', self.warped)
globalstate.classes['PWarpTab'] = class_PWarpTab

@dataclass
class class_SmtgAlgoDescription:
	idnum: int = 0
	precision: int = 3
	grainSize: int = 300
	overlap: float = 0.2
	variance: float = 0.8
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'precision' in obj_data: self.precision = obj_data['precision']
		if 'grainSize' in obj_data: self.grainSize = obj_data['grainSize']
		if 'overlap' in obj_data: self.overlap = obj_data['overlap']
		if 'variance' in obj_data: self.variance = obj_data['variance']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'precision', self.precision)
		makeval__int(xmlobj, 'grainSize', self.grainSize)
		makeval__float(xmlobj, 'overlap', self.overlap)
		makeval__float(xmlobj, 'variance', self.variance)
globalstate.classes['SmtgAlgoDescription'] = class_SmtgAlgoDescription

@dataclass
class class_ElastiquePreset:
	idnum: int = 0
	processingmode: str = ''
	stereomode: str = ''
	formantpreservation: int = 0
	tapestylemode: int = 0
	pitchaccuratemode: int = 1
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'processingMode' in obj_data: self.processingmode = obj_data['processingMode']
		if 'stereoMode' in obj_data: self.stereomode = obj_data['stereoMode']
		if 'formantPreservation' in obj_data: self.formantpreservation = obj_data['formantPreservation']
		if 'tapeStyleMode' in obj_data: self.tapestylemode = obj_data['tapeStyleMode']
		if 'pitchAccurateMode' in obj_data: self.pitchaccuratemode = obj_data['pitchAccurateMode']
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 'processingMode', self.processingmode, 0)
		makeval__string(xmlobj, 'stereoMode', self.stereomode, 0)
		makeval__int(xmlobj, 'formantPreservation', self.formantpreservation)
		makeval__int(xmlobj, 'tapeStyleMode', self.tapestylemode)
		makeval__int(xmlobj, 'pitchAccurateMode', self.pitchaccuratemode)
globalstate.classes['ElastiquePreset'] = class_ElastiquePreset
