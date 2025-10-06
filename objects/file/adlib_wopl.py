# SPDX-FileCopyrightText: 2025 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

from objects.inst_params import fm_opl
from external.easybinrw import easybinrw

def read_inst(ebrw_readstr, oplo, isbank):
	oplo.name = ebrw_readstr.string(32, encoding='ascii')
	oplo.key_offs1 = ebrw_readstr.int_u16()
	oplo.key_offs2 = ebrw_readstr.int_u16()
	oplo.vel_offset = ebrw_readstr.int_s8()
	oplo.second_detune = ebrw_readstr.int_s8()
	oplo.perc_key = ebrw_readstr.int_u8()
	bitflags = ebrw_readstr.int_u8()
	if not bitflags&1: oplo.numops = 2
	if bitflags&2: oplo.pseudo4 = True
	if bitflags&4: oplo.is_blank = True
	oplo.perc_type = bitflags>>4
	oplo.fmfb1(ebrw_readstr.int_u8())
	oplo.fmfb2(ebrw_readstr.int_u8())
	for x in oplo.ops:
		x.avekf(ebrw_readstr.int_u8())
		x.ksl_lvl(ebrw_readstr.int_u8())
		x.att_dec(ebrw_readstr.int_u8())
		x.sus_rel(ebrw_readstr.int_u8())
		x.waveform = ebrw_readstr.int_u8()

class opli_file:
	def __init__(self):
		self.version = 0
		self.patch = fm_opl.opl_inst()

	def read_file(self, oplifile):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(oplifile)
		ebrw_readstr.magic_check(b'WOPL3-INST\x00')
		self.version = ebrw_readstr.int_u16()
		self.patch.perc_on = bool(ebrw_readstr.int_u8())
		read_inst(ebrw_readstr, self.patch, False)
