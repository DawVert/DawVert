# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

from external.easybinrw import easybinrw

class vst3_main:
	def __init__(self):
		self.version = 1
		self.uuid = '00000000000000000000000000000000'
		self.data = b''

	def read_file(self, fxfile):
		ebrw_readstr = self.ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(fxfile)
		self.parse(ebrw_readstr)

	def parse(self, ebrw_readstr):
		ebrw_readstr.magic_check(b'VST3')
		self.version = ebrw_readstr.uint32()
		self.uuid = ebrw_readstr.string(32)
		size = ebrw_readstr.uint32()
		ebrw_readstr.skip(4)
		self.data = ebrw_readstr.raw(size)

	def write(self, ebrw_writestr):
		ebrw_writestr.raw(b'VST3')
		ebrw_writestr.int_u32(self.version)
		ebrw_writestr.string(self.uuid, 32)
		ebrw_writestr.int_u32(len(self.data))
		ebrw_writestr.int_u32(0)
		ebrw_writestr.raw(self.data)

	def write_to_file(self, output_file):
		ebrw_writestr = easybinrw.binwrite()
		self.write(ebrw_writestr)
		ebrw_writestr.to_file(output_file)
