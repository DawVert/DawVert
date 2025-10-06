# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from external.easybinrw import easybinrw
from external.easybinrw import chunked
from objects.exceptions import ProjectFileParserException
import numpy as np

import logging
logger_projparse = logging.getLogger('projparse')

# --------------------------------------------------------- Machine ---------------------------------------------------------

class caustic_machine_SSYN:
	def __init__(self, ebrw_readstr):
		self.controls = caustic_controls()
		self.patterns = caustic_patterns()

		self.unknown1 = ebrw_readstr.int_u16()
		self.unknown2 = ebrw_readstr.int_u8()
		self.unknown3 = ebrw_readstr.int_u8()
		self.controls.parse(ebrw_readstr)
		self.presetname = ebrw_readstr.string(32)
		self.presetpath = ebrw_readstr.string_i32()
		self.unknown4 = ebrw_readstr.int_u32()
		self.customwaveform1 = ebrw_readstr.list_int_s16(660)
		self.customwaveform2 = ebrw_readstr.list_int_s16(660)
		self.poly = ebrw_readstr.int_u32()
		self.osc1_mode = ebrw_readstr.int_u32()
		self.osc2_mode = ebrw_readstr.int_u32()
		self.patterns.parse(ebrw_readstr)

class caustic_machine_BLNE:
	def __init__(self, ebrw_readstr):
		self.controls = caustic_controls()
		self.patterns = caustic_patterns()

		self.unknown1 = ebrw_readstr.int_u16()
		self.unknown2 = ebrw_readstr.int_u8()
		self.unknown3 = ebrw_readstr.int_u8()
		self.controls.parse(ebrw_readstr)
		self.presetname = ebrw_readstr.string(32)
		self.presetpath = ebrw_readstr.string_i32()
		self.keyboard_octave = ebrw_readstr.int_u32()
		self.patterns.parse(ebrw_readstr)
		self.legacy_glide = ebrw_readstr.float()
		self.customwaveform1 = ebrw_readstr.list_int_s16(660)

class caustic_machine_PADS:
	def __init__(self, ebrw_readstr):
		self.controls = caustic_controls()
		self.patterns = caustic_patterns()
		
		self.controls.parse(ebrw_readstr)
		self.presetname = ebrw_readstr.string(32)
		self.presetpath = ebrw_readstr.string_i32()
		self.keyboard_octave = ebrw_readstr.int_u32()
		self.unknown1 = ebrw_readstr.int_u32()
		self.visual = ebrw_readstr.int_u32()
		self.harm1 = ebrw_readstr.list_float(24)
		self.harm1vol = ebrw_readstr.float()
		self.harm2 = ebrw_readstr.list_float(24)
		self.harm2vol = ebrw_readstr.float()
		self.patterns.parse(ebrw_readstr)

class caustic_machine_ORGN:
	def __init__(self, ebrw_readstr):
		self.controls = caustic_controls()
		self.patterns = caustic_patterns()
		
		self.controls.parse(ebrw_readstr)
		self.presetname = ebrw_readstr.string(32)
		self.presetpath = ebrw_readstr.string_i32()
		self.keyboard_octave = ebrw_readstr.int_u32()
		self.unknown1 = ebrw_readstr.int_u32()

class caustic_machine_FMSN:
	def __init__(self, ebrw_readstr):
		self.controls = caustic_controls()
		self.patterns = caustic_patterns()
		
		self.unknown1 = ebrw_readstr.int_u16()
		self.unknown2 = ebrw_readstr.int_u8()
		self.unknown3 = ebrw_readstr.int_u8()
		self.controls.parse(ebrw_readstr)
		self.algorithm = ebrw_readstr.int_u32()
		self.poly = ebrw_readstr.int_u32()
		self.presetname = ebrw_readstr.string(32)
		self.presetpath = ebrw_readstr.string_i32()
		self.keyboard_octave = ebrw_readstr.int_u32()
		self.patterns.parse(ebrw_readstr)

