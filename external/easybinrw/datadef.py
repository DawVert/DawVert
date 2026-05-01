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
			else: self.parts.read_parts(x)

	def read_lenval(self, state, outval):
		if self.size_source == 'manual': return self.size_manual
		elif self.size_source == 'part': return self.part_size.read_value_size(state, outval)
		elif self.size_source == 'lenval': return state.lengths[self.size_name]
		elif self.size_source == 'fromkey': return outval[self.size_local_name]

	def read_value_list(self, state, outval):
		reader = state.reader
		size = self.read_lenval(state, outval)

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

	def read_value_size(self, state, outval):
		reader = state.reader
		if self.bintype == 'int_u8': return reader.int_u8()
		elif self.bintype == 'int_u16': return reader.int_u16()
		elif self.bintype == 'int_u32': return reader.int_u32()
		elif self.bintype == 'int_u64': return reader.int_u64()
		elif self.bintype == 'int_u16_b': return reader.int_u16_b()
		elif self.bintype == 'int_u32_b': return reader.int_u32_b()
		elif self.bintype == 'int_u64_b': return reader.int_u64_b()
		elif self.bintype == 'int_u16_l': return reader.int_u16_l()
		elif self.bintype == 'int_u32_l': return reader.int_u32_l()
		elif self.bintype == 'int_u64_l': return reader.int_u64_l()

	def read_value(self, state, outval):
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

		elif self.bintype == 'skip': return reader.skip(self.read_lenval(state, outval))

		elif self.bintype == 'raw': return reader.raw(self.read_lenval(state, outval))
		elif self.bintype == 'string': return reader.string(self.read_lenval(state, outval))
		elif self.bintype == 'string16': return reader.string16(self.read_lenval(state, outval))
		elif self.bintype == 'string_t': return reader.string_t()
		elif self.bintype == 'struct': 
			printtab(state, '>> STRUCT_START', None, None, None)
			outv = {}
			state.parse_struct(self.struct_name, outv)
			printtab(state, '<< STRUCT_END', None, None, None)
			return outv

		elif self.bintype == 'list': return self.read_value_list(state, outval)

	def parse(self, state, outval, num):
		if self.type == 'part':
			name = self.name if self.name else 'unk_%i'%num
			value = self.read_value(state, outval)
			printtab(state, 'PART', self.bintype, name, value)
			outval[name] = value
		elif self.type == 'length':
			if self.name:
				state.lengths[self.name] = self.read_value_size(state, outval)
				printtab(state, 'LEN_STORE', self.bintype, self.name, state.lengths[self.name])
			else:
				print('length must have a name')

	def write_size(self, state, inval):
		writer = state.writer
		if self.bintype == 'int_u8': writer.int_u8(inval)
		elif self.bintype == 'int_u16': writer.int_u16(inval)
		elif self.bintype == 'int_u32': writer.int_u32(inval)
		elif self.bintype == 'int_u64': writer.int_u64(inval)
		elif self.bintype == 'int_u16_b': writer.int_u16_b(inval)
		elif self.bintype == 'int_u32_b': writer.int_u32_b(inval)
		elif self.bintype == 'int_u64_b': writer.int_u64_b(inval)
		elif self.bintype == 'int_u16_l': writer.int_u16_l(inval)
		elif self.bintype == 'int_u32_l': writer.int_u32_l(inval)
		elif self.bintype == 'int_u64_l': writer.int_u64_l(inval)
		else: 
			print('unsupported size type', self.bintype)
			exit()

	def write_len(self, state, indict, count):
		if self.size_source == 'manual': return self.size_manual
		elif self.size_source == 'part':
			self.part_size.write_size(state, count)
			return count
		elif self.size_source == 'fromkey':
			d = indict[self.size_local_name]
			return d
		else: 
			print('unsupported length source', self.size_source)
			exit()

	def write_list(self, state, inval, length):
		writer = state.writer
		if length>-1:
			if self.list_bintype == 'int_s8': writer.list_int_s8(inval, length)
			elif self.list_bintype == 'int_u8': writer.list_int_u8(inval, length)
			elif self.list_bintype == 'int_s16': writer.list_int_s16(inval, length)
			elif self.list_bintype == 'int_u16': writer.list_int_u16(inval, length)
			elif self.list_bintype == 'int_s32': writer.list_int_s32(inval, length)
			elif self.list_bintype == 'int_u32': writer.list_int_u32(inval, length)
			elif self.list_bintype == 'int_s64': writer.list_int_s64(inval, length)
			elif self.list_bintype == 'int_u64': writer.list_int_u64(inval, length)
			elif self.list_bintype == 'float': writer.list_float(inval, length)
			elif self.list_bintype == 'double': writer.list_double(inval, length)
			elif self.list_bintype == 'int_s16_b': writer.list_int_s16_b(inval, length)
			elif self.list_bintype == 'int_u16_b': writer.list_int_u16_b(inval, length)
			elif self.list_bintype == 'int_s32_b': writer.list_int_s32_b(inval, length)
			elif self.list_bintype == 'int_u32_b': writer.list_int_u32_b(inval, length)
			elif self.list_bintype == 'int_s64_b': writer.list_int_s64_b(inval, length)
			elif self.list_bintype == 'int_u64_b': writer.list_int_u64_b(inval, length)
			elif self.list_bintype == 'float_b': writer.list_float_b(inval, length)
			elif self.list_bintype == 'double_b': writer.list_double_b(inval, length)
			elif self.list_bintype == 'int_s16_l': writer.list_int_s16_l(inval, length)
			elif self.list_bintype == 'int_u16_l': writer.list_int_u16_l(inval, length)
			elif self.list_bintype == 'int_s32_l': writer.list_int_s32_l(inval, length)
			elif self.list_bintype == 'int_u32_l': writer.list_int_u32_l(inval, length)
			elif self.list_bintype == 'int_s64_l': writer.list_int_s64_l(inval, length)
			elif self.list_bintype == 'int_u64_l': writer.list_int_u64_l(inval, length)
			elif self.list_bintype == 'float_l': writer.list_float_l(inval, length)
			elif self.list_bintype == 'double_l': writer.list_double_l(inval, length)
			elif self.list_bintype == 'dict': 
				for x in inval:
					self.parts.write(state, x)
			elif self.list_bintype == 'struct':
				if self.struct_name in state.structs:
					structdata = state.structs[self.struct_name]
					for x in inval:
						structdata.write(state, x)
				else:
					print('write: struct not found', self.struct_name)
				#exit()

			else: 
				print('write: unsupported list_bintype', self.list_bintype)
				exit()

	def write(self, state, indict, num):
		name = self.name if self.name else 'unk_%i'%num
		inval = indict[name]
		writer = state.writer

		if self.bintype == 'int_s8': writer.int_s8(inval)
		elif self.bintype == 'int_u8': writer.int_u8(inval)
		elif self.bintype == 'int_s16': writer.int_s16(inval)
		elif self.bintype == 'int_u16': writer.int_u16(inval)
		elif self.bintype == 'int_s32': writer.int_s32(inval)
		elif self.bintype == 'int_u32': writer.int_u32(inval)
		elif self.bintype == 'int_s64': writer.int_s64(inval)
		elif self.bintype == 'int_u64': writer.int_u64(inval)
		elif self.bintype == 'float': writer.float(inval)
		elif self.bintype == 'double': writer.double(inval)

		elif self.bintype == 'int_s16_b': writer.int_s16_b(inval)
		elif self.bintype == 'int_u16_b': writer.int_u16_b(inval)
		elif self.bintype == 'int_s32_b': writer.int_s32_b(inval)
		elif self.bintype == 'int_u32_b': writer.int_u32_b(inval)
		elif self.bintype == 'int_s64_b': writer.int_s64_b(inval)
		elif self.bintype == 'int_u64_b': writer.int_u64_b(inval)
		elif self.bintype == 'float_b': writer.float_b(inval)
		elif self.bintype == 'double_b': writer.double_b(inval)

		elif self.bintype == 'int_s16_l': writer.int_s16_l(inval)
		elif self.bintype == 'int_u16_l': writer.int_u16_l(inval)
		elif self.bintype == 'int_s32_l': writer.int_s32_l(inval)
		elif self.bintype == 'int_u32_l': writer.int_u32_l(inval)
		elif self.bintype == 'int_s64_l': writer.int_s64_l(inval)
		elif self.bintype == 'int_u64_l': writer.int_u64_l(inval)
		elif self.bintype == 'float_l': writer.float_l(inval)
		elif self.bintype == 'double_l': writer.double_l(inval)

		elif self.bintype == 'string_t': writer.string_t(inval)
		
		elif self.bintype == 'struct': 
			if self.struct_name in state.structs:
				structdata = state.structs[self.struct_name]
				for x in inval:
					structdata.write(state, x)
			else:
				print('write: struct not found', self.struct_name)
			#exit()

		elif self.bintype == 'raw':
			length = self.write_len(state, indict, len(inval))
			writer.raw_n(inval, length)
		elif self.bintype == 'string':
			length = self.write_len(state, indict, len(inval))
			writer.string(inval, length)
		elif self.bintype == 'string16':
			length = self.write_len(state, indict, len(inval))
			writer.string16(inval, length)
		elif self.bintype == 'list':
			length = self.write_len(state, indict, len(inval))
			self.write_list(state, inval, length)

		else: 
			print('unsupported bintype', self.bintype)
			exit()

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

