# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

VERBOSE = False
from external.easybinrw import easybinrw
from external.easybinrw import riff_chunks

# ---------------------- ITEMS ----------------------
class item_svip:
	def __init__(self):
		self.data = None

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr, size):
		cls = cls()
		cls.data = ebrw_readstr.raw(size)
		return cls

class item_file:
	def __init__(self):
		self.folder = ''
		self.type = 0
		self.file = ''
		self.type2 = 0
		self.file2 = ''

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr, size):
		cls = cls()
		cls.folder = ebrw_readstr.string(128, errors="ignore")
		ebrw_readstr.skip(2)
		cls.video = ebrw_readstr.string(126, errors="ignore")
		ebrw_readstr.skip(2)
		cls.type = ebrw_readstr.int_u16()
		cls.file = ebrw_readstr.string(256, errors="ignore")
		ebrw_readstr.skip(2)
		cls.type2 = ebrw_readstr.int_u16()
		cls.file2 = ebrw_readstr.string(256, errors="ignore")
		return cls


class item_trci:
	def __init__(self):
		self.data = None
		self.unknowns = []
		self.vol = 1
		self.pan = 0
		self.name = ''

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr, size):
		cls = cls()
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.int_u16() )
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.int_u16() )
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.int_u32() )
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.int_u32() )
		if ebrw_readstr.remaining(): val1 = ebrw_readstr.float()
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.int_u32() )
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.int_u32() )
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.int_u32() )
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.int_u32() )
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.int_u16() )
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.int_u16() )
		if ebrw_readstr.remaining(): cls.vol = ebrw_readstr.int_s32()/32767
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.int_u16() )
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.int_u16() )
		if ebrw_readstr.remaining(): cls.name = ebrw_readstr.string(48)
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.int_u32() )
		if ebrw_readstr.remaining(): cls.unknowns.append( ebrw_readstr.int_u32() )
		if ebrw_readstr.remaining(): cls.pan = ebrw_readstr.float()/32767
		if ebrw_readstr.remaining(): cls.data = ebrw_readstr.rest()
		return cls


class item_cntr:
	def __init__(self):
		self.data = None

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr, size):
		cls = cls()
		cls.data = ebrw_readstr.raw(size)
		return cls



class item_objc:
	def __init__(self):
		self.unknowns = []
		self.fileid = 0
		self.offset = 0
		self.size = 0
		self.start = 0
		self.end = 0
		self.unk_color = [0,0,0,0]
		self.fg_color = [0,0,0,0]
		self.bg_color = [0,0,0,0]
		self.fade_in = 0
		self.fade_out = 0
		self.vol = 0
		self.loop_end = 0
		self.name = ''
		self.speed = 1
		self.pitch = 0
		self.group = 0

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr, size):
		cls = cls()
		cls.fileid = ebrw_readstr.int_u32()
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.offset = ebrw_readstr.int_u32()
		cls.size = ebrw_readstr.int_u32()
		cls.start = ebrw_readstr.int_u64()
		cls.end = ebrw_readstr.int_u64()
		cls.unknowns.append( ebrw_readstr.int_u8() )
		cls.unknowns.append( ebrw_readstr.int_u8() )
		cls.unknowns.append( ebrw_readstr.int_u8() )
		cls.unknowns.append( ebrw_readstr.int_u8() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unk_color = ebrw_readstr.list_int_u8(4)
		cls.fg_color = ebrw_readstr.list_int_u8(4)
		cls.bg_color = ebrw_readstr.list_int_u8(4)
		cls.group = ebrw_readstr.int_u32()
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.fade_in = ebrw_readstr.int_u64()
		cls.fade_out = ebrw_readstr.int_u64()
		cls.vol = ebrw_readstr.int_u32()
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.loop_end = ebrw_readstr.int_u32()
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.name = ebrw_readstr.string(32, errors="ignore")
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_s32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		if ebrw_readstr.remaining(): ebrw_readstr.raw(4)
		if ebrw_readstr.remaining(): cls.speed = ebrw_readstr.float()
		if ebrw_readstr.remaining(): ebrw_readstr.skip(8)
		if ebrw_readstr.remaining(): cls.pitch = ebrw_readstr.float()

		return cls



class item_oeff:
	def __init__(self):
		self.data = None

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr, size):
		cls = cls()
		cls.data = ebrw_readstr.raw(size)
		return cls