class caustic_machine_KSSN:
	def __init__(self, ebrw_readstr):
		self.controls = caustic_controls()
		self.patterns = caustic_patterns()
		
		self.unknown1 = ebrw_readstr.int_u16()
		self.unknown2 = ebrw_readstr.int_u8()
		self.unknown3 = ebrw_readstr.int_u8()
		self.controls.parse(ebrw_readstr)
		self.presetname = ebrw_readstr.string(32)
		self.presetpath = ebrw_readstr.string_i32()
		self.keyboard_octave = ebrw_readstr.int_u32()
		self.patterns.parse(ebrw_readstr)

class caustic_machine_SAWS:
	def __init__(self, ebrw_readstr):
		self.controls = caustic_controls()
		self.patterns = caustic_patterns()
		
		self.unknown1 = ebrw_readstr.int_u16()
		self.unknown2 = ebrw_readstr.int_u8()
		self.unknown3 = ebrw_readstr.int_u8()
		self.controls.parse(ebrw_readstr)
		self.presetname = ebrw_readstr.string(32)
		self.presetpath = ebrw_readstr.string_i32()
		self.keyboard_octave = ebrw_readstr.int_u32()
		self.poly = ebrw_readstr.int_u32()
		self.patterns.parse(ebrw_readstr)

class caustic_machine_8SYN:
	def __init__(self, ebrw_readstr):
		self.controls = caustic_controls()
		self.patterns = caustic_patterns()
		
		self.unknown1 = ebrw_readstr.int_u16()
		self.unknown2 = ebrw_readstr.int_u8()
		self.unknown3 = ebrw_readstr.int_u8()
		self.controls.parse(ebrw_readstr)
		self.bitcode1 = ebrw_readstr.string(128)
		self.bitcode2 = ebrw_readstr.string(128)
		self.unknown4 = ebrw_readstr.int_u32()
		self.unknown5 = ebrw_readstr.int_u32()
		self.presetname = ebrw_readstr.string(32)
		self.presetpath = ebrw_readstr.string_i32()
		self.keyboard_octave = ebrw_readstr.int_u32()
		self.patterns.parse(ebrw_readstr)

class caustic_machine_BBOX_sample:
	def __init__(self, ebrw_readstr):
		self.name = ebrw_readstr.string(32)
		self.len = ebrw_readstr.int_u32()
		self.hz = ebrw_readstr.int_u32()
		self.chan = ebrw_readstr.int_u32()
		logger_projparse.info('caustic3: BBOX | len:'+str(self.len)+', hz:'+str(self.hz)+', ch:'+str(self.chan))
		self.data = ebrw_readstr.read((self.len*2)*self.chan)
		self.mute = 0
		self.solo = 0
		self.mutegroup = 0
		
class caustic_machine_BBOX:
	def __init__(self, ebrw_readstr):
		self.controls = caustic_controls()
		self.patterns = caustic_patterns()
		
		self.unknown1 = ebrw_readstr.int_u16()
		self.unknown2 = ebrw_readstr.int_u8()
		self.unknown3 = ebrw_readstr.int_u8()
		self.controls.parse(ebrw_readstr)
		self.patterns.parse(ebrw_readstr)
		ebrw_readstr.skip(4)
		self.presetpath = ebrw_readstr.string(256)
		ebrw_readstr.skip(4)
		self.samples = [caustic_machine_BBOX_sample(ebrw_readstr) for _ in range(8)]
		for _ in range(8):
			self.mute = ebrw_readstr.int_u8()
			self.solo = ebrw_readstr.int_u8()
			self.mutegroup = ebrw_readstr.int_u8()
		self.presetname = ebrw_readstr.string(32)
		self.presetpath = ebrw_readstr.string_i32()

class caustic_machine_VCDR_sample:
	def __init__(self, ebrw_readstr):
		self.name = ebrw_readstr.string(256)
		ebrw_readstr.skip(4)
		self.len = ebrw_readstr.int_u32()
		self.hz = ebrw_readstr.int_u32()
		self.data = ebrw_readstr.read(self.len*2)
		logger_projparse.info('caustic3: VCDR | len:'+str(self.len)+', hz:'+str(self.hz))
		
