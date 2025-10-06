# SPDX-FileCopyrightText: 2025 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

from objects.inst_params import fm_opl
from external.easybinrw import easybinrw

class bnk_file:
	def __init__(self):
		self.index = []
		self.used = []
		self.names = []
		self.num_used = 0
		self.offset_data = 0
		self.ebrw_readstr = None

	def read_file(self, oplifile):
		bio_in = open(oplifile, 'rb')

		ebrw_readstr = self.ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(oplifile)

		verMajor = ebrw_readstr.int_u8()
		verMinor = ebrw_readstr.int_u8()
		ebrw_readstr.magic_check(b'ADLIB-')
		self.num_used = ebrw_readstr.int_u16()
		num_insts = ebrw_readstr.int_u16()
		offset_name = ebrw_readstr.int_u32()
		self.offset_data = ebrw_readstr.int_u32()
		ebrw_readstr.skip(8)

		ebrw_readstr.seek(offset_name)
		for _ in range(num_insts):
			self.index.append(ebrw_readstr.int_u16())
			self.used.append(ebrw_readstr.int_u8())
			self.names.append(ebrw_readstr.string(9))

	def get_inst_index(self, num):
		instindex = self.index[num]
		instused = self.used[num]
		instname = self.names[num]

		opli = fm_opl.opl_inst()
		opli.set_opl2()

		if instused and self.ebrw_readstr:
			opli.name = instname
			instloc = (30*(instindex))+self.offset_data
			self.ebrw_readstr.seek(instloc)
			opli.perc_mode = bool(self.ebrw_readstr.int_u8())
			opli.perc_voicenum = self.ebrw_readstr.int_u8()
			for n in range(2):
				opd = opli.ops[n]
				opd.ksl = self.ebrw_readstr.int_u8()
				opd.freqmul = self.ebrw_readstr.int_u8()
				fb = self.ebrw_readstr.int_u8()
				opd.env_attack = self.ebrw_readstr.int_u8()
				opd.env_sustain = self.ebrw_readstr.int_u8()
				opd.sustained = bool(self.ebrw_readstr.int_u8())
				opd.env_decay = self.ebrw_readstr.int_u8()
				opd.env_release = self.ebrw_readstr.int_u8()
				opd.level = self.ebrw_readstr.int_u8()
				opd.tremolo = bool(self.ebrw_readstr.int_u8())
				opd.vibrato = bool(self.ebrw_readstr.int_u8())
				opd.ksr = bool(self.ebrw_readstr.int_u8())
				con = self.ebrw_readstr.int_u8()

				if n == 0: 
					opli.feedback_1 = fb
					opli.fm_1 = not bool(con)

			for n in range(2): opli.ops[1-n].waveform = self.ebrw_readstr.int_u8()

		else: opli.is_blank = True

		return opli