class item_otrn:
	def __init__(self):
		self.data = None

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr, size):
		cls = cls()
		cls.data = ebrw_readstr.raw(size)
		return cls


class item_rubb:
	def __init__(self):
		self.data = None

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr, size):
		cls = cls()
		cls.data = ebrw_readstr.raw(size)
		return cls


class item_crsr:
	def __init__(self):
		self.data = None

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr, size):
		cls = cls()
		cls.data = ebrw_readstr.raw(size)
		return cls


class item_proi:
	def __init__(self):
		self.data = None
		self.sample_rate = 44100
		self.timeisg_num = 4
		self.timeisg_denom = 4
		self.tempo = 120

		self.unknowns = []


	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr, size):
		cls = cls()
		#cls.data = ebrw_readstr.raw(size)
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.sample_rate = ebrw_readstr.int_u32()
		cls.timeisg_num = ebrw_readstr.int_u32()
		cls.timeisg_denom = ebrw_readstr.int_u32()
		cls.tempo = ebrw_readstr.float()
		return cls


class item_teq:
	def __init__(self):
		self.data = None

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr, size):
		cls = cls()
		cls.data = ebrw_readstr.raw(size)
		return cls


class item_tpq:
	def __init__(self):
		self.data = None

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr, size):
		cls = cls()
		cls.data = ebrw_readstr.raw(size)
		return cls


class item_comp:
	def __init__(self):
		self.data = None

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr, size):
		cls = cls()
		cls.data = ebrw_readstr.raw(size)
		return cls


