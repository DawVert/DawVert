# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import dataclasses
from dataclasses import dataclass
from dataclasses import dataclass, field

from objects.file_proj._cubasexml.func import *

@dataclass
class class_MMidiNote:
	idnum: int = 0
	start: float = 0
	channel: int = 0
	data1: int = 0
	data2: int = 0
	flags: int = 0
	length: float = 0
	initial_startoffset: float = 0
	initial_lengthoffset: float = 0
	data3: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Channel' in obj_data: self.channel = obj_data['Channel']
		if 'Data1' in obj_data: self.data1 = obj_data['Data1']
		if 'Data2' in obj_data: self.data2 = obj_data['Data2']
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Initial Startoffset' in obj_data: self.initial_startoffset = obj_data['Initial Startoffset']
		if 'Initial Lengthoffset' in obj_data: self.initial_lengthoffset = obj_data['Initial Lengthoffset']
		if 'Data3' in obj_data: self.data3 = obj_data['Data3']
	def make_xml(self, xmlobj):
		makeval__float(xmlobj, 'Start', self.start)
		if self.channel: makeval__int(xmlobj, 'Channel', self.channel)
		makeval__int(xmlobj, 'Data1', self.data1)
		makeval__int(xmlobj, 'Data2', self.data2)
		makeval__int(xmlobj, 'Flags', self.flags)
		makeval__float(xmlobj, 'Length', self.length)
		if self.initial_startoffset: makeval__float(xmlobj, 'Initial Startoffset', self.initial_startoffset)
		if self.initial_lengthoffset: makeval__float(xmlobj, 'Initial Lengthoffset', self.initial_lengthoffset)
		makeval__int(xmlobj, 'Data3', self.data3)
globalstate.classes['MMidiNote'] = class_MMidiNote

@dataclass
class class_MMidiPartEvent:
	idnum: int = 0
	node_idnum: int = -1
	start: float = 0
	length: float = 0
	offset: int = 0
	additional_attributes: dict = field(default_factory=dict)
	z_order: int = 1
	transpose: int = 0
	quantize: obj_pointer = field(default_factory=obj_pointer)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Offset' in obj_data: self.offset = obj_data['Offset']
		if 'Node' in obj_data: self.node_idnum = obj_data['Node'].idnum
		if 'Additional Attributes' in obj_data: self.additional_attributes = obj_data['Additional Attributes']
		if 'Z-Order' in obj_data: self.z_order = obj_data['Z-Order']
		if 'Transpose' in obj_data: self.transpose = obj_data['Transpose']
		if 'Quantize' in obj_data: self.quantize = obj_data['Quantize']
	def make_xml(self, xmlobj):
		makeval__float(xmlobj, 'Start', self.start)
		makeval__float(xmlobj, 'Length', self.length)
		if self.offset: makeval__float(xmlobj, 'Offset', self.offset)
		if self.node_idnum: makeval__pointer(xmlobj, 'Node', self.node_idnum)
		if self.additional_attributes: makeval__dict(xmlobj, 'Additional Attributes', self.additional_attributes)
		makeval__int(xmlobj, 'Z-Order', self.z_order)
		if self.transpose: makeval__int(xmlobj, 'Transpose', self.transpose)
		makeval__obj(xmlobj, 'Quantize', self.quantize)
globalstate.classes['MMidiPartEvent'] = class_MMidiPartEvent

@dataclass
class class_MMidiController:
	idnum: int = 0
	start: float = 0
	data1: int = 0
	data2: int = 0
	flags: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Data1' in obj_data: self.data1 = obj_data['Data1']
		if 'Data2' in obj_data: self.data2 = obj_data['Data2']
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
	def make_xml(self, xmlobj):
		makeval__float(xmlobj, 'Start', self.start)
		makeval__int(xmlobj, 'Data1', self.data1)
		if self.data2: makeval__int(xmlobj, 'Data2', self.data2)
		makeval__int(xmlobj, 'Flags', self.flags)
globalstate.classes['MMidiController'] = class_MMidiController

@dataclass
class class_MMidiAfterTouch:
	idnum: int = 0
	start: float = 0
	data1: int = 0
	flags: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Data1' in obj_data: self.data1 = obj_data['Data1']
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
	def make_xml(self, xmlobj):
		makeval__float(xmlobj, 'Start', self.start)
		if self.data1: makeval__int(xmlobj, 'Data1', self.data1)
		makeval__int(xmlobj, 'Flags', self.flags)
globalstate.classes['MMidiAfterTouch'] = class_MMidiAfterTouch

@dataclass
class class_MMidiPitchBend:
	idnum: int = 0
	start: float = 0
	data1: int = 0
	data2: int = 0
	flags: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Data1' in obj_data: self.data1 = obj_data['Data1']
		if 'Data2' in obj_data: self.data2 = obj_data['Data2']
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
	def make_xml(self, xmlobj):
		makeval__float(xmlobj, 'Start', self.start)
		if self.data1: makeval__int(xmlobj, 'Data1', self.data1)
		if self.data2: makeval__int(xmlobj, 'Data2', self.data2)
		makeval__int(xmlobj, 'Flags', self.flags)
globalstate.classes['MMidiPitchBend'] = class_MMidiPitchBend

@dataclass
class class_MMidiPart:
	idnum: int = 0
	name: str = ''
	domain: seq_domain = field(default_factory=seq_domain)
	events: cubasexml_list_obj = field(default_factory=cubasexml_list_obj)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'Domain' in obj_data: self.domain.from_dict(obj_data['Domain'])
		if 'Events' in obj_data: self.events = obj_data['Events']
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 'Name', self.name, 1)
		makeval__dict(xmlobj, 'Domain', self.domain.to_dict())
		makeval__list(xmlobj, 'Events', self.events)
globalstate.classes['MMidiPart'] = class_MMidiPart
