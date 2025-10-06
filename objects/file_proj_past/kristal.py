# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from external.easybinrw import easybinrw

VERBOSE = False

# ==================================== MAIN CHUNKS ====================================

class CProjectInfo:
	def __init__(self, ebrw_readstr):
		if VERBOSE: print()
		if ebrw_readstr.int_u32()!=1: exit('CProjectInfo is not 1')
		self.data = [ebrw_readstr.string_t() for x in range(ebrw_readstr.int_u32())]

class CAudioEngine:
	def __init__(self, ebrw_readstr):
		unks = []
		if ebrw_readstr.int_u32()!=1: exit('CAudioEngine is not 1')
		self.freq = ebrw_readstr.float()
		self.unk = ebrw_readstr.int_u32()
		unks.append(ebrw_readstr.int_u32())
		unks.append(ebrw_readstr.int_u32())
		self.freq_total = ebrw_readstr.int_u32()
		if VERBOSE: print(unks)

class CMixer:
	def __init__(self, ebrw_readstr):
		if ebrw_readstr.int_u32()!=1: exit('CMixer is not 1')
		self.vol_l = ebrw_readstr.float()
		self.vol_r = ebrw_readstr.float()
		self.pan = ebrw_readstr.float()
		self.num_tracks = ebrw_readstr.int_u32()
		if VERBOSE: print(self.vol_l, self.vol_r)

class CMixerChannel:
	def __init__(self, ebrw_readstr):
		if ebrw_readstr.int_u32()!=1: exit('CMixerChannel is not 1')
		self.vol = ebrw_readstr.float()
		self.pan = ebrw_readstr.float()
		self.muted = ebrw_readstr.int_u8()
		self.solo = ebrw_readstr.int_u8()
		if VERBOSE: print(self.vol, self.pan)

class CInsertProcessor:
	def __init__(self, ebrw_readstr):
		if ebrw_readstr.int_u32()!=1: exit('CInsertProcessor is not 1')
		self.slots_enabled = list(ebrw_readstr.list_int_u8(ebrw_readstr.int_u32()))
		if VERBOSE: print(self.slots_enabled)

class CTransport:
	def __init__(self, ebrw_readstr):
		if ebrw_readstr.int_u32()!=2: exit('CTransport is not 2')
		unks = []
		unks.append(ebrw_readstr.int_u32())
		unks.append(ebrw_readstr.int_u32())
		unks.append(ebrw_readstr.int_u32())
		unks.append(ebrw_readstr.int_u16())
		unks.append(ebrw_readstr.int_u32())
		unks.append(ebrw_readstr.int_u32())
		unks.append(ebrw_readstr.int_u16())
		unks.append(ebrw_readstr.int_u8())
		self.timesig_num = ebrw_readstr.int_u32()
		self.timesig_denom = ebrw_readstr.int_u32()
		unks.append(ebrw_readstr.int_u32())
		if VERBOSE: print(unks)

class CMetronome:
	def __init__(self, ebrw_readstr):
		if ebrw_readstr.int_u32()!=1: exit('CMetronome is not 1')
		self.enabled = ebrw_readstr.int_u8()
		self.bpm = ebrw_readstr.int_u32()
		self.vol = ebrw_readstr.float()
		if VERBOSE: print(self.enabled, self.bpm)

class WindowLayout:
	def __init__(self, ebrw_readstr):
		if ebrw_readstr.int_u32()!=1: exit('WindowLayout is not 1')
		unks = []
		unks.append(ebrw_readstr.int_u32())
		unks.append(ebrw_readstr.int_u32())
		unks.append(ebrw_readstr.int_u32())
		if VERBOSE: print(unks)

class TransportPanel:
	def __init__(self, ebrw_readstr):
		unks = []
		unks.append(ebrw_readstr.int_u8())
		unks.append(ebrw_readstr.int_u32())
		unks.append(ebrw_readstr.int_u32())
		unks.append(ebrw_readstr.int_u32())
		unks.append(ebrw_readstr.int_u32())
		if VERBOSE: print(unks)

