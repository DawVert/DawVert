# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from external.easybinrw import easybinrw
from external.easybinrw import chunked
import struct
import zipfile

VERBOSE = False
VERBOSE_CHANNEL = False
VERBOSE_RACK = False

def chunkview(ebrw_readstr, chunk_obj, supported, numl, viewbytes):
	if supported == 0: supportedtxt = '#'
	if supported == 0.5: supportedtxt = '='
	if supported == 1: supportedtxt = ' '
	print(supportedtxt, '      '*numl, chunk_obj.id, str(chunk_obj.size).ljust(7), end='')
	if viewbytes: print(ebrw_readstr.raw(min(chunk_obj.size, 32)))
	else: print()

def verify(ebrw_readstr, magicnum, name):
	try: ebrw_readstr.magic_check(magicnum)
	except ValueError as t: raise ProjectFileParserException('flm: '+name+' '+str(t))

class flm_rack_device_sampler_zone:
	def __init__(self, ebrw_readstr):
		self.name = ebrw_readstr.raw(1020)

class flm_rack_device_sampler:
	def __init__(self, ebrw_readstr, size, intype):
		self.zones = []
		self.path = None

		if intype == 1:
			verify(ebrw_readstr, b'10WD', 'device_sampler')
	
			for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, None):
				if chunk_obj.id == b'ZONE':
					if VERBOSE_RACK: chunkview(ebrw_readstr, chunk_obj, 1, 3, False)
					self.zones.append(flm_rack_device_sampler_zone(ebrw_readstr))
				elif chunk_obj.id == b'PATh':
					if VERBOSE_RACK: chunkview(ebrw_readstr, chunk_obj, 1, 3, False)
					pathsize = ebrw_readstr.int_u32()
					self.path = ebrw_readstr.raw(pathsize)
				else:
					if VERBOSE_RACK: chunkview(ebrw_readstr, chunk_obj, 0, 3, False)

