# SPDX-FileCopyrightText: 2025 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions.dawspecific import flp_plugchunks
from external.easybinrw import easybinrw
from objects.dawspecific import flp_plugins_directwave

def utf16decode(event_data):
	return event_data.decode('utf-16le').rstrip('\x00\x00')

def utf16encode(text):
	out_text = text if text != None else ''
	return out_text.encode('utf-16le') + b'\x00\x00'

def utf8encode(text):
	out_text = text if text != None else ''
	return out_text.encode('utf-8') + b'\x00'

class flp_autopoint:
	def __init__(self, ebrw_readstr):
		self.pos = 0
		self.val = 0
		self.tension = 0
		self.type = 0
		self.selected = 0
		self.t_sign = 0
		if ebrw_readstr is not None:
			self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.pos = ebrw_readstr.double()
		self.val = ebrw_readstr.double()
		self.tension = ebrw_readstr.float()
		self.type = ebrw_readstr.int_u16()
		self.selected = ebrw_readstr.int_u8()
		self.t_sign = ebrw_readstr.int_u8()

VERBOSE = False

# ---------------------------------------------------- FPC ----------------------------------------------------

class fpc_plugin_layer:
	def __init__(self):
		self.filename = b''
		self.vol = 80
		self.pan = 0
		self.vel_min = 0
		self.vel_max = 127
		self.flags = [0]
		self.tune = 0
		self.unk = -1

	def read(self, ebrw_readstr):
		while ebrw_readstr.remaining():
			chunktype, chunksize = flp_plugchunks.read_header(ebrw_readstr)

			ebrw_readstr.isolate_size(chunksize)
			if VERBOSE:
				print('\t\t\t',chunktype, chunksize, end='')
				if chunktype not in [105]:
					print( ebrw_readstr.raw(ebrw_readstr.remaining()).hex() )
					ebrw_readstr.seek(0)
				else:
					print()

			if chunktype == 300: 
				self.filename = ebrw_readstr.raw(chunksize)
			if chunktype == 301: 
				self.vol = ebrw_readstr.int_s32()
				self.pan = ebrw_readstr.int_s32()
				self.vel_min = ebrw_readstr.int_s32()
				self.vel_max = ebrw_readstr.int_s32()
				self.flags = ebrw_readstr.flags_i32()
				self.tune = ebrw_readstr.int_s32()
				self.unk = ebrw_readstr.int_s32() # -1
			ebrw_readstr.isolate_end()

	def dump(self):
		info__ebrw_writestr = easybinrw.binwrite()
		info__ebrw_writestr.int_s32(self.vol)
		info__ebrw_writestr.int_s32(self.pan)
		info__ebrw_writestr.int_s32(self.vel_min)
		info__ebrw_writestr.int_s32(self.vel_max)
		info__ebrw_writestr.flags_i32(self.flags)
		info__ebrw_writestr.int_s32(self.tune)
		info__ebrw_writestr.int_s32(self.unk)

		total_writer = easybinrw.binwrite()
		flp_plugchunks.write_chunk(total_writer, 300, self.filename)
		flp_plugchunks.write_chunk(total_writer, 301, info__ebrw_writestr.getvalue())
		flp_plugchunks.write_chunk(total_writer, 302, b'')
		return total_writer.getvalue()

