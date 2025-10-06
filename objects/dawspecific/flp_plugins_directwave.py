# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions.dawspecific import flp_plugchunks
from external.easybinrw import easybinrw
from objects.dawspecific import flp_plugins
from dataclasses import dataclass
from dataclasses import field

VERBOSE = False

dw_chunks = {}

dw_chunks[1] = 'Main:Program'
dw_chunks[6] = 'Main:Main'
dw_chunks[5] = 'Main:Channel'
dw_chunks[518] = 'Main:Settings'

dw_chunks[500] = 'Region:Main'
dw_chunks[501] = 'Region:Name'
dw_chunks[502] = 'Region:Path'
dw_chunks[503] = 'Region:Sample'
dw_chunks[504] = 'Region:PitchKtrkTicks'
dw_chunks[505] = 'Region:Time'
dw_chunks[506] = 'Region:Sends_FX'
dw_chunks[507] = 'Region:Filter'
dw_chunks[508] = 'Region:SySl'
dw_chunks[509] = 'Region:ASDREnv_Main'
dw_chunks[510] = 'Region:FX_Ringmod'
dw_chunks[511] = 'Region:FX_Decimator'
dw_chunks[512] = 'Region:FX_Quantizer'
dw_chunks[513] = 'Region:FX_Phaser'
dw_chunks[514] = 'Region:ASDREnv_Alt'
dw_chunks[515] = 'Region:LFO'
dw_chunks[516] = 'Region:ModMatrix'
dw_chunks[517] = 'Region:PCMData'

dw_chunks[100] = 'Program:Main'
dw_chunks[102] = 'Program:Name'
dw_chunks[103] = 'Program:PresetPath'
dw_chunks[104] = 'Program:FX_Drive'
dw_chunks[105] = 'Program:FX_Delay'
dw_chunks[106] = 'Program:FX_Reverb'
dw_chunks[107] = 'Program:FX_Chorus'
dw_chunks[108] = 'Program:LFO'
dw_chunks[109] = 'Program:ModVal'

def getname(num): 
	return dw_chunks[num] if num in dw_chunks else '?Unknown:%i?' % num

# ============================================= region ============================================= 

@dataclass
class directwave_region_main:
	key_root: int = 60
	key_min: int = 0
	key_max: int = 127
	vel_min: int = 0
	vel_max: int = 127
	mute: int = 0
	flags: list = field(default_factory=list)
	gain: float = 1.0
	pan: float = 0.5
	unk_2: float = 0.0
	unk_3: int = 0
	unk_4: int = 0
	unk_5: int = 0

	def from_ebrw(self, ebrw_readstr): 
		self.key_root = ebrw_readstr.int_u8()
		self.key_min = ebrw_readstr.int_u8()
		self.key_max = ebrw_readstr.int_u8()
		self.vel_min = ebrw_readstr.int_u8()
		self.vel_max = ebrw_readstr.int_u8()
		self.mute = ebrw_readstr.int_u16()
		self.flags = ebrw_readstr.flags_i16()
		self.gain = ebrw_readstr.float()
		self.pan = ebrw_readstr.float()
		self.unk_2 = ebrw_readstr.float()
		self.unk_3 = ebrw_readstr.int_u8()
		self.unk_4 = ebrw_readstr.int_u8()
		self.unk_5 = ebrw_readstr.int_u16()

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u8(self.key_root)
		ebrw_writestr.int_u8(self.key_min)
		ebrw_writestr.int_u8(self.key_max)
		ebrw_writestr.int_u8(self.vel_min)
		ebrw_writestr.int_u8(self.vel_max)
		ebrw_writestr.int_u16(self.mute)
		ebrw_writestr.flags_i16(self.flags)
		ebrw_writestr.float(self.gain)
		ebrw_writestr.float(self.pan)
		ebrw_writestr.float(self.unk_2)
		ebrw_writestr.int_u8(self.unk_3)
		ebrw_writestr.int_u8(self.unk_4)
		ebrw_writestr.int_u16(self.unk_5)
		return ebrw_writestr.getvalue()

