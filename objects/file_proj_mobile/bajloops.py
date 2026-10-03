
from external.easybinrw import easybinrw

DEBUGTXT = 0

class bajloop_pattern:
	def __init__(self):
		self.name = ''

	def read_events(self, ebrw_readstr):
		self.events = []
		num_events = ebrw_readstr.int_u16_b()
		#print(num_events, end=' [')
		if num_events:
			num_events_size = ebrw_readstr.int_u16_b()
			for _ in range(num_events): 
				event = ebrw_readstr.list_int_u8(16)
				self.events.append(event)
			ebrw_readstr.skip(16*(num_events_size-num_events))
			self.events = self.events[0:num_events_size]
		#print('', end='] | ')

	def read(self, ebrw_readstr):
		if DEBUGTXT: print('PAT:', end=' ')
		self.unk1 = ebrw_readstr.int_u8()
		if DEBUGTXT: print(self.unk1, end=' | ')
		self.unk2 = ebrw_readstr.int_u8()
		if DEBUGTXT: print(self.unk2, end=' | ')
		self.color = ebrw_readstr.list_int_u8(3)
		if DEBUGTXT: print(self.color.tobytes().hex(), end=' | ')
		self.name = ebrw_readstr.string_t(encoding='iso-8859-1')
		if DEBUGTXT: print(self.name, end=' | ')
		self.read_events(ebrw_readstr)
		if DEBUGTXT: print('')

class bajloop_sample:
	def __init__(self):
		self.name = ''
		self.data = b''

	def read(self, ebrw_readstr):
		assert(ebrw_readstr.int_u8()==6)
		self.bits = ebrw_readstr.int_u8()
		#print(  self.bits, end=' | '  )
		self.channels = ebrw_readstr.int_u8()
		#print(  self.channels, end=' | '  )
		self.unk1 = ebrw_readstr.raw(2).hex()
		#print(  self.unk1, end=' | '  )
		self.freq = ebrw_readstr.int_u16_b()
		#print(  self.freq, end=' | '  )
		self.num_samples = ebrw_readstr.int_u32_b()
		#print(  self.num_samples, end=' | '  )
		self.loop_1 = ebrw_readstr.int_u32()
		#print(  self.loop_1, end=' | '  )
		self.loop_2 = ebrw_readstr.int_u32()
		#print(  self.loop_1+self.loop_2, end=' | '  )
		self.name = ebrw_readstr.string_t(encoding='iso-8859-1')
		#print(  self.name, end=' | '  )
		self.unk3 = ebrw_readstr.raw(4).hex()
		#print(  self.unk3, end=' | '  )
		self.data_size = ebrw_readstr.int_u32_b()
		#print(  self.data_size, end=' | '  )
		self.data = ebrw_readstr.raw(self.data_size)
		#print()

class bajloop_inst:
	def __init__(self):
		self.name = ''
		self.unk = []

	def read(self, ebrw_readstr):
		assert(ebrw_readstr.int_u8()==0)
		self.sample_num = ebrw_readstr.int_u8()
		#print(  self.sample_num, end=' | '  )
		self.unk.append(ebrw_readstr.raw(22).hex())
		self.vol = ebrw_readstr.int_u8()
		self.unk.append(ebrw_readstr.raw(1).hex())
		self.pan = ebrw_readstr.int_u8()
		self.basenote = ebrw_readstr.int_s16()
		self.pitch = ebrw_readstr.int_s16()
		#print( self.basenote , end=' | '  )
		self.unk.append(ebrw_readstr.raw(34).hex())
		#print( self.unk , end=' | '  )
		self.color = ebrw_readstr.list_int_u8(3)
		self.name = ebrw_readstr.string_t(encoding='iso-8859-1')
		#print(  self.name, end=' | '  )

class bajloop_fx:
	def __init__(self):
		self.name = ''
		self.params = []

	def read(self, ebrw_readstr):
		self.unk = ebrw_readstr.raw(5).hex()
		#print(self.unk, end=' ')
		isf = ebrw_readstr.int_u8()
		if isf:
			self.name = ebrw_readstr.string_t()
			self.params = ebrw_readstr.list_int_s16(32)
			if DEBUGTXT: print('FX', self.name, self.params.tolist())

def bajloop_automation_part(ebrw_readstr):
	header1 = ebrw_readstr.int_u8()
	if header1==255:
		assert(ebrw_readstr.int_u8()==1)
		outdata1 = ebrw_readstr.int_u16_b()
		outdata2 = ebrw_readstr.int_u8()
		#print('PART', outdata1)
		return outdata1, outdata2
	else: 
		return None