# ---------------------- ROOT ----------------------
class root_group:
	def __init__(self):
		self.data_svip = None
		self.data_phys = None
		self.data_trks = None
		self.data_rngs = None
		self.data_crss = None
		self.data_proi = None
		self.data_teq = {}
		self.data_tpq = {}
		self.data_comp = None

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)
		riffchunks = riff_chunks.riff_chunk()
		riffchunks.read(ebrw_readstr, 0)

		for x in riffchunks.iter_reader(ebrw_readstr):
			if x.id == b'SVIP':
				if not x.is_list: self.data_svip = item_svip.from_ebrw_readstr(ebrw_readstr, x.size)
				elif VERBOSE: print(x.id, 'is not an item')
			elif x.id == b'phys':
				if x.is_list: self.data_phys = group_phys.from_riffchunks(x, ebrw_readstr)
				elif VERBOSE: print(x.id, 'is not a group')
			elif x.id == b'trks':
				if x.is_list: self.data_trks = group_trks.from_riffchunks(x, ebrw_readstr)
				elif VERBOSE: print(x.id, 'is not a group')
			elif x.id == b'rngs':
				if x.is_list: self.data_rngs = group_rngs.from_riffchunks(x, ebrw_readstr)
				elif VERBOSE: print(x.id, 'is not a group')
			elif x.id == b'crss':
				if x.is_list: self.data_crss = group_crss.from_riffchunks(x, ebrw_readstr)
				elif VERBOSE: print(x.id, 'is not a group')
			elif x.id == b'PROI':
				if not x.is_list: self.data_proi = item_proi.from_ebrw_readstr(ebrw_readstr, x.size)
				elif VERBOSE: print(x.id, 'is not an item')
			elif x.id == b'teq1':
				if not x.is_list: self.data_teq[1] = item_teq.from_ebrw_readstr(ebrw_readstr, x.size)
				elif VERBOSE: print(x.id, 'is not an item')
			elif x.id == b'teq2':
				if not x.is_list: self.data_teq[2] = item_teq.from_ebrw_readstr(ebrw_readstr, x.size)
				elif VERBOSE: print(x.id, 'is not an item')
			elif x.id == b'teq3':
				if not x.is_list: self.data_teq[3] = item_teq.from_ebrw_readstr(ebrw_readstr, x.size)
				elif VERBOSE: print(x.id, 'is not an item')
			elif x.id == b'teq4':
				if not x.is_list: self.data_teq[4] = item_teq.from_ebrw_readstr(ebrw_readstr, x.size)
				elif VERBOSE: print(x.id, 'is not an item')
			elif x.id == b'teq5':
				if not x.is_list: self.data_teq[5] = item_teq.from_ebrw_readstr(ebrw_readstr, x.size)
				elif VERBOSE: print(x.id, 'is not an item')
			elif x.id == b'tpq1':
				if not x.is_list: self.data_tpq[1] = item_tpq.from_ebrw_readstr(ebrw_readstr, x.size)
				elif VERBOSE: print(x.id, 'is not an item')
			elif x.id == b'tpq2':
				if not x.is_list: self.data_tpq[2] = item_tpq.from_ebrw_readstr(ebrw_readstr, x.size)
				elif VERBOSE: print(x.id, 'is not an item')
			elif x.id == b'tpq3':
				if not x.is_list: self.data_tpq[3] = item_tpq.from_ebrw_readstr(ebrw_readstr, x.size)
				elif VERBOSE: print(x.id, 'is not an item')
			elif x.id == b'tpq4':
				if not x.is_list: self.data_tpq[4] = item_tpq.from_ebrw_readstr(ebrw_readstr, x.size)
				elif VERBOSE: print(x.id, 'is not an item')
			elif x.id == b'tpq5':
				if not x.is_list: self.data_tpq[5] = item_tpq.from_ebrw_readstr(ebrw_readstr, x.size)
				elif VERBOSE: print(x.id, 'is not an item')
			elif x.id == b'comp':
				if not x.is_list: self.data_comp = item_comp.from_ebrw_readstr(ebrw_readstr, x.size)
				elif VERBOSE: print(x.id, 'is not an item')
			elif VERBOSE: print('unknown chunk in root: '+str(x.id))
		return True

# ---------------------- GROUP ----------------------
class group_phys:
	def __init__(self):
		self.files = []

	@classmethod
	def from_riffchunks(cls, riffchunks, ebrw_readstr):
		cls = cls()
		for x in riffchunks.iter_reader(ebrw_readstr):
			if x.id == b'file':
				if not x.is_list: cls.files.append(item_file.from_ebrw_readstr(ebrw_readstr, x.size))
				elif VERBOSE: print(x.id, 'is not an item')
			elif VERBOSE: print('unknown chunk in phys: '+str(x.id))
		return cls


class group_trks:
	def __init__(self):
		self.data_trck = []

	@classmethod
	def from_riffchunks(cls, riffchunks, ebrw_readstr):
		cls = cls()
		for x in riffchunks.iter_reader(ebrw_readstr):
			if x.id == b'trck':
				if x.is_list:
					cls.data_trck.append(group_trck.from_riffchunks(x, ebrw_readstr))
				elif VERBOSE: print(x.id, 'is not a group')
			elif VERBOSE: print('unknown chunk in trks: '+str(x.id))
		return cls


