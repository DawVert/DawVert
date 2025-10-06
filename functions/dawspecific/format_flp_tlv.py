# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import varint
from external.easybinrw import easybinrw

VERBOSE = False

# ---------------------- decode

def read_tlv(tlv_data):
	event_id = tlv_data.int_u8()
	if event_id <= 63 and event_id >= 0: 
		outval = tlv_data.int_u8()
		if VERBOSE: print('INT8, ', f"{event_id:#010b}"[2:],'|',str(event_id).ljust(3), f"{outval:#010b}"[2:], outval)
		return event_id, outval
	if event_id <= 127 and event_id >= 64: 
		outval = tlv_data.int_u16()
		if VERBOSE: print('INT16,', f"{event_id:#010b}"[2:],'|',str(event_id).ljust(3), f"{outval:#028b}"[2:], outval)
		return event_id, outval
	if event_id <= 191 and event_id >= 128: 
		outval = tlv_data.int_u32()
		if VERBOSE: print('INT32,', f"{event_id:#010b}"[2:],'|',str(event_id).ljust(3), f"{outval:#034b}"[2:], outval)
		return event_id, outval
	if event_id <= 224 and event_id >= 192: 
		if VERBOSE: print('TEXT, ', f"{event_id:#010b}"[2:],'|',event_id)
		return event_id, tlv_data.raw(tlv_data.varint())
	if event_id <= 255 and event_id >= 225: 
		if VERBOSE: print('RAW,  ', f"{event_id:#010b}"[2:],'|',event_id)
		return event_id, tlv_data.raw(tlv_data.varint())

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

def encode(eventtable):
	ebrw_writestr = easybinrw.binwrite()
	for event_data in eventtable: write_tlv(ebrw_writestr, event_data[0], event_data[1])
	return ebrw_writestr.getvalue()