class flm_rack_device:
	def __init__(self, ebrw_readstr, size):

		self.type = None
		self.head_val_1 = None
		self.head_val_2 = None
		self.desc_name = None
		self.desc_name_2 = None
		self.preset_name = ''
		self.preset_path = ''
		self.add1 = None
		self.prms = None
		self.cstm = None
		self.pads = None
		self.minimized = 0

		self.wet_pan = 0.5
		self.mix = 1.0
		self.post_gain = 0.5

		self.drumsamples = []
		
		self.type = ebrw_readstr.int_u32()
		self.order = ebrw_readstr.int_u32()

		for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, None):
			if chunk_obj.id == b'HEAD':
				if VERBOSE_RACK: chunkview(ebrw_readstr, chunk_obj, 0.5, 2, False)
				self.type = ebrw_readstr.int_s32()
				self.head_val_1 = ebrw_readstr.int_s32()
				self.head_val_2 = ebrw_readstr.int_s8()

			elif chunk_obj.id == b'DESC':
				if VERBOSE_RACK: chunkview(ebrw_readstr, chunk_obj, 1, 2, False)
				self.desc_name = ebrw_readstr.string(256)
				self.desc_name_2 = ebrw_readstr.string(256)

			elif chunk_obj.id == b'PRST':
				if VERBOSE_RACK: chunkview(ebrw_readstr, chunk_obj, 1, 2, False)
				self.preset_name = ebrw_readstr.raw(ebrw_readstr.int_u32())
				self.preset_path = ebrw_readstr.raw(ebrw_readstr.int_u32())

			elif chunk_obj.id == b'ADD1':
				if VERBOSE_RACK: chunkview(ebrw_readstr, chunk_obj, 0.5, 2, False)
				self.minimized = ebrw_readstr.int_s8()
				#self.add1 = ebrw_readstr.raw(chunk_obj.size)

			elif chunk_obj.id == b'PRMS':
				if VERBOSE_RACK: chunkview(ebrw_readstr, chunk_obj, 1, 2, False)
				self.prms = ebrw_readstr.list_float(chunk_obj.size//4)

			elif chunk_obj.id == b'PADS':
				if VERBOSE_RACK: chunkview(ebrw_readstr, chunk_obj, 0.5, 2, False)
				self.pads = ebrw_readstr.raw(chunk_obj.size)

			elif chunk_obj.id == b'CSTM':
				if VERBOSE_RACK: chunkview(ebrw_readstr, chunk_obj, 0, 2, False)
				self.cstm = flm_rack_device_sampler(ebrw_readstr, chunk_obj.size, self.type)

			elif chunk_obj.id == b'SMPl':
				if VERBOSE_RACK: chunkview(ebrw_readstr, chunk_obj, 0, 2, False)
				self.drumsamples.append( flm_channel_clip_sample(ebrw_readstr, chunk_obj.size, 3) )

			elif chunk_obj.id == b'SMPR':
				if VERBOSE_RACK: chunkview(ebrw_readstr, chunk_obj, 1, 2, False)
				self.wet_pan = ebrw_readstr.float()
				self.mix = ebrw_readstr.float()
				self.post_gain = ebrw_readstr.float()

			else:
				if VERBOSE_RACK: chunkview(ebrw_readstr, chunk_obj, 0, 2, True)


class flm_rack:
	def __init__(self, ebrw_readstr, size):
		self.header_val_0 = 0
		self.tracktype = 0
		self.fx_id = 0
		self.target = 0
		self.unk0 = 0

		self.volume = 0
		self.pan = 0
		self.mute = 0
		self.solo = 0
		self.param_val_4 = 0
		self.param_val_5 = 0

		ebrw_readstr.skip(4)
		verify(ebrw_readstr, b'10KR', 'rack')

		self.devices_sampler = None
		self.devices = []

		for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, None):

			if chunk_obj.id == b'RHED':
				if VERBOSE_RACK: chunkview(ebrw_readstr, chunk_obj, 0.5, 1, False)
				self.header_val_0 = ebrw_readstr.int_s32()
				self.tracktype = ebrw_readstr.int_s32()
				self.fx_id = ebrw_readstr.int_s32()
				self.target = ebrw_readstr.int_s32()

			elif chunk_obj.id == b'RPRM':
				if VERBOSE_RACK: chunkview(ebrw_readstr, chunk_obj, 1, 1, False)
				self.volume = ebrw_readstr.float()
				self.pan = ebrw_readstr.float()
				self.mute = ebrw_readstr.float()
				self.solo = ebrw_readstr.float()
				self.param_val_4 = ebrw_readstr.float()
				self.param_val_5 = ebrw_readstr.float()

			elif chunk_obj.id == b'RSMP':
				if VERBOSE_RACK: chunkview(ebrw_readstr, chunk_obj, 1, 1, False)
				self.devices_sampler = flm_rack_device(ebrw_readstr, chunk_obj.size)
			elif chunk_obj.id == b'RMOd':
				if VERBOSE_RACK: chunkview(ebrw_readstr, chunk_obj, 1, 1, False)
				self.devices.append( flm_rack_device(ebrw_readstr, chunk_obj.size) )
			else:
				if VERBOSE_RACK: chunkview(ebrw_readstr, chunk_obj, 0, 1, True)