class group_trck:
	def __init__(self):
		self.data_trci = None
		self.data_cntr = []
		self.data_objs = []
		self.data_rubb = []

	@classmethod
	def from_riffchunks(cls, riffchunks, ebrw_readstr):
		cls = cls()
		for x in riffchunks.iter_reader(ebrw_readstr):
			if x.id == b'trci':
				if not x.is_list: cls.data_trci = item_trci.from_ebrw_readstr(ebrw_readstr, x.size)
				elif VERBOSE: print(x.id, 'is not an item')
			elif x.id == b'cntr':
				if not x.is_list: cls.data_cntr.append(item_cntr.from_ebrw_readstr(ebrw_readstr, x.size))
				elif VERBOSE: print(x.id, 'is not an item')
			elif x.id == b'objs':
				if x.is_list:
					cls.data_objs.append(group_objs.from_riffchunks(x, ebrw_readstr))
				elif VERBOSE: print(x.id, 'is not a group')
			elif x.id == b'rubb':
				if not x.is_list: cls.data_rubb.append(item_rubb.from_ebrw_readstr(ebrw_readstr, x.size))
				elif VERBOSE: print(x.id, 'is not an item')
			elif VERBOSE: print('unknown chunk in trck: '+str(x.id))
		return cls


class item_3dau:
	def __init__(self):
		self.data = None
		self.unknowns = []

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr, size):
		cls = cls()
		cls.unknowns.append( ebrw_readstr.int_u32() )
		cls.unknowns.append( ebrw_readstr.float() )
		cls.unknowns.append( ebrw_readstr.int_u32() )
		return cls

class item_orup:
	def __init__(self):
		self.data = None
		self.unknowns = []

	@classmethod
	def from_ebrw_readstr(cls, ebrw_readstr, size):
		cls = cls()
		cls.unknowns.append( ebrw_readstr.int_u32() )
		ebrw_readstr.skip(4)
		cls.unknowns.append( ebrw_readstr.int_s32() )
		ebrw_readstr.skip(4)
		cls.unknowns.append( ebrw_readstr.int_u32() )
		ebrw_readstr.skip(4)
		cls.unknowns.append( ebrw_readstr.double() )
		return cls



class group_objs:
	def __init__(self):
		self.data_objc = None
		self.data_oeff = None
		self.data_otrn = None
		self.data_3dau = None
		self.data_orup = []

	@classmethod
	def from_riffchunks(cls, riffchunks, ebrw_readstr):
		cls = cls()
		for x in riffchunks.iter_reader(ebrw_readstr):
			if x.id == b'objc':
				if not x.is_list: cls.data_objc = item_objc.from_ebrw_readstr(ebrw_readstr, x.size)
				elif VERBOSE: print(x.id, 'is not an item')
			elif x.id == b'oeff':
				if not x.is_list: cls.data_oeff = item_oeff.from_ebrw_readstr(ebrw_readstr, x.size)
				elif VERBOSE: print(x.id, 'is not an item')
			elif x.id == b'otrn':
				if not x.is_list: cls.data_otrn = item_otrn.from_ebrw_readstr(ebrw_readstr, x.size)
				elif VERBOSE: print(x.id, 'is not an item')
			elif x.id == b'3dau':
				if not x.is_list: cls.data_3dau = item_3dau.from_ebrw_readstr(ebrw_readstr, x.size)
				elif VERBOSE: print(x.id, 'is not an item')
			elif x.id == b'orup':
				if not x.is_list: cls.data_orup.append(item_orup.from_ebrw_readstr(ebrw_readstr, x.size))
				elif VERBOSE: print(x.id, 'is not an item')
			elif VERBOSE: print('unknown chunk in objs: '+str(x.id))
		return cls


class group_crss:
	def __init__(self):
		self.data_crsr = []

	@classmethod
	def from_riffchunks(cls, riffchunks, ebrw_readstr):
		cls = cls()
		for x in riffchunks.iter_reader(ebrw_readstr):
			if x.id == b'crsr':
				if not x.is_list: cls.data_crsr.append(item_crsr.from_ebrw_readstr(ebrw_readstr, x.size))
				elif VERBOSE: print(x.id, 'is not an item')
			elif VERBOSE: print('unknown chunk in crss: '+str(x.id))
		return cls


class group_rngs:
	def __init__(self):
		self.data = []

	@classmethod
	def from_riffchunks(cls, riffchunks, ebrw_readstr):
		cls = cls()
		cls.data = [x for x in riffchunks.iter_reader(ebrw_readstr)]
		return cls