class Console:
	def __init__(self, ebrw_readstr):
		unks = []
		unks.append(ebrw_readstr.int_u8())
		unks.append(ebrw_readstr.int_u32())
		unks.append(ebrw_readstr.int_u32())
		unks.append(ebrw_readstr.int_u32())
		unks.append(ebrw_readstr.int_u32())
		if VERBOSE: print(unks)

		#unks = []
		#unks.append(ebrw_readstr.int_u32())
		#print(unks)

def iter_stringchunk(ebrw_readstr):
	name = ebrw_readstr.string_t()
	outchunk = None
	if VERBOSE: print('CHUNK >', name.ljust(20), end=' - ')
	if name == 'CProjectInfo': outchunk = CProjectInfo(ebrw_readstr)
	elif name == 'CAudioEngine': outchunk = CAudioEngine(ebrw_readstr)
	elif name == 'CMixer': outchunk = CMixer(ebrw_readstr)
	elif name == 'CMixerChannel': outchunk = CMixerChannel(ebrw_readstr)
	elif name == 'CInsertProcessor': outchunk = CInsertProcessor(ebrw_readstr)
	elif name == 'CTransport': outchunk = CTransport(ebrw_readstr)
	elif name == 'CMetronome': outchunk = CMetronome(ebrw_readstr)
	elif name == 'Window Layout': WindowLayout(ebrw_readstr)
	elif name == 'TransportPanel': outchunk = TransportPanel(ebrw_readstr)
	elif name == 'Console': outchunk = Console(ebrw_readstr)
	else:
		print('unknown chunk', name)
		exit()
	return name, outchunk
		
# ==================================== AUDIOINPUT ====================================

def iter_stringchunk_inp(ebrw_readstr):
	name = ebrw_readstr.string_t()
	outchunk = None
	if VERBOSE: print('CHUNK >', name.ljust(20), end=' - ')
	if name == 'CCrystalInput': outchunk = CCrystalInput(ebrw_readstr)
	else:
		print('unknown chunk', name)
		exit()
	return name, outchunk
		
# ==================================== WAVER ====================================

def iter_stringchunk_waver(ebrw_readstr):
	name = ebrw_readstr.string_t()
	outchunk = None
	if VERBOSE: print('CHUNK >', name.ljust(20), end=' - ')
	if name == 'CAudioTrack': outchunk = CAudioTrack(ebrw_readstr)
	elif name == 'CAudioPart': outchunk = CAudioPart(ebrw_readstr)
	elif name == 'CFolderPart': outchunk = CFolderPart(ebrw_readstr)
	elif name == 'CPath': outchunk = CPath(ebrw_readstr)
	elif name == 'CWaverRecordPort': outchunk = CWaverRecordPort(ebrw_readstr)
	elif name == 'CTimeLine': outchunk = CTimeLine(ebrw_readstr)
	elif name == 'CTimeSnapper': outchunk = CTimeSnapper(ebrw_readstr)
	elif name == 'CConnection': outchunk = CConnection(ebrw_readstr)
	else:
		if name:
			print('unknown chunk', name)
			exit()
	return name, outchunk
		
class CConnection:
	def __init__(self, ebrw_readstr):
		if ebrw_readstr.int_u32()!=1: exit('CConnection is not 1')
		unks = []
		unks.append(ebrw_readstr.int_u32())
		unks.append(ebrw_readstr.int_u32())
		unks.append(ebrw_readstr.int_s32())
		unks.append(ebrw_readstr.string_t())
		if VERBOSE: print(unks)

class CTimeSnapper:
	def __init__(self, ebrw_readstr):
		if ebrw_readstr.int_u32()!=1: exit('CTimeSnapper is not 1')
		unks = []
		unks.append(ebrw_readstr.int_u8())
		unks.append(ebrw_readstr.int_u32())
		unks.append(ebrw_readstr.int_u32())

		if VERBOSE: print(unks)

class CTimeLine:
	def __init__(self, ebrw_readstr):
		if ebrw_readstr.int_u32()!=2: exit('CTimeLine is not 2')
		self.zoom = ebrw_readstr.int_u64()
		self.offset = ebrw_readstr.int_u64()
		self._unk1 = ebrw_readstr.int_u64()
		self.mode = ebrw_readstr.int_u32()
		if VERBOSE: print(self.zoom, self.offset, self._unk1, self.mode)

