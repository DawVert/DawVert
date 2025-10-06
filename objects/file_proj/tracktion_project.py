# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from external.easybinrw import easybinrw
import logging

def make_id(value, ebrw_writestr):
	out = ('0'*(8-len(value)))+value
	ebrw_writestr.raw(bytes.fromhex(out)[4::-1])

def get_id(ebrw_readstr):
	outv = ebrw_readstr.raw(4)[4::-1].hex()
	while outv:
		if outv[0] == '0': outv = outv[1:]
		else: break
	return outv

class tracktion_project_object:
	def __init__(self):
		self.name = ''
		self.type = ''
		self.info = ''
		self.path = ''
		self.id = ''
		self.id2 = ''

	def read(self, ebrw_readstr):
		self.name = ebrw_readstr.string_t()
		self.type = ebrw_readstr.string_t()
		self.info = ebrw_readstr.string_t()
		self.path = ebrw_readstr.string_t()
		self.id = get_id(ebrw_readstr)
		self.id2 = get_id(ebrw_readstr)

	def __len__(self):
		out = 0
		out += len(self.name.encode())+1
		out += len(self.type.encode())+1
		out += len(self.info.encode())+1
		out += len(self.path.encode())+1
		return out

	def write(self, ebrw_writestr):
		ebrw_writestr.string_t(self.name)
		ebrw_writestr.string_t(self.type)
		ebrw_writestr.string_t(self.info)
		ebrw_writestr.string_t(self.path)
		make_id(self.id, ebrw_writestr)
		make_id(self.id2, ebrw_writestr)

class tracktion_project:
	def __init__(self):
		self.projectId = 0
		self.props = {}
		self.objects = {}
		self.indexes = {}

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)
		ebrw_readstr.magic_check(b'TP01')

		self.projectId = get_id(ebrw_readstr)
		objectOffset = ebrw_readstr.int_u32()
		indexOffset = ebrw_readstr.int_u32()
		numprops = ebrw_readstr.int_u32()

		for _ in range(numprops):
			name = ebrw_readstr.string_t()
			data = ebrw_readstr.string_i32()
			self.props[name] = data

		ebrw_readstr.seek(objectOffset)

		wobjects = []

		num = ebrw_readstr.int_u32()
		if (num < 20000):
			for _ in range(num):
				itemID = get_id(ebrw_readstr)
				fileOffset = ebrw_readstr.int_u32()
				wobjects.append([itemID, fileOffset])

		for itemID, fileOffset in wobjects:
			ebrw_readstr.seek(fileOffset)
			obj_obj = tracktion_project_object()
			obj_obj.read(ebrw_readstr)
			self.objects[itemID] = obj_obj

		ebrw_readstr.seek(indexOffset)
		for _ in range(ebrw_readstr.int_u32()):
			name = ebrw_readstr.string_t()
			numids = ebrw_readstr.int_u16() 
			iids = [get_id(ebrw_readstr) for x in range(numids)]
			self.indexes[name] = iids

	def write(self, ebrw_writestr):
		ebrw_writestr.raw(b'TP01')
		make_id(self.projectId, ebrw_writestr)

		objectOffset = 16
		part_first = easybinrw.binwrite()
		part_first.int_u32(len(self.props))
		for k, d in self.props.items():
			part_first.string_t(k)
			part_first.string_i32(d)
		objectOffset += len(part_first.getvalue())

		offsets = []
		part_second = easybinrw.binwrite()
		for k, d in self.objects.items(): 
			offsets.append(objectOffset+part_second.tell())
			d.write(part_second)
		objectOffset += len(part_second.getvalue())

		part_third = easybinrw.binwrite()
		part_third.int_u32(len(self.objects))
		for n, k in enumerate(self.objects): 
			make_id(k, part_third)
			part_third.int_u32(offsets[n])

		ebrw_writestr.int_u32(objectOffset)
		objectOffset += len(part_third.getvalue())

		part_fourth = easybinrw.binwrite()
		part_fourth.int_u32(len(self.indexes))
		for k, d in self.indexes.items():
			part_fourth.string_t(k)
			part_fourth.int_u16(len(d)) 
			for c in d: make_id(c, part_fourth)

		ebrw_writestr.int_u32(objectOffset)

		ebrw_writestr.raw(part_first.getvalue())
		ebrw_writestr.raw(part_second.getvalue())
		ebrw_writestr.raw(part_third.getvalue())
		ebrw_writestr.raw(part_fourth.getvalue())

	def save_to_file(self, output_file):
		ebrw_writestr = easybinrw.binwrite()
		self.write(ebrw_writestr)
		f = open(output_file, 'wb')
		f.write(ebrw_writestr.getvalue())
