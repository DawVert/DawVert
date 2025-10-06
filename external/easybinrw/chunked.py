# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: MIT
# easybinrw is MIT

from external.easybinrw import easybinrw

class chunk_part_data:
	def __init__(self):
		self.start = 0
		self.end = 0
		self.size = 0
		self.id = None
		self.data = None

	def __repr__(self):
		outtxt = '< '
		outtxt += 'ID: %s | ' % str(self.id)
		outtxt += 'Start: %s | ' % str(self.start)
		outtxt += 'Size: %s | ' % str(self.size)
		outtxt += '>'
		return outtxt

class chunk_part_size:
	def __init__(self):
		self.name_size = 4
		self.name_numeric = False
		self.name_endian = False
		self.size_size = 4
		self.size_endian = False

def chunk_part_read(reader, do_data, sizedata):
	if sizedata is None: sizedata = chunk_part_size()
	if reader.remaining()>=(sizedata.name_size+sizedata.size_size):
		part_obj = chunk_part_data()
		if not sizedata.name_numeric: part_obj.id = reader.raw(sizedata.name_size)
		else: part_obj.id = reader.int_ud(sizedata.name_size, sizedata.name_endian)
		part_obj.size = reader.int_ud(sizedata.size_size, sizedata.size_endian)
		part_obj.start = reader.tell_real()
		part_obj.end = part_obj.start+part_obj.size
		if part_obj.size<=reader.remaining():
			if do_data: part_obj.data = reader.raw(part_obj.size)
			return part_obj

def chunk_part_read_all(reader, sizedata):
	while reader.remaining():
		out = chunk_part_read(reader, 1, sizedata)
		if out is not None: yield out
		else: break

def chunk_part_read_all_iso(reader, sizedata):
	while reader.remaining():
		part_obj = chunk_part_read(reader, 0, sizedata)
		if part_obj is not None: 
			reader.isolate_size(part_obj.size)
			yield part_obj
			reader.isolate_end()
		else: break

def chunk_part_read_end_iso(reader, sizedata, cus_end):
	while reader.tell_real()<cus_end:
		part_obj = chunk_part_read(reader, 0, sizedata)
		if part_obj is not None: 
			reader.isolate_size(part_obj.size)
			yield part_obj
			reader.isolate_end()
		else: break