@dataclass
class directwave_region_sample:
	num_samples: int = 1
	channels: int = 0
	bits: int = 0
	hz: float = 44100
	loop_type: int = 0
	loop_start: int = 0
	loop_end: int = 0
	start: int = 0

	def from_ebrw(self, ebrw_readstr): 
		self.num_samples = ebrw_readstr.int_u32()
		ebrw_readstr.skip(4)
		self.channels = ebrw_readstr.int_u32()
		self.bits = ebrw_readstr.int_u32()
		self.hz = ebrw_readstr.float()
		self.loop_type = ebrw_readstr.int_u32()
		self.loop_start = ebrw_readstr.int_u32()
		self.loop_end = ebrw_readstr.int_u32()
		self.start = ebrw_readstr.int_u32()
		#print(  ebrw_readstr.rest()  )

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u32(max(0, self.num_samples))
		ebrw_writestr.int_u32(0)
		ebrw_writestr.int_u32(self.channels)
		ebrw_writestr.int_u32(self.bits)
		ebrw_writestr.float(self.hz)
		ebrw_writestr.int_u32(self.loop_type)
		ebrw_writestr.int_u32(int(self.loop_start))
		ebrw_writestr.int_u32(int(self.loop_end))
		ebrw_writestr.int_u32(int(self.start))
		ebrw_writestr.raw(b'\x10\x00\x00\x00')
		return ebrw_writestr.getvalue()

@dataclass
class directwave_region_pitch:
	tune: float = 0.5
	semi: int = 0
	fine: int = 0
	k_trk: int = 100

	def from_ebrw(self, ebrw_readstr): 
		self.tune = ebrw_readstr.float()
		self.semi = ebrw_readstr.int_s8()
		self.fine = ebrw_readstr.int_s8()
		self.k_trk = ebrw_readstr.int_u16()

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.float(self.tune)
		ebrw_writestr.int_s8(self.semi)
		ebrw_writestr.int_s8(self.fine)
		ebrw_writestr.int_u16(self.k_trk)
		return ebrw_writestr.getvalue()

@dataclass
class directwave_region_timestretch:
	time: int = 0
	sync: int = 0
	stretch: float = 0.5
	grain: float = 0.5
	smooth: float = 1

	def from_ebrw(self, ebrw_readstr): 
		self.time = ebrw_readstr.int_u8()
		self.sync = ebrw_readstr.int_u8()
		self.stretch = ebrw_readstr.float()
		self.grain = ebrw_readstr.float()
		self.smooth = ebrw_readstr.float()

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u8(self.time)
		ebrw_writestr.int_u8(self.sync)
		ebrw_writestr.float(self.stretch)
		ebrw_writestr.float(self.grain)
		ebrw_writestr.float(self.smooth)
		return ebrw_writestr.getvalue()

@dataclass
class directwave_region_filter:
	cutoff: float = 0.4724409580230713
	reso: float = 0.5
	shape: float = 0
	type: int = 0

	def from_ebrw(self, ebrw_readstr): 
		self.type = ebrw_readstr.int_u32()
		self.cutoff = ebrw_readstr.float()
		self.reso = ebrw_readstr.float()
		self.shape = ebrw_readstr.float()

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u32(self.type)
		ebrw_writestr.float(self.cutoff)
		ebrw_writestr.float(self.reso)
		ebrw_writestr.float(self.shape)
		ebrw_writestr.int_u32(0)
		return ebrw_writestr.getvalue()

@dataclass
class directwave_region_sysl:
	sy: int = 0
	sl: int = 0

	def from_ebrw(self, ebrw_readstr): 
		self.sy = ebrw_readstr.int_u8()
		self.sl = ebrw_readstr.int_u8()

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u8(self.sy)
		ebrw_writestr.int_u8(self.sl)
		return ebrw_writestr.getvalue()

