# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.file_proj_past._cakewalk_wrk import events
from objects.file_proj_past._cakewalk_wrk import chunks

class gen3_track_evn_part:
	def __init__(self, ebrw_readstr):
		self.headerdata = []
		self.envdata = []
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		time1 = ebrw_readstr.int_u16()
		time2 = ebrw_readstr.int_u16()
		self.headerdata.append( time2+(time1/65535) )
		self.headerdata.append( ebrw_readstr.int_u8() )
		self.headerdata.append( ebrw_readstr.int_u8() )
		self.headerdata.append( ebrw_readstr.int_s16() )
		self.cmdnum, self.channum = ebrw_readstr.bytesplit()

		if self.cmdnum == 0 and self.channum == 4:
			self.envdata.append( ebrw_readstr.int_u8() )
			self.envdata.append( ebrw_readstr.int_u8() )
			self.envdata.append( ebrw_readstr.int_u8() )
			self.envdata.append( ebrw_readstr.raw(4).hex() )
			self.envdata.append( ebrw_readstr.int_u8() )
			d = ebrw_readstr.int_u32()
			self.envdata.append( ebrw_readstr.raw(d) )
			self.envdata.append( ebrw_readstr.int_u32() )
			self.envdata.append( ebrw_readstr.raw(4).hex() )
		elif self.cmdnum == 6: # rpn
			self.envdata.append( ebrw_readstr.int_u32() )
			self.envdata.append( ebrw_readstr.int_u32() )
			self.envdata.append( ebrw_readstr.int_u32() )
		elif self.cmdnum == 7: # nrpn
			self.envdata.append( ebrw_readstr.int_u32() )
			self.envdata.append( ebrw_readstr.int_u32() )
			self.envdata.append( ebrw_readstr.int_u32() )
		elif self.cmdnum == 9: # note
			self.envdata.append( ebrw_readstr.int_u32() )
			self.envdata.append( ebrw_readstr.int_u32() )
			self.envdata.append( ebrw_readstr.int_u32() )
			self.envdata.append( ebrw_readstr.int_u32() )
			self.envdata.append( ebrw_readstr.int_u32() )
			self.envdata.append( ebrw_readstr.int_u32() )
			self.envdata.append( ebrw_readstr.int_u32() )
		elif self.cmdnum == 11: # control
			self.envdata.append( ebrw_readstr.int_u32() )
			self.envdata.append( ebrw_readstr.int_u32() )
		elif self.cmdnum == 14: # wheel
			self.envdata.append( ebrw_readstr.int_u32() )
		elif self.cmdnum == 13: # aftertouch
			self.envdata.append( ebrw_readstr.int_u32() )
		else:
			print('unknown event ', self.channum, channum)
			exit()

		#print('part', self.headerdata, self.envdata)

class chunk_gen3_track_events:
	def __init__(self, ebrw_readstr):
		self.parts = []
		if ebrw_readstr: self.read(ebrw_readstr)

	def read(self, ebrw_readstr):
		self.unkdata = []
		self.tracknum = ebrw_readstr.int_u32()
		self.unkdata.append( ebrw_readstr.int_u32() )
		self.unkdata.append( ebrw_readstr.int_u32() )
		self.unkdata.append( ebrw_readstr.int_u8() )
		self.unkdata.append( ebrw_readstr.int_u8() )
		self.pos = ebrw_readstr.int_u32()
		self.unkdata.append( ebrw_readstr.int_u16() )
		self.unkdata.append( ebrw_readstr.int_u32() )
		self.offset = ebrw_readstr.double()
		self.unkdata.append( ebrw_readstr.int_u32() )
		self.seconds = ebrw_readstr.double()
		self.id = ebrw_readstr.raw(16).hex()
		self.unkdata.append( ebrw_readstr.raw(4).hex() )
		self.name = ebrw_readstr.raw_i8()
		self.unkdata.append( ebrw_readstr.raw(4).hex() )
		self.unkdata.append( ebrw_readstr.int_u32() )
		self.unkdata.append( ebrw_readstr.raw(8).hex() )
		self.unkdata.append( ebrw_readstr.raw(8).hex() )
		self.unkdata.append( ebrw_readstr.raw(16).hex() )

		self.unkdata.append( ebrw_readstr.int_u32() )
		self.unkdata.append( ebrw_readstr.int_s32() )
		self.unkdata.append( ebrw_readstr.int_u32() )
		self.unkdata.append( ebrw_readstr.int_u32() )
		self.unkdata.append( ebrw_readstr.int_u32() )
		self.unkdata.append( ebrw_readstr.int_u32() )

		num_something = ebrw_readstr.int_u32()

		for x in range(num_something):
			self.parts.append(gen3_track_evn_part(ebrw_readstr))

	def viewchunks(ebrw_readstr):

		print( 'tracknum', ebrw_readstr.int_u32() )
		print( '?', ebrw_readstr.int_u32() )
		print( '?', ebrw_readstr.int_u32() )
		print( '?', ebrw_readstr.int_u8() )
		print( '?', ebrw_readstr.int_u8() )
		print( 'pos', ebrw_readstr.int_u32() )
		print( '?', ebrw_readstr.int_u16() )
		print( '?', ebrw_readstr.int_u32() )
		print( 'offset', ebrw_readstr.double() )
		print( '?', ebrw_readstr.int_u32() )
		print( 'seconds', ebrw_readstr.double() )
		print( 'id', ebrw_readstr.raw(16).hex() )
		print( '?', ebrw_readstr.raw(4).hex() )
		print( 'name', ebrw_readstr.raw_i8() )
		print( '?', ebrw_readstr.raw(4).hex() )
		print( '?', ebrw_readstr.int_u32() )
		print( '?', ebrw_readstr.raw(8).hex() )
		print( '?', ebrw_readstr.raw(8).hex() )
		print( '?', ebrw_readstr.raw(16).hex() )

		print( '?', ebrw_readstr.int_u32() )
		print( '?', ebrw_readstr.int_s32() )
		print( '?', ebrw_readstr.int_u32() )
		print( '?', ebrw_readstr.int_u32() )
		print( '?', ebrw_readstr.int_u32() )
		print( '?', ebrw_readstr.int_u32() )

		num_something = ebrw_readstr.int_u32()

		for x in range(num_something):
			T = gen3_track_evn_part(ebrw_readstr)

			print(T.headerdata, T.envdata)