class flm_channel_evnt:
	def __init__(self, ebrw_readstr, size, version):

		self.events = []

		if version == 1:
			for x in range(size//18):
				event = ebrw_readstr.raw(18)
				unpstruct = struct.unpack('<Idhbbh', event)
				self.events.append(unpstruct)

		if version == 2:
			eventstruct = None
			self.chunksize = ebrw_readstr.int_u16()

			if self.chunksize == 19: eventstruct = '<IdhbbHb'
			if self.chunksize == 20: eventstruct = '<IdhbbHbb'
			numnotes = (size-2)//self.chunksize

			for x in range(numnotes):
				event = ebrw_readstr.raw(self.chunksize)
				unpstruct = struct.unpack(eventstruct, event)
				self.events.append(unpstruct)

class flm_channel_clip_sample:
	def __init__(self, ebrw_readstr, size, debugn):
		verify(ebrw_readstr, b'20LS', 'clip sample')

		self.prms = []
		self.evn2 = None
		self.stretch_on = 0
		self.stretch_size = 1
		self.pitch = 1
		self.stretch_unk_1 = 0.5
		self.stretch_unk_2 = 0.5

		self.main_unk_1 = -1
		self.drumsamplenum = 0
		self.main_unk_4 = 1
		self.shift = 0
		self.shift_one = 0.5
		self.cut_group = 0
		self.poly = 1

		self.sample_path = b''

		self.preset_name = ''
		self.preset_path = ''

		for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, None):

			if chunk_obj.id == b'EVN2':
				if VERBOSE_CHANNEL: chunkview(ebrw_readstr, chunk_obj, 0.5, debugn, False)
				self.evn2 = flm_channel_evnt(ebrw_readstr, chunk_obj.size, 2)

			elif chunk_obj.id == b'STRC':
				if VERBOSE_CHANNEL: chunkview(ebrw_readstr, chunk_obj, 0.5, debugn, False)
				self.stretch_on = ebrw_readstr.int_u8()
				self.stretch_size = ebrw_readstr.double()
				self.pitch = ebrw_readstr.double()
				self.stretch_unk_1 = ebrw_readstr.float()
				self.stretch_unk_2 = ebrw_readstr.float()

			elif chunk_obj.id == b'PRMS':
				if VERBOSE_CHANNEL: chunkview(ebrw_readstr, chunk_obj, 1, debugn, False)
				self.prms = ebrw_readstr.list_float(chunk_obj.size//4)

			elif chunk_obj.id == b'PRST':
				if VERBOSE_RACK: chunkview(ebrw_readstr, chunk_obj, 1, debugn, False)
				self.preset_name = ebrw_readstr.raw(ebrw_readstr.int_u32())
				self.preset_path = ebrw_readstr.raw(ebrw_readstr.int_u32())

			elif chunk_obj.id == b'MAIN':
				if VERBOSE_CHANNEL: chunkview(ebrw_readstr, chunk_obj, 0.5, debugn, False)
				self.main_unk_1 = ebrw_readstr.int_s32()
				self.drumsamplenum = int(ebrw_readstr.double())
				self.sample_name = ebrw_readstr.string(512)
				self.sample_folder = ebrw_readstr.string(512)
				self.main_unk_4 = ebrw_readstr.int_s8()
				self.shift = ebrw_readstr.double()
				self.shift_one = ebrw_readstr.float()
				self.cut_group = ebrw_readstr.int_s8()
				self.poly = ebrw_readstr.int_s8()

			elif chunk_obj.id == b'PTH1':
				if VERBOSE_CHANNEL: chunkview(ebrw_readstr, chunk_obj, 1, debugn, False)
				pathsize = ebrw_readstr.int_u16()
				self.sample_path = ebrw_readstr.raw(pathsize)

			else:
				if VERBOSE_CHANNEL: chunkview(ebrw_readstr, chunk_obj, 0, debugn, True)

class flm_channel_clip:
	def __init__(self, ebrw_readstr, size, auto_on):
		self.position = ebrw_readstr.int_u32()
		self.evn2 = None
		self.evnt = None
		self.sample = None

		self.zoom_start = 0
		self.zoom_2 = 0
		self.zoom_3 = 0

		self.duration = 4
		self.loop_end = 4
		self.cut_start = 0

		self.id = 0
		self.unk_1 = 0
		self.mute = 0

		header = ebrw_readstr.raw(4)
		if header in [b'20LC', b'10LC']:
			for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, None):

				if chunk_obj.id == b'EVN2':
					if VERBOSE_CHANNEL: chunkview(ebrw_readstr, chunk_obj, 1, 3, False)
					self.evn2 = flm_channel_evnt(ebrw_readstr, chunk_obj.size, 2)
				elif chunk_obj.id == b'EVNT':
					if VERBOSE_CHANNEL: chunkview(ebrw_readstr, chunk_obj, 1, 3, False)
					self.evn2 = flm_channel_evnt(ebrw_readstr, chunk_obj.size, 1)
				elif chunk_obj.id == b'ZOOM':
					if VERBOSE_CHANNEL: chunkview(ebrw_readstr, chunk_obj, 1, 3, False)
					self.zoom_start = ebrw_readstr.double()
					self.zoom_2 = ebrw_readstr.double()
					self.zoom_3 = ebrw_readstr.double()
				elif chunk_obj.id == b'CLSm':
					if VERBOSE_CHANNEL: chunkview(ebrw_readstr, chunk_obj, 1, 3, False)
					self.sample = flm_channel_clip_sample(ebrw_readstr, chunk_obj.size, 4)
				elif chunk_obj.id == b'CLHd':
					if VERBOSE_CHANNEL: chunkview(ebrw_readstr, chunk_obj, 1, 3, False)
					self.duration = ebrw_readstr.double()
					self.loop_end = ebrw_readstr.double()
					self.cut_start = ebrw_readstr.double()
					self.id = ebrw_readstr.int_u32()
					self.unk_1 = ebrw_readstr.double()
					self.mute = ebrw_readstr.int_u8()
				elif chunk_obj.id == b'CLHD':
					if VERBOSE_CHANNEL: chunkview(ebrw_readstr, chunk_obj, 1, 3, False)
					self.duration = ebrw_readstr.double()
					self.loop_end = ebrw_readstr.double()
					self.cut_start = ebrw_readstr.double()
				else:
					if VERBOSE_CHANNEL: chunkview(ebrw_readstr, chunk_obj, 0, 3, True)
		else:
			raise ProjectFileParserException("flm: Magic Check Failed: b'20LC' or b'10LC'")

