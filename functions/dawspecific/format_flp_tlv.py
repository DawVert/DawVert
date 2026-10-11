# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import varint
from external.easybinrw import easybinrw

VERBOSE = False

# ---------------------- decode

def read_tlv(ebrw_writestr):
	event_id = ebrw_writestr.int_u8()
	if event_id <= 63 and event_id >= 0: 
		outval = ebrw_writestr.int_u8()
		if VERBOSE: print('INT8, ', f"{event_id:#010b}"[2:],'|',str(event_id).ljust(3), f"{outval:#010b}"[2:], outval)
		return event_id, outval
	if event_id <= 127 and event_id >= 64: 
		outval = ebrw_writestr.int_u16()
		if VERBOSE: print('INT16,', f"{event_id:#010b}"[2:],'|',str(event_id).ljust(3), f"{outval:#028b}"[2:], outval)
		return event_id, outval
	if event_id <= 191 and event_id >= 128: 
		outval = ebrw_writestr.int_u32()
		if VERBOSE: print('INT32,', f"{event_id:#010b}"[2:],'|',str(event_id).ljust(3), f"{outval:#034b}"[2:], outval)
		return event_id, outval
	if event_id <= 224 and event_id >= 192: 
		if VERBOSE: print('TEXT, ', f"{event_id:#010b}"[2:],'|',event_id)
		return event_id, ebrw_writestr.raw(ebrw_writestr.varint())
	if event_id <= 255 and event_id >= 225: 
		if VERBOSE: print('RAW,  ', f"{event_id:#010b}"[2:],'|',event_id)
		return event_id, ebrw_writestr.raw(ebrw_writestr.varint())

def decode(song_data):
	eventtable = []
	while song_data.remaining():
		event_id, event_data = read_tlv(song_data)
		eventtable.append([event_id, event_data])
	return eventtable

# ---------------------- encode

def write_tlv(ebrw_writestr, value, data):
	ebrw_writestr.int_u8(value)
	if value <= 63 and value >= 0: ebrw_writestr.int_u8(data)
	if value <= 127 and value >= 64: ebrw_writestr.int_u16(data)
	if value <= 191 and value >= 128: ebrw_writestr.int_u32(data)
	if value <= 224 and value >= 192:
		ebrw_writestr.varint(len(data))
		ebrw_writestr.raw(data)
	if value <= 255 and value >= 225:
		ebrw_writestr.varint(len(data))
		ebrw_writestr.raw(data)

def write_utf8(ebrw_writestr, value, stri):
	write_tlv(ebrw_writestr, value, stri.encode('utf8') + b'\x00')

def encode(eventtable):
	ebrw_writestr = easybinrw.binwrite()
	for event_data in eventtable: write_tlv(ebrw_writestr, event_data[0], event_data[1])
	return ebrw_writestr.getvalue()

# ---------------------- encode

class tlv_reader:
	def __init__(self, ebrw_readstr):
		self.ebrw_readstr = ebrw_readstr
		self.debug_eventtxt = {}

	def debug_load(self):
		if not self.debug_eventtxt:
			with open('data_debug/flp_eventname.txt') as f:
				lines = f.readlines()

			for line in lines:
				idname = line.rstrip().split()
				if len(idname) > 1:
					self.debug_eventtxt[int(idname[0])] = idname[1]

	def printpart_event(self, event_id, data):
		event_name = self.debug_eventtxt[event_id] if event_id in self.debug_eventtxt else '_unknown'

		out = ''
		eeval = ''
		if event_id <= 63 and event_id >= 0: 
			out += 'INT8,  '
			eeval = data
		if event_id <= 127 and event_id >= 64: 
			out += 'INT16, '
			eeval = data
		if event_id <= 191 and event_id >= 128: 
			out += 'INT32, '
			eeval = data
		if event_id <= 224 and event_id >= 192: 
			out += 'TEXT,  '
			eeval = 'HEX '+data.hex()
		if event_id <= 255 and event_id >= 225: 
			out += 'RAW,   '
			eeval = 'HEX '+data.hex()

		out += str(event_id).ljust(5)
		out += event_name.ljust(18)
		out += str(eeval)
		return out

	def view_event(self):
		value, data = read_tlv(self.ebrw_readstr)
		print(self.printpart_event(value, data))

	def debugtxt_event(self):
		value, data = read_tlv(self.ebrw_readstr)
		return self.printpart_event(value, data)

	def read_event(self):
		return read_tlv(self.ebrw_readstr)

class tlv_writer:
	def __init__(self, ebrw_writestr):
		self.ebrw_writestr = ebrw_writestr

	def str8(self, value, data):
		write_utf8(self.ebrw_writestr, value, data)

	def out(self, value, stri):
		write_tlv(self.ebrw_writestr, value, stri)