@dataclass
class directwave_region_adsr:
	attack: float = 0
	decay: float = 0.5
	sustain: float = 0.5
	release: float = 0.25

	def from_ebrw(self, ebrw_readstr): 
		self.attack = ebrw_readstr.float()
		self.decay = ebrw_readstr.float()
		self.sustain = ebrw_readstr.float()
		self.release = ebrw_readstr.float()

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.float(self.attack)
		ebrw_writestr.float(self.decay)
		ebrw_writestr.float(self.sustain)
		ebrw_writestr.float(self.release)
		return ebrw_writestr.getvalue()

@dataclass
class directwave_region_fx_2param:
	enable: int = 0
	param1: float = 0
	param2: float = 1

	def from_ebrw(self, ebrw_readstr): 
		self.enable = ebrw_readstr.int_u8()
		self.param1 = ebrw_readstr.float()
		self.param2 = ebrw_readstr.float()

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u8(self.enable)
		ebrw_writestr.float(self.param1)
		ebrw_writestr.float(self.param2)
		return ebrw_writestr.getvalue()

@dataclass
class directwave_region_lfo:
	wave: int = 0
	ratetype: int = 0
	rate: float = 0.10000000149011612
	phase: float = 1
	attack: float = 0

	def from_ebrw(self, ebrw_readstr): 
		self.wave = ebrw_readstr.int_u8()
		self.ratetype = ebrw_readstr.int_u16()
		ebrw_readstr.skip(1)
		self.rate = ebrw_readstr.float()
		self.phase = ebrw_readstr.float()
		self.attack = ebrw_readstr.float()

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u8(self.wave)
		ebrw_writestr.int_u16(self.ratetype)
		ebrw_writestr.int_u8(0)
		ebrw_writestr.float(self.rate)
		ebrw_writestr.float(self.phase)
		ebrw_writestr.float(self.attack)
		ebrw_writestr.int_u32(0)
		return ebrw_writestr.getvalue()

@dataclass
class directwave_region_mod:
	mod_from: int = 0
	mod_to: int = 0
	amount: float = 0.5

	def from_ebrw(self, ebrw_readstr): 
		self.mod_from = ebrw_readstr.int_u16()
		self.mod_to = ebrw_readstr.int_u16()
		self.amount = ebrw_readstr.float()

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u16(self.mod_from)
		ebrw_writestr.int_u16(self.mod_to)
		ebrw_writestr.float(self.amount)
		return ebrw_writestr.getvalue()