class CWaverRecordPort:
	def __init__(self, ebrw_readstr):
		if ebrw_readstr.int_u32()!=1: exit('CWaverRecordPort is not 1')
		self.data = ebrw_readstr.string_t()
		if VERBOSE: print(self.data)

class CPath:
	def __init__(self, ebrw_readstr):
		if ebrw_readstr.int_u32()!=1: exit('CPath is not 1')
		self.path = ebrw_readstr.string_t()
		if VERBOSE: print(self.path)

class CFolderPart:
	def __init__(self, ebrw_readstr):
		if ebrw_readstr.int_u32()!=2: exit('CFolderPart is not 2')
		self.parts = []
		self.position = ebrw_readstr.int_u64()
		self.offset = ebrw_readstr.int_u64()
		self.duration = ebrw_readstr.int_u64()
		self.unk1 = ebrw_readstr.int_u32()
		self.unk2 = ebrw_readstr.int_u32()
		self.max_size = ebrw_readstr.int_u64()
		self.color = list(ebrw_readstr.list_int_u8(4))
		self.name = ebrw_readstr.string_t()
		self.flags = ebrw_readstr.flags_i32()
		if VERBOSE: print(self.name)
		self.parts = [iter_stringchunk_waver(ebrw_readstr) for _ in range(ebrw_readstr.int_u32())]

class CAudioPart:
	def __init__(self, ebrw_readstr):
		num = ebrw_readstr.int_u32()

		self.position = ebrw_readstr.int_u64()
		self.offset = ebrw_readstr.int_u64()
		self.duration = ebrw_readstr.int_u64()
		self.unk1 = ebrw_readstr.int_u32()
		self.unk2 = ebrw_readstr.int_u32()
		self.max_size = ebrw_readstr.int_u64()
		self.color = list(ebrw_readstr.list_int_u8(4))
		self.name = ebrw_readstr.string_t()
		self.flags = ebrw_readstr.flags_i32()
		self.fade_in = ebrw_readstr.int_u64()
		self.fade_out = ebrw_readstr.int_u64()
		self.volume = ebrw_readstr.float()
		if VERBOSE: print(self.name)
		self.path = iter_stringchunk_waver(ebrw_readstr)

class CAudioTrack:
	def __init__(self, ebrw_readstr):
		if ebrw_readstr.int_u32()!=1: exit('CAudioTrack is not 1')
		self.name = ebrw_readstr.string_t()
		if VERBOSE: print(self.name)
		self.parts = [iter_stringchunk_waver(ebrw_readstr) for _ in range(ebrw_readstr.int_u32())]
		self.flags = ebrw_readstr.flags_i16()

class CCrystalInput:
	def __init__(self, ebrw_readstr):
		self.parts = []
		self.tracks = []
		self.timeline = None
		self.timesnapper = None
		if ebrw_readstr.int_u32()!=1: exit('CCrystalInput is not 1')
		self.type = ebrw_readstr.raw(4)

		if self.type == b'Wavr':
			if VERBOSE: print()
			if ebrw_readstr.int_u32()!=1: exit('CCrystalInput is not 1')
			num_tracks = ebrw_readstr.int_u32()
			self.tracks = [iter_stringchunk_waver(ebrw_readstr) for _ in range(num_tracks*2)]
			self.timeline = iter_stringchunk_waver(ebrw_readstr)
			self.timesnapper = iter_stringchunk_waver(ebrw_readstr)
			self.connections = [iter_stringchunk_waver(ebrw_readstr) for _ in range(ebrw_readstr.int_u32())]

# ==================================== MAIN ====================================

