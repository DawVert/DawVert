# SPDX-FileCopyrightText: 2025 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import struct
from external.easybinrw import easybinrw
from functions import data_bytes

class vst2_fxBank:
	def __init__(self, ebrw_readstr):
		self.fourid = 0
		self.version = 0
		self.num_programs = 0
		self.current_program = 0
		self.programs = []
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.fourid = ebrw_readstr.int_u32_b()
		ebrw_readstr.skip(4)
		self.num_programs = ebrw_readstr.int_u32_b()
		self.current_program = ebrw_readstr.int_u32_b()
		ebrw_readstr.skip(124)
		for _ in range(self.num_programs):
			vers = ebrw_readstr.int_u32_b()
			size = ebrw_readstr.int_u32_b()
			program_obj = vst2_program()
			program_obj.parse(ebrw_readstr, size)
			self.programs.append([vers, program_obj])

	def write(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u32_b(self.fourid)
		ebrw_writestr.int_u32_b(1)
		ebrw_writestr.int_u32_b(len(self.programs))
		ebrw_writestr.int_u32_b(self.current_program)
		ebrw_writestr.raw(b'\x00'*124)
		for vers, program_obj in self.programs:
			progd = program_obj.write()
			ebrw_writestr.int_u32_b(vers)
			ebrw_writestr.int_u32_b(len(progd))
			ebrw_writestr.raw(progd)
		return ebrw_writestr.getvalue()

class vst2_fxChunkSet_bank:
	def __init__(self, ebrw_readstr):
		self.fourid = 0
		self.version = 0
		self.num_programs = 0
		self.chunk = b''
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.fourid = ebrw_readstr.int_u32_b()
		self.version = ebrw_readstr.int_u32_b()
		self.num_programs = ebrw_readstr.int_u32_b()
		ebrw_readstr.skip(128)
		self.chunk = ebrw_readstr.raw(ebrw_readstr.int_u32_b())

	def write(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u32_b(self.fourid)
		ebrw_writestr.int_u32_b(self.version)
		ebrw_writestr.int_u32_b(self.num_programs)
		ebrw_writestr.raw(b'\x00'*128)
		ebrw_writestr.int_u32_b(len(self.chunk))
		ebrw_writestr.raw(self.chunk)
		return ebrw_writestr.getvalue()

class vst2_fxChunkSet:
	def __init__(self, ebrw_readstr):
		self.fourid = 0
		self.version = 0
		self.num_programs = 0
		self.prgname = ''
		self.chunk = b''
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.fourid = ebrw_readstr.int_u32_b()
		self.version = ebrw_readstr.int_u32_b()
		self.num_programs = ebrw_readstr.int_u32_b()
		try:
			self.prgname = ebrw_readstr.string(28)
		except:
			pass
		self.chunk = ebrw_readstr.raw(ebrw_readstr.int_u32_b())

	def write(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u32_b(self.fourid)
		ebrw_writestr.int_u32_b(self.version)
		ebrw_writestr.int_u32_b(self.num_programs)
		ebrw_writestr.string(self.prgname, 28)
		ebrw_writestr.int_u32_b(len(self.chunk))
		ebrw_writestr.raw(self.chunk)
		return ebrw_writestr.getvalue()

class vst2_fxProgram:
	def __init__(self, ebrw_readstr):
		self.fourid = 0
		self.version = 0
		self.num_params = 0
		self.prgname = ''
		self.params = []
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.fourid = ebrw_readstr.int_u32_b()
		self.version = ebrw_readstr.int_u32_b()
		self.num_params = ebrw_readstr.int_u32_b()
		self.prgname = ebrw_readstr.string(28)
		self.params = ebrw_readstr.list_float_b(self.num_params)

	def write(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u32_b(self.fourid)
		ebrw_writestr.int_u32_b(self.version)
		ebrw_writestr.int_u32_b(self.num_params)
		ebrw_writestr.string(self.prgname, 28)
		ebrw_writestr.list_float_b(self.params, self.num_params)
		return ebrw_writestr.getvalue()

class vst2_program:
	def __init__(self):
		self.type = 0
		self.data = None

	def set_fxChunkSet(self, ebrw_readstr):
		self.type = 1
		self.data = vst2_fxChunkSet(ebrw_readstr)
		return self.data

	def set_fxProgram(self, ebrw_readstr):
		self.type = 2
		self.data = vst2_fxProgram(ebrw_readstr)
		return self.data

	def set_fxBank(self, ebrw_readstr):
		self.type = 3
		self.data = vst2_fxBank(ebrw_readstr)
		return self.data

	def set_fxChunkSet_bank(self, ebrw_readstr):
		self.type = 4
		self.data = vst2_fxChunkSet_bank(ebrw_readstr)
		return self.data

	def parse(self, ebrw_readstr, size):
		if size:
			ebrw_readstr.isolate_size(size)
			ccnk_type = ebrw_readstr.raw(4)
			ccnk_size = ebrw_readstr.int_u32_b()
			if ccnk_type == b'FPCh': self.set_fxChunkSet(ebrw_readstr)
			elif ccnk_type == b'FxCk': self.set_fxProgram(ebrw_readstr)
			elif ccnk_type == b'FxBk': self.set_fxBank(ebrw_readstr)
			elif ccnk_type == b'FBCh': self.set_fxChunkSet_bank(ebrw_readstr)
			ebrw_readstr.isolate_end()
		else:
			ccnk_type = ebrw_readstr.raw(4)
			ccnk_size = ebrw_readstr.int_u32_b()
			if ccnk_type == b'FPCh': self.set_fxChunkSet(ebrw_readstr)
			elif ccnk_type == b'FxCk': self.set_fxProgram(ebrw_readstr)
			elif ccnk_type == b'FxBk': self.set_fxBank(ebrw_readstr)
			elif ccnk_type == b'FBCh': self.set_fxChunkSet_bank(ebrw_readstr)

	def write(self):
		ccnk_type = b'    '
		ccnk_data = b''
		if self.type == 1: 
			ccnk_type = b'FPCh'
			ccnk_data = self.data.write()
		if self.type == 2: 
			ccnk_type = b'FxCk'
			ccnk_data = self.data.write()
		if self.type == 3: 
			ccnk_type = b'FxBk'
			ccnk_data = self.data.write()
		if self.type == 4: 
			ccnk_type = b'FBCh'
			ccnk_data = self.data.write()
		return struct.pack('>4sI', ccnk_type, 1) + ccnk_data

class vst2_main:
	def __init__(self):
		self.program = vst2_program()

	def parse(self, ebrw_readstr):
		if ebrw_readstr.read(4) == b'CcnK':
			size = ebrw_readstr.int_u32_b()
			self.program.parse(ebrw_readstr, size)

	def load_from_file(self, inputfile):
		self.ebrw_readstr = easybinrw.binread()
		self.ebrw_readstr.load_file(inputfile)
		self.parse(self.ebrw_readstr)

	def load_raw(self, in_bytes):
		self.ebrw_readstr = easybinrw.binread()
		self.ebrw_readstr.load_data(in_bytes)
		self.parse(self.ebrw_readstr)

	def write(self, ebrw_writestr):
		ccnk__ebrw_writestr = easybinrw.binwrite()
		ccnk__ebrw_writestr.raw(self.program.write())
		CcnK_value = ccnk__ebrw_writestr.getvalue()

		ebrw_writestr.raw(b'CcnK')
		ebrw_writestr.int_u32_b(len(CcnK_value))
		ebrw_writestr.raw(CcnK_value)
			
	def write_to_file(self, output_file):
		ebrw_writestr = easybinrw.binwrite()
		self.write(ebrw_writestr)
		ebrw_writestr.to_file(output_file)

	def write_to_raw(self):
		ebrw_writestr = easybinrw.binwrite()
		self.write(ebrw_writestr)
		return ebrw_writestr.getvalue()