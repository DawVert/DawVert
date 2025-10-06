# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def read_header(ebrw_readstr):
	chunktype = ebrw_readstr.int_u32()
	chunksize = ebrw_readstr.int_u32()
	assert ebrw_readstr.int_u32()==0
	return chunktype, chunksize

def write_chunk(ebrw_writestr, chunkid, chunkdata):
	ebrw_writestr.int_u32(chunkid)
	ebrw_writestr.int_u32(len(chunkdata))
	ebrw_writestr.int_u32(0)
	ebrw_writestr.raw(chunkdata)