class datadef_parse_state_reader:
	def __init__(self):
		self.structs = {}
		self.lengths = {}
		self.reader = easybinrw.binread()
		self.tabnum = 0

	def parse_struct(self, structname, outval):
		if structname in self.structs:
			return self.structs[structname].parse(self, outval)

class datadef_parse_state_writer:
	def __init__(self):
		self.structs = {}
		self.lengths = {}
		self.writer = easybinrw.binwrite()
		self.tabnum = 0

	def write_struct(self, structname, outval):
		if structname in self.structs:
			return self.structs[structname].parse(self, outval)

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

	def read_parts(self, x):
		part_obj = xmltags[x.tag]()
		part_obj.read(x)
		self.parts.append(part_obj)

	def write(self, state, indict):
		for num, part in enumerate(self.parts):
			if part.type=='part': part.write(state, indict, num)
			elif part.type=='length': 
				print('write: storing length part not supported')
				exit()

class datadef_struct:
	def __init__(self):
		self.parts = datadef_partlist()

	def read(self, xml_obj):
		for x in xml_obj:
			self.parts.read_parts(x)

	def parse(self, state, outval):
		state.tabnum += 1
		o = self.parts.parse(state, outval, debugsource='struct')
		state.tabnum -= 1
		return o

	def write(self, state, indict):
		self.parts.write(state, indict)

class datadef_file:
	def __init__(self):
		self.structs = {}

	def load_from_file(self, filename):
		self.__init__()
		import xml.etree.ElementTree as ET
		tree = ET.parse(filename)
		root = tree.getroot()
		self.read_xml(root)

	def read_xml(self, xmldata):
		for x in xmldata:
			if x.tag == 'struct':
				struct_obj = datadef_struct()
				struct_obj.read(x)
				self.structs[x.get('name')] = struct_obj

	def parse_data(self, data, structname):
		state = datadef_parse_state_reader()
		state.reader.load_data(data)
		state.structs = self.structs
		outval = {}
		if structname in self.structs: self.structs[structname].parse(state, outval)
		return outval

	def parse_file(self, filename, structname):
		state = datadef_parse_state_reader()
		state.reader.load_file(filename)
		state.structs = self.structs
		outval = {}
		if structname in self.structs: self.structs[structname].parse(state, outval)
		return outval

	def dump_bytes(self, structname, inval):
		state = datadef_parse_state_writer()
		state.structs = self.structs
		if structname in self.structs: 
			self.structs[structname].write(state, inval)
			return state.writer.getvalue()
		else: return b''

