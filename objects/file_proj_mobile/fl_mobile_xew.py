
from external.easybinrw import easybinrw
import numpy as np
import struct

class oldflm_note:
	def __init__(self, ebrw_readstr):
		self.pos = ebrw_readstr.int_u32()
		self.dur = ebrw_readstr.int_u16()
		self.key = ebrw_readstr.int_u8()
		self.vol = ebrw_readstr.int_u8()
		self.num_auto = ebrw_readstr.int_u16()
		self.unk7 = ebrw_readstr.int_u8()
		self.unk8 = ebrw_readstr.int_u8()

		self.auto = []

def read_notes(ebrw_readstr):
	numnotes = ebrw_readstr.int_u32()
	keys = []
	for n in range(numnotes):
		key = oldflm_note(ebrw_readstr)
		keys.append(key)

	for n in keys:
		if n.num_auto:
			for _ in range(n.num_auto):
				a_pos = ebrw_readstr.int_u16()
				a_dur = ebrw_readstr.int_u16()
				n.auto.append([a_pos, a_dur])
	return keys

class oldflm_track:
	def __init__(self, ebrw_readstr):
		self.numid = ebrw_readstr.int_u8()
		self.type = ebrw_readstr.int_u8()
		self.unk1 = ebrw_readstr.int_u8()
		if self.type == 1:
			self.unk2 = ebrw_readstr.int_u8()
			self.num_stepinst = ebrw_readstr.int_u8()
			self.drumprop = []

			for n in range(self.num_stepinst):
				st = []
				st.append(  ebrw_readstr.float()  )
				st.append(  ebrw_readstr.float()  )
				st.append(  ebrw_readstr.float()  )
				st.append(  ebrw_readstr.float()  )
				st.append(  ebrw_readstr.int_u8()  )
				st.append(  ebrw_readstr.int_u8()  )
				st.append(  ebrw_readstr.int_u8()  )
				st.append(  ebrw_readstr.int_u8()  )
				self.drumprop.append(st)
			self.unk3 = ebrw_readstr.int_u8()

		self.unkvars = []
		self.unkvars.append(  ebrw_readstr.int_u32()  )
		self.unkvars.append(  ebrw_readstr.float()  )
		self.unkvars.append(  ebrw_readstr.float()  )
		self.unkvars.append(  ebrw_readstr.float()  )
		self.unkvars.append(  ebrw_readstr.int_u8()  )
		self.unkvars.append(  ebrw_readstr.int_u8()  )
		fx_enabled = ebrw_readstr.int_u8()
		self.vol = ebrw_readstr.float()
		self.pan = ebrw_readstr.float()
		self.unkvars.append(  ebrw_readstr.float()  )
		self.unkvars.append(  ebrw_readstr.float()  )
		self.notes = read_notes(ebrw_readstr)

class oldflm_song:
	def __init__(self):
		self.tracks = []

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)
		ebrw_readstr.magic_check(b'\x00\x80\xD4\x44')
		self.unk1 = ebrw_readstr.int_u8()
		self.unk2 = ebrw_readstr.int_u8()
		self.unk3 = ebrw_readstr.int_u8()
		self.unk4 = ebrw_readstr.int_u8()
		self.bpm = ebrw_readstr.int_u8()
		self.unk5 = ebrw_readstr.raw(16).hex()
		num_tracks = ebrw_readstr.int_u8()
		for _ in range(num_tracks):
			track = oldflm_track(ebrw_readstr)
			self.tracks.append(track)
		return True