def bajloop_automations(ebrw_readstr):
	header1 = ebrw_readstr.int_u8()
	if header1==255:
		assert(ebrw_readstr.int_u8()==1)
		tracknum = ebrw_readstr.int_s8()
		paramnum = ebrw_readstr.int_u8()
		data = {}
		while True:
			d = bajloop_automation_part(ebrw_readstr)
			if d==None: break
			else: data[d[0]] = d[1]
		return tracknum, paramnum, data
	else: 
		#print('DONE')
		#print()
		return None

class bajloop_sections:
	def __init__(self):
		self.data1 = []
		self.data2 = b''
		self.data3 = []

	def read(self, ebrw_readstr):
		ebrw_readstr.skip(1)
		num_sections = ebrw_readstr.int_u8()
		for _ in range(num_sections):
			d = ebrw_readstr.raw(7)
			n = ebrw_readstr.string_t()
			self.data1.append([d, n])
		self.data2 = ebrw_readstr.raw(10)
		for x in range(6):
			self.data3.append(  ebrw_readstr.raw(21).hex()  )

class bajloop_file:
	def __init__(self):
		self.name = None
		self.string2 = None
		self.unk1 = None
		self.unk2 = None
		self.unk3 = None
		self.placements = None
		self.unk4 = None
		self.unk5 = None
		self.unk6 = None
		self.fx = []
		self.autos = []
		self.patterns = []
		self.samples = []
		self.insts = []

	def load_from_raw(self, input_data):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_data(input_data)
		return self.load(ebrw_readstr)

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)
		return self.load(ebrw_readstr)

	def load(self, ebrw_readstr):
		self.version = ebrw_readstr.int_u8()
		assert(self.version==10)
		#print('VERSION', self.version)

		if DEBUGTXT: print('--- HEADER ---')
		ebrw_readstr.magic_check(b'Recipe for pure veg song 1.00:\x00')
		self.name = ebrw_readstr.string_t()
		if DEBUGTXT: print('name', self.name)
		self.info = ebrw_readstr.string_t()
		if DEBUGTXT: print('info', self.info)
		self.unk1 = ebrw_readstr.raw(23)
		if DEBUGTXT: print('unk1', self.unk1)
		self.unk2 = ebrw_readstr.raw(15*8)
		if DEBUGTXT: print('unk2', self.unk2)
		self.unk3 = [ebrw_readstr.list_int_u8(2).tolist() for x in range(12)]
		if DEBUGTXT: print('unk3', self.unk3)
		self.unk4 = ebrw_readstr.raw(3)
		self.tempo = ebrw_readstr.int_u8()
		if DEBUGTXT: print('unk4', self.unk4)
		
		self.placements = [ebrw_readstr.list_int_u8(8) for x in range(240)]

		self.unk5 = ebrw_readstr.int_u32()
		if DEBUGTXT: print('unk5', self.unk5)
		self.unk6 = ebrw_readstr.raw(60)

		if DEBUGTXT: print('--- FX ---')
		for _ in range(5):
			fx_obj = bajloop_fx()
			fx_obj.read(ebrw_readstr)
			self.fx.append(fx_obj)

		self.unk7 = ebrw_readstr.raw(2).hex()
		self.unk8 = ebrw_readstr.raw(2).hex()

		#print(self.unk7, self.unk8)

		while True:
			o = bajloop_automations(ebrw_readstr)
			if o==None: break
			else: self.autos.append(o)

		sections = bajloop_sections()
		sections.read(ebrw_readstr)

		if DEBUGTXT: print('--- PATTERN ---')
		for _ in range(128):
			pattern_obj = bajloop_pattern()
			pattern_obj.read(ebrw_readstr)
			self.patterns.append(pattern_obj)

		if DEBUGTXT: print('--- SAMPLES ---')
		num_samples = ebrw_readstr.int_u16_b()
		for _ in range(num_samples):
			sample_obj = bajloop_sample()
			sample_obj.read(ebrw_readstr)
			self.samples.append(sample_obj)
		
		if DEBUGTXT: print('--- INSTRUMENTS ---')
		for _ in range(32):
			inst_obj = bajloop_inst()
			inst_obj.read(ebrw_readstr)
			self.insts.append(inst_obj)

		return True