class directwave_region:
	def __init__(self):
		self.main = directwave_region_main()
		self.sample = directwave_region_sample()
		self.pitch = directwave_region_pitch()
		self.timestretch = directwave_region_timestretch()
		self.filter_a = directwave_region_filter()
		self.filter_b = directwave_region_filter()
		self.sysl = directwave_region_sysl()
		self.env_main = directwave_region_adsr()
		self.env_alt1 = directwave_region_adsr()
		self.env_alt2 = directwave_region_adsr()

		self.lfo1 = directwave_region_lfo()
		self.lfo2 = directwave_region_lfo()

		self.fx_ringmod = directwave_region_fx_2param()
		self.fx_decimator = directwave_region_fx_2param()
		self.fx_quantizer = directwave_region_fx_2param()
		self.fx_phaser = directwave_region_fx_2param()

		self.modmatrix = [directwave_region_mod() for x in range(16)]

		self.fx_phaser.param1 = 0.5

		self.modmatrix[0].mod_from = 2
		self.modmatrix[0].mod_to = 2
		self.modmatrix[0].amount = 1

		self.modmatrix[1].mod_from = 3
		self.modmatrix[1].mod_to = 34
		self.modmatrix[1].amount = 0.75

		self.modmatrix[2].mod_from = 12
		self.modmatrix[2].mod_to = 1

		self.lfo2.rate = 0.550000011920929

		self.env_main.sustain = 1

		self.sends_fx = [.5,.5,.5,1]
		self.name = b''
		self.path = b''
		self.pcmdata = None
		self.flacdata = None

	def read(self, ebrw_readstr):
		self.modmatrix = []
		filternum = 0
		altenvnum = 0
		lfonum = 0
		while ebrw_readstr.remaining():
			chunktype, chunksize = flp_plugchunks.read_header(ebrw_readstr)

			ebrw_readstr.isolate_size(chunksize)

			if VERBOSE: 
				print('\t\t\t', getname(chunktype), chunksize, end='')
				print(ebrw_readstr.rest().hex())
				ebrw_readstr.seek(0)
			if chunktype == 500: self.main.from_ebrw(ebrw_readstr)
			elif chunktype == 501: self.name = ebrw_readstr.raw(chunksize)
			elif chunktype == 502: self.path = ebrw_readstr.raw(chunksize)
			elif chunktype == 503: self.sample.from_ebrw(ebrw_readstr)
			elif chunktype == 504: self.pitch.from_ebrw(ebrw_readstr)
			elif chunktype == 505: self.timestretch.from_ebrw(ebrw_readstr)
			elif chunktype == 506: self.sends_fx = ebrw_readstr.list_float(4)
			elif chunktype == 507:
				if filternum == 0: self.filter_a.from_ebrw(ebrw_readstr)
				if filternum == 1: self.filter_b.from_ebrw(ebrw_readstr)
				filternum += 1
			elif chunktype == 508: self.sysl.from_ebrw(ebrw_readstr)
			elif chunktype == 509: self.env_main.from_ebrw(ebrw_readstr)
			elif chunktype == 510: self.fx_ringmod.from_ebrw(ebrw_readstr)
			elif chunktype == 511: self.fx_decimator.from_ebrw(ebrw_readstr)
			elif chunktype == 512: self.fx_quantizer.from_ebrw(ebrw_readstr)
			elif chunktype == 513: self.fx_phaser.from_ebrw(ebrw_readstr)
			elif chunktype == 514:
				if altenvnum == 0: self.env_alt1.from_ebrw(ebrw_readstr)
				if altenvnum == 1: self.env_alt2.from_ebrw(ebrw_readstr)
				altenvnum += 1
			elif chunktype == 515:
				if lfonum == 0: self.lfo1.from_ebrw(ebrw_readstr)
				if lfonum == 1: self.lfo2.from_ebrw(ebrw_readstr)
				lfonum += 1
			elif chunktype == 516:
				mod_obj = directwave_region_mod()
				mod_obj.from_ebrw(ebrw_readstr)
				self.modmatrix.append(mod_obj)
			elif chunktype == 517:
				self.pcmdata = ebrw_readstr.raw(chunksize)
			elif chunktype == 518:
				self.flacdata = ebrw_readstr.raw(chunksize)

			ebrw_readstr.isolate_end()
			
	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		flp_plugchunks.write_chunk(ebrw_writestr, 500, self.main.dump())
		flp_plugchunks.write_chunk(ebrw_writestr, 501, self.name)
		flp_plugchunks.write_chunk(ebrw_writestr, 502, self.path)
		flp_plugchunks.write_chunk(ebrw_writestr, 503, self.sample.dump())
		flp_plugchunks.write_chunk(ebrw_writestr, 504, self.pitch.dump())
		flp_plugchunks.write_chunk(ebrw_writestr, 505, self.timestretch.dump())

		info_sendsfx = easybinrw.binwrite()
		info_sendsfx.list_float(self.sends_fx, 4)
		info_sendsfx.raw(b'\0'*32)
		flp_plugchunks.write_chunk(ebrw_writestr, 506, info_sendsfx.getvalue())
		flp_plugchunks.write_chunk(ebrw_writestr, 507, self.filter_a.dump())
		flp_plugchunks.write_chunk(ebrw_writestr, 507, self.filter_b.dump())
		flp_plugchunks.write_chunk(ebrw_writestr, 508, self.sysl.dump())
		flp_plugchunks.write_chunk(ebrw_writestr, 509, self.env_main.dump())
		flp_plugchunks.write_chunk(ebrw_writestr, 510, self.fx_ringmod.dump())
		flp_plugchunks.write_chunk(ebrw_writestr, 511, self.fx_decimator.dump())
		flp_plugchunks.write_chunk(ebrw_writestr, 512, self.fx_quantizer.dump())
		flp_plugchunks.write_chunk(ebrw_writestr, 513, self.fx_phaser.dump())
		flp_plugchunks.write_chunk(ebrw_writestr, 514, self.env_alt1.dump())
		flp_plugchunks.write_chunk(ebrw_writestr, 514, self.env_alt2.dump())
		flp_plugchunks.write_chunk(ebrw_writestr, 515, self.lfo1.dump())
		flp_plugchunks.write_chunk(ebrw_writestr, 515, self.lfo2.dump())
		for mod_obj in self.modmatrix:
			flp_plugchunks.write_chunk(ebrw_writestr, 516, mod_obj.dump())
		if self.pcmdata is not None:
			flp_plugchunks.write_chunk(ebrw_writestr, 517, self.pcmdata)
		if self.flacdata is not None:
			flp_plugchunks.write_chunk(ebrw_writestr, 518, self.flacdata)
		flp_plugchunks.write_chunk(ebrw_writestr, 4, b'')

		return ebrw_writestr.getvalue()

