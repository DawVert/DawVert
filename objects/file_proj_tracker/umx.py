# SPDX-FileCopyrightText: 2024 SatyrDiamond and B0ney
# SPDX-License-Identifier: GPL-3.0-or-later

from external.easybinrw import easybinrw
from objects.exceptions import ProjectFileParserException
import logging

MINIMUM_VERSION = 61

def get_entry(version, ebrw_readstr):
	if version < 64: return ebrw_readstr.string_t()
	else: return ebrw_readstr.string_i8()

# https://wiki.beyondunreal.com/Legacy:Package_File_Format/Data_Details
def read_compact_index(ebrw_readstr):
	output = 0
	signed = False

	for i in range(5):
		x = ebrw_readstr.int_u8()

		if i == 0:
			if (x & 0x80) > 0: signed = True
			output |= x & 0x3F
			if x & 0x40 == 0: break

		elif i == 4:
			output |= (x & 0x1F) << (6 + (3 * 7))
		else:
			output |= (x & 0x7F) << (6 + ((i - 1) * 7))
			if x & 0x80 == 0: break

	if signed: output *= -1

	return output

class umx_file:
	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)

		try: ebrw_readstr.magic_check(b'\xc1\x83\x2a\x9e')
		except ValueError as t: raise ProjectFileParserException('umx: '+str(t))

		self.version = ebrw_readstr.int_u32()

		if self.version < MINIMUM_VERSION: raise ProjectFileParserException("umx: UMX versions below {MINIMUM_VERSION} are not supported")

		ebrw_readstr.skip(4)
		name_count = ebrw_readstr.int_u32()
		name_offset = ebrw_readstr.int_u32()
		ebrw_readstr.skip(4)
		export_offset = ebrw_readstr.int_u32()

		ebrw_readstr.seek(name_offset) # Jump to the name table

		self.nametable = []
		for _ in range(name_count):
			self.nametable.append(get_entry(self.version, ebrw_readstr))
			ebrw_readstr.skip(4)

		ebrw_readstr.seek(export_offset)
	
		self.classindex = read_compact_index(ebrw_readstr)
		self.superindex = read_compact_index(ebrw_readstr)
		self.group = ebrw_readstr.int_u32()
		self.objname = read_compact_index(ebrw_readstr)
		self.objflags = ebrw_readstr.flags_i32()

		serial_size = read_compact_index(ebrw_readstr)

		if serial_size == 0: raise ProjectFileParserException("umx: UMX doesn't contain anything")
		
		serial_offset = read_compact_index(ebrw_readstr)
		ebrw_readstr.seek(serial_offset)  
		self.nameindex = read_compact_index(ebrw_readstr)
	
		if self.version > MINIMUM_VERSION: ebrw_readstr.skip(4)
	
		objsizefield = read_compact_index(ebrw_readstr)
		inner_size = read_compact_index(ebrw_readstr)
		self.outdata = ebrw_readstr.raw(inner_size)

		return True