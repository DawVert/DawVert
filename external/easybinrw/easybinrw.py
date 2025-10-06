# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: MIT
# easybinrw is MIT

from struct import *
import mmap
import os
import numpy as np
import sys
import io
import varint

def val_to_flags(numbits, value):
	return [b for b in range(numbits) if value&(1<<b)]

def flags_to_val(flagslist):
	return sum([(1<<(x)) for x in flagslist])

class binrw_state:
	__slots__ = ['start', 'end', 'endian', 'oldpos']
	def __init__(self):
		self.start = 0
		self.end = 0
		self.endian = 0
		self.oldpos = 0

class binread:
	unp_s8 = Struct('b').unpack
	unp_u8 = Struct('B').unpack

	unp_s16_b = Struct('>h').unpack
	unp_u16_b = Struct('>H').unpack
	unp_s32_b = Struct('>i').unpack
	unp_u32_b = Struct('>L').unpack
	unp_s64_b = Struct('>q').unpack
	unp_u64_b = Struct('>Q').unpack
	unp_float_b = Struct('>f').unpack
	unp_double_b = Struct('>d').unpack

	unp_s16_l = Struct('<h').unpack
	unp_u16_l = Struct('<H').unpack
	unp_s32_l = Struct('<i').unpack
	unp_u32_l = Struct('<L').unpack
	unp_s64_l = Struct('<q').unpack
	unp_u64_l = Struct('<Q').unpack
	unp_float_l = Struct('<f').unpack
	unp_double_l = Struct('<d').unpack

	dt_s8 = np.dtype('b')
	dt_u8 = np.dtype('B')

	dt_s16_n = np.dtype('h')
	dt_u16_n = np.dtype('H')
	dt_s32_n = np.dtype('i')
	dt_u32_n = np.dtype('I')
	dt_s64_n = np.dtype('q')
	dt_u64_n = np.dtype('Q')
	dt_float_n = np.dtype('f')
	dt_double_n = np.dtype('d')

	dt_s16_b = np.dtype('>h')
	dt_u16_b = np.dtype('>H')
	dt_s32_b = np.dtype('>i')
	dt_u32_b = np.dtype('>I')
	dt_s64_b = np.dtype('>q')
	dt_u64_b = np.dtype('>Q')
	dt_float_b = np.dtype('>f')
	dt_double_b = np.dtype('>d')

	dt_s16_l = np.dtype('<h')
	dt_u16_l = np.dtype('<H')
	dt_s32_l = np.dtype('<i')
	dt_u32_l = np.dtype('<I')
	dt_s64_l = np.dtype('<q')
	dt_u64_l = np.dtype('<Q')
	dt_float_l = np.dtype('<f')
	dt_double_l = np.dtype('<d')

	def __init__(self):
		self.str = None

		self.file = None
		self.filenum = None
		self.filename = None
		self.is_file = False

		self.state = binrw_state()
		self.state_store = []

	def load_file(self, filename):
		try:
			self.state.__init__()

			self.file = open(filename, 'rb')
			self.filenum = self.file.fileno()
			self.filename = filename
			self.is_file = True

			self.str = mmap.mmap(self.filenum, 0, access=mmap.ACCESS_READ)
			self.state.end = os.path.getsize(filename)
			return True
		except:
			self.__init__()
			return False

	def load_data(self, data):
		self.str = io.BytesIO(data)
		self.state.end = len(data)

	def fileno(self): return self.filenum

	def magic_check(self, bind): assert bind==self.str.read(len(bind))

	def read(self, num): return self.str.read(num)
	def tell(self): return self.str.tell()-self.state.start
	def seek(self, num): return self.str.seek(num+self.state.start)

	def tell_real(self): return self.str.tell()
	def seek_real(self, num): return self.str.seek(num)

	def skip(self, num): return self.str.seek(self.str.tell()+num)

	def remaining(self): return max(0, self.state.end-self.str.tell())
	def rest(self): return self.str.read(self.remaining())

	def isolate_range_real(self, start, end):
		oldpos = self.state.oldpos = self.str.tell()
		endian = self.state.endian
		self.state_store.append(self.state)
		self.state = binrw_state()
		self.state.start = start
		self.state.end = end
		self.state.endian = endian

	def isolate_size(self, size):
		oldpos = self.state.oldpos = self.str.tell()
		endian = self.state.endian
		self.state_store.append(self.state)
		self.state = binrw_state()
		self.state.start = oldpos
		self.state.end = oldpos+size
		self.state.endian = endian

	def isolate_end(self):
		self.str.seek(self.state.end)
		self.state = self.state_store.pop()

	def isolate_end_noseek(self):
		self.state = self.state_store.pop()

	def int_ud(self, bn, endian): 
		if bn == 1: return self.unp_u8(self.str.read(1))[0]
		if bn == 2: return (self.unp_u16_b if endian else self.unp_u16_l)(self.str.read(2))[0] 
		if bn == 4: return (self.unp_u32_b if endian else self.unp_u32_l)(self.str.read(4))[0] 
		if bn == 8: return (self.unp_u64_b if endian else self.unp_u64_l)(self.str.read(8))[0] 

	def int_u4_2(self): 
		val = self.unp_u8(self.str.read(1))[0]
		return val>>4, val&0xf

	def bool_8(self): return bool(self.int_u8())
	def bool_16(self): return bool(self.int_u16())
	def bool_32(self): return bool(self.int_u32())
	def bool_64(self): return bool(self.int_u64())

	def int_s8(self): return self.unp_s8(self.str.read(1))[0]
	def int_u8(self): return self.unp_u8(self.str.read(1))[0]

	def int_s16(self): return (self.unp_s16_b if self.state.endian else self.unp_s16_l)(self.str.read(2))[0] 
	def int_u16(self): return (self.unp_u16_b if self.state.endian else self.unp_u16_l)(self.str.read(2))[0] 
	def int_s32(self): return (self.unp_s32_b if self.state.endian else self.unp_s32_l)(self.str.read(4))[0] 
	def int_u32(self): return (self.unp_u32_b if self.state.endian else self.unp_u32_l)(self.str.read(4))[0] 
	def int_s64(self): return (self.unp_s64_b if self.state.endian else self.unp_s64_l)(self.str.read(8))[0] 
	def int_u64(self): return (self.unp_u64_b if self.state.endian else self.unp_u64_l)(self.str.read(8))[0] 
	def float(self): return (self.unp_float_b if self.state.endian else self.unp_float_l)(self.str.read(4))[0] 
	def double(self): return (self.unp_double_b if self.state.endian else self.unp_double_l)(self.str.read(8))[0] 
	def varint(self): return varint.decode_stream(self.str)

	def int_s16_b(self): return self.unp_s16_b(self.str.read(2))[0]
	def int_u16_b(self): return self.unp_u16_b(self.str.read(2))[0]
	def int_s32_b(self): return self.unp_s32_b(self.str.read(4))[0]
	def int_u32_b(self): return self.unp_u32_b(self.str.read(4))[0]
	def int_s64_b(self): return self.unp_s64_b(self.str.read(8))[0]
	def int_u64_b(self): return self.unp_u64_b(self.str.read(8))[0]
	def float_b(self): return self.unp_float_b(self.str.read(4))[0]
	def double_b(self): return self.unp_double_b(self.str.read(8))[0]

	def int_s16_l(self): return self.unp_s16_l(self.str.read(2))[0]
	def int_u16_l(self): return self.unp_u16_l(self.str.read(2))[0]
	def int_s32_l(self): return self.unp_s32_l(self.str.read(4))[0]
	def int_u32_l(self): return self.unp_u32_l(self.str.read(4))[0]
	def int_s64_l(self): return self.unp_s64_l(self.str.read(8))[0]
	def int_u64_l(self): return self.unp_u64_l(self.str.read(8))[0]
	def float_l(self): return self.unp_float_l(self.str.read(4))[0]
	def double_l(self): return self.unp_double_l(self.str.read(8))[0]

	def int_u24(self): return self.int_u24_b() if self.state.endian else self.int_u24_l()
	def int_u24_b(self): return self.unp_u32_b(b'\x00'+self.str.read(3))[0]
	def int_u24_l(self): return self.unp_s32_l(self.str.read(3)+b'\x00')[0]

	def raw(self, num): return self.str.read(num)
	def string(self, num, **k): return self.str.read(num).split(b'\x00')[0].decode(**k)
	def string16(self, num, **k): return self.str.read(num*2).decode(encoding='utf16').rstrip('\x00')
	def string_t(self, **k): 
		out = b''
		while self.remaining():
			v = self.str.read(1)
			if v==b'\x00': break
			else: out += (v)
		return out.decode(**k)

	def flags_i8(self): return val_to_flags(8, self.int_u8())

	def flags_i16(self): return val_to_flags(16, self.int_u16())
	def flags_i16_b(self): return val_to_flags(16, self.int_u16_b())
	def flags_i16_l(self): return val_to_flags(16, self.int_u16_l())

	def flags_i24(self): return val_to_flags(24, self.int_u24())
	def flags_i24_b(self): return val_to_flags(24, self.int_u24_b())
	def flags_i24_l(self): return val_to_flags(24, self.int_u24_l())

	def flags_i32(self): return val_to_flags(32, self.int_u32())
	def flags_i32_b(self): return val_to_flags(32, self.int_u32_b())
	def flags_i32_l(self): return val_to_flags(32, self.int_u32_l())

	def flags_i64(self): return val_to_flags(64, self.int_u64())
	def flags_i64_b(self): return val_to_flags(64, self.int_u64_b())
	def flags_i64_l(self): return val_to_flags(64, self.int_u64_l())

	def string_i8(self, **k): return self.str.read(self.int_u8()).split(b'\x00')[0].decode(**k)
	def string_i16(self, **k): return self.str.read(self.int_u16()).split(b'\x00')[0].decode(**k)
	def string_i32(self, **k): 
		o = self.str.read(self.int_u32())
		print(o)
		return o.decode(**k).rstrip('\x00')
	def string_i64(self, **k): return self.str.read(self.int_u64()).split(b'\x00')[0].decode(**k)
	def string_i16_b(self, **k): return self.str.read(self.int_u16_b()).split(b'\x00')[0].decode(**k)
	def string_i32_b(self, **k): return self.str.read(self.int_u32_b()).split(b'\x00')[0].decode(**k)
	def string_i64_b(self, **k): return self.str.read(self.int_u64_b()).split(b'\x00')[0].decode(**k)
	def string_i16_l(self, **k): return self.str.read(self.int_u16_l()).split(b'\x00')[0].decode(**k)
	def string_i32_l(self, **k): return self.str.read(self.int_u32_l()).split(b'\x00')[0].decode(**k)
	def string_i64_l(self, **k): return self.str.read(self.int_u64_l()).split(b'\x00')[0].decode(**k)
	def string_varint(self, **k): return self.str.read(self.varint()).split(b'\x00')[0].decode(**k)

	def raw_i8(self): return self.str.read(self.int_u8())
	def raw_i16(self): return self.str.read(self.int_u16())
	def raw_i32(self): return self.str.read(self.int_u32())
	def raw_i64(self): return self.str.read(self.int_u64())
	def raw_i16_b(self): return self.str.read(self.int_u16_b())
	def raw_i32_b(self): return self.str.read(self.int_u32_b())
	def raw_i64_b(self): return self.str.read(self.int_u64_b())
	def raw_i16_l(self): return self.str.read(self.int_u16_l())
	def raw_i32_l(self): return self.str.read(self.int_u32_l())
	def raw_i64_l(self): return self.str.read(self.int_u64_l())

	def internal_readarr(self, num, numbytes, dtype): 
		byteds = self.read(num*numbytes)
		return np.frombuffer(byteds, dtype)

	def list_int_s8(self, num): return self.internal_readarr(num, 1, self.dt_s8)
	def list_int_u8(self, num): return self.internal_readarr(num, 1, self.dt_u8)

	def list_int_s16(self, num): return self.internal_readarr(num, 2, self.dt_s16_b if self.state.endian else self.dt_s16_l)
	def list_int_u16(self, num): return self.internal_readarr(num, 2, self.dt_u16_b if self.state.endian else self.dt_u16_l)
	def list_int_s32(self, num): return self.internal_readarr(num, 4, self.dt_s32_b if self.state.endian else self.dt_s32_l)
	def list_int_u32(self, num): return self.internal_readarr(num, 4, self.dt_u32_b if self.state.endian else self.dt_u32_l)
	def list_int_s64(self, num): return self.internal_readarr(num, 8, self.dt_s64_b if self.state.endian else self.dt_s64_l)
	def list_int_u64(self, num): return self.internal_readarr(num, 8, self.dt_u64_b if self.state.endian else self.dt_u64_l)
	def list_float(self, num): return self.internal_readarr(num, 4, self.dt_float_b if self.state.endian else self.dt_float_l)
	def list_double(self, num): return self.internal_readarr(num, 8, self.dt_double_b if self.state.endian else self.dt_double_l)

	def list_int_s16_b(self, num): return self.internal_readarr(num, 2, self.dt_s16_b)
	def list_int_u16_b(self, num): return self.internal_readarr(num, 2, self.dt_u16_b)
	def list_int_s32_b(self, num): return self.internal_readarr(num, 4, self.dt_s32_b)
	def list_int_u32_b(self, num): return self.internal_readarr(num, 4, self.dt_u32_b)
	def list_int_s64_b(self, num): return self.internal_readarr(num, 8, self.dt_s64_b)
	def list_int_u64_b(self, num): return self.internal_readarr(num, 8, self.dt_u64_b)
	def list_float_b(self, num): return self.internal_readarr(num, 4, self.dt_float_b)
	def list_double_b(self, num): return self.internal_readarr(num, 8, self.dt_double_b)

	def list_int_s16_l(self, num): return self.internal_readarr(num, 2, self.dt_s16_l)
	def list_int_u16_l(self, num): return self.internal_readarr(num, 2, self.dt_u16_l)
	def list_int_s32_l(self, num): return self.internal_readarr(num, 4, self.dt_s32_l)
	def list_int_u32_l(self, num): return self.internal_readarr(num, 4, self.dt_u32_l)
	def list_int_s64_l(self, num): return self.internal_readarr(num, 8, self.dt_s64_l)
	def list_int_u64_l(self, num): return self.internal_readarr(num, 8, self.dt_u64_l)
	def list_float_l(self, num): return self.internal_readarr(num, 4, self.dt_float_l)
	def list_double_l(self, num): return self.internal_readarr(num, 8, self.dt_double_l)

	def list_int_u4(self, num): 
		o = []
		for x in range(num): o += self.int_u4_2()
		return o

	def list_int_u24(self, num):
		return self.str.read(num*3)

	def detectheader(self, offset, data):
		self.seek(offset)
		return self.str.read(len(data))==data