# ============================================= Program ============================================= 

@dataclass
class directwave_program_fx_drive:
	a_enable: int = 0
	b_enable: int = 0
	a_amount: float = 0
	b_amount: float = 0

	def from_ebrw(self, ebrw_readstr): 
		self.a_enable = ebrw_readstr.int_u8()
		self.b_enable = ebrw_readstr.int_u8()
		self.a_amount = ebrw_readstr.float()
		self.b_amount = ebrw_readstr.float()

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u8(self.a_enable)
		ebrw_writestr.int_u8(self.b_enable)
		ebrw_writestr.float(self.a_amount)
		ebrw_writestr.float(self.b_amount)
		return ebrw_writestr.getvalue()

@dataclass
class directwave_program_fx_delay:
	enable: int = 0
	mode: int = 0
	delay: float = 0.75
	feedback: float = 0.75
	low_cut: float = 0.5
	high_cut: float = 0.75

	def from_ebrw(self, ebrw_readstr): 
		self.enable = ebrw_readstr.int_u8()
		self.mode = ebrw_readstr.int_u8()
		self.delay = ebrw_readstr.float()
		self.feedback = ebrw_readstr.float()
		self.low_cut = ebrw_readstr.float()
		self.high_cut = ebrw_readstr.float()

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u8(self.enable)
		ebrw_writestr.int_u8(self.mode)
		ebrw_writestr.float(self.delay)
		ebrw_writestr.float(self.feedback)
		ebrw_writestr.float(self.low_cut)
		ebrw_writestr.float(self.high_cut)
		return ebrw_writestr.getvalue()

@dataclass
class directwave_program_fx_reverb:
	enable: int = 0
	room: float = 0.25
	damp: float = 0.5
	diffusion: float = 0.75
	decay: float = 0.25

	def from_ebrw(self, ebrw_readstr): 
		self.enable = ebrw_readstr.int_u8()
		self.room = ebrw_readstr.float()
		self.damp = ebrw_readstr.float()
		self.diffusion = ebrw_readstr.float()
		self.decay = ebrw_readstr.float()

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u8(self.enable)
		ebrw_writestr.float(self.room)
		ebrw_writestr.float(self.damp)
		ebrw_writestr.float(self.diffusion)
		ebrw_writestr.float(self.decay)
		return ebrw_writestr.getvalue()

@dataclass
class directwave_program_fx_chorus:
	enable: int = 0
	delay: float = 0.25
	depth: float = 0.5
	rate: float = 0.25
	feedback: float = 0

	def from_ebrw(self, ebrw_readstr): 
		self.enable = ebrw_readstr.int_u8()
		self.delay = ebrw_readstr.float()
		self.depth = ebrw_readstr.float()
		self.rate = ebrw_readstr.float()
		self.feedback = ebrw_readstr.float()

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u8(self.enable)
		ebrw_writestr.float(self.delay)
		ebrw_writestr.float(self.depth)
		ebrw_writestr.float(self.rate)
		ebrw_writestr.float(self.feedback)
		return ebrw_writestr.getvalue()

