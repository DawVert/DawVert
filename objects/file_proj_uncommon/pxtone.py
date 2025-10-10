# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from external.easybinrw import easybinrw
from objects.data_bytes import dynbytearr
from objects.exceptions import ProjectFileParserException
import numpy as np
import struct
import logging

VERBOSE = False
DEBUG_IN_OUT = False

logger_projparse = logging.getLogger('projparse')

class ptcop_delay:
	def __init__(self):
		self.delay_voice = 0
		self.delay_group = 0
		self.delay_rate = 0
		self.delay_freq = 0

class ptcop_overdrive:
	def __init__(self):
		self.xxx = 0
		self.group = 0
		self.cut = 0
		self.amp = 0
		self.yyy = 0

class ptcop_voice:
	def __init__(self):
		self.type = None
		self.name = ''

		self.ch = None
		self.bits = None
		self.basic_key_field = 60
		self.sps2 = None
		self.key_correct = None
		self.samples = None
		self.hz = None
		self.channels = None
		self.data = None

class ptcop_unit:
	def __init__(self):
		self.name = None

event_premake = dynbytearr.dynbytearr_premake([
	('position', np.uint32),
	('unitnum', np.uint8),
	('eventnum', np.uint8),
	('value', np.uint32),
	('d_position', np.uint32),
	])

