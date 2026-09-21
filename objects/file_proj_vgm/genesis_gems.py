
from external.easybinrw import easybinrw
from objects import audio_data

class gems_sample:
	def __init__(self):
		self.num = 0
		self.rate = 0
		self.start = 0
		self.size = 0
		self.size2 = 0
		self.data = b''

	def write_sample_file(self, wave_path):
		audio_obj = audio_data.audio_obj()
		audio_obj.rate = 8000
		audio_obj.channels = 1
		audio_obj.pcm_from_bytes(self.data)
		if self.size2: audio_obj.loop = [self.size2, self.size]
		audio_obj.to_file_wav(wave_path)

class gems_samplepack:
	def __init__(self):
		self.samples = []

	def load_from_file(self, inputfile):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(inputfile)
		self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		firstsample = 1<<32
		while ebrw_readstr.remaining() and ebrw_readstr.tell()<firstsample:
			sample = gems_sample()
			sample.num = len(self.samples)
			sample.rate = ebrw_readstr.int_u8()
			sample.start = ebrw_readstr.int_u32()
			if not sample.num: firstsample = sample.start
			if sample.start>ebrw_readstr.state.end: break
			ebrw_readstr.skip(1)
			sample.size = ebrw_readstr.int_u16()
			sample.size2 = ebrw_readstr.int_u16()
			ebrw_readstr.skip(2)
			self.samples.append(sample)
		startloc = ebrw_readstr.tell()

		for x in self.samples:
			ebrw_readstr.seek(x.start)
			x.data = ebrw_readstr.read(x.size)

class gems_seqpack:
	def __init__(self):
		self.songptrs = []

	def load_from_file(self, inputfile):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(inputfile)
		self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		firstptr = 1<<32
		while ebrw_readstr.remaining() and ebrw_readstr.tell()<firstptr:
			ptr = ebrw_readstr.int_u16()
			if not len(self.songptrs): firstptr = ptr
			self.songptrs.append(ptr)

		for ptr in self.songptrs:
			ebrw_readstr.seek(ptr)
			numchans = ebrw_readstr.int_u8()
			chan = []
			for x in range(numchans):
				d = ebrw_readstr.int_u16()
				d += ebrw_readstr.int_u8()<<16
				chan.append(d)
			print(chan)