@dataclass
class directwave_program_lfo:
	enable: int = 0
	wave: int = 0
	rate: float = 0.1
	phase: float = 1
	attack: float = 0

	def from_ebrw(self, ebrw_readstr): 
		self.enable = ebrw_readstr.int_u8()
		self.wave = ebrw_readstr.int_u8()
		ebrw_readstr.skip(2)
		self.rate = ebrw_readstr.float()
		self.phase = ebrw_readstr.float()
		self.attack = ebrw_readstr.float()

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u8(self.enable)
		ebrw_writestr.int_u8(self.wave)
		ebrw_writestr.raw(b'\0'*2)
		ebrw_writestr.float(self.rate)
		ebrw_writestr.float(self.phase)
		ebrw_writestr.float(self.attack)
		ebrw_writestr.raw(b'\0'*4)
		return ebrw_writestr.getvalue()

@dataclass
class directwave_program_main:
	num: int = 0
	playmode: int = 0
	glidemode: int = 0
	vol: float = 1
	glidetime: float = 0
	used: int = 0

	def from_ebrw(self, ebrw_readstr): 
		self.num = ebrw_readstr.int_u32()
		self.playmode = ebrw_readstr.int_u8()
		self.glidemode = ebrw_readstr.int_u8()
		self.vol = ebrw_readstr.float()
		self.glidetime = ebrw_readstr.float()
		self.used = ebrw_readstr.int_u32()

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u32(self.num)
		ebrw_writestr.int_u8(self.playmode)
		ebrw_writestr.int_u8(self.glidemode)
		ebrw_writestr.float(self.vol)
		ebrw_writestr.float(self.glidetime)
		ebrw_writestr.int_u32(self.used)
		ebrw_writestr.int_u32(0)
		ebrw_writestr.int_u32(0)
		ebrw_writestr.int_u32(0)
		return ebrw_writestr.getvalue()