class kristal_plugchunk:
	def __init__(self, ebrw_readstr, chunkid):
		self.name = ''
		self.size = -1
		self.start = -1
		self.type = None
		self.chunkid = chunkid

		self.chunkdata = []
		self.bindata = None

		if ebrw_readstr: self.read(ebrw_readstr, chunkid)

	def read(self, ebrw_readstr, chunkid):
		self.chunkid = chunkid
		self.type = ebrw_readstr.read(4)
		if self.type in [b'VSTf', b'Plug']:
			self.name = ebrw_readstr.string_t()
			type2 = ebrw_readstr.read(4)
			if (self.type==b'Plug' and type2==b'DDat') or (self.type==b'VSTf' and type2==b'FDat'):
				self.size = ebrw_readstr.int_u32()-4
				self.start = ebrw_readstr.tell_real()
				ebrw_readstr.skip(self.size)

	def parse(self, ebrw_readstr):
		if self.name:
			ebrw_readstr.seek(self.start)
			ebrw_readstr.isolate_size(self.size)
			if self.name == 'Waver.cin' and self.chunkid == 4:
				self.chunkdata = iter_stringchunk_inp(ebrw_readstr)
			if self.type == b'VSTf':
				self.bindata = ebrw_readstr.rest()
			ebrw_readstr.isolate_end_noseek()

def decodeplugrack(ebrw_readstr):
	dataout = {}

	chunkid = ebrw_readstr.int_u32()
	if chunkid == 1:
		dataout = kristal_plugchunk(ebrw_readstr, chunkid)

	elif chunkid == 3:
		dataout = []
		for num in range(4):
			dataout.append(kristal_plugchunk(ebrw_readstr, chunkid))

	elif chunkid == 4:
		dataout = []
		for num in range(4):
			dataout.append(kristal_plugchunk(ebrw_readstr, chunkid))

	elif chunkid == 16:
		dataout = []
		for num in range(16):
			dataout.append([[], []])
			dataout[num][0] = kristal_plugchunk(ebrw_readstr, chunkid)
			for _ in range(ebrw_readstr.int_u32()):
				dataout[num][1].append(kristal_plugchunk(ebrw_readstr, chunkid))
	else:
		print('UNKNOWN PLUGRANK CHUNK', chunkid)
		exit()
	return chunkid, dataout

# ==================================== MAIN ====================================

class kristal_song:
	def __init__(self):
		self.chunks = []
		self.infodata = []
		self.windowdata = []
		self.globalinserts = []
		self.audio_output = None
		self.audio_input = None
		self.mixer = None
		self.master = None

	def parse_chunk(self, ebrw_readstr, name, size):
		ebrw_readstr.isolate_size(size)
		if name == b'Glob':
			while ebrw_readstr.remaining():
				subname, subchunk = iter_stringchunk(ebrw_readstr)
				self.globalinserts.append([subname, subchunk])

		if name == b'Info':
			while ebrw_readstr.remaining():
				subname, subchunk = iter_stringchunk(ebrw_readstr)
				if subname == 'CProjectInfo': self.infodata = subchunk

		if name == b'Wind':
			while ebrw_readstr.remaining():
				subname, subchunk = iter_stringchunk(ebrw_readstr)
				if subname == 'Window Layout': self.windowdata = subchunk

		if name == b'ADev':
			self.audio_output = decodeplugrack(ebrw_readstr)
			self.audio_input = decodeplugrack(ebrw_readstr)

		if name == b'Mixr':
			self.mixer = decodeplugrack(ebrw_readstr)
			self.master = decodeplugrack(ebrw_readstr)
		ebrw_readstr.isolate_end_noseek()

		if name == b'ADev':
			for x in self.audio_input[1]: x.parse(ebrw_readstr)

		if name == b'Mixr':
			for x in self.mixer[1]: 
				x[0].parse(ebrw_readstr)
				for y in x[1]: y.parse(ebrw_readstr)

			for x in self.master[1]: 
				x.parse(ebrw_readstr)

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)

		while ebrw_readstr.remaining():
			name = ebrw_readstr.raw(4)
			size = ebrw_readstr.int_u32()-4
			start = ebrw_readstr.tell()
			self.chunks.append([name, size, start])
			ebrw_readstr.skip(size)

		for name, size, start in self.chunks:
			ebrw_readstr.seek(start)
			self.parse_chunk(ebrw_readstr, name, size)
		return True