class flm_channel_track:
	def __init__(self, ebrw_readstr, size):

		self.clips = []
		self.auto_on = 0
		self.auto_device = 0
		self.auto_param = 0
		self.unk1 = 0
		self.unk2 = 0
		self.unk3 = 1
		self.unk4 = 0
		self.hide_value = 0
		self.name = ''

		for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, None):
			if chunk_obj.id == b'CLIP':
				if VERBOSE_CHANNEL: chunkview(ebrw_readstr, chunk_obj, 1, 2, False)
				self.clips.append( flm_channel_clip(ebrw_readstr, chunk_obj.size, self.auto_on) )
			elif chunk_obj.id == b'DESc':
				if VERBOSE_CHANNEL: chunkview(ebrw_readstr, chunk_obj, 1, 2, False)
				self.auto_on = ebrw_readstr.int_u16()
				self.unk4 = ebrw_readstr.int_u16()
				self.auto_device = ebrw_readstr.int_s32()
				self.auto_param = ebrw_readstr.int_s32()
				self.unk1 = ebrw_readstr.int_s32()
				self.unk2 = ebrw_readstr.int_s32()
				self.unk3 = ebrw_readstr.int_s32()
				self.hide_value = ebrw_readstr.int_s32()
				self.name = ebrw_readstr.string(1024)
			else:
				if VERBOSE_CHANNEL: chunkview(ebrw_readstr, chunk_obj, 0, 2, True)

class flm_channel_send:
	def __init__(self, ebrw_readstr, size):
		self.target = ebrw_readstr.int_u32()
		self.enabled = ebrw_readstr.float()
		self.param2 = ebrw_readstr.float()
		self.enabled2 = ebrw_readstr.float()
		self.amount = ebrw_readstr.float()

class flm_channel:
	def __init__(self, ebrw_readstr, size):

		self.name = ''
		self.tracknum = 0
		self.order = 0
		self.color = 0

		self.unk3 = 0
		self.unk4 = 0

		self.unk1 = ebrw_readstr.int_u16()
		self.unk2 = ebrw_readstr.int_u16()

		self.sends = []
		self.tracks = []

		header = ebrw_readstr.raw(4)
		if header in [b'20HC', b'10HC']:
			for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, None):
				if chunk_obj.id == b'CHHD':
					if VERBOSE_CHANNEL: chunkview(ebrw_readstr, chunk_obj, 0.5, 1, False)
					self.name = ebrw_readstr.string(1024)
					self.tracknum = ebrw_readstr.double()
					self.order = ebrw_readstr.float()
					self.color = ebrw_readstr.float()
					self.unk3 = ebrw_readstr.double()
					self.unk4 = ebrw_readstr.double()
				elif chunk_obj.id == b'TRKH':
					if VERBOSE_CHANNEL: chunkview(ebrw_readstr, chunk_obj, 1, 1, False)
					self.tracks.append( flm_channel_track(ebrw_readstr, chunk_obj.size) ) 
				elif chunk_obj.id == b'SEND':
					if VERBOSE_CHANNEL: chunkview(ebrw_readstr, chunk_obj, 1, 1, False)
					self.sends.append( flm_channel_send(ebrw_readstr, chunk_obj.size) )
				else:
					if VERBOSE_CHANNEL: chunkview(ebrw_readstr, chunk_obj, 0, 1, True)
		else:
			raise ProjectFileParserException("flm: Magic Check Failed: b'20HC' or b'10HC'")



