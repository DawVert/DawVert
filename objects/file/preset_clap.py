# SPDX-FileCopyrightText: 2025 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

from external.easybinrw import easybinrw

class clap_preset:
	def __init__(self):
		self.id = ''
		self.data = b''

	def parse(self, ebrw_readstr):
		ebrw_readstr.magic_check(b'clap')
		self.id = ebrw_readstr.string_i32_b()
		self.data = ebrw_readstr.rest()

	def read_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)
		self.parse(ebrw_readstr)

	def read_raw(self, indata):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_data(indata)
		self.parse(ebrw_readstr)

	def write(self, ebrw_writestr):
		ebrw_writestr.raw(b'clap')
		ebrw_writestr.string_i32_b(self.id)
		ebrw_writestr.raw(self.data)

	def write_to_file(self, output_file):
		ebrw_writestr = easybinrw.binwrite()
		self.write(ebrw_writestr)
		ebrw_writestr.to_file(output_file)

	def write_to_raw(self):
		ebrw_writestr = easybinrw.binwrite()
		self.write(ebrw_writestr)
		return ebrw_writestr.getvalue()
