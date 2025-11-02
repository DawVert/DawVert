# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import zipfile
from external.easybinrw import easybinrw
from objects.exceptions import ProjectFileParserException

VERBOSE = False
SHOWALL = False

# ---------------------- CHUNKS ----------------------

class chunk__unknown_data:
	def __init__(self, ebrw_readstr):
		size = ebrw_readstr.int_s32()
		self.unknowndata = []
		self.data_a = ebrw_readstr.int_s32()
		self.data_b = ebrw_readstr.float()
		self.data_c = ebrw_readstr.int_s32()

class chunk__regiondata:
	def __init__(self, ebrw_readstr):
		self.unknowndata = []
		self.unknowndata.append( ebrw_readstr.int_u32() )
		numchars1 = ebrw_readstr.int_u32()
		self.unknowndata.append( ebrw_readstr.int_u32() )
		self.unknowndata.append( ebrw_readstr.int_u32() )
		numchars2 = ebrw_readstr.int_u32()
		self.filename = ebrw_readstr.string16(numchars1//2)
		self.filename2 = ebrw_readstr.string16(numchars2//2)
		self.unknowndata.append( ebrw_readstr.int_u32() )
		self.unknowndata.append( ebrw_readstr.int_u32() )

#class chunk__regiondata_2:
#	def __init__(self, ebrw_readstr):
#		self.unknowndata = []
#		self.unknowndata.append( ebrw_readstr.int_s32() )
#		self.unknowndata.append( ebrw_readstr.int_s32() )
#		self.unknowndata.append( ebrw_readstr.int_s32() )
#		self.unknowndata.append( ebrw_readstr.int_s32() )
#		self.unknowndata.append( ebrw_readstr.int_s32() )
#		self.unknowndata.append( ebrw_readstr.int_s32() )
#		self.unknowndata.append( ebrw_readstr.int_s32() )
#		self.unknowndata.append( ebrw_readstr.int_s32() )
#		self.unknowndata.append( ebrw_readstr.int_s32() )
#		self.unknowndata.append( ebrw_readstr.int_s32() )
#		self.unknowndata.append( ebrw_readstr.int_s32() )
#		self.unknowndata.append( ebrw_readstr.int_s32() )
#		self.unknowndata.append( ebrw_readstr.int_s32() )
#		self.unknowndata.append( ebrw_readstr.int_s32() )
#		self.unknowndata.append( ebrw_readstr.int_s32() )
#		self.filename = ebrw_readstr.string16_t()
#		self.filename2 = ebrw_readstr.string16_t()
#		self.name = ebrw_readstr.string16_t()
#		self.name2 = ebrw_readstr.string16_t()
#		#self.unknowndata.append( ebrw_readstr.int_u32() )
#		#self.unknowndata.append( ebrw_readstr.int_u32() )
#		print( self.unknowndata, self.name2, ebrw_readstr.rest().hex()  )

class chunk__peak:
	def __init__(self, ebrw_readstr):
		self.unknowndata = []
		self.unknowndata.append( ebrw_readstr.int_s32() )
		self.unknowndata.append( ebrw_readstr.int_s32() )
		self.unknowndata.append( ebrw_readstr.int_s64() )
		self.unknowndata.append( ebrw_readstr.float() )

class chunk__region:
	def __init__(self, ebrw_readstr):
		size = ebrw_readstr.int_s32()
		self.unknowndata = []
		self.unknowndata.append( ebrw_readstr.int_s32() )
		self.flags = ebrw_readstr.flags_i64()
		self.pos = ebrw_readstr.int_s64()
		self.size = ebrw_readstr.int_s64()
		self.offset = ebrw_readstr.int_s64()
		self.pitch = ebrw_readstr.double()
		self.unknowndata.append( ebrw_readstr.double() )
		self.unknowndata.append( ebrw_readstr.int_s32() )
		self.unknowndata.append( ebrw_readstr.int_s32() )
		self.id = ebrw_readstr.int_s32()
		self.unknowndata.append( ebrw_readstr.int_s32() )
		self.index = ebrw_readstr.int_s32()
		self.unknowndata.append( ebrw_readstr.int_s32() )
		self.unknowndata.append( ebrw_readstr.int_s32() )
		self.unknowndata.append( ebrw_readstr.int_s32() )
		self.fade_in = ebrw_readstr.int_s64()
		self.fade_out = ebrw_readstr.int_s64()
		self.vol = ebrw_readstr.float()

class chunk__maindata:
	def __init__(self, ebrw_readstr):
		self.unknowndata = []
		size = ebrw_readstr.int_s32()
		self.version = ebrw_readstr.int_u16()
		#if self.version>5:
		#	raise ProjectFileParserException('new_acid: Version '+str(self.version)+' is not supported.') 
		self.unknowndata.append( ebrw_readstr.int_u16() )
		self.unknowndata.append( ebrw_readstr.int_u32() )
		self.freq = ebrw_readstr.int_u32()
		self.unknowndata.append( ebrw_readstr.double() )
		self.tempo = ebrw_readstr.double()
		self.unknowndata.append( ebrw_readstr.int_u64() )
		self.timesig_num = ebrw_readstr.int_u16()
		self.timesig_denom = ebrw_readstr.int_u16()
		self.ppq = ebrw_readstr.int_u32()
		self.unknowndata.append( ebrw_readstr.int_u32() )
		self.unknowndata.append( ebrw_readstr.int_u32() )
		numchars1 = ebrw_readstr.int_u32()//2
		numchars2 = ebrw_readstr.int_u32()//2
		self.unknowndata.append( ebrw_readstr.int_u32() )
		self.unknowndata.append( ebrw_readstr.int_u32() )
		self.unknowndata.append( ebrw_readstr.int_u32() )
		self.unknowndata.append( ebrw_readstr.int_u32() )
		self.unknowndata.append( ebrw_readstr.int_u32() )
		self.unknowndata.append( ebrw_readstr.int_u32() )
		self.unknowndata.append( ebrw_readstr.int_u8() )
		self.unknowndata.append( ebrw_readstr.int_u8() )
		self.unknowndata.append( ebrw_readstr.int_u8() )
		self.unknowndata.append( ebrw_readstr.int_u8() )
		self.unknowndata.append( ebrw_readstr.int_u32() )
		self.file_project = ebrw_readstr.string16(numchars1)
		self.file_prog = ebrw_readstr.string16(numchars2)

class chunk__track_data:
	def __init__(self, ebrw_readstr):
		self.unknowndata = []
		self.version = ebrw_readstr.int_u32()
		self.filename = ''
		self.name = ''

		if self.version==64:
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.flags = ebrw_readstr.flags_i32()
			self.size = ebrw_readstr.int_u32()
			self.type = ebrw_readstr.int_u32()
			self.color = ebrw_readstr.int_u32()
			self.stretchtype = ebrw_readstr.int_u32()
			self.id = ebrw_readstr.int_u32()
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.numaudio = ebrw_readstr.int_u32()
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.seconds = ebrw_readstr.int_u32()/10000000
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.filename = ebrw_readstr.string16_t()
			self.name = ebrw_readstr.string16_t()
			self.name2 = ebrw_readstr.string16_t()

		if self.version==56:
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.flags = ebrw_readstr.flags_i32()
			self.size = ebrw_readstr.int_u32()
			self.type = ebrw_readstr.int_u32()
			self.color = ebrw_readstr.int_u32()
			self.id = ebrw_readstr.int_u32()
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.numaudio = ebrw_readstr.int_u32()
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.name = ebrw_readstr.string16_t()

class chunk__audioinfo:
	def __init__(self, ebrw_readstr):
		self.unknowndata = []
		self.unknowndata.append( ebrw_readstr.int_s32() )
		self.unknowndata.append( ebrw_readstr.int_s32() )
		self.unknowndata.append( ebrw_readstr.int_s32() )
		self.vol = ebrw_readstr.float()
		self.pan = ebrw_readstr.float()
		self.unknowndata.append( ebrw_readstr.int_s32() )
		self.unknowndata.append( ebrw_readstr.float() )
		self.unknowndata.append( ebrw_readstr.int_s32() )
		#self.unknowndata.append( ebrw_readstr.rest() )

class chunk__marker:
	def __init__(self, ebrw_readstr):
		size = ebrw_readstr.int_u32()
		ebrw_readstr.skip(4)
		self.pos = ebrw_readstr.int_s64()
		self.end = ebrw_readstr.int_s64()
		self.id = ebrw_readstr.int_s32()
		self.type = ebrw_readstr.int_s32()
		numchars = ebrw_readstr.int_s32()//2
		ebrw_readstr.skip(4)
		self.name = ebrw_readstr.string16(numchars)

class chunk__tempokeypoint:
	def __init__(self, ebrw_readstr):
		size = ebrw_readstr.int_u32()
		self.unknowndata = []
		ebrw_readstr.skip(4)
		self.pos_synctime = ebrw_readstr.int_s64()
		self.pos_samples = ebrw_readstr.int_s64()
		self.tempo = ebrw_readstr.int_s32()
		self.base_note = ebrw_readstr.int_s32()

class chunk__audiostretch:
	def __init__(self, ebrw_readstr):
		size = ebrw_readstr.int_u32()
		self.unknowndata = []
		self.unknowndata.append( ebrw_readstr.int_u32() )
		self.flags = ebrw_readstr.flags_i32()
		self.root_note = ebrw_readstr.int_u8()
		self.unknowndata.append( ebrw_readstr.int_u8() )
		self.unknowndata.append( ebrw_readstr.int_u8() )
		self.unknowndata.append( ebrw_readstr.int_u8() )
		self.unknowndata.append( ebrw_readstr.int_u8() )
		self.unknowndata.append( ebrw_readstr.int_u8() )
		self.unknowndata.append( ebrw_readstr.int_u8() )
		self.unknowndata.append( ebrw_readstr.int_u8() )
		self.downbeat_offset = ebrw_readstr.int_u32()
		self.timesig_num = ebrw_readstr.int_u16()
		self.timesig_denom = ebrw_readstr.int_u16()
		self.tempo = ebrw_readstr.float()

class chunk__startingparam:
	def __init__(self, ebrw_readstr):
		size = ebrw_readstr.int_u32()
		self.unknowndata = []
		self.unknowndata.append( ebrw_readstr.int_u32() )
		self.tempo = ebrw_readstr.int_u32()
		self.root_note = ebrw_readstr.int_u32()
		self.unknowndata.append( ebrw_readstr.int_u32() )
		self.unknowndata.append( ebrw_readstr.int_u32() )

class chunk__track_automation:
	def __init__(self, ebrw_readstr):
		version = ebrw_readstr.int_u32()

		self.points = []
		self.unknowndata = []

		#print('---------------points', version)
		if version == 48:
			self.group = ebrw_readstr.int_u32()
			self.param = ebrw_readstr.int_u32()
			self.min = ebrw_readstr.float()
			self.max = ebrw_readstr.float()
			self.defv = ebrw_readstr.float()
			self.numpoints = ebrw_readstr.int_u32()
			self.unknowndata.append( ebrw_readstr.int_u32() )
			for _ in range(self.numpoints):
				pointdata = []
				pointdata.append( ebrw_readstr.int_u32() )
				pointdata.append( ebrw_readstr.int_s32() )
				pointdata.append( ebrw_readstr.float() )
				pointdata.append( ebrw_readstr.int_u32() )
				self.points.append(pointdata)
		elif version == 72:
			self.group = ebrw_readstr.int_u32()
			self.param = ebrw_readstr.int_u32()
			self.min = ebrw_readstr.float()
			self.max = ebrw_readstr.float()
			self.defv = ebrw_readstr.float()
			self.numpoints = ebrw_readstr.int_u32()
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.float() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			for _ in range(self.numpoints):
				pointdata = []
				pointdata.append( ebrw_readstr.int_u32() )
				pointdata.append( ebrw_readstr.int_s32() )
				pointdata.append( ebrw_readstr.float() )
				pointdata.append( ebrw_readstr.int_u32() )
				self.points.append(pointdata)
		elif version == 80:
			self.group = ebrw_readstr.int_u32()
			self.param = ebrw_readstr.int_u32()
			self.min = ebrw_readstr.float()
			self.max = ebrw_readstr.float()
			self.defv = ebrw_readstr.float()
			self.numpoints = ebrw_readstr.int_u32()
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.float() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			self.unknowndata.append( ebrw_readstr.int_u32() )
			for _ in range(self.numpoints):
				pointdata = []
				pointdata.append( ebrw_readstr.int_u32() )
				pointdata.append( ebrw_readstr.int_s32() )
				pointdata.append( ebrw_readstr.float() )
				pointdata.append( ebrw_readstr.int_u32() )
				pointdata.append( ebrw_readstr.int_u32() )
				pointdata.append( ebrw_readstr.int_u32() )
				self.points.append(pointdata)
		#else:
		#	for _ in range(self.numpoints):
		#		pointdata = []
		#		pointdata.append( ebrw_readstr.int_u32() )
		#		pointdata.append( ebrw_readstr.int_s32() )
		#		pointdata.append( ebrw_readstr.float() )
		#		pointdata.append( ebrw_readstr.int_u32() )
		#		print(pointdata)
		#		self.points.append(pointdata)
		# print([x[0] for x in self.points])

class chunk__audiodefinfo:
	def __init__(self, ebrw_readstr):
		size = ebrw_readstr.int_u32()
		self.unknowndata = []
		self.unknowndata.append( ebrw_readstr.int_u32() )
		self.unknowndata.append( ebrw_readstr.int_u32() )
		self.color = ebrw_readstr.int_u32()
		self.unknowndata.append( ebrw_readstr.int_u32() )
		numchars1 = ebrw_readstr.int_u32()//2
		numchars2 = ebrw_readstr.int_u32()//2
		numchars3 = ebrw_readstr.int_u32()//2
		self.pitch = ebrw_readstr.float()
		self.filename = ebrw_readstr.string16(numchars1)
		self.filename2 = ebrw_readstr.string16(numchars2)
		self.name = ebrw_readstr.string16(numchars3)
		self.unknowndata.append( ebrw_readstr.int_u32() )
		self.unknowndata.append( ebrw_readstr.int_u32() )
		self.stretchtype = ebrw_readstr.int_u32()
		self.preserve_pitch = ebrw_readstr.int_u32()
		self.seconds = ebrw_readstr.int_u32()/10000000
		self.unknowndata.append( ebrw_readstr.int_u32() )
		self.stretch_algo = ebrw_readstr.int_u32()
		self.stretch_algo_mode = ebrw_readstr.int_u32()
		self.unknowndata.append( ebrw_readstr.int_u32() )
		self.formant_shift = ebrw_readstr.float()
		self.unknowndata.append( ebrw_readstr.float() )
		self.unknowndata.append( ebrw_readstr.int_u32() )

class chunk__metadata:
	def __init__(self, ebrw_readstr):
		self.unk1 = ebrw_readstr.int_u32()
		self.metadata = {}
		for _ in range(ebrw_readstr.int_u32()):
			chunk_name = ebrw_readstr.raw(4)
			chunk_data = ebrw_readstr.string16(ebrw_readstr.int_u32()//2)
			self.metadata[chunk_name] = chunk_data

class chunk__tracksfolder:
	def __init__(self, ebrw_readstr):
		self.unk1 = ebrw_readstr.int_u32()
		self.idnum = ebrw_readstr.int_u32()
		self.unk3 = ebrw_readstr.int_u32()
		self.unk4 = ebrw_readstr.int_u32()
		self.flags = ebrw_readstr.flags_i32()
		self.num_tracks = ebrw_readstr.int_u32()
		self.unk6 = ebrw_readstr.int_u32()
		self.name = ebrw_readstr.string16_t()
		self.inchunks = sony_acid_chunk()
		if self.num_tracks: self.inchunks.read(ebrw_readstr, 0)
		self.rest = ebrw_readstr.rest()
		#print('grp', self.unk3, self.unk4, self.flags, self.unk6)

class chunk__trackstrack:
	def __init__(self, ebrw_readstr):
		self.unk1 = ebrw_readstr.int_u32()
		self.idnum = ebrw_readstr.int_u32()
		self.unk3 = ebrw_readstr.int_u32()
		self.unk4 = ebrw_readstr.int_u32()
		self.tracknum = ebrw_readstr.int_u32()
		self.unk6 = ebrw_readstr.int_u32()
		#print('trk', self.unk1, self.idnum, self.unk3, self.unk4, self.tracknum, self.unk6)

class chunk__arrangerpart:
	def __init__(self, ebrw_readstr):
		self.unknowns = []
		self.unknowns.append(  ebrw_readstr.int_u32()  )
		self.unknowns.append(  ebrw_readstr.int_u16()  )
		self.unknowns.append(  ebrw_readstr.int_u16()  )
		self.pos = ebrw_readstr.int_u64()
		self.dur = ebrw_readstr.int_u64()
		self.idnum = ebrw_readstr.int_u32()
		self.unknowns.append(  ebrw_readstr.int_u8()  )
		self.unknowns.append(  ebrw_readstr.int_u8()  )
		self.unknowns.append(  ebrw_readstr.int_u8()  )
		self.unknowns.append(  ebrw_readstr.int_u8()  )
		stringsize = ebrw_readstr.int_u32()
		self.unknowns.append(  ebrw_readstr.int_u32()  )
		self.color = ebrw_readstr.int_u32()
		self.unknowns.append(  ebrw_readstr.int_u32()  )
		self.name = ebrw_readstr.string16(stringsize)

class chunk__grooveinfo:
	def __init__(self, ebrw_readstr):
		self.unk1 = ebrw_readstr.int_u32()
		self.unk2 = ebrw_readstr.int_u32()
		self.idnum = ebrw_readstr.int_u32()
		self.path1_size = ebrw_readstr.int_u32()
		self.path2_size = ebrw_readstr.int_u32()
		self.unk3 = ebrw_readstr.int_u32()
		self.path1 = ebrw_readstr.string16_t()
		self.path2 = ebrw_readstr.string16_t()
		self.unk4 = ebrw_readstr.int_u32()
		self.unk5 = ebrw_readstr.int_s32()
		self.unk6 = ebrw_readstr.flags_i32()
		self.unk7 = ebrw_readstr.int_s32()
		self.num_parts = ebrw_readstr.int_s32()
		self.parts = []

		for x in range(self.num_parts):
			partdata = []
			partdata.append( ebrw_readstr.int_u32() )
			partdata.append( ebrw_readstr.int_s32() )
			partdata.append( ebrw_readstr.int_s64() )
			partdata.append( ebrw_readstr.int_s64() )
			partdata.append( ebrw_readstr.float() )
			partdata.append( ebrw_readstr.int_u32() )
			self.parts.append(partdata)

		self.rest = ebrw_readstr.rest()

chunksdef = {}
chunksdef['754be33a5ef5ec44a2f0f4eb3c53af7d'] = chunk__peak
chunksdef['6a208d162123d21186b000c04f8edb8a'] = chunk__region
chunksdef['5a2d8fb20f23d21186af00c04f8edb8a'] = chunk__maindata
chunksdef['49076c4d1623d21186b000c04f8edb8a'] = chunk__track_data
chunksdef['276cd4690b7fd211871700c04f8edb8a'] = chunk__audioinfo
chunksdef['4212abe5d43b1e439148fb80c038eaeb'] = chunk__unknown_data
chunksdef['5d2d8fb20f23d21186af00c04f8edb8a'] = chunk__regiondata
chunksdef['5662f7ab2d39d21186c700c04f8edb8a'] = chunk__marker
chunksdef['07521655f6713e4e83be9dee9c5ba303'] = chunk__tempokeypoint
chunksdef['5287535c45e3784f83b8551935b4c6f7'] = chunk__audiostretch
chunksdef['be3967941a398443878538bda35f409a'] = chunk__startingparam
chunksdef['5c1b70846368d21186fd00c04f8edb8a'] = chunk__track_automation
chunksdef['44030abfa7f8f44788cba63c7756ba9e'] = chunk__audiodefinfo
chunksdef['1d4f23715752d21186dc00c04f8edb8a'] = chunk__metadata
chunksdef['d0fb0bbbaec4044685662b4bf9cccbb5'] = chunk__tracksfolder
chunksdef['2b959c4d344c664295f519126b4420a8'] = chunk__trackstrack
chunksdef['716655fbb8f792429c1a763355d5f0cd'] = chunk__arrangerpart
chunksdef['1b1ce45016af194e8cdba707237b7921'] = chunk__grooveinfo
#chunksdef['b5c7e0971f2d46449de8c07ff6f43b3b'] = chunk__regiondata_2

# ---------------------- INDATA ----------------------

verboseid = {}
verboseid['5a2d8fb20f23d21186af00c04f8edb8a'] = 'MainData'
verboseid['49076c4d1623d21186b000c04f8edb8a'] = 'TrackData'
verboseid['276cd4690b7fd211871700c04f8edb8a'] = 'TrackAudioInfo'
verboseid['3e0c0223541dfc44aab68330c9121f22'] = 'TrackMIDIInfo'
verboseid['6a208d162123d21186b000c04f8edb8a'] = 'TrackRegion'
verboseid['d0fb0bbbaec4044685662b4bf9cccbb5'] = 'TrackSFolder'
verboseid['2b959c4d344c664295f519126b4420a8'] = 'TrackSTrack'
verboseid['9d74b872ab14884594a939343aeef7cc'] = 'MixerChannel'
verboseid['a132b74c04e40d498806ede87d7d2c4f'] = 'TrackGroove'
verboseid['5c1b70846368d21186fd00c04f8edb8a'] = 'TrackAutomation'
verboseid['1b1ce45016af194e8cdba707237b7921'] = 'GrooveInfo'
verboseid['b5c7e0971f2d46449de8c07ff6f43b3b'] = 'RegionDataMIDI'
verboseid['5662f7ab2d39d21186c700c04f8edb8a'] = 'Marker'
verboseid['754be33a5ef5ec44a2f0f4eb3c53af7d'] = 'Peak?'
verboseid['4212abe5d43b1e439148fb80c038eaeb'] = 'V3Peak?'
verboseid['5287535c45e3784f83b8551935b4c6f7'] = 'AudioStretch'
verboseid['07521655f6713e4e83be9dee9c5ba303'] = 'TempoKeyPoint'
verboseid['44030abfa7f8f44788cba63c7756ba9e'] = 'AudioDef:Info'
verboseid['5d2d8fb20f23d21186af00c04f8edb8a'] = 'RegionDataAudio'
verboseid['be3967941a398443878538bda35f409a'] = 'StartingParams'
verboseid['1d4f23715752d21186dc00c04f8edb8a'] = 'MetaData'
verboseid['f7ef7162791cb545a06eeb59467bcb28'] = 'TrackOrder'
verboseid['716655fbb8f792429c1a763355d5f0cd'] = 'ArrangerPart'

verboseid['a95c808a7402c242b8b9572f6786317c'] = 'Group:AudioDefList'
verboseid['1d54047b1c0adc4faeb3d4935206611d'] = 'Group:AudioDef'
verboseid['5b2d8fb20f23d21186af00c04f8edb8a'] = 'Group:RegionDatas'
verboseid['a59e8054b89bcd458d2b3ef94586a8e0'] = 'Group:GroovePool'
verboseid['48076c4d1623d21186b000c04f8edb8a'] = 'Group:Track'
verboseid['47076c4d1623d21186b000c04f8edb8a'] = 'Group:TrackList'
verboseid['e42b0d22d37fd211871800c04f8edb8a'] = 'Group:Mixer'
verboseid['f40e02902d39d21186c700c04f8edb8a'] = 'Group:Markers'
verboseid['172d16be624d2c48b80bfcf30fa53b02'] = 'Group:Peaks'
verboseid['4a076c4d1623d21186b000c04f8edb8a'] = 'Group:Regions'
verboseid['266cd4690b7fd211871700c04f8edb8a'] = 'Group:AudioInfo'
verboseid['07521655f6713e4e83be9dee9c5ba303'] = 'Group:TempoKeyPoints'
verboseid['5287535c45e3784f83b8551935b4c6f7'] = 'Group:AudioStretch'
verboseid['be3967941a398443878538bda35f409a'] = 'Group:StartingParams'
verboseid['5d1b70846368d21186fd00c04f8edb8a'] = 'Group:TrackAuto'
verboseid['bc945f925a52d21186dc00c04f8edb8a'] = 'Group:MetaData'
verboseid['35fdff0c5f03ec4a9cc373b0187005a7'] = 'Group:Arranger'

class sony_acid_chunk:
	def __init__(self):
		self.id = None
		self.size = 0
		self.start = 0
		self.end = 0
		self.is_list = False
		self.in_data = []
		self.content = None

	def __getitem__(self, v):
		return self.in_data[v]

	def __iter__(self):
		return self.in_data.__iter__()

	def __repr__(self):
		idname = self.id.hex()
		if idname in verboseid: visname = verboseid[idname]
		else: visname = 'UnknownData:'+self.id.hex()
		return '<SF ACID Chunk - %s>' % visname

	def iter_wtypes(self):
		for x in self.in_data.__iter__():
			idname = x.id.hex()
			yield x, verboseid[idname] if idname in verboseid else None

	def read(self, ebrw_readstr, tnum, verb=VERBOSE):
		self.id = ebrw_readstr.raw(16)
		self.size = ebrw_readstr.int_u64()-24
		self.start = ebrw_readstr.tell_real()
		self.is_list = self.id[0:4] in [b'riff', b'list']

		if self.is_list:
			self.id = ebrw_readstr.raw(16)
			gidname = self.id.hex()
			if gidname in verboseid: gidname = verboseid[gidname]
			if verb: print('\t'*tnum, '$Group %s \\' % gidname)
			ebrw_readstr.isolate_size(self.size-16)
			while ebrw_readstr.remaining():
				inchunk = sony_acid_chunk()
				inchunk.read(ebrw_readstr, tnum+1)
				self.in_data.append(inchunk)
			ebrw_readstr.isolate_end()
			if verb: print('\t'*tnum, '       /')

		else:
			idname = self.id.hex()

			if verb:
				if idname in verboseid: visname = verboseid[idname]
				else: visname = 'UnknownData:'+self.id.hex()
				print('\t'*tnum,  visname)

			if idname in chunksdef and not SHOWALL: 
				ebrw_readstr.isolate_size(self.size)
				self.content = chunksdef[idname](ebrw_readstr)
				ebrw_readstr.isolate_end()
				#print(ebrw_readstr.raw(self.size).hex())
			else:
				if verb: print('\t'*tnum,  ebrw_readstr.raw(self.size).hex())
				else: ebrw_readstr.skip(self.size)

class sony_acid_song:
	def __init__(self):
		self.root = sony_acid_chunk()
		self.zipped = False
		self.zipfile = None

	def load_from_file(self, input_file):
		self.zipped = False
		self.zipfile = None

		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)

		if ebrw_readstr.read(2) == b'PK':
			self.zipped = True
			self.zipfile = zipfile.ZipFile(input_file, 'r')
			acdfound = False
			for filename in self.zipfile.namelist():
				if filename.endswith('.acd'):
					ebrw_readstr.load_data(self.zipfile.read(filename))
					acdfound = True
			if not acdfound:
				raise ProjectFileParserException('new_acid: ACID file not found in zip')
		ebrw_readstr.seek(0)

		self.root = sony_acid_chunk()
		self.root.read(ebrw_readstr, 0)
		return True

#apeinst_obj = sony_acid_song()
#apeinst_obj.load_from_file("testin.acd")