class ptcop_song:
	def __init__(self):
		self.comment = ''
		self.title = ''
		self.events = event_premake.create()
		self.units = []
		self.voices = {}
		self.delays = []
		self.overdrives = []

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)

		self.header = ebrw_readstr.raw(16)

		ebrw_readstr.skip(4)

		voicenum = 0

		while ebrw_readstr.remaining():
			chunk_id = ebrw_readstr.raw(8)
			chunk_size = ebrw_readstr.int_u32()

			if chunk_id == b'MasterV5':
				self.unk1 = ebrw_readstr.int_u16()
				self.beat = ebrw_readstr.int_u8()
				self.unk2 = ebrw_readstr.int_u16()
				self.beattempo = struct.unpack(">f", struct.pack("I", int.from_bytes(ebrw_readstr.read(2), "big")))[0]
				self.repeat = ebrw_readstr.int_u32()
				self.last = ebrw_readstr.int_u32()

			elif chunk_id == b'Event V5':
				ev_cur = self.events.create_cursor()
				for _ in range(ebrw_readstr.int_u32()):
					ev_cur.add()
					ev_cur['position'] = ebrw_readstr.varint()
					ev_cur['unitnum'] = ebrw_readstr.int_u8()
					ev_cur['eventnum'] = ebrw_readstr.int_u8()
					ev_cur['value'] = ebrw_readstr.varint()

			elif chunk_id == b'effeDELA':
				ebrw_readstr.skip(2)
				delay_obj = ptcop_delay()
				delay_obj.unit = ebrw_readstr.int_u16()
				delay_obj.group = ebrw_readstr.int_u16()
				delay_obj.rate = ebrw_readstr.int_u16()
				delay_obj.freq = ebrw_readstr.float()
				self.delays.append(delay_obj)
				if VERBOSE: print('effeDELA:', delay_obj.unit, delay_obj.group)

			elif chunk_id == b'effeOVER':
				overdrive_obj = ptcop_overdrive()
				overdrive_obj.xxx = ebrw_readstr.int_u16()
				overdrive_obj.group = ebrw_readstr.int_u16()
				overdrive_obj.cut = ebrw_readstr.float()
				overdrive_obj.amp = ebrw_readstr.float()
				overdrive_obj.yyy = ebrw_readstr.float()
				self.overdrives.append(overdrive_obj)
				if VERBOSE: print('effeOVER:', overdrive_obj.group)

			elif chunk_id == b'mateOGGV':
				voice_obj = ptcop_voice()
				ebrw_readstr.skip(3)
				voice_obj.type = 'ogg'
				voice_obj.basic_key_field = ebrw_readstr.int_u8()
				voice_obj.sps2 = ebrw_readstr.flags_i32()
				voice_obj.key_correct = ebrw_readstr.float()
				voice_obj.channels = ebrw_readstr.int_u32()
				voice_obj.hz = ebrw_readstr.int_u32()
				voice_obj.samples = ebrw_readstr.int_u32()
				voice_obj.data = ebrw_readstr.raw(ebrw_readstr.int_u32())
				self.voices[voicenum] = voice_obj
				if VERBOSE: print('mateOGGV:', voicenum)
				voicenum += 1

			elif chunk_id == b'matePCM ':
				voice_obj = ptcop_voice()
				ebrw_readstr.skip(3)
				voice_obj.type = 'pcm'
				voice_obj.basic_key_field = ebrw_readstr.int_u8()
				voice_obj.sps2 = ebrw_readstr.flags_i32()
				voice_obj.ch = ebrw_readstr.int_u16()
				voice_obj.bits = ebrw_readstr.int_u16()
				voice_obj.hz = ebrw_readstr.int_u32()
				voice_obj.key_correct = ebrw_readstr.float()
				voice_obj.samples = ebrw_readstr.int_u32()//(voice_obj.bits//8)
				voice_obj.data = ebrw_readstr.raw((voice_obj.bits//8) * voice_obj.samples)
				self.voices[voicenum] = voice_obj
				if VERBOSE: print('mate PCM:', voicenum)
				voicenum += 1

			elif chunk_id == b'matePTV ':
				voice_obj = ptcop_voice()
				voice_obj.type = 'ptvoice'
				ebrw_readstr.skip(4)
				voice_obj.key_correct = ebrw_readstr.float()
				datasize = ebrw_readstr.int_u32()
				voice_obj.data = ebrw_readstr.raw(datasize)
				self.voices[voicenum] = voice_obj
				if VERBOSE: print('mate PTV:', voicenum)
				voicenum += 1

			elif chunk_id == b'matePTN ':
				voice_obj = ptcop_voice()
				voice_obj.type = 'ptnoise'
				ebrw_readstr.skip(8)
				voice_obj.key_correct = ebrw_readstr.float()
				ebrw_readstr.skip(4)
				voice_obj.data = ebrw_readstr.raw(chunk_size-16)
				self.voices[voicenum] = voice_obj
				if VERBOSE: print('mate PTN:', voicenum)
				voicenum += 1

			elif chunk_id == b'assiWOIC':
				voice_num = ebrw_readstr.int_u32()
				self.voices[voice_num].name = ebrw_readstr.string(chunk_size-4, encoding="shift-jis")
				if VERBOSE: print('assiWOIC:', voice_num, self.voices[voice_num].name)

			elif chunk_id == b'assiUNIT':
				unit_num = ebrw_readstr.int_u32()
				self.units[unit_num].name = ebrw_readstr.string(chunk_size-4, encoding="shift-jis")
				if VERBOSE: print('assiUNIT:', unit_num, self.units[unit_num].name)

			elif chunk_id == b'num UNIT':
				self.units = [ptcop_unit() for _ in range(ebrw_readstr.int_u32())]
				if VERBOSE: print('num UNIT:', self.voices[voice_num].name)

			elif chunk_id == b'textCOMM':
				self.comment = ebrw_readstr.string(chunk_size, encoding="shift-jis")
				if VERBOSE: print('textCOMM:', self.comment)

			elif chunk_id == b'textNAME':
				self.title = ebrw_readstr.string(chunk_size, encoding="shift-jis")
				if VERBOSE: print('textNAME:', self.title)

			elif chunk_id == b'pxtoneND':
				break

			else: raise ProjectFileParserException('pxtone: unknown chunk: '+str(chunk_id))

		self.events.clean()

		return True

	def postprocess(self):
		curpos = 0
		for x in self.events:
			curpos += x['position']
			x['d_position'] = curpos