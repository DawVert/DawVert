# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

from external.easybinrw import easybinrw

class dx_preset:
	def __init__(self):
		self.id = ''
		self.data = b''

	def read_file(self, fxfile):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(fxfile)
		self.parse(ebrw_readstr)

	def read_raw(self, bytesd):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_data(bytesd)
		self.parse(ebrw_readstr)

	def parse(self, ebrw_readstr):
		self.id = ebrw_readstr.raw(16).hex()
		dsize = ebrw_readstr.int_u32()
		self.data = ebrw_readstr.raw(dsize)

	def write(self, ebrw_writestr):
		ebrw_writestr.raw(bytes.fromhex(self.id))
		ebrw_writestr.int_u32(len(self.data))
		ebrw_writestr.raw(self.data)

	def write_to_file(self, output_file):
		ebrw_writestr = easybinrw.binwrite()
		self.write(ebrw_writestr)
		ebrw_writestr.to_file(output_file)

	def write_to_raw(self):
		ebrw_writestr = easybinrw.binwrite()
		self.write(ebrw_writestr)
		return ebrw_writestr.getvalue()
