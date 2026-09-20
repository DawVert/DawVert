# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import dataclasses
from dataclasses import dataclass
from dataclasses import dataclass, field

from objects.file_proj._cubasexml.func import *

@dataclass
class class_StMedia__PureCategoryFilter:
	idnum: int = 0
	ctype: int = 0
	filters: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'type' in obj_data: self.ctype = obj_data['type']
		if 'filters' in obj_data: self.filters = obj_data['filters']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'type', self.ctype)
		makeval__dict(xmlobj, 'filters', self.filters)
globalstate.classes['StMedia::PureCategoryFilter'] = class_StMedia__PureCategoryFilter

@dataclass
class class_StMedia__MultiAttributeFilter:
	idnum: int = 0
	operator: int = 5
	attributes: dict = field(default_factory=dict)
	searchString: str = ''
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'operator' in obj_data: self.operator = obj_data['operator']
		if 'attributes' in obj_data: self.attributes = obj_data['attributes']
		if 'searchString' in obj_data: self.searchString = obj_data['searchString']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'operator', self.operator)
		makeval__dict(xmlobj, 'attributes', self.attributes)
		makeval__string(xmlobj, 'searchString', self.searchString, 1)
globalstate.classes['StMedia::MultiAttributeFilter'] = class_StMedia__MultiAttributeFilter

@dataclass
class class_StMedia__CategoryFilter:
	idnum: int = 0
	ctype: int = 0
	filters: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'type' in obj_data: self.ctype = obj_data['type']
		if 'filters' in obj_data: self.filters = obj_data['filters']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'type', self.ctype)
		makeval__dict(xmlobj, 'filters', self.filters)
globalstate.classes['StMedia::CategoryFilter'] = class_StMedia__CategoryFilter

@dataclass
class class_StMedia__RatingFilter:
	idnum: int = 0
	ctype: int = 0
	filters: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'type' in obj_data: self.ctype = obj_data['type']
		if 'filters' in obj_data: self.filters = obj_data['filters']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'type', self.ctype)
		makeval__dict(xmlobj, 'filters', self.filters)
globalstate.classes['StMedia::RatingFilter'] = class_StMedia__RatingFilter

@dataclass
class class_StMedia__TypeFilter:
	idnum: int = 0
	types: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'types' in obj_data: self.types = obj_data['types']
	def make_xml(self, xmlobj):
		makeval__dict(xmlobj, 'types', self.types)
globalstate.classes['StMedia::TypeFilter'] = class_StMedia__TypeFilter

@dataclass
class class_StMedia__ExtraMultiAttributeFilter:
	idnum: int = 0
	operator: int = 9
	attributes: dict = field(default_factory=dict)
	searchString: str = ''
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'operator' in obj_data: self.operator = obj_data['operator']
		if 'attributes' in obj_data: self.attributes = obj_data['attributes']
		if 'searchString' in obj_data: self.searchString = obj_data['searchString']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'operator', self.operator)
		makeval__dict(xmlobj, 'attributes', self.attributes)
		makeval__string(xmlobj, 'searchString', self.searchString, 1)
globalstate.classes['StMedia::ExtraMultiAttributeFilter'] = class_StMedia__ExtraMultiAttributeFilter

@dataclass
class class_StMedia__ValueListFilter:
	idnum: int = 0
	attribId: str = ''
	op: int = 0
	values: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'attribId' in obj_data: self.attribId = obj_data['attribId']
		if 'op' in obj_data: self.op = obj_data['op']
		if 'values' in obj_data: self.values = obj_data['values']
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 'attribId', self.attribId, 0)
		makeval__int(xmlobj, 'op', self.op)
		makeval__dict(xmlobj, 'values', self.values)
globalstate.classes['StMedia::ValueListFilter'] = class_StMedia__ValueListFilter

@dataclass
class class_StMedia__ValueMatrixFilter:
	idnum: int = 0
	ctype: int = 0
	filters: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'type' in obj_data: self.ctype = obj_data['type']
		if 'filters' in obj_data: self.filters = obj_data['filters']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'type', self.ctype)
		makeval__dict(xmlobj, 'filters', self.filters)
globalstate.classes['StMedia::ValueMatrixFilter'] = class_StMedia__ValueMatrixFilter
