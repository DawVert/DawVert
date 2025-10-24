# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: MIT
# easybinrw is MIT

from external.easybinrw import easybinrw

class riff_chunk:
	def __init__(self):
		self.start = 0
		self.end = 0
		self.size = 0
		self.id = b'    '
		self.is_list = True
		self.data = None
		self.indata = []
		self.is_header = True

	def __getitem__(self, v):
		return self.indata[v]

	def iter_reader(self, reader):
		for x in self.indata:
			reader.seek_real(x.start)
			reader.isolate_range_real(x.start, x.end)
			yield x
			reader.isolate_end()

	def read_file(self, filename, load_data):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(filename)
		self.read(ebrw_readstr, load_data)
		return ebrw_readstr

	def read(self, reader, load_data):
		self.id = reader.raw(4)
		self.size = reader.int_u32()
		self.start = reader.tell_real()
		self.end = self.start+self.size
		if self.id in [b'LIST', b'RIFF']:
			#print('LIST START')
			self.is_list = True
			self.id = reader.raw(4)
			self.size = self.size-4
			reader.isolate_size(self.size)
			while reader.remaining():
				in_ch = riff_chunk()
				in_ch.read(reader, load_data)
				self.indata.append(in_ch)
			reader.isolate_end()
			#print('LIST END')
		else:
			self.is_list = False
			if load_data: 
				self.loaded_bytes = True
				self.data = reader.raw(self.size)
			else: reader.skip(self.size+(self.size%2))
		#print(self.is_list, self.id, self.size, self.start, self.end)

	def add_part(self, idtxt):
		in_ch = riff_chunk()
		in_ch.id = idtxt
		in_ch.is_list = False
		self.indata.append(in_ch)
		return in_ch

	def add_group(self, idtxt):
		in_ch = riff_chunk()
		in_ch.id = idtxt
		in_ch.is_list = True
		self.indata.append(in_ch)
		return in_ch

	def write_chunk(self, ebrw_writestr):

		if not self.is_list:
			ebrw_writestr.raw(self.id)
			outdata = self.data
		else:
			ebrw_writestr.raw(b'LIST' if not self.is_header else b'RIFF')
			inner__ebrw_writestr = easybinrw.binwrite()
			inner__ebrw_writestr.raw(self.id)
			for x in self.indata: x.write_chunk(inner__ebrw_writestr)
			outdata = inner__ebrw_writestr.getvalue()

		ebrw_writestr.int_u32(len(outdata))
		ebrw_writestr.raw(outdata)
		if (len(outdata)%2): ebrw_writestr.raw(b'\0')

	def write_data(self):
		ebrw_writestr = easybinrw.binwrite()
		self.write_chunk(ebrw_writestr)
		return ebrw_writestr.getvalue()

	def write_to_file(self, filename):
		ebrw_writestr = easybinrw.binwrite()
		self.write_chunk(ebrw_writestr)
		ebrw_writestr.to_file(filename)