class directwave_program:
	def __init__(self):
		self.regions = []
		self.name = b'---'
		self.path = b''
		self.main = directwave_program_main()
		self.fx_drive = directwave_program_fx_drive()
		self.fx_delay = directwave_program_fx_delay()
		self.fx_reverb = directwave_program_fx_reverb()
		self.fx_chorus = directwave_program_fx_chorus()
		self.lfo1 = directwave_program_lfo()
		self.lfo2 = directwave_program_lfo()
		self.modvals = [0,0,0,0]

	def add_region(self):
		region_obj = directwave_region()
		self.regions.append(region_obj)
		return region_obj

	def read(self, ebrw_readstr):
		self.regions = []
		self.modvals = []
		lfonum = 0
		while ebrw_readstr.remaining():
			chunktype, chunksize = flp_plugchunks.read_header(ebrw_readstr)
			with ebrw_readstr.isolate_size(chunksize, True) as ebrw_readstr: 
				if VERBOSE: print('\t\t', getname(chunktype), chunksize, end=' > ')
				if chunktype == 100:
					self.main.from_ebrw(ebrw_readstr)
					if VERBOSE: print(self.main)
				elif chunktype == 102:
					self.name = ebrw_readstr.raw(chunksize)
					if VERBOSE: print(self.name)
				elif chunktype == 103:
					self.path = ebrw_readstr.raw(chunksize)
					if VERBOSE: print(self.path)
				elif chunktype == 104:
					self.fx_drive.from_ebrw(ebrw_readstr)
					if VERBOSE: print(self.fx_drive)
				elif chunktype == 105:
					self.fx_delay.from_ebrw(ebrw_readstr)
					if VERBOSE: print(self.fx_delay)
				elif chunktype == 106:
					self.fx_reverb.from_ebrw(ebrw_readstr)
					if VERBOSE: print(self.fx_reverb)
				elif chunktype == 107:
					self.fx_chorus.from_ebrw(ebrw_readstr)
					if VERBOSE: print(self.fx_chorus)
				elif chunktype == 108:
					if VERBOSE: print()
					if lfonum == 0: self.lfo1.from_ebrw(ebrw_readstr)
					if lfonum == 1: self.lfo2.from_ebrw(ebrw_readstr)
					lfonum += 1
				elif chunktype == 109:
					if VERBOSE: print()
					self.modvals.append(ebrw_readstr.float())
				elif chunktype == 3:
					if VERBOSE: print()
					region_obj = directwave_region()
					region_obj.read(ebrw_readstr)
					self.regions.append(region_obj)
				else:
					if VERBOSE: print(ebrw_readstr.raw(chunksize).hex())

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		flp_plugchunks.write_chunk(ebrw_writestr, 100, self.main.dump())
		flp_plugchunks.write_chunk(ebrw_writestr, 102, self.name)
		flp_plugchunks.write_chunk(ebrw_writestr, 103, self.path)
		flp_plugchunks.write_chunk(ebrw_writestr, 104, self.fx_drive.dump())
		flp_plugchunks.write_chunk(ebrw_writestr, 105, self.fx_delay.dump())
		flp_plugchunks.write_chunk(ebrw_writestr, 106, self.fx_reverb.dump())
		flp_plugchunks.write_chunk(ebrw_writestr, 107, self.fx_chorus.dump())
		flp_plugchunks.write_chunk(ebrw_writestr, 108, self.lfo1.dump())
		flp_plugchunks.write_chunk(ebrw_writestr, 108, self.lfo2.dump())
		for x in self.modvals:
			modvals__ebrw_writestr = easybinrw.binwrite()
			modvals__ebrw_writestr.float(x)
			flp_plugchunks.write_chunk(ebrw_writestr, 109, modvals__ebrw_writestr.getvalue())
		for x in range(100):
			modvals__ebrw_writestr = easybinrw.binwrite()
			modvals__ebrw_writestr.int_u8(x)
			modvals__ebrw_writestr.int_u32(0)
			modvals__ebrw_writestr.float(1)
			modvals__ebrw_writestr.int_u32(0)
			flp_plugchunks.write_chunk(ebrw_writestr, 110, modvals__ebrw_writestr.getvalue())
		for region in self.regions:
			flp_plugchunks.write_chunk(ebrw_writestr, 3, region.dump())
		flp_plugchunks.write_chunk(ebrw_writestr, 2, b'')
		return ebrw_writestr.getvalue()

# ============================================= Main ============================================= 