class flm_project:
	def __init__(self):
		self.version_1 = 2
		self.version_2 = 1
		self.name = ''
		self.timediv_num = 4
		self.timediv_denum = 4
		self.racks = []
		self.channels = []
		self.tempo = 140
		self.space_start = 0
		self.space_end = 0
		self.zoom_size = 4
		self.zoom_pos = 0

		self.keyb = ''

		self.meta_artist = ''
		self.meta_unk1 = 0
		self.meta_unk2 = 0
		self.meta_title = ''
		self.meta_locked = 0
		self.meta_url = ''

		self.zipfile = None

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)

		if ebrw_readstr.read(2) == b'PK':
			self.zipped = True
			self.zipfile = zipfile.ZipFile(input_file, 'r')
			flpfound = False
			for filename in self.zipfile.namelist():
				if filename.endswith('.flm'):
					flmdata = self.zipfile.read(filename)
					ebrw_readstr = easybinrw.binread()
					ebrw_readstr.load_data(flmdata)
					return self.load(ebrw_readstr)
			if not flpfound:
				raise ProjectFileParserException('FLM: FLM file not found in zip')
		else:
			ebrw_readstr.seek(0)
			return self.load(ebrw_readstr)

	def load(self, ebrw_readstr):
		verify(ebrw_readstr, b'10LF', 'main')

		for chunk_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, None):
			if chunk_obj.id == b'RACK':
				if VERBOSE_RACK: chunkview(ebrw_readstr, chunk_obj, 1, 0, False)
				self.racks.append(flm_rack(ebrw_readstr, chunk_obj.size))
			elif chunk_obj.id == b'CHNL':
				if VERBOSE_CHANNEL: chunkview(ebrw_readstr, chunk_obj, 1, 0, False)
				self.channels.append(flm_channel(ebrw_readstr, chunk_obj.size))
			elif chunk_obj.id == b'TDIV':
				if VERBOSE: chunkview(ebrw_readstr, chunk_obj, 1, 0, False)
				self.timediv_num = ebrw_readstr.int_s8()
				self.timediv_denum = ebrw_readstr.int_s8()
			elif chunk_obj.id == b'HEAD':
				if VERBOSE_CHANNEL: chunkview(ebrw_readstr, chunk_obj, 0.5, 0, False)
				self.version_1 = ebrw_readstr.int_u32()
				self.version_2 = ebrw_readstr.int_u32()
				self.name = ebrw_readstr.string(256)
				self.tempo = ebrw_readstr.double()
				self.space_start = ebrw_readstr.double()
				self.space_end = ebrw_readstr.double()
				self.zoom_size = ebrw_readstr.double()
				self.zoom_pos = ebrw_readstr.double()
			elif chunk_obj.id == b'META':
				if VERBOSE_CHANNEL: chunkview(ebrw_readstr, chunk_obj, 1, 0, False)
				self.meta_artist = ebrw_readstr.string(256)
				self.meta_unk1 = ebrw_readstr.float()
				self.meta_unk2 = ebrw_readstr.float()
				self.meta_title = ebrw_readstr.string(256)
				self.meta_locked = ebrw_readstr.string(256)
				self.meta_url = ebrw_readstr.int_u8()
			elif chunk_obj.id == b'KEYB':
				if VERBOSE_CHANNEL: chunkview(ebrw_readstr, chunk_obj, 1, 0, False)
				self.keyb = ebrw_readstr.raw(ebrw_readstr.int_u32())
			else:
				if VERBOSE: chunkview(ebrw_readstr, chunk_obj, 0, 0, True)
		return True

	def itertracks(self):
		for n, x in enumerate(self.racks):
			yield n, x, self.channels[n]



#test_obj = flm_project()



#test_obj.load_from_file('G:\\DawVert\\DawProj_Reverse\\New Song (1).flm')



#test_obj.load_from_file('G:\\RandomMusicFiles\\daw_fl-mobile\\test\\New Song.flm')