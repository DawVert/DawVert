# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: MIT
# easybinrw is MIT

from external.easybinrw import easybinrw
import numpy as np

DEBUGTXT = 0

def printtab(state, a, b, c, val):
	if DEBUGTXT: 
		print('    '*state.tabnum, end='')
		if a is not None: print(a, '-', end=' ')
		if b is not None: print(b, '-', end=' ')
		if c is not None: print(c, end=' ')
		if val is not None:
			if type(val) not in [dict, list]: 
				if isinstance(val, bytes): print('-', val.hex())
				else: print('-', val)
			else: print()
		else: print()

class datadef_match:
	def __init__(self):
		self.bintype = None
		self.match_value = None
		self.name = None
		self.parts = datadef_partlist()
		self.mode = 'eq'

	def read(self, xml_obj):
		self.type = xml_obj.tag
		for k, v in xml_obj.attrib.items():
			if k=='type': self.bintype = v
			elif k=='match_value': self.match_value = v
			elif k=='name': self.name = v
			elif k=='mode': self.mode = v
			else: print('unsupported match attrib:', k)
		for x in xml_obj:
			self.parts.read_part(x)

	def match(self, val):
		if self.bintype == 'int':
			if self.mode=='eq': return int(self.match_value)==val
			if self.mode=='ne': return int(self.match_value)!=val
			if self.mode=='hi': return int(self.match_value)<val
			if self.mode=='lo': return int(self.match_value)>val

	def parse(self, state, outval):
		omatch = self.match(outval[self.name])
		if omatch:
			return self.parts.parse(state, outval, debugsource='match')

class datadef_part:
	def __init__(self):
		self.type = None
		self.bintype = None
		self.name = None
		self.size_source = None
		self.size_manual = 0
		self.size_name = None
		self.size_local_name = None
		self.list_bintype = 'dict'
		self.struct_name = ''
		self.parts = datadef_partlist()
		self.part_size = None

	def read(self, xml_obj):
		self.type = xml_obj.tag
		for k, v in xml_obj.attrib.items():
			if k=='type': self.bintype = v
			elif k=='name': self.name = v
			elif k=='size':
				self.size_source = 'manual'
				self.size_manual = int(v)
			elif k=='size_name':
				self.size_source = 'lenval'
				self.size_name = v
			elif k=='size_local_name':
				self.size_source = 'fromkey'
				self.size_local_name = v
			elif k=='struct_name': self.struct_name = v
			elif k=='list_type': self.list_bintype = v
			else: print('unsupported part attrib:', k)

		for x in xml_obj:
			if x.tag == 'size': 
				self.part_size = readpart(x)
				self.size_source = 'part'
			else: self.parts.read_part(x)

	def get_lenval(self, state, outval):
		if self.size_source == 'manual': return self.size_manual
		elif self.size_source == 'part': return self.part_size.getvalue(state, outval)
		elif self.size_source == 'lenval': return state.lengths[self.size_name]
		elif self.size_source == 'fromkey': return outval[self.size_local_name]

	def getvaluelist(self, state, outval):
		reader = state.reader
		size = self.get_lenval(state, outval)

		if size>-1:
			if self.list_bintype == 'dict':
				printtab(state, '>> LIST_START', None, None, None)
				listd = []
				for _ in range(size):
					ioutval = {}
					self.parts.parse(state, ioutval, debugsource='dict')
					listd.append(ioutval)
				printtab(state, '<< LIST_END', None, None, None)
				return listd

			elif self.list_bintype == 'int_s8': return reader.list_int_s8(size)
			elif self.list_bintype == 'int_u8': return reader.list_int_u8(size)
			elif self.list_bintype == 'int_s16': return reader.list_int_s16(size)
			elif self.list_bintype == 'int_u16': return reader.list_int_u16(size)
			elif self.list_bintype == 'int_s32': return reader.list_int_s32(size)
			elif self.list_bintype == 'int_u32': return reader.list_int_u32(size)
			elif self.list_bintype == 'int_s64': return reader.list_int_s64(size)
			elif self.list_bintype == 'int_u64': return reader.list_int_u64(size)
			elif self.list_bintype == 'float': return reader.list_float(size)
			elif self.list_bintype == 'double': return reader.list_double(size)
			elif self.list_bintype == 'int_s16_b': return reader.list_int_s16_b(size)
			elif self.list_bintype == 'int_u16_b': return reader.list_int_u16_b(size)
			elif self.list_bintype == 'int_s32_b': return reader.list_int_s32_b(size)
			elif self.list_bintype == 'int_u32_b': return reader.list_int_u32_b(size)
			elif self.list_bintype == 'int_s64_b': return reader.list_int_s64_b(size)
			elif self.list_bintype == 'int_u64_b': return reader.list_int_u64_b(size)
			elif self.list_bintype == 'float_b': return reader.list_float_b(size)
			elif self.list_bintype == 'double_b': return reader.list_double_b(size)
			elif self.list_bintype == 'int_s16_l': return reader.list_int_s16_l(size)
			elif self.list_bintype == 'int_u16_l': return reader.list_int_u16_l(size)
			elif self.list_bintype == 'int_s32_l': return reader.list_int_s32_l(size)
			elif self.list_bintype == 'int_u32_l': return reader.list_int_u32_l(size)
			elif self.list_bintype == 'int_s64_l': return reader.list_int_s64_l(size)
			elif self.list_bintype == 'int_u64_l': return reader.list_int_u64_l(size)
			elif self.list_bintype == 'float_l': return reader.list_float_l(size)
			elif self.list_bintype == 'double_l': return reader.list_double_l(size)
			elif self.list_bintype == 'struct':
				outd = []
				for _ in range(size):
					printtab(state, '>> LIST_STRUCT_START', None, None, None)
					outv = {}
					d = state.parse_struct(self.struct_name, outv)
					outd.append(outv)
					printtab(state, '<< LIST_STRUCT_END', None, None, None)
				return outd
		if size==-1:
			if self.list_bintype == 'struct':
				outd = []
				while True:
					outv = {}
					printtab(state, '>> LIST_STRUCT_START', None, None, None)
					exitval = state.parse_struct(self.struct_name, outv)
					printtab(state, '<< LIST_STRUCT_END', None, None, None)
					outd.append(outv)
					if exitval=='BREAK': break
				return outd

	def getvalue(self, state, outval):
		reader = state.reader
		if self.bintype == 'int_s8': return reader.int_s8()
		elif self.bintype == 'int_u8': return reader.int_u8()
		elif self.bintype == 'int_s16': return reader.int_s16()
		elif self.bintype == 'int_u16': return reader.int_u16()
		elif self.bintype == 'int_s32': return reader.int_s32()
		elif self.bintype == 'int_u32': return reader.int_u32()
		elif self.bintype == 'int_s64': return reader.int_s64()
		elif self.bintype == 'int_u64': return reader.int_u64()
		elif self.bintype == 'float': return reader.float()
		elif self.bintype == 'double': return reader.double()

		elif self.bintype == 'int_s16_b': return reader.int_s16_b()
		elif self.bintype == 'int_u16_b': return reader.int_u16_b()
		elif self.bintype == 'int_s32_b': return reader.int_s32_b()
		elif self.bintype == 'int_u32_b': return reader.int_u32_b()
		elif self.bintype == 'int_s64_b': return reader.int_s64_b()
		elif self.bintype == 'int_u64_b': return reader.int_u64_b()
		elif self.bintype == 'float_b': return reader.float_b()
		elif self.bintype == 'double_b': return reader.double_b()

		elif self.bintype == 'int_s16_l': return reader.int_s16_l()
		elif self.bintype == 'int_u16_l': return reader.int_u16_l()
		elif self.bintype == 'int_s32_l': return reader.int_s32_l()
		elif self.bintype == 'int_u32_l': return reader.int_u32_l()
		elif self.bintype == 'int_s64_l': return reader.int_s64_l()
		elif self.bintype == 'int_u64_l': return reader.int_u64_l()
		elif self.bintype == 'float_l': return reader.float_l()
		elif self.bintype == 'double_l': return reader.double_l()

		elif self.bintype == 'skip': return reader.skip(self.get_lenval(state, outval))

		elif self.bintype == 'raw': return reader.raw(self.get_lenval(state, outval))
		elif self.bintype == 'string': return reader.string(self.get_lenval(state, outval))
		elif self.bintype == 'struct': 
			printtab(state, '>> STRUCT_START', None, None, None)
			outv = {}
			state.parse_struct(self.struct_name, outv)
			printtab(state, '<< STRUCT_END', None, None, None)
			return outv

		elif self.bintype == 'list': return self.getvaluelist(state, outval)

	def parse(self, state, outval, num):
		if self.type == 'part':
			name = self.name if self.name else 'unk_%i'%num
			value = self.getvalue(state, outval)
			printtab(state, 'PART', self.bintype, name, value)
			outval[name] = value
		elif self.type == 'length':
			if self.name:
				state.lengths[self.name] = self.getvalue(state, outval)
				printtab(state, 'LEN_STORE', self.bintype, self.name, state.lengths[self.name])
			else:
				print('length must have a name')