class fpc_plugin_pad:
	def __init__(self):
		self.pads = []
		self.key = 0
		self.vol = 99
		self.pan = 0
		self.flags = 0
		self.key = 37
		self.output = 0
		self.cut = -1
		self.cut_by = -1
		self.tune = 0
		self.color = 0
		self.icon = 0
		self.name = b''
		self.auto_vol = []
		self.auto_pan = []
		self.layers = [fpc_plugin_layer()]

	def layers_clear(self):
		self.layers = []

	def layer_add(self):
		layer_obj = fpc_plugin_layer()
		self.layers.append(layer_obj)
		return layer_obj

	def read(self, ebrw_readstr):
		self.layers = []
		while ebrw_readstr.remaining():
			chunktype, chunksize = flp_plugchunks.read_header(ebrw_readstr)

			ebrw_readstr.isolate_size(chunksize)

			if VERBOSE:
				print('\t\t',chunktype, chunksize, end='')
				if chunktype not in [105]:
					print( ebrw_readstr.raw(ebrw_readstr.remaining()).hex() )
					ebrw_readstr.seek(0)
				else:
					print()

			if chunktype == 100:
				self.vol = ebrw_readstr.int_s32()
				self.pan = ebrw_readstr.int_s32()
				self.flags = ebrw_readstr.int_s32()
				self.key = ebrw_readstr.int_s32()
				self.output = ebrw_readstr.int_s32()
				self.cut = ebrw_readstr.int_s32()
				self.cut_by = ebrw_readstr.int_s32()
				self.tune = ebrw_readstr.int_s32()
				self.color = ebrw_readstr.int_s32()
				self.icon = ebrw_readstr.int_s32()
				# 000000000000000000000000000000000000000000000000
			elif chunktype == 101:
				self.name = ebrw_readstr.raw(chunksize)
			elif chunktype == 102:
				# b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
				pass
			elif chunktype == 103:
				autonum = ebrw_readstr.int_s32()
			elif chunktype == 104:
				ebrw_readstr.skip(4)
				version = ebrw_readstr.int_s32()
				numpoints = ebrw_readstr.int_s32()
				points = [flp_autopoint(ebrw_readstr) for x in range(numpoints)]
				if autonum == 0: self.auto_vol = points
				if autonum == 1: self.auto_pan = points
				b'\x80\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00'
			elif chunktype == 105:
				layer_obj = fpc_plugin_layer()
				layer_obj.read(ebrw_readstr)
				self.layers.append(layer_obj)

			ebrw_readstr.isolate_end()
			
	def dump(self):
		total_writer = easybinrw.binwrite()

		info_padinfo = easybinrw.binwrite()
		info_padinfo.int_s32(self.vol)
		info_padinfo.int_s32(self.pan)
		info_padinfo.int_s32(self.flags)
		info_padinfo.int_s32(self.key)
		info_padinfo.int_s32(self.output)
		info_padinfo.int_s32(self.cut)
		info_padinfo.int_s32(self.cut_by)
		info_padinfo.int_s32(self.tune)
		info_padinfo.int_s32(self.color)
		info_padinfo.int_s32(self.icon)
		info_padinfo.list_int_s32([0,0,0,0,0,0], 6)
		flp_plugchunks.write_chunk(total_writer, 100, info_padinfo.getvalue())
		flp_plugchunks.write_chunk(total_writer, 101, self.name)
		flp_plugchunks.write_chunk(total_writer, 102, b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

		for layer_obj in self.layers:
			flp_plugchunks.write_chunk(total_writer, 105, layer_obj.dump())
		flp_plugchunks.write_chunk(total_writer, 103, b'\x00\x00\x00\x00\x00\x00\x00\x00')
		flp_plugchunks.write_chunk(total_writer, 104, b'\x01\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe8?\x00\x00\x00\x00\x00\x00\xf0?\xcd\xccL>\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\xf8?\x00\x00\x00\x00\x00\x00\xe0?\xcd\xccL>\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\xd0?\x00\x00\x00\x00\x00\x00\x00\x00\xcd\xccL>\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\xff\xff\xff\xff\x02\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00')
		flp_plugchunks.write_chunk(total_writer, 103, b'\x01\x00\x00\x00\x00\x00\x00\x00')
		flp_plugchunks.write_chunk(total_writer, 104, b'\x01\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe0?\xcd\xccL>\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x80\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00')

		flp_plugchunks.write_chunk(total_writer, 106, b'')
		return total_writer.getvalue()

class fpc_plugin:
	def __init__(self):
		self.midifile = None
		self.pads = [fpc_plugin_pad() for _ in range(32)]
		self.version = 1000014

	def read(self, ebrw_readstr):
		self.pads = []
		self.version = ebrw_readstr.uint32()
		#print('START')
		while ebrw_readstr.remaining():
			chunktype, chunksize = flp_plugchunks.read_header(ebrw_readstr)
			#print('\t',chunktype, chunksize)

			ebrw_readstr.isolate_size(chunksize)
			if chunktype == 2:
				pad_obj = fpc_plugin_pad()
				pad_obj.read(ebrw_readstr)
				self.pads.append(pad_obj)
			if chunktype == 1:
				self.midifile = ebrw_readstr.raw(chunksize)
			ebrw_readstr.isolate_end()

		#ebrw_readstr.seek(0)
		#compd = ebrw_readstr.rest()
		#compo = self.dump()

		#f = open('test_i.bin', 'wb')
		#f.write(compd)

		#d = open('test_o.bin', 'wb')
		#d.write(compo)

	def dump(self):
		total_writer = easybinrw.binwrite()
		total_writer.int_u32(self.version)
		for pad_obj in self.pads:
			flp_plugchunks.write_chunk(total_writer, 2, pad_obj.dump())
		flp_plugchunks.write_chunk(total_writer, 1, b'')
		return total_writer.getvalue()

# ---------------------------------------------------- Wrapper ----------------------------------------------------

class fruity_wrapper:
	def __init__(self):
		self.version = 10
		self.midi = None
		self.flags = None
		self.io = None
		self.outputs = None
		self.fourid = None
		self.uuid = None
		self.state = None
		self.name = None
		self.file = None
		self.vendor = None
		self.unk_57 = None
		self.unk_31 = None
		self.plugin_type = -1
		self.plugin_other = b''
		self.clapid = None

	def read(self, ebrw_readstr):
		self.version = ebrw_readstr.int_u32()
		while ebrw_readstr.remaining():
			chunktype, chunksize = flp_plugchunks.read_header(ebrw_readstr)

			ebrw_readstr.isolate_size(chunksize)
			if chunktype == 1: self.midi = ebrw_readstr.raw(chunksize)
			elif chunktype == 2: self.flags = ebrw_readstr.raw(chunksize)
			elif chunktype == 30: self.io = ebrw_readstr.raw(chunksize)
			elif chunktype == 31: self.unk_31 = ebrw_readstr.raw(chunksize)
			elif chunktype == 32: self.outputs = ebrw_readstr.raw(chunksize)
			elif chunktype == 50: 
				self.plugin_type = ebrw_readstr.int_u32()
				self.plugin_other = ebrw_readstr.raw(chunksize-4)
			elif chunktype == 51: self.fourid = ebrw_readstr.int_u32()
			elif chunktype == 52: self.uuid = ebrw_readstr.raw(chunksize)
			elif chunktype == 57: self.unk_57 = ebrw_readstr.raw(chunksize)
			elif chunktype == 54: self.name = ebrw_readstr.string(chunksize)
			elif chunktype == 55: self.file = ebrw_readstr.string(chunksize)
			elif chunktype == 56: self.vendor = ebrw_readstr.string(chunksize)
			elif chunktype == 58: self.clapid = ebrw_readstr.string(chunksize)
			elif chunktype == 53: self.state = ebrw_readstr.raw(chunksize)
			#else: 
			#	print('unknown fruity wrapper chunk num:', 
			#		chunktype,
			#		ebrw_readstr.raw(chunksize)
			#		)
			ebrw_readstr.isolate_end()

	def dump(self):
		ebrw_writestr = easybinrw.binwrite()
		ebrw_writestr.int_u32(self.version)
		if self.midi: flp_plugchunks.write_chunk(ebrw_writestr, 1, self.midi)
		if self.flags: flp_plugchunks.write_chunk(ebrw_writestr, 2, self.flags)
		if self.io: flp_plugchunks.write_chunk(ebrw_writestr, 30, self.io)
		if self.unk_31: flp_plugchunks.write_chunk(ebrw_writestr, 31, self.unk_31)
		if self.outputs: flp_plugchunks.write_chunk(ebrw_writestr, 32, self.outputs)
		if self.plugin_type!=-1:
			typed__ebrw_writestr = easybinrw.binwrite()
			typed__ebrw_writestr.int_u32(self.plugin_type)
			typed__ebrw_writestr.raw(self.plugin_other)
			flp_plugchunks.write_chunk(ebrw_writestr, 50, typed__ebrw_writestr.getvalue())
		if self.fourid: flp_plugchunks.write_chunk(ebrw_writestr, 51, self.fourid.to_bytes(4, "little"))
		if self.uuid: flp_plugchunks.write_chunk(ebrw_writestr, 52, self.uuid)
		if self.unk_57: flp_plugchunks.write_chunk(ebrw_writestr, 57, self.unk_57)
		if self.name: flp_plugchunks.write_chunk(ebrw_writestr, 54, self.name.encode())
		if self.file: flp_plugchunks.write_chunk(ebrw_writestr, 55, self.file.encode())
		if self.vendor: flp_plugchunks.write_chunk(ebrw_writestr, 56, self.vendor.encode())
		if self.clapid: flp_plugchunks.write_chunk(ebrw_writestr, 58, self.clapid.encode())
		if self.state: flp_plugchunks.write_chunk(ebrw_writestr, 53, self.state)
		return ebrw_writestr.getvalue()