class binwrite:
	pak_s8 = Struct('b').pack
	pak_u8 = Struct('B').pack

	pak_s16_b = Struct('>h').pack
	pak_u16_b = Struct('>H').pack
	pak_s32_b = Struct('>i').pack
	pak_u32_b = Struct('>L').pack
	pak_s64_b = Struct('>q').pack
	pak_u64_b = Struct('>Q').pack
	pak_float_b = Struct('>f').pack
	pak_double_b = Struct('>d').pack

	pak_s16_l = Struct('<h').pack
	pak_u16_l = Struct('<H').pack
	pak_s32_l = Struct('<i').pack
	pak_u32_l = Struct('<L').pack
	pak_s64_l = Struct('<q').pack
	pak_u64_l = Struct('<Q').pack
	pak_float_l = Struct('<f').pack
	pak_double_l = Struct('<d').pack

	dt_s8 = np.dtype('b')
	dt_u8 = np.dtype('B')

	dt_s16_n = np.dtype('h')
	dt_u16_n = np.dtype('H')
	dt_s32_n = np.dtype('i')
	dt_u32_n = np.dtype('I')
	dt_s64_n = np.dtype('q')
	dt_u64_n = np.dtype('Q')
	dt_float_n = np.dtype('f')
	dt_double_n = np.dtype('d')

	dt_s16_b = np.dtype('>h')
	dt_u16_b = np.dtype('>H')
	dt_s32_b = np.dtype('>i')
	dt_u32_b = np.dtype('>I')
	dt_s64_b = np.dtype('>q')
	dt_u64_b = np.dtype('>Q')
	dt_float_b = np.dtype('>f')
	dt_double_b = np.dtype('>d')

	dt_s16_l = np.dtype('<h')
	dt_u16_l = np.dtype('<H')
	dt_s32_l = np.dtype('<i')
	dt_u32_l = np.dtype('<I')
	dt_s64_l = np.dtype('<q')
	dt_u64_l = np.dtype('<Q')
	dt_float_l = np.dtype('<f')
	dt_double_l = np.dtype('<d')

	def __init__(self):
		self.str = io.BytesIO()
		self.file = None
		self.state = binrw_state()
		self.state_store = []

	def tell(self): return self.str.tell()

	def internal_writearr(self, v, num, dtype): 
		if 0>num: 
			iv = np.array(v, dtype)
			self.str.write(iv.tobytes())
		elif num>0: 
			maxv = min(num, len(v))
			iv = np.zeros(num, dtype)
			iv[0:maxv] = v[0:maxv]
			self.str.write(iv.tobytes())

	def getvalue(self): return self.str.getvalue()

	def to_file(self, filename):
		f = open(filename, 'wb')
		f.write(self.getvalue())
		f.flush()
		f.close()

	def int_s8(self, v): self.str.write(self.pak_s8(v))
	def int_u8(self, v): self.str.write(self.pak_u8(v))

	def int_s16(self, v): self.str.write((self.pak_s16_b if self.state.endian else self.pak_s16_l)(v))
	def int_u16(self, v): self.str.write((self.pak_u16_b if self.state.endian else self.pak_u16_l)(v))
	def int_s32(self, v): self.str.write((self.pak_s32_b if self.state.endian else self.pak_s32_l)(v))
	def int_u32(self, v): self.str.write((self.pak_u32_b if self.state.endian else self.pak_u32_l)(v))
	def int_s64(self, v): self.str.write((self.pak_s64_b if self.state.endian else self.pak_s64_l)(v))
	def int_u64(self, v): self.str.write((self.pak_u64_b if self.state.endian else self.pak_u64_l)(v))
	def float(self, v): self.str.write((self.pak_float_b if self.state.endian else self.pak_float_l)(v))
	def double(self, v): self.str.write((self.pak_double_b if self.state.endian else self.pak_double_l)(v))
	def varint(self, v): self.str.write(varint.encode(v))

	def int_s16_b(self, v): self.str.write(self.pak_s16_b(v))
	def int_u16_b(self, v): self.str.write(self.pak_u16_b(v))
	def int_s32_b(self, v): self.str.write(self.pak_s32_b(v))
	def int_u32_b(self, v): self.str.write(self.pak_u32_b(v))
	def int_s64_b(self, v): self.str.write(self.pak_s64_b(v))
	def int_u64_b(self, v): self.str.write(self.pak_u64_b(v))
	def float_b(self, v): self.str.write(self.pak_float_b(v))
	def double_b(self, v): self.str.write(self.pak_double_b(v))

	def int_s16_l(self, v): self.str.write(self.pak_s16_l(v))
	def int_u16_l(self, v): self.str.write(self.pak_u16_l(v))
	def int_s32_l(self, v): self.str.write(self.pak_s32_l(v))
	def int_u32_l(self, v): self.str.write(self.pak_u32_l(v))
	def int_s64_l(self, v): self.str.write(self.pak_s64_l(v))
	def int_u64_l(self, v): self.str.write(self.pak_u64_l(v))
	def float_l(self, v): self.str.write(self.pak_float_l(v))
	def double_l(self, v): self.str.write(self.pak_double_l(v))

	def raw(self, v): self.str.write(v)
	def string(self, v, num):
		outtxt = np.zeros(1, (np.void, num))
		outtxt[:] = str(v).encode()
		self.str.write(outtxt[0])
	def string_nolimit(self, v): self.str.write(str(v).encode())
	def string_t(self, v): 
		self.str.write(str(v).encode())
		self.str.write(b'\0')

	def flags_i8(self, v): return self.int_u8(flags_to_val(v))
	def flags_i16(self, v): return self.int_u16(flags_to_val(v))
	def flags_i32(self, v): return self.int_u32(flags_to_val(v))
	def flags_i64(self, v): return self.int_u64(flags_to_val(v))
	def flags_i16_b(self, v): return self.int_u16_b(flags_to_val(v))
	def flags_i32_b(self, v): return self.int_u32_b(flags_to_val(v))
	def flags_i64_b(self, v): return self.int_u64_b(flags_to_val(v))
	def flags_i16_l(self, v): return self.int_u16_l(flags_to_val(v))
	def flags_i32_l(self, v): return self.int_u32_l(flags_to_val(v))
	def flags_i64_l(self, v): return self.int_u64_l(flags_to_val(v))

	def internal_string_p(self, v, funct): 
		v = str(v).encode()
		funct(len(v))
		self.str.write(v)

	def string_i8(self, v): self.internal_string_p(v, self.int_u8)
	def string_i16(self, v): self.internal_string_p(v, self.int_u16)
	def string_i32(self, v): self.internal_string_p(v, self.int_u32)
	def string_i64(self, v): self.internal_string_p(v, self.int_u64)
	def string_i16_b(self, v): self.internal_string_p(v, self.int_u16_b)
	def string_i32_b(self, v): self.internal_string_p(v, self.int_u32_b)
	def string_i64_b(self, v): self.internal_string_p(v, self.int_u64_b)
	def string_i16_l(self, v): self.internal_string_p(v, self.int_u16_l)
	def string_i32_l(self, v): self.internal_string_p(v, self.int_u32_l)
	def string_i64_l(self, v): self.internal_string_p(v, self.int_u64_l)
	def string_varint(self, v): self.internal_string_p(v, self.varint)

	def internal_raw_p(self, v, funct): 
		funct(len(v))
		self.str.write(v)

	def raw_i8(self, v): self.internal_raw_p(v, self.int_u8)
	def raw_i16(self, v): self.internal_raw_p(v, self.int_u16)
	def raw_i32(self, v): self.internal_raw_p(v, self.int_u32)
	def raw_i64(self, v): self.internal_raw_p(v, self.int_u64)
	def raw_i16_b(self, v): self.internal_raw_p(v, self.int_u16_b)
	def raw_i32_b(self, v): self.internal_raw_p(v, self.int_u32_b)
	def raw_i64_b(self, v): self.internal_raw_p(v, self.int_u64_b)
	def raw_i16_l(self, v): self.internal_raw_p(v, self.int_u16_l)
	def raw_i32_l(self, v): self.internal_raw_p(v, self.int_u32_l)
	def raw_i64_l(self, v): self.internal_raw_p(v, self.int_u64_l)

	def list_int_s8(self, v, num): self.internal_writearr(v, num, self.dt_s8)
	def list_int_u8(self, v, num): self.internal_writearr(v, num, self.dt_u8)

	def list_int_s16(self, v, num): self.internal_writearr(v, num, self.dt_s16_b if self.state.endian else self.dt_s16_l)
	def list_int_u16(self, v, num): self.internal_writearr(v, num, self.dt_u16_b if self.state.endian else self.dt_u16_l)
	def list_int_s32(self, v, num): self.internal_writearr(v, num, self.dt_s32_b if self.state.endian else self.dt_s32_l)
	def list_int_u32(self, v, num): self.internal_writearr(v, num, self.dt_u32_b if self.state.endian else self.dt_u32_l)
	def list_int_s64(self, v, num): self.internal_writearr(v, num, self.dt_s64_b if self.state.endian else self.dt_s64_l)
	def list_int_u64(self, v, num): self.internal_writearr(v, num, self.dt_u64_b if self.state.endian else self.dt_u64_l)
	def list_float(self, v, num): self.internal_writearr(v, num, self.dt_float_b if self.state.endian else self.dt_float_l)
	def list_double(self, v, num): self.internal_writearr(v, num, self.dt_double_b if self.state.endian else self.dt_double_l)

	def list_int_s16_b(self, v, num): self.internal_writearr(v, num, self.dt_s16_b)
	def list_int_u16_b(self, v, num): self.internal_writearr(v, num, self.dt_u16_b)
	def list_int_s32_b(self, v, num): self.internal_writearr(v, num, self.dt_s32_b)
	def list_int_u32_b(self, v, num): self.internal_writearr(v, num, self.dt_u32_b)
	def list_int_s64_b(self, v, num): self.internal_writearr(v, num, self.dt_s64_b)
	def list_int_u64_b(self, v, num): self.internal_writearr(v, num, self.dt_u64_b)
	def list_float_b(self, v, num): self.internal_writearr(v, num, self.dt_float_b)
	def list_double_b(self, v, num): self.internal_writearr(v, num, self.dt_double_b)

	def list_int_s16_l(self, v, num): self.internal_writearr(v, num, self.dt_s16_l)
	def list_int_u16_l(self, v, num): self.internal_writearr(v, num, self.dt_u16_l)
	def list_int_s32_l(self, v, num): self.internal_writearr(v, num, self.dt_s32_l)
	def list_int_u32_l(self, v, num): self.internal_writearr(v, num, self.dt_u32_l)
	def list_int_s64_l(self, v, num): self.internal_writearr(v, num, self.dt_s64_l)
	def list_int_u64_l(self, v, num): self.internal_writearr(v, num, self.dt_u64_l)
	def list_float_l(self, v, num): self.internal_writearr(v, num, self.dt_float_l)
	def list_double_l(self, v, num): self.internal_writearr(v, num, self.dt_double_l)