class datadef_break:
	def __init__(self):
		pass

	def read(self, xml_obj):
		pass

xmltags = {
	'part': datadef_part,
	'length': datadef_part,
	'size': datadef_part,
	'match': datadef_match,
	'break': datadef_break
}

def readpart(x):
	part_obj = xmltags[x.tag]()
	part_obj.read(x)
	return part_obj

class datadef_partlist:
	def __init__(self):
		self.parts = []

	def parse(self, state, outval, **args):
		for num, part in enumerate(self.parts):
			if isinstance(part, datadef_part): part.parse(state, outval, num)
			if isinstance(part, datadef_match): 
				oc = part.parse(state, outval)
				if oc: return oc
			if isinstance(part, datadef_break): 
				return 'BREAK'

	def read_part(self, x):
		part_obj = xmltags[x.tag]()
		part_obj.read(x)
		self.parts.append(part_obj)

class datadef_file_struct:
	def __init__(self):
		self.parts = datadef_partlist()

	def read(self, xml_obj):
		for x in xml_obj:
			self.parts.read_part(x)

	def parse(self, state, outval):
		state.tabnum += 1
		o = self.parts.parse(state, outval, debugsource='struct')
		state.tabnum -= 1
		return o

class datadef_parse_state:
	def __init__(self):
		self.structs = {}
		self.lengths = {}
		self.reader = easybinrw.binwrite()
		self.tabnum = 0

	def parse_struct(self, structname, outval):
		if structname in self.structs:
			return self.structs[structname].parse(self, outval)

class datadef_file:
	def __init__(self):
		self.structs = {}

	def load_from_file(self, filename):
		self.__init__()
		import xml.etree.ElementTree as ET
		tree = ET.parse(filename)
		root = tree.getroot()
		for x in root:
			if x.tag == 'struct':
				struct_obj = datadef_file_struct()
				struct_obj.read(x)
				self.structs[x.get('name')] = struct_obj

	def parse_file(self, filename, structname):
		state = datadef_parse_state()
		state.reader.load_file(filename)
		state.structs = self.structs
		outval = {}
		if structname in self.structs: self.structs[structname].parse(state, outval)
		return outval