class caustic_machine_VCDR:
	def __init__(self, ebrw_readstr):
		self.controls = caustic_controls()
		self.patterns = caustic_patterns()
		
		self.unknown1 = ebrw_readstr.int_u16()
		self.unknown2 = ebrw_readstr.int_u8()
		self.unknown3 = ebrw_readstr.int_u8()
		self.controls.parse(ebrw_readstr)
		self.currentnumber = ebrw_readstr.int_u32()
		ebrw_readstr.read(28)
		ebrw_readstr.read(8)
		self.samples = [caustic_machine_VCDR_sample(ebrw_readstr) for _ in range(6)]

		self.keyboard_octave = ebrw_readstr.int_u32()
		self.patterns.parse(ebrw_readstr)

class caustic_machine_MDLR:
	def __init__(self, ebrw_readstr):
		self.controls = caustic_controls()
		self.patterns = caustic_patterns()
		self.slots = [caustic_modularslot() for x in range(16)]
		self.main = caustic_modularslot()
		self.connections = []
		
		for m in self.slots: m.slot_type = ebrw_readstr.int_u32()

		for m in self.slots: 
			if m.slot_type != 0:
				ebrw_readstr.magic_check(b'MCOM')
				m.params = ebrw_readstr.list_float(ebrw_readstr.int_u32()//4)

		ebrw_readstr.magic_check(b'MCOM')
		self.main.params = ebrw_readstr.list_float(ebrw_readstr.int_u32()//4)
		self.controls.parse(ebrw_readstr)
		ebrw_readstr.read(5)
		self.unknown1 = ebrw_readstr.int_u32()
		for linknum in range(ebrw_readstr.int_u32()): 
			self.connections.append( ebrw_readstr.list_int_u32(9) )

		self.patterns.parse(ebrw_readstr)

		self.presetname = ebrw_readstr.string(32)
		self.presetpath = ebrw_readstr.string_i32()

class caustic_machine_PCMS_sample:
	def __init__(self, ebrw_readstr):
		self.volume = ebrw_readstr.float()
		ebrw_readstr.skip(4)
		self.pan = ebrw_readstr.float()
		self.key_root = ebrw_readstr.int_u32()
		self.key_lo = ebrw_readstr.int_u32()
		self.key_hi = ebrw_readstr.int_u32()
		self.mode = ebrw_readstr.int_u32()
		self.start = ebrw_readstr.int_u32()
		self.end = ebrw_readstr.int_u32()-1
		self.path = ebrw_readstr.string(256)
		ebrw_readstr.skip(4)
		self.samp_size = ebrw_readstr.int_u32()
		self.samp_hz = ebrw_readstr.int_u32()
		ebrw_readstr.skip(4)
		self.samp_chan = ebrw_readstr.int_u32()
		self.samp_data = ebrw_readstr.read((self.samp_size*2)*self.samp_chan)

class caustic_machine_PCMS:
	def __init__(self, ebrw_readstr):
		self.controls = caustic_controls()
		self.patterns = caustic_patterns()

		self.unknown1 = ebrw_readstr.int_u16()
		self.unknown2 = ebrw_readstr.int_u8()
		self.unknown3 = ebrw_readstr.int_u8()
		self.controls.parse(ebrw_readstr)
		self.presetname = ebrw_readstr.string(32)
		self.presetpath = ebrw_readstr.string_i32()
		ebrw_readstr.skip(4)
		self.samples = [caustic_machine_PCMS_sample(ebrw_readstr) for _ in range(ebrw_readstr.int_u32())]
		ebrw_readstr.read(9)
		self.patterns.parse(ebrw_readstr)

# --------------------------------------------------------- MAIN ---------------------------------------------------------

class caustic_controls:
	def __init__(self):
		self.data = {}

	def parse(self, ebrw_readstr):
		ebrw_readstr.magic_check(b'CCOL')
		CCOL_size = ebrw_readstr.int_u32()
		ebrw_readstr.isolate_size(CCOL_size)
		for part_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, None):
			pid = ebrw_readstr.int_u32()
			self.data[pid] = ebrw_readstr.float()
		ebrw_readstr.isolate_end()
		logger_projparse.info('caustic3: CCOL | '+str(len(self.data))+' Controls')

class caustic_modularslot:
	def __init__(self):
		self.slot_type = 0
		self.params = []

class caustic_machine:
	machobjs = {
	'SSYN': caustic_machine_SSYN,
	'BLNE': caustic_machine_BLNE,
	'PADS': caustic_machine_PADS,
	'ORGN': caustic_machine_ORGN,
	'FMSN': caustic_machine_FMSN,
	'KSSN': caustic_machine_KSSN,
	'SAWS': caustic_machine_SAWS,
	'8SYN': caustic_machine_8SYN,
	'BBOX': caustic_machine_BBOX,
	'VCDR': caustic_machine_VCDR,
	'MDLR': caustic_machine_MDLR,
	'PCMS': caustic_machine_PCMS
	}

	def __init__(self):
		self.mach_id = 'NULL'
		self.name = ''
		self.data = None

	def parse(self, ebrw_readstr):
		if self.mach_id in caustic_machine.machobjs:
			self.data = caustic_machine.machobjs[self.mach_id](ebrw_readstr)

class caustic_mixer:
	def __init__(self):
		self.controls = caustic_controls()
		self.solo_mute = [0 for x in range(28)]
		self.controls = []
		self.chainnum = 0

	def parse(self, ebrw_readstr):
		ebrw_readstr.skip(4)
		controls = caustic_controls()
		controls.parse(ebrw_readstr)
		self.controls.append(controls)
		for n in range(14): self.solo_mute[(self.chainnum*2)+n] = ebrw_readstr.int_u8()
		self.chainnum += 7

class caustic_fxslot:
	def __init__(self):
		self.controls = caustic_controls()
		self.mode = 0
		self.fx_type = -1

	def parse(self, ebrw_readstr):
		self.fx_type = ebrw_readstr.int_u32()
		if self.fx_type == 0: #Delay
			self.controls.parse(ebrw_readstr)
			self.mode = ebrw_readstr.int_u32()
		if self.fx_type == 1: #Reverb
			self.controls.parse(ebrw_readstr)
		if self.fx_type == 2: #Distortion
			self.controls.parse(ebrw_readstr)
		if self.fx_type == 3: #Compresser
			self.controls.parse(ebrw_readstr)
			self.mode = ebrw_readstr.int_u32()
		if self.fx_type == 4: #Bitcrush
			self.controls.parse(ebrw_readstr)
		if self.fx_type == 5: #Flanger
			self.controls.parse(ebrw_readstr)
			self.mode = ebrw_readstr.int_u32()
		if self.fx_type == 6: #Phaser
			self.controls.parse(ebrw_readstr)
		if self.fx_type == 7: #Chorus
			self.controls.parse(ebrw_readstr)
			self.mode = ebrw_readstr.int_u32()
		if self.fx_type == 8: #AutoWah
			self.controls.parse(ebrw_readstr)
		if self.fx_type == 9: #Param EQ
			self.controls.parse(ebrw_readstr)
		if self.fx_type == 10: #Limiter
			self.controls.parse(ebrw_readstr)
		if self.fx_type == 11: #VInylSim
			self.controls.parse(ebrw_readstr)
		if self.fx_type == 12: #Comb
			self.controls.parse(ebrw_readstr)
		if self.fx_type == 14: #Cab Sim
			self.controls.parse(ebrw_readstr)
		if self.fx_type == 16: #StaticFlanger
			self.controls.parse(ebrw_readstr)
			self.mode = ebrw_readstr.int_u32()
		if self.fx_type == 17: #Filter
			self.controls.parse(ebrw_readstr)
			self.mode = ebrw_readstr.int_u32()
		if self.fx_type == 18: #Octaver
			self.controls.parse(ebrw_readstr)
		if self.fx_type == 19: #Vibrato
			self.controls.parse(ebrw_readstr)
			self.mode = ebrw_readstr.int_u32()
		if self.fx_type == 20: #Tremolo
			self.controls.parse(ebrw_readstr)
		if self.fx_type == 21: #AutoPan
			self.controls.parse(ebrw_readstr)

class caustic_fxchain:
	def __init__(self):
		self.chainnum = 0
		self.fxslots = [caustic_fxslot() for x in range(28)]
	def parse(self, ebrw_readstr):
		for n in range(14): 
			self.fxslots[n+self.chainnum].parse(ebrw_readstr)
		if self.chainnum == 0: ebrw_readstr.read(4)
		self.chainnum += 14

class caustic_master:
	def __init__(self):
		self.fxslots = [caustic_fxslot() for x in range(2)]
		self.controls = caustic_controls()
	def parse(self, ebrw_readstr):
		for n in range(2): self.fxslots[n].parse(ebrw_readstr)
		self.controls.parse(ebrw_readstr)

class caustic_autoblocks:
	def __init__(self):
		self.ctrl_id = 0
		self.smooth = 0.5
		self.data = []

class caustic_pattern:
	def __init__(self):
		self.measures = 0
		self.numnote = 0
		self.notes = []

class caustic_patterns:
	def __init__(self):
		self.data = [caustic_pattern() for x in range(16*4)]
		self.auto = [{} for x in range(16*4)]

	def parse(self, ebrw_readstr):
		logger_projparse.info('caustic3: SPAT')
		ebrw_readstr.magic_check(b'SPAT')

		SPAT_size = ebrw_readstr.int_u32()
		end_pos = ebrw_readstr.tell()+SPAT_size

		for n in range(16*4): self.data[n].measures = ebrw_readstr.int_u32()
		for n in range(16*4): self.data[n].numnote = ebrw_readstr.int_u32()
		for n in range(16*4):
			pln = np.frombuffer(ebrw_readstr.read(56*self.data[n].numnote), dtype=dtype_notearr)
			self.data[n].notes = pln[np.where(pln['type']==0)]

		ebrw_readstr.skip(512)
		unknown1 = ebrw_readstr.float()
		autoctrlid = ebrw_readstr.list_int_u32(64)

		ebrw_readstr.skip(256)
		ebrw_readstr.skip(512)

		for n, i in enumerate(autoctrlid):
			for v in range(i):
				blockobj = caustic_autoblocks()
				autoblkhdr = np.frombuffer(ebrw_readstr.read(24), dtype=[('ctrl_id', np.int32),('unk2', np.single),('unk3', np.single),('unk4', np.single),('smooth', np.single),('unk6', np.single)])[0]
				blockobj.ctrl_id = autoblkhdr['ctrl_id']
				blockobj.smooth = autoblkhdr['smooth']
				blockobj.data = ebrw_readstr.list_float(self.data[n].measures*32)
				self.auto[n][blockobj.ctrl_id] = blockobj

		ebrw_readstr.seek(end_pos)

dtype_notearr = np.dtype([
	('mach', np.int32), 
	('type', np.int32), 
	('pos', np.single), 
	('dur', np.single),

	('unk1', np.int32),
	('unk2', np.single), 

	('key', np.int8), 
	('unk4', np.int8), 
	('mode', np.int8), 
	('unk6', np.int8), 

	('unk7', np.single), 
	('unk8', np.int32), 
	('unk9', np.single), 
	('unk10', np.single), 
	('unk11', np.single), 
	('unk12', np.single), 
	('vol', np.single), 
	]) 

dtype_autoset = np.dtype([
	('unk1', np.int32),
	('unk2', np.int32),
	('id', np.int32),
	('pos', np.single),
	('val', np.single)
	]) 

class caustic_autoset:
	def __init__(self):
		self.data = {}

	def parse(self, data):
		numofautoctrl = int.from_bytes(data.read(4), "little")
		for ctrlauto_num in range(numofautoctrl):
			ctrlid = int.from_bytes(data.read(4), "little")
			n = int.from_bytes(data.read(4), "little")
			self.data[ctrlid] = []
			for _ in range(n):
				ctrldata = data.read(20)
				ctrlp = np.frombuffer(ctrldata, dtype=dtype_autoset)
				self.data[ctrlid].append(ctrlp)

class caustic_sequence:
	def __init__(self):
		self.parts = []
		self.notes = []
		self.tempoauto = []

		self.auto_mach = [caustic_autoset() for x in range(14)]
		self.auto_fx = [caustic_autoset() for x in range(2)]
		self.auto_mixer = [caustic_autoset() for x in range(2)]
		self.auto_master = caustic_autoset()

	def parse(self, ebrw_readstr):
		ebrw_readstr.skip(4)
		pl_count = ebrw_readstr.int_u32()

		pln = np.frombuffer(ebrw_readstr.read(56*pl_count), dtype=dtype_notearr)

		for _ in range(pl_count):
			np.where(pln['type']==2)
			self.parts = pln[np.where(pln['type']==2)]
			self.notes = pln[np.where(pln['type']==0)]

		ebrw_readstr.read(46)

		for m in self.auto_mach: m.parse(ebrw_readstr)
		for m in self.auto_fx: m.parse(ebrw_readstr)
		for m in self.auto_mixer: m.parse(ebrw_readstr)
		self.auto_master.parse(ebrw_readstr)
		ebrw_readstr.skip(2)
		n = ebrw_readstr.int_u32()
		s = ebrw_readstr.int_u32()
		for _ in range(n): self.tempoauto.append(ebrw_readstr.list_float(2))

class caustic_project:

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)

		self.effx = caustic_fxchain()
		self.mixr = caustic_mixer()
		self.mstr = caustic_master()
		self.seqn = caustic_sequence()

		self.machines = [caustic_machine() for x in range(14)]

		self.tempo = 120
		self.numerator = 4

		self.effxnum = 0
		self.mixrnum = 0

		rackchunkfound = False
		for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, None):
			if chunk_obj.id == b'RACK':
				rackchunkfound = True
				header = ebrw_readstr.read(4)
				name = ebrw_readstr.read(260)
				while chunk_obj.end > ebrw_readstr.tell():
					chunk_datatype = ebrw_readstr.read(4)
					logger_projparse.info('caustic3: main | chunk: '+str(chunk_datatype))
					if chunk_datatype == b'OUTP': self.read_OUTP(ebrw_readstr)
					elif chunk_datatype == b'EFFX': self.read_EFFX(ebrw_readstr)
					elif chunk_datatype == b'MIXR': self.read_MIXR(ebrw_readstr)
					elif chunk_datatype == b'MSTR': self.read_MSTR(ebrw_readstr)
					elif chunk_datatype == b'SEQN': self.read_SEQN(ebrw_readstr)
					else: break
		if not rackchunkfound:
			raise ProjectFileParserException('Caustic3: RACK chunk not found')
		else:
			return True

	def read_OUTP(self, ebrw_readstr):
		OUTP_size = ebrw_readstr.int_u32()

		ebrw_readstr.isolate_size(OUTP_size)
		ebrw_readstr.skip(82)
		self.tempo = ebrw_readstr.float()
		self.numerator = ebrw_readstr.int_u8()
		ebrw_readstr.isolate_end()

		for n in range(14):
			self.machines[n].mach_id = ebrw_readstr.string(4)
			ebrw_readstr.skip(1)

		for n, machdata in enumerate(self.machines):
			logger_projparse.info('caustic3: OUTP | '+machdata.mach_id)
			if machdata.mach_id != 'NULL':
				machdata.name = ebrw_readstr.string(10)
				mach_head = ebrw_readstr.raw(4)
				data_size = ebrw_readstr.int_u32()
				ebrw_readstr.isolate_size(data_size)
				machdata.parse(ebrw_readstr)
				ebrw_readstr.isolate_end()

	def read_EFFX(self, ebrw_readstr):
		data_size = ebrw_readstr.int_u32()
		ebrw_readstr.isolate_size(data_size)
		self.effx.parse(ebrw_readstr)
		if self.effxnum == 0: ebrw_readstr.read(4)
		ebrw_readstr.isolate_end()
		if self.effxnum == 0: ebrw_readstr.read(4)
		self.effxnum += 1

	def read_MIXR(self, ebrw_readstr):
		data_size = ebrw_readstr.int_u32()
		ebrw_readstr.isolate_size(data_size)
		self.mixr.parse(ebrw_readstr)
		ebrw_readstr.isolate_end()
		if self.mixrnum == 0: ebrw_readstr.read(4)
		self.mixrnum += 1

	def read_MSTR(self, ebrw_readstr):
		data_size = ebrw_readstr.int_u32()
		ebrw_readstr.isolate_size(data_size)
		self.mstr.parse(ebrw_readstr)
		ebrw_readstr.isolate_end()

	def read_SEQN(self, ebrw_readstr):
		data_size = ebrw_readstr.int_u32()
		ebrw_readstr.isolate_size(data_size)
		self.seqn.parse(ebrw_readstr)
		ebrw_readstr.isolate_end()