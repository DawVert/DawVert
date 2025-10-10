# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import shlex

from objects.exceptions import ProjectFileParserException

import logging
logger_projparse = logging.getLogger('projparse')

# UNFINISHED
DEBUG_IN_OUT = False

# ============================================= instrument ============================================= 

class famitracker_dpcm:
	def __init__(self):
		self.name = ''
		self.data = b''

class famitracker_dpcmkey:
	def __init__(self):
		self.inst = -1
		self.octave = -1
		self.note = -1
		self.id = -1
		self.pitch = -1
		self.loop = -1

	def read(self, i_list):
		keydpcm = [int(x) for x in i_list]
		self.inst = keydpcm[0]
		self.octave = keydpcm[1]
		self.note = keydpcm[2]
		self.id = keydpcm[3]
		self.pitch = keydpcm[4]
		self.loop = keydpcm[5]

class famitracker_fds_macro:
	def __init__(self):
		self.inst = 0
		self.type = -1
		self.loop = -1
		self.release = -1
		self.setting = -1
		self.data = []

	def read(self, i_txt):
		macrosplit = [shlex.split(s) for s in i_txt.split(':')]
		if len(macrosplit)>1:
			m_target, m_data = macrosplit
			m_target = [int(x) for x in m_target]
			m_data = [int(x) for x in m_data]
			self.inst = m_target[0]
			self.type = m_target[1]
			self.id = m_target[2]
			self.loop = m_target[3]
			self.release = m_target[4]
			self.data = m_data

class famitracker_macro:
	def __init__(self, i_chip):
		self.chip = i_chip
		self.type = -1
		self.id = -1
		self.loop = -1
		self.release = -1
		self.setting = -1
		self.data = []

	def read(self, i_txt):
		macrosplit = [shlex.split(s) for s in i_txt.split(':')]
		if len(macrosplit)>1:
			m_target, m_data = macrosplit
			m_target = [int(x) for x in m_target]
			m_data = [int(x) for x in m_data]
			self.type = m_target[0]
			self.id = m_target[1]
			self.loop = m_target[2]
			self.release = m_target[3]
			self.setting = m_target[4]
			self.data = m_data

	def make(self):
		o = 'MACRO    '
		o += str(self.type).rjust(4)
		o += str(self.id).rjust(4)
		o += str(self.loop).rjust(4)
		o += str(self.release).rjust(4)
		o += str(self.setting).rjust(4)
		o += ' : '
		o += ' '.join([str(x) for x in self.data])
		return o

class famitracker_inst:
	def __init__(self, i_chip):
		self.name = ''
		self.chip = i_chip
		self.id = -1
		self.macro_vol = -1
		self.macro_arp = -1
		self.macro_pitch = -1
		self.macro_hipitch = -1
		self.macro_duty = -1
		self.fds_wave = []
		self.fds_mod = None
		self.fds_mod_enable = None
		self.fds_mod_speed = None
		self.fds_mod_depth = None
		self.fds_mod_delay = None
		self.fds_macros = []
		self.n163_size = 0
		self.n163_pos = 0
		self.n163_count = 0
		self.n163_waves = {}
		self.vrc7_patch = 0
		self.vrc7_regs = [0,0,0,0,0,0,0,0]
		self.dpcm_keys = {}

	def read(self, i_list):
		if self.chip in ['2A03','VRC6','S5B']:
			self.id = int(i_list[0])
			self.macro_vol = int(i_list[1])
			self.macro_arp = int(i_list[2])
			self.macro_pitch = int(i_list[3])
			self.macro_hipitch = int(i_list[4])
			self.macro_duty = int(i_list[5])
			self.name = i_list[6]
		if self.chip in ['FDS']:
			self.id = int(i_list[0])
			self.fds_mod_enable = int(i_list[1])
			self.fds_mod_speed = int(i_list[2])
			self.fds_mod_depth = int(i_list[3])
			self.fds_mod_delay = int(i_list[4])
			self.name = i_list[5]
		if self.chip in ['N163']:
			self.id = int(i_list[0])
			self.macro_vol = int(i_list[1])
			self.macro_arp = int(i_list[2])
			self.macro_pitch = int(i_list[3])
			self.macro_hipitch = int(i_list[4])
			self.macro_duty = int(i_list[5])
			self.n163_size = int(i_list[6])
			self.n163_pos = int(i_list[7])
			self.n163_count = int(i_list[8])
			self.name = i_list[9]
		if self.chip in ['VRC7']:
			self.id = int(i_list[0])
			self.vrc7_patch = int(i_list[1])
			self.vrc7_regs = [int(x, 16) for x in i_list[2:10]]
			self.name = i_list[10]

# ============================================= pattern ============================================= 

keytable_vals = [0,2,4,5,7,9,11]
keytable = ['C','D','E','F','G','A','B']

def parse_note(cellkey):
	cellkey_note = cellkey[0]
	cellkey_sharp = cellkey[1]
	cellkey_oct = cellkey[2]
	if cellkey == '---': return '---'
	elif cellkey == '===': return '==='
	elif cellkey != '...':
		out_note = 0
		if cellkey_oct != '#':
			out_note += keytable_vals[keytable.index(cellkey_note)]
			out_note += (int(cellkey_oct)-3)*12
			if cellkey_sharp == '#': out_note += 1
			return out_note
		else:
			out_note = int(cellkey_note, 16)
			return out_note

class famitracker_pattern:
	def __init__(self):
		self.patdata = {}
	def add_data(self, rownum, channum, rowdata):
		note, inst, vol = rowdata[0:3]
		fx = rowdata[3:]
		if note != '...' or inst != '..' or vol != '.' or fx.count('...') != len(fx):
			outdata = [None, None, None, []]
			outdata[0] = parse_note(note)
			outdata[1] = int(inst, 16) if inst!='..' else None
			outdata[2] = int(vol[0], 16) if vol!='.' else None
			for x in fx:
				if x != '...':
					outdata[3].append([x[0], int(x[1:], 16)])
			if channum not in self.patdata: self.patdata[channum] = {}
			if rownum not in self.patdata[channum]: self.patdata[channum][rownum] = {}
			self.patdata[channum][rownum] = outdata

# ============================================= song ============================================= 

class famitracker_song:
	def __init__(self):
		self.name = ''
		self.patlen = 128
		self.speed = 1
		self.tempo = 120
		self.orders = {}
		self.patterns = {}
		self.columns = []

class famitracker_project:
	def __init__(self):
		self.title = None
		self.author = None
		self.copyright = None
		self.comment = []
		self.machine = 0
		self.framerate = 0
		self.expansion = 0
		self.vibrato = 0
		self.split = 0
		self.n163channels = 1
		self.dpcm = {}
		self.macros = []
		self.macros_vrc6 = []
		self.macros_n163 = []
		self.macros_s5b = []
		self.inst = {}
		self.song = []

	def load_from_file(self, input_file):
		bytestream = open(input_file, 'r')
		try:
			for line in bytestream.readlines():
				linespl = line.strip().split(' ', 1)

				if len(linespl) > 1:
					if linespl[0:3] != 'ROW':
						linedata = shlex.split(linespl[1])
					linetype = linespl[0]

					if linetype == 'TITLE': self.title = linedata[0]
					elif linetype == 'AUTHOR': self.author = linedata[0]
					elif linetype == 'COPYRIGHT': self.copyright = linedata[0]
					elif linetype == 'COMMENT': self.comment.append(linedata[0])
					elif linetype == 'MACHINE': self.machine = int(linedata[0])
					elif linetype == 'FRAMERATE': self.framerate = int(linedata[0])
					elif linetype == 'EXPANSION': self.expansion = int(linedata[0])
					elif linetype == 'VIBRATO': self.vibrato = int(linedata[0])
					elif linetype == 'SPLIT': self.split = int(linedata[0])
					elif linetype == 'N163CHANNELS': self.n163channels = int(linedata[0])


					elif linetype == 'MACRO': 
						ft_macro = famitracker_macro('2A03')
						ft_macro.read(linespl[1])
						self.macros.append(ft_macro)
					elif linetype == 'MACROVRC6': 
						ft_macro = famitracker_macro('2A03')
						ft_macro.read(linespl[1])
						self.macros_vrc6.append(ft_macro)
					elif linetype == 'MACRON163': 
						ft_macro = famitracker_macro('N163')
						ft_macro.read(linespl[1])
						self.macros_n163.append(ft_macro)
					elif linetype == 'MACROS5B': 
						ft_macro = famitracker_macro('S5B')
						ft_macro.read(linespl[1])
						self.macros_s5b.append(ft_macro)


					elif linetype == 'DPCMDEF':
						dpcm_id = int(linedata[0])
						self.current_dpcm = famitracker_dpcm()
						self.current_dpcm.name = linedata[2]
						self.dpcm[dpcm_id] = self.current_dpcm

					elif linetype == 'DPCM':
						self.current_dpcm.data += bytes.fromhex(linespl[1].split(':')[1])



					elif linetype == 'KEYDPCM':
						dpcmkey = famitracker_dpcmkey()
						dpcmkey.read(linedata)
						self.inst[dpcmkey.inst].dpcm_keys[dpcmkey.id] = dpcmkey
					elif linetype == 'N163WAVE':
						fds_idwav = linespl[1].split(': ')
						n163_id, n163_wavnum = fds_idwav[0].split()
						n163_id = int(n163_id)
						n163_wavnum = int(n163_wavnum)
						self.inst[n163_id].n163_waves[n163_wavnum] = [int(x) for x in fds_idwav[1].split()]
					elif linetype == 'FDSWAVE':
						fds_id, fds_wave = linespl[1].split(': ')
						fds_id = int(fds_id)
						self.inst[fds_id].fds_wave = [int(x) for x in fds_wave.split()]
					elif linetype == 'FDSMOD':
						fds_id, fds_wave = linespl[1].split(': ')
						fds_id = int(fds_id)
						self.inst[fds_id].fds_mod = [int(x) for x in fds_wave.split()]
					elif linetype == 'FDSMACRO':
						macro_data = famitracker_fds_macro()
						macro_data.read(linespl[1])
						self.inst[macro_data.inst].fds_macros.append(macro_data)


					elif linetype == 'INST2A03':
						ft_inst = famitracker_inst('2A03')
						ft_inst.read(linedata)
						self.inst[ft_inst.id] = ft_inst
					elif linetype == 'INSTVRC6':
						ft_inst = famitracker_inst('VRC6')
						ft_inst.read(linedata)
						self.inst[ft_inst.id] = ft_inst
					elif linetype == 'INSTS5B':
						ft_inst = famitracker_inst('S5B')
						ft_inst.read(linedata)
						self.inst[ft_inst.id] = ft_inst
					elif linetype == 'INSTN163':
						ft_inst = famitracker_inst('N163')
						ft_inst.read(linedata)
						self.inst[ft_inst.id] = ft_inst
					elif linetype == 'INSTFDS':
						ft_inst = famitracker_inst('FDS')
						ft_inst.read(linedata)
						self.inst[ft_inst.id] = ft_inst
					elif linetype == 'INSTVRC7':
						ft_inst = famitracker_inst('VRC7')
						ft_inst.read(linedata)
						self.inst[ft_inst.id] = ft_inst


					elif linetype == 'TRACK':
						self.current_song = famitracker_song()
						self.current_song.patlen = int(linedata[0])
						self.current_song.speed = int(linedata[1])
						self.current_song.tempo = int(linedata[2])
						self.current_song.name = linedata[3]
						self.song.append(self.current_song)
						logger_projparse.info('Famitracker: Song: '+self.current_song.name)
					elif linetype == 'ORDER': 
						sordernum, sorderdata = [shlex.split(s) for s in linespl[1].split(':')]
						ordernum = int(sordernum[0], 16)
						orderdata = [int(x, 16) for x in sorderdata]
						for n, v in enumerate(orderdata):
							if n not in self.current_song.orders: self.current_song.orders[n] = []
							self.current_song.orders[n].append(v)
					elif linetype == 'PATTERN': 
						self.current_patnum = int(linedata[0], 16)
						self.current_patdata = self.current_song.patterns[self.current_patnum] = famitracker_pattern()
						logger_projparse.info('Famitracker: Pattern #'+str(self.current_patnum+1))
					elif linetype == 'ROW': 
						rowsplit = [shlex.split(s) for s in linespl[1].split(': ')]
						rownum = int(rowsplit[0][0], 16)
						for channum, rowdata in enumerate(rowsplit[1:]):
							self.current_patdata.add_data(rownum, channum, rowdata)

					elif linetype == 'COLUMNS': 
						self.current_song.columns = [int(x) for x in linedata[1:]]
					elif linetype == '#': pass
					else:
						#print(linetype, linespl[1])
						return False
		except UnicodeDecodeError:
			raise ProjectFileParserException('famistudio_txt: File is not text')

		if DEBUG_IN_OUT:
			import shutil
			shutil.copy(input_file, 'debug_in.txt')
			self.save_to_file('debug_out.txt')

		return True

	def save_to_file(self, output_file):
		f = open(output_file, 'w')
		f.write('# FamiTracker text export 0.4.2\n')
		f.write('\n')
		f.write('# Song information\n')
		f.write('TITLE           "%s"\n' % (self.title))
		f.write('AUTHOR          "%s"\n' % (self.author))
		f.write('COPYRIGHT       "%s"\n' % (self.copyright))
		f.write('\n')
		f.write('# Song comment\n')
		for c in self.comment: f.write('COMMENT "%s"\n' % (c))
		f.write('\n')
		f.write('# Global settings\n')
		f.write('MACHINE         %i\n' % (self.machine))
		f.write('FRAMERATE       %i\n' % (self.framerate))
		f.write('EXPANSION       %i\n' % (self.expansion))
		f.write('VIBRATO         %i\n' % (self.vibrato))
		f.write('SPLIT           %i\n' % (self.split))
		f.write('\n')
		f.write('# Macros\n')
		for m in self.macros: f.write(m.make()+'\n')
		f.write('\n')
		f.write('# DPCM samples\n')
		for n, d in self.dpcm.items():
			datasize = len(d.data) 
			f.write('DPCMDEF')
			f.write(str(n).rjust(4))
			f.write('  ')
			f.write(str(datasize).rjust(4))
			f.write(' "%s"' % (d.name))
			f.write('\n')
			numblocks = (datasize/32).__ceil__()
			for x in range(numblocks):
				h = d.data[x*32:(x+1)*32]
				f.write('DPCM : '+(h.hex(sep=' ').upper()))
				f.write('\n')

		f.write('\n')
		f.write('# Instruments\n')
		for n, i in self.inst.items():
			if i.chip == "2A03": f.write('INST2A03')
			if i.chip == "VRC6": f.write('INSTVRC6')
			if i.chip == "S5B": f.write('INSTS5B')
			if i.chip == "FDS": f.write('INSTFDS')

			if i.chip in ['2A03','VRC6','S5B']:
				f.write( str(n).rjust(4) )
				f.write( '  ' )
				f.write( str(i.macro_vol).rjust(4) )
				f.write( str(i.macro_arp).rjust(4) )
				f.write( str(i.macro_pitch).rjust(4) )
				f.write( str(i.macro_hipitch).rjust(4) )
				f.write( str(i.macro_duty).rjust(4) )
				f.write(' "%s"' % (i.name))
				f.write('\n')

			elif i.chip == 'FDS':
				f.write( '    ' )
				f.write( str(n) )
				f.write( '  ' )
				f.write( str(i.fds_mod_enable).rjust(4) )
				f.write( str(i.fds_mod_speed).rjust(4) )
				f.write( str(i.fds_mod_depth).rjust(4) )
				f.write( str(i.fds_mod_delay).rjust(4) )
				f.write(' "%s"' % (i.name))
				f.write('\n')
				if i.fds_wave:
					f.write('FDSWAVE    '+str(n)+' : ')
					f.write( ' '.join([str(x).rjust(2) for x in i.fds_wave]) )
					f.write('\n')
				if i.fds_mod:
					f.write('FDSMOD     '+str(n)+' : ')
					f.write( ' '.join([str(x).rjust(2) for x in i.fds_mod]) )
					f.write('\n')
				if i.fds_macros:
					for m in i.fds_macros:
						f.write('FDSMACRO   '+str(n)+' ')
						f.write( str(m.type).rjust(3) )
						f.write( str(m.id).rjust(4) )
						f.write( str(m.loop).rjust(4) )
						f.write( str(m.release).rjust(4) )
						f.write(' : ')
						f.write( ' '.join([str(x) for x in m.data]) )
						f.write('\n')

			else:
				f.write('\n')

			for dn, dk in i.dpcm_keys.items():
				f.write('KEYDPCM')
				f.write( str(dk.inst).rjust(4) )
				f.write( str(dk.octave).rjust(4) )
				f.write( str(dk.note).rjust(4) )
				f.write( str(dk.id).rjust(6) )
				f.write( str(dk.pitch).rjust(4) )
				f.write( str(dk.loop).rjust(4) )
				f.write('     0  -1\n')

		f.write('\n')
		f.write('# Tracks\n')
		f.write('\n')
		for song in self.song:
			f.write('TRACK ')
			f.write(str(song.patlen).rjust(3))
			f.write(str(song.speed).rjust(4))
			f.write(str(song.tempo).rjust(4))
			f.write(' "%s"\n' % (song.name))

			numchans = len(song.columns)
			f.write('COLUMNS : ')
			f.write( ' '.join([str(x) for x in song.columns]) )
			f.write('\n')

			f.write('\n')
			firstlen = len(song.orders[0])
			for on in range(firstlen):
				f.write('ORDER %0.2X :' % on )
				for x in range(numchans):
					f.write(' %0.2X' % (song.orders[x][on] if on<len(song.orders[x]) else 0) )
				f.write('\n')
			f.write('\n')

			#"0x%0.2X" % integerVariable

			print(song.orders[0])


			

		# FamiTracker text export 0.4.2