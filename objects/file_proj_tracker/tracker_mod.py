# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from external.easybinrw import easybinrw
from objects.exceptions import ProjectFileParserException
import numpy as np

import logging
logger_projparse = logging.getLogger('projparse')

DEBUG_IN_OUT = False

class mod_sample:
	def __init__(self, ebrw_readstr): 
		self.name = ebrw_readstr.string(22, encoding="ascii", errors="ignore") if ebrw_readstr else ''
		self.length = ebrw_readstr.int_u16() if ebrw_readstr else 0
		self.finetune = ebrw_readstr.int_u8() if ebrw_readstr else 0
		self.default_vol = ebrw_readstr.int_u8() if ebrw_readstr else 0
		self.loop_start = ebrw_readstr.int_u16() if ebrw_readstr else 0
		self.loop_length = ebrw_readstr.int_u16() if ebrw_readstr else 0
		self.data = None

	def write(self, ebrw_writestr):
		ebrw_writestr.string(self.name, 22)
		ebrw_writestr.int_u16(self.length)
		ebrw_writestr.int_u8(self.finetune)
		ebrw_writestr.int_u8(self.default_vol)
		ebrw_writestr.int_u16(self.loop_start)
		ebrw_writestr.int_u16(self.loop_length)

pattern_dt = np.dtype('>H')

class mod_pattern:
	def __init__(self, ebrw_readstr, num_chans):
		if ebrw_readstr:
			self.data = np.frombuffer(ebrw_readstr.raw(64*num_chans*4), pattern_dt).reshape(64, num_chans, 2)
		else:
			self.data = np.empty((64, num_chans, 2), dtype=pattern_dt)

class mod_song:
	def __init__(self):
		self.title = ''
		self.samples = []
		self.tag = None
		self.num_chans = None
		self.patterns = []
		self.extravalue = 0

	def load_from_raw(self, input_file, IGNORE_ERRORS):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_data(input_file)
		ebrw_readstr.state.endian = True
		return self.load(ebrw_readstr, IGNORE_ERRORS)

	def load_from_file(self, input_file, IGNORE_ERRORS):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)
		ebrw_readstr.state.endian = True

		self.load(ebrw_readstr, IGNORE_ERRORS)

		if DEBUG_IN_OUT:
			self.save_to_file('debug_out.mod')
			try:
				import shutil
				shutil.copy(input_file, 'debug_in.mod')
			except:
				pass

		return True

	def load(self, ebrw_readstr, IGNORE_ERRORS):
		from objects.file_proj_tracker import tracker_mod as proj_mod

		self.title = ebrw_readstr.string(20, encoding="ascii", errors="ignore")
		logger_projparse.info('mod: Song Name: ' + str(self.title))
		for _ in range(31):
			sample_obj = mod_sample(ebrw_readstr)
			if sample_obj.finetune > 15: 
				if not IGNORE_ERRORS:
					raise ProjectFileParserException('mod: sample finetune over 15')
				else:
					logger_projparse.warning('mod: sample finetune over 15')
			self.samples.append(sample_obj)
		num_orders = ebrw_readstr.int_u8()
		self.extravalue = ebrw_readstr.int_u8()
		if not num_orders:
			if IGNORE_ERRORS:
				self.l_order = ebrw_readstr.list_int_s8(128)
			else:
				raise ProjectFileParserException('mod: Pattern Order is 0')
		else:
			self.l_order = ebrw_readstr.list_int_s8(128)[0:num_orders]
		self.num_patterns = max(self.l_order)

		self.tag = ebrw_readstr.string(4, errors="ignore")
		self.num_chans = 4

		logger_projparse.info('mod: Sample Tag: ' + str(self.tag))
		logger_projparse.info('mod: Channels: ' + str(self.num_chans))

		if self.tag == '1CHN': self.num_chans = 1
		if self.tag == '6CHN': self.num_chans = 6
		if self.tag == '8CHN': self.num_chans = 8
		if self.tag == 'CD81': self.num_chans = 8
		if self.tag == 'OKTA': self.num_chans = 8
		if self.tag == 'OCTA': self.num_chans = 8
		if self.tag == '6CHN': self.num_chans = 6
		if self.tag[-2:] == 'CH': self.num_chans = int(self.tag[:2])
		if self.tag == '2CHN': self.num_chans = 2
		if self.tag[-2:] == 'CN': self.num_chans = int(self.tag[:2])
		if self.tag == 'TDZ1': self.num_chans = 1
		if self.tag == 'TDZ2': self.num_chans = 2
		if self.tag == 'TDZ3': self.num_chans = 3
		if self.tag == '5CHN': self.num_chans = 5
		if self.tag == '7CHN': self.num_chans = 7
		if self.tag == '9CHN': self.num_chans = 9
		if self.tag == 'FLT4': self.num_chans = 4
		if self.tag == 'FLT8': self.num_chans = 8

		self.patterns = [mod_pattern(ebrw_readstr, self.num_chans) for _ in range(self.num_patterns+1)]
		for sample_obj in self.samples: sample_obj.data = ebrw_readstr.raw(sample_obj.length*2)
		return True

	def write(self, ebrw_writestr):
		ebrw_writestr.state.endian = True
		ebrw_writestr.string(self.title, 20)
		for x in self.samples: x.write(ebrw_writestr)
		ebrw_writestr.int_u8(len(self.l_order))
		ebrw_writestr.int_u8(self.extravalue)
		ebrw_writestr.list_int_s8(self.l_order, 128)
		ebrw_writestr.string(self.tag, 4)
		for p in self.patterns: ebrw_writestr.raw(p.data.tobytes())
		for s in self.samples: ebrw_writestr.raw(s.data)

	def save_to_file(self, output_file):
		ebrw_writestr = easybinrw.binwrite()
		self.write(ebrw_writestr)
		ebrw_writestr.to_file(output_file)