@dataclass
class directwave_channel:
	channelid: int = 0
	unk1: float = 0.0078125
	prognum: int = 0
	output: int = 0
	mute: int = 0
	solo: int = 0
	pitchbend_range: int = 200
	pitch_bend: float = 0
	mod_wheel: float = 0
	mast_vol: float = 0.787401556968689
	mast_pan: float = 0.5
	mast_exp: float = 1
	res_005: float = 0
	res_006: float = 0
	res_007: float = 0
	res_008: float = 0
	res_009: float = 0
	res_010: float = 0
	res_011: float = 0
	res_012: float = 0
	res_013: float = 0
	res_014: float = 0
	res_015: float = 0

	def from_ebrw(self, ebrw_readstr): 
		self.channelid = ebrw_readstr.int_u8()
		self.unk1 = ebrw_readstr.float()
		ebrw_readstr.skip(515)
		self.prognum = ebrw_readstr.int_u8()
		self.output = ebrw_readstr.int_u8()
		ebrw_readstr.skip(2)
		self.mute = ebrw_readstr.int_u8()
		self.solo = ebrw_readstr.int_u8()
		ebrw_readstr.skip(2)
		ebrw_readstr.skip(4)
		self.pitchbend_range = ebrw_readstr.int_s32()
		ebrw_readstr.skip(28)
		self.pitch_bend = ebrw_readstr.float()
		self.mod_wheel = ebrw_readstr.float()
		self.mast_vol = ebrw_readstr.float()
		self.mast_pan = ebrw_readstr.float()
		self.mast_exp = ebrw_readstr.float()
		self.res_005 = ebrw_readstr.float()
		self.res_006 = ebrw_readstr.float()
		self.res_007 = ebrw_readstr.float()
		self.res_008 = ebrw_readstr.float()
		self.res_009 = ebrw_readstr.float()
		self.res_010 = ebrw_readstr.float()
		self.res_011 = ebrw_readstr.float()
		self.res_012 = ebrw_readstr.float()
		self.res_013 = ebrw_readstr.float()
		self.res_014 = ebrw_readstr.float()
		self.res_015 = ebrw_readstr.float()

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u8(self.channelid)
		ebrw_writestr.float(self.unk1)
		ebrw_writestr.raw(b'\0'*515)
		ebrw_writestr.int_u8(self.prognum)
		ebrw_writestr.int_u8(self.output)
		ebrw_writestr.raw(b'\0'*2)
		ebrw_writestr.int_u8(self.mute)
		ebrw_writestr.int_u8(self.solo)
		ebrw_writestr.raw(b'\0'*2)
		ebrw_writestr.raw(b'\0'*4)
		ebrw_writestr.int_s32(self.pitchbend_range)
		ebrw_writestr.raw(b'\0'*28)
		ebrw_writestr.float(self.pitch_bend)
		ebrw_writestr.float(self.mod_wheel)
		ebrw_writestr.float(self.mast_vol)
		ebrw_writestr.float(self.mast_pan)
		ebrw_writestr.float(self.mast_exp)
		ebrw_writestr.float(self.res_005)
		ebrw_writestr.float(self.res_006)
		ebrw_writestr.float(self.res_007)
		ebrw_writestr.float(self.res_008)
		ebrw_writestr.float(self.res_009)
		ebrw_writestr.float(self.res_010)
		ebrw_writestr.float(self.res_011)
		ebrw_writestr.float(self.res_012)
		ebrw_writestr.float(self.res_013)
		ebrw_writestr.float(self.res_014)
		ebrw_writestr.float(self.res_015)
		return ebrw_writestr.getvalue()

class directwave_plugin:
	def __init__(self):
		self.version = 38
		self.programs = []
		self.channels = []
		for x in range(16):
			channel_obj = directwave_channel()
			channel_obj.channelid = x
			channel_obj.prognum = x
			self.channels.append(channel_obj)
		for x in range(128):
			program_obj = directwave_program()
			#program_obj.name = str(x).encode()
			program_obj.main.num = x
			self.programs.append(program_obj)

	def read(self, ebrw_readstr):
		self.programs = []
		self.channels = []
		self.version = ebrw_readstr.int_u32()
		while ebrw_readstr.remaining():
			chunktype, chunksize = flp_plugchunks.read_header(ebrw_readstr)

			ebrw_readstr.isolate_size(chunksize)
			if VERBOSE: print('\t', getname(chunktype), chunksize, end=' > ')
			if chunktype == 1:
				if VERBOSE: print()
				program_obj = directwave_program()
				program_obj.read(ebrw_readstr)
				self.programs.append(program_obj)
			elif chunktype == 5:
				if VERBOSE: print()
				channel_obj = directwave_channel()
				channel_obj.from_ebrw(ebrw_readstr)
				self.channels.append(channel_obj)
			else:
				if VERBOSE: print(ebrw_readstr.raw(chunksize).hex())

			ebrw_readstr.isolate_end()

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u32(self.version)
		flp_plugchunks.write_chunk(ebrw_writestr, 6, b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		flp_plugchunks.write_chunk(ebrw_writestr, 518, b'\x01\x00\x00\x00\x00\x00\x00')
		for channel_obj in self.channels:
			flp_plugchunks.write_chunk(ebrw_writestr, 5, channel_obj.dump())
		for program_obj in self.programs:
			flp_plugchunks.write_chunk(ebrw_writestr, 1, program_obj.dump())
		return ebrw_writestr.getvalue()