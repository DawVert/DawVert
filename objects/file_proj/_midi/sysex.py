
from io import BytesIO
#from objects import globalstore

from external.easybinrw import easybinrw

from objects.file_proj._midi.vendors import universal
from objects.file_proj._midi.vendors import roland
from objects.file_proj._midi.vendors import yamaha
from objects.file_proj._midi.vendors import sony

class vendor_obj:
	def __init__(self, ebrw_readstr):
		self.id = None
		self.ext = False
		self.name = None
		self.hex = None
		if ebrw_readstr:
			self.id = ebrw_readstr.read(1)
			if self.id[0] == 0:
				self.ext = True
				self.id += ebrw_readstr.read(2)

			self.hex = '#'+bytes.hex(self.id)
			#if idvals_sysex_brands.check_exists(self.hex): 
			#	self.name = idvals_sysex_brands.get_idval(str(self.hex), 'name')
			self.id = int.from_bytes(self.id, 'big')

def decode_anvil_color(anvilcolordata):
	red_p1 = anvilcolordata[3] & 0x3f 
	red_p2 = anvilcolordata[2] & 0xe0
	out_red = (red_p1 << 2) + (red_p2 >> 5)

	green_p1 = anvilcolordata[2] & 0x1f
	green_p2 = anvilcolordata[1] & 0xf0
	out_green = (green_p1 << 3) + (green_p2 >> 4)

	blue_p1 = anvilcolordata[1] & 0x0f
	blue_p2 = anvilcolordata[0] & 0x0f
	out_blue = (blue_p1 << 4) + blue_p2
	return [out_red, out_green, out_blue]

class seqspec_obj:
	def __init__(self):
		self.data = None
		self.known = False

		self.sequencer = None
		self.command = None
		self.param = None
		self.value = None

	def detect(self, sysexdata):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_data(sysexdata)

		self.vendor = vendor_obj(ebrw_readstr)
		if self.vendor.id == 5 and self.vendor.ext == False:
			self.sequencer = 'anvil_studio'
			first = ebrw_readstr.read(1)[0]
			if first == 15:
				second = ebrw_readstr.read(1)[0]
				if second == 52: self.param, self.value = 'color', decode_anvil_color(ebrw_readstr.read(4))
				elif second == 45: self.param, self.value = 'data', ebrw_readstr.rest().decode().split(',')
				elif second == 6: self.param, self.value = 'synth_name', ebrw_readstr.rest().decode()
				else: self.value = [15, second, ebrw_readstr.rest()]
			else: self.value = [first[0], ebrw_readstr.rest()]

		elif self.vendor.id == 83 and self.vendor.ext == False:
			if ebrw_readstr.read(5) == b'ign\x01\xff': 
				self.sequencer = 'signal_midi'
				self.param = 'color'
				self.value = [x for x in ebrw_readstr.read(3)[::-1]]

		elif self.vendor.id == 80 and self.vendor.ext == False:
			if ebrw_readstr.read(5) == b'reS\x01\xff':
				self.sequencer = 'studio_one'
				self.param = 'color'
				self.value = [x for x in ebrw_readstr.read(3)[::-1]]

		else:
			self.value = ebrw_readstr.rest()

	def print(self):
		print(self.vendor.id, self.vendor.name, self.data, self.sequencer, self.param, self.value if self.param != None else self.value.hex())


class sysex_obj:
	def __init__(self):
		#globalstore.idvals.load('midi_sysex', './data_main/idvals/midi_sysex.csv')

		self.known = False

		self.starttxt = None

		self.vendor = None

		self.model_id = None
		self.model_name = None

		self.device = None
		self.command = None

		self.category = None
		self.group = None
		self.subgroup = None
		self.num = None

		self.param = None
		self.value = None

		self.address = None


	def detect(self, sysexdata):
		datlen = len(sysexdata)
		self.starttxt = sysexdata[0:10]

		ebrw_readstr = BytesIO(sysexdata)

		self.vendor = vendor_obj(ebrw_readstr)

		if datlen <= 3: return False

		self.device = ebrw_readstr.read(1)[0]
		self.model_id = ebrw_readstr.read(1)[0]
		self.command = ebrw_readstr.read(1)[0]

		if self.vendor.ext == False:
			if self.vendor.id == 65: 
				roland.decode(self, ebrw_readstr)

			elif self.vendor.id in [126, 127]: 
				universal.decode(self, ebrw_readstr)

			elif self.vendor.id == 76: 
				sony.decode(self, ebrw_readstr)

			elif self.vendor.id == 67: 
				yamaha.decode(self, ebrw_readstr)

		#self.print()

		return True

	def print(self):
		codehex = self.starttxt.hex()
		print(
			self.known, '|', 
			self.vendor.hex, self.vendor.name, self.vendor.id, '|',
			self.device, self.command, '|',
			self.model_id, self.model_name, '|',
			self.category, self.group, self.subgroup, self.num, '|',
			self.param, self.value, '|', ' '.join([codehex[i:i+2] for i in range(0,len(codehex), 2)])
			)

