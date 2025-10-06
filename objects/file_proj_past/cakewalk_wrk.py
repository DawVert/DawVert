# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from external.easybinrw import easybinrw
from objects.file_proj_past._cakewalk_wrk import chunks

class cakewalk_wrk_file:
	def __init__(self):
		self.version = 0

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)

		ebrw_readstr.magic_check(b'CAKEWALK\x1a\x00')
		self.version = ebrw_readstr.int_u8()

		self.chunks = []
		while ebrw_readstr.remaining():
			chunk = chunks.cakewalk_wrk_chunk(ebrw_readstr)
			self.chunks.append(chunk)
		return True

	def viewchunks(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)

		ebrw_readstr.magic_check(b'CAKEWALK\x1a\x00')
		self.version = ebrw_readstr.int_u8()

		while ebrw_readstr.remaining():
			self.id = ebrw_readstr.int_u8()
			if self.id != 255: 
				csize = ebrw_readstr.int_u32()
				name = '?? Unknown ?? '
				if self.id in chunks.chunkids: name = chunks.chunkids[self.id]

				name = ('# ' if self.id in chunks.chunkobjects else '  ') + name
				f = False
				if self.id in chunks.chunkobjects:
					if 'viewchunks' in dir(chunks.chunkobjects[self.id]):
						f = True
						with ebrw_readstr.isolate_size(csize, True) as bye_stream:
							chunks.chunkobjects[self.id].viewchunks(bye_stream)
				if not f:
					data = ebrw_readstr.raw(csize)
					print(str(self.id).rjust(4), '|', name.ljust(32), data.hex())





	#def write_to_file(self, output_file):
	#	byw_stream = bytewriter.bytewriter()
#
	#	byw_stream.raw(b'CAKEWALK\x1a\x00')
	#	byw_stream.uint8(self.version)
#
	#	f = open(output_file, 'wb')
	#	f.write(byw_stream.getvalue())
