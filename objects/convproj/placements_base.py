# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.convproj import time
from objects.convproj import visual
from functions import xtramath
import copy

def internal_addloops(pldata, eq_connect, loopcompat):
	old_data = copy.deepcopy(pldata)
	new_data = []

	prev = None
	for pl in old_data:
		if not eq_connect(pl, prev, loopcompat):
			new_data.append(pl)
		else:
			cur_time_obj = pl.time
			cur_duration = cur_time_obj.get_dur()
			cur_cut_start = cur_time_obj.get_offset()

			prevreal = new_data[-1]
			pr_time_obj = prevreal.time
			pr_time_obj.calc_dur_add(cur_duration)
			if pr_time_obj.cut_type == 'none': 
				pr_time_obj.cut_type = 'loop'
				pr_time_obj.calc_loopend_add(cur_duration)
			if 'loop_adv' in loopcompat:
				if pr_time_obj.cut_type == 'cut': 
					pr_time_obj.cut_type = 'loop_off'
					pr_time_obj.cut_loopstart.set(cur_cut_start, 'ppq')
					pr_time_obj.calc_loopend_add(cur_duration+cur_cut_start)
		prev = pl

	return new_data

def internal_removeloops(pldata, out__placement_loop):
	new_data = []

	for oldpl_obj in pldata: 
		oldtime_obj = oldpl_obj.time

		##print(oldtime_obj.cut_type, cut_start, loop_loopstart, loop_loopend)

		if oldtime_obj.cut_type in ['loop', 'loop_eq', 'loop_off', 'loop_adv', 'loop_adv_off'] and oldtime_obj.cut_type not in out__placement_loop:

			cut_start, loop_loopstart, loop_loopend = oldtime_obj.get_loop_data()

			#print(oldtime_obj.cut_type, cut_start, loop_loopstart, loop_loopend)

			if oldtime_obj.cut_type in ['loop_adv', 'loop_adv_off'] and 'loop_eq' in out__placement_loop:
				dur = oldtime_obj.get_dur()
				offset = oldtime_obj.get_offset()

				cutplpl_obj = copy.deepcopy(oldpl_obj)
				cutplpl_obj.time.set_dur(min(loop_loopend-offset, dur))
				cutplpl_obj.time.set_offset(offset)
				new_data.append(cutplpl_obj)

				if dur>loop_loopend:
					cutplpl_obj = copy.deepcopy(oldpl_obj)
					cpl_time_obj = cutplpl_obj.time
					cpl_time_obj.calc_pos_add(loop_loopend-offset)
					cpl_time_obj.set_dur((dur-loop_loopend)+offset)
					cpl_time_obj.set_loop_data(loop_loopstart, loop_loopstart, loop_loopend)
					new_data.append(cutplpl_obj)

			else:
				position = oldtime_obj.get_pos()
				outeq = oldtime_obj.get_dur()

				if oldtime_obj.cut_type == 'loop_eq': 
					dur = outeq+cut_start
				elif oldtime_obj.cut_type == 'loop_adv_off': 
					durr = cut_start-(loop_loopend-loop_loopstart)
					dur = outeq+cut_start-durr
				else: 
					dur = outeq

				for cutpoint in xtramath.cutloop(oldtime_obj.get_pos(), dur, cut_start, loop_loopstart, loop_loopend):
					cutplpl_obj = copy.deepcopy(oldpl_obj)

					cpl_time_obj = cutplpl_obj.time
					cpl_time_obj.cut_type = 'cut'
					cpl_time_obj.set_pos(cutpoint[0])
					cpl_time_obj.set_dur(cutpoint[1])
					cpl_time_obj.set_m_offset(cutpoint[2])

					new_data.append(cutplpl_obj)
		else: 
			new_data.append(oldpl_obj)

	#for x in new_data: print(oldpl_obj.time.get_offset())

		#print('tttttttttttt',   [x.time.get_offset() for x in new_data ]  )
	return new_data

def internal_sort(pldata):
	ta_bsort = {}
	ta_sorted = {}
	new_a = []
	for n in pldata:
		n_time = n.time
		pos = n_time.get_pos()
		if pos not in ta_bsort: ta_bsort[pos] = []
		ta_bsort[pos].append(n)
	ta_sorted = dict(sorted(ta_bsort.items(), key=lambda item: item[0]))
	for p in ta_sorted:
		for note in ta_sorted[p]: new_a.append(note)
	return new_a

def internal_get_dur(pldata):
	duration_final = 0
	for pl in pldata:
		pl_end = pl.time.get_end()
		if duration_final < pl_end: duration_final = pl_end
	return duration_final

def internal_get_start(pldata):
	start_final = 100000000000000000
	for pl in pldata:
		pl_start = curpl_time.get_pos()
		if pl_start < start_final: start_final = pl_start
	return start_final

def internal_eq_content(pl, prev):
	curpl_time = pl.time
	prevpl_time = prev.time
	isvalid_b = curpl_time.cut_type==prevpl_time.cut_type
	isvalid_c = curpl_time.get_offset()==prevpl_time.get_offset()
	isvalid_d = curpl_time.get_loopstart()==prevpl_time.get_loopstart()
	isvalid_e = curpl_time.get_loopend()==prevpl_time.get_loopend()
	isvalid_f = pl.muted==prev.muted
	return isvalid_b & isvalid_c & isvalid_d & isvalid_e & isvalid_f

def internal_eq_connect(pl, prev, loopcompat):
	curpl_time = pl.time
	prevpl_time = prev.time
	isvalid_b = curpl_time.cut_type in ['none', 'cut']
	isvalid_c = (prevpl_time.get_end()-curpl_time.get_pos())==0
	isvalid_d = prevpl_time.cut_type in ['none', 'cut']
	isvalid_e = ('loop_adv' in loopcompat) if curpl_time.cut_type == 'cut' else True
	isvalid_f = curpl_time.get_dur()==prevpl_time.get_dur()
	return isvalid_b & isvalid_c & isvalid_d & isvalid_e & isvalid_f

class cvpj_placement_fade:
	__slots__ = ['dur','time_type','skew','slope','shapetype']

	def __init__(self):
		self.dur = 0
		self.time_type = 'seconds'
		self.shapetype = ''
		self.skew = 0
		self.slope = 0

	def clear(self):
		self.dur = 0
		self.time_type = 'seconds'
		self.shapetype = ''
		self.skew = 0
		self.slope = 0

	def set_dur(self, dur, time_type):
		self.dur = dur
		self.time_type = time_type

	def get_dur_beat(self, tempo):
		if self.time_type == 'seconds': return self.dur*(tempo/120)*2
		if self.time_type == 'beats': return self.dur

	def get_dur_seconds(self, tempo):
		if self.time_type == 'beats': return self.dur/(tempo/120)/2
		if self.time_type == 'seconds': return self.dur

#					|_______|_______|_______|_______|_______|_______|_______|_______|
#	loop			Start/LoopStart                                                 LoopEnd
#	loop_eq							Start/LoopStart                                 LoopEnd
#	loop_off		LoopStart                       Start                           LoopEnd
#	loop_adv		Start                           LoopStart                       LoopEnd
#	loop_adv_off	        Start                   LoopStart                       LoopEnd

class cvpj_placement_timing:
	#__slots__ = ['position','duration','position_real','duration_real',
	#'cut_type','cut_start','cut_loopstart','cut_loopend',
	#'time_ppq','position_timemode','duration_timemode','content_timemode']
	def __init__(self, time_ppq):
		self.time_ppq = time_ppq

		self.position = time.time_position()
		self.duration = time.time_duration()

		self.cut_type = 'none'
		self.cut_start = time.time_duration()
		self.cut_loopstart = time.time_duration()
		self.cut_loopend = time.time_duration()

		self.realtime_tempo = 120

	def debugtxt(self):
		print(self.cut_type.ljust(10), end=' | ')
		print(self.position.__repr__(), end=' ')
		print(self.duration.__repr__(), end=' | ')
		if self.cut_type == 'none':
			pass
		elif self.cut_type == 'cut':
			print(self.cut_start.__repr__(), end=' ')
		elif 'loop' in self.cut_type:
			print(self.cut_start.__repr__(), end=' ')
			print(self.cut_loopstart.__repr__(), end=' ')
			print(self.cut_loopend.__repr__(), end=' ')
		print()

	# ---------------- Position ----------------

	def set_pos(self, pos):
		self.position.set(pos, 'ppq')
 
	def set_pos_real(self, pos):
		self.position.set(pos, 'seconds')
 
	def get_pos(self):
		return self.position.get('ppq', self.time_ppq)

	def get_pos_real(self):
		return self.position.get('seconds', self.time_ppq)

	def calc_pos_add(self, val):
		self.position.calc_add('ppq', val, self.time_ppq, self.realtime_tempo)

	# ---------------- Duration ----------------

	def set_dur(self, dur):
		self.duration.set(dur, 'ppq')
 
	def get_dur(self):
		return self.duration.get('ppq', self.time_ppq, self.realtime_tempo)

	def set_dur_real(self, dur):
		self.duration.set(dur, 'seconds')
 
	def set_block_dur(self, durval, blksize):
		dur = (durval/blksize).__ceil__()*blksize
		self.duration.set(dur, 'ppq')

	def get_dur_real(self):
		return self.duration.get('seconds', self.time_ppq, self.realtime_tempo)

	def calc_dur_add(self, val):
		self.duration.calc_add('ppq', val, self.time_ppq, self.realtime_tempo)

	def calc_dur_mul(self, val):
		self.duration.calc_mul('ppq', val, self.time_ppq, self.realtime_tempo)

	# ---------------- Offset ----------------

	def set_offset(self, offset):
		if offset:
			self.cut_type = 'cut'
			self.cut_start.set(offset, 'ppq')

	def set_offset_real(self, offset):
		if offset:
			self.cut_type = 'cut'
			self.cut_start.set(offset, 'seconds')

	def set_m_offset(self, offset):
		self.cut_start.set(offset, 'ppq')

	def set_m_offset_real(self, offset):
		self.cut_start.set(offset, 'seconds')

	def get_offset(self):
		return self.cut_start.get('ppq', self.time_ppq, self.realtime_tempo)

	def get_offset_real(self):
		return self.cut_start.get('seconds', self.time_ppq, self.realtime_tempo)

	def calc_offset_add(self, val):
		self.cut_start.calc_add('ppq', val, self.time_ppq, self.realtime_tempo)

	def calc_offset_mul(self, val):
		self.cut_start.calc_mul('ppq', val, self.time_ppq, self.realtime_tempo)

	# ---------------- Both ----------------

	def set_posdur(self, pos, dur):
		self.position.set(pos, 'ppq')
		self.duration.set(dur, 'ppq')
 
	def set_posdur_real(self, pos, dur):
		self.position.set(pos, 'seconds')
		self.duration.set(dur, 'seconds')
 
	def get_posdur(self):
		return self.position.get('ppq', self.time_ppq), self.duration.get('ppq', self.time_ppq, self.realtime_tempo)

	def get_posdur_real(self):
		posstart = self.position.get('seconds', self.time_ppq)
		durstart = self.duration.get('seconds', self.time_ppq, self.realtime_tempo)
		return posstart, durstart

	def set_block_posdur(self, pos, blocksize):
		self.set_posdur(pos*blocksize, blocksize)

	# ---- startend

	def set_startend(self, start, end):
		self.set_posdur(start, end-start)

	def get_startend(self):
		posstart = self.position.get('ppq', self.time_ppq)
		durstart = self.duration.get('ppq', self.time_ppq, self.realtime_tempo)
		return posstart, posstart+durstart

	def get_startend_beats(self):
		posstart = self.position.get('beats', self.time_ppq)
		durstart = self.duration.get('beats', self.time_ppq, self.realtime_tempo)
		return posstart, posstart+durstart

	def get_end(self):
		return self.get_pos()+self.get_dur()

	def set_startend_real(self, start, end):
		self.set_posdur_real(start, end-start)

	def get_startend_real(self):
		posstart = self.position.get('seconds', self.time_ppq)
		durstart = self.duration.get('seconds', self.time_ppq, self.realtime_tempo)
		return posstart, posstart+durstart

	# ---------------- Loop ----------------

	def set_loop_data(self, start, loopstart, loopend):
		if start and start==loopstart: self.cut_type = 'loop_eq'
		elif loopstart and start: self.cut_type = 'loop_adv_off'
		elif loopstart: self.cut_type = 'loop_adv'
		elif start: self.cut_type = 'loop_off'
		elif loopend: self.cut_type = 'loop'
		self.cut_start.set(start, 'ppq')
		self.cut_loopstart.set(loopstart, 'ppq')
		self.cut_loopend.set(loopend, 'ppq')

	def get_loop_data(self):
		loop_start = self.cut_start.get('ppq', self.time_ppq, self.realtime_tempo)
		loop_loopstart = self.cut_loopstart.get('ppq', self.time_ppq, self.realtime_tempo)
		loop_loopend = self.cut_loopend.get('ppq', self.time_ppq, self.realtime_tempo)
		if loop_loopend==0: loop_loopend = self.duration.get('ppq', self.time_ppq, self.realtime_tempo)
		return loop_start, loop_loopstart, loop_loopend

	def get_loopstart(self):
		return self.cut_loopstart.get('ppq', self.time_ppq, self.realtime_tempo)

	def get_loopend(self):
		return self.cut_loopend.get('ppq', self.time_ppq, self.realtime_tempo)

	def loop_scale(self, v):
		self.cut_start.calc_mul('ppq', v, self.time_ppq, self.realtime_tempo)
		self.cut_loopstart.calc_mul('ppq', v, self.time_ppq, self.realtime_tempo)
		self.cut_loopend.calc_mul('ppq', v, self.time_ppq, self.realtime_tempo)

	def loop_shift(self, v):
		self.cut_start.calc_add('ppq', v, self.time_ppq, self.realtime_tempo)
		self.cut_loopstart.calc_add('ppq', v, self.time_ppq, self.realtime_tempo)
		self.cut_loopend.calc_add('ppq', v, self.time_ppq, self.realtime_tempo)

	def get_loopcount(self):
		pos = self.position.get('seconds', self.time_ppq)
		dur = self.duration.get('seconds', self.time_ppq, self.realtime_tempo)
		return pos, pos+dur

	def calc_loopstart_add(self, val):
		self.cut_loopstart.calc_add('ppq', val, self.time_ppq, self.realtime_tempo)

	def calc_loopend_add(self, val):
		self.cut_loopend.calc_add('ppq', val, self.time_ppq, self.realtime_tempo)

	# ---------------- Other ----------------

	def copy(self):
		return copy.deepcopy(self)

	def change_timing(self, old_ppq, new_ppq):
		self.position.change_ppq(old_ppq, new_ppq)
		self.duration.change_ppq(old_ppq, new_ppq)
		self.cut_start.change_ppq(old_ppq, new_ppq)
		self.cut_loopstart.change_ppq(old_ppq, new_ppq)
		self.cut_loopend.change_ppq(old_ppq, new_ppq)
		self.time_ppq = new_ppq

	def change_seconds(self, is_seconds, bpm, ppq):
		if is_seconds:
			start, end = self.get_startend_beats()
			start_sec = time.pos_get_pos(self.position.timeid, start, True)
			end_sec = time.pos_get_pos(self.position.timeid, end, True)
			self.position.convert('seconds', ppq)
			self.duration.set((end_sec-start_sec), 'seconds')
		else:
			self.position.convert('ppq', ppq)
			self.duration.convert('ppq', ppq, self.realtime_tempo)
		
class cvpj_placement_base:
	__slots__ = ['time_ppq','time','visual','muted','fade_in','fade_out','vol','locked','group']
	def __init__(self, time_ppq):
		self.time_ppq = time_ppq
		self.time = cvpj_placement_timing(time_ppq)
		self.visual = visual.cvpj_visual()
		self.muted = False
		self.fade_in = cvpj_placement_fade()
		self.fade_out = cvpj_placement_fade()
		self.vol = 1
		self.locked = False
		self.group = None

class cvpj_placements_multi_base:
	__slots__ = ['time_ppq','data','plclass']
	def __init__(self, time_ppq, plclass):
		self.time_ppq = time_ppq
		self.data = []
		self.plclass = plclass

	def __iter__(self):
		for x in self.data: yield x

	def __len__(self):
		return self.data.__len__()

	def __bool__(self):
		return bool(self.data)

	def add(self):
		pl_obj = self.plclass(self.time_ppq)
		self.data.append(pl_obj)
		return pl_obj
		
	def sort(self):
		self.data = internal_sort(self.data)

	def get_dur(self):
		return internal_get_dur(self.data)

	def get_start(self):
		return internal_get_start(self.data)

	def add_loops(self, loopcompat):
		self.data = internal_addloops(self.data, self.eq_connect, loopcompat)

	def remove_loops(self, out__placement_loop):
		self.data = internal_removeloops(self.data, out__placement_loop)

	def eq_content(self, pl, prev):
		if prev:
			isvalid_a = pl.custom==prev.custom
			isvalid_b = internal_eq_content(pl, prev)
			return isvalid_a & isvalid_b
		else:
			return False

	def eq_connect(self, pl, prev, loopcompat):
		if prev:
			isvalid_a = self.eq_content(pl, prev)
			isvalid_b = internal_eq_connect(pl, prev, loopcompat)
			return isvalid_a & isvalid_b
		else:
			return False

	def change_seconds(self, is_seconds, bpm, ppq):
		for pl in self.data: 
			pl.time.change_seconds(is_seconds, bpm, ppq)

	def change_timings(self, time_ppq):
		for pl in self.data: pl.time.change_timing(self.time_ppq, time_ppq)
		self.time_ppq = time_ppq

	def append(self, value):
		self.data.append(value)

	def check_overlap_timeobj(self, time_obj):
		start, end = time_obj.get_startend()
		return self.check_overlap(start, end)

	def check_overlap(self, start, end):
		for npl in self.data:
			istart, iend = npl.time.get_startend()
			if xtramath.overlap(start, start+end, istart, iend):
				return True
		return False

	def clear(self):
		self.data = []
		
	def remove_overlaps(self):
		old_data_notes = copy.deepcopy(self.data)
		new_data_notes = []

		prev = None
		for pl in old_data_notes:
			time_obj = pl.time
			position, duration = time_obj.get_posdur()
			if prev: 
				prev_time_obj = prev.time
				prev_time_obj.set_dur( min(prev_time_obj.get_dur(), position-prev_time_obj.get_pos()) )
			prev = pl
			new_data_notes.append(pl)

		self.data = new_data_notes


class cvpj_placements_multi_auto_base:
	__slots__ = ['data','time_ppq','val_type','plclass']
	def __init__(self, time_ppq, val_type, plclass):
		self.time_ppq = time_ppq
		self.val_type = val_type
		self.data = []
		self.plclass = plclass

	def __iter__(self):
		for x in self.data: yield x

	def __len__(self):
		return self.data.__len__()

	def __bool__(self):
		return bool(self.data)

	def add(self, val_type):
		pl_obj = self.plclass(self.time_ppq, self.val_type)
		self.data.append(pl_obj)
		return pl_obj

	def get_dur(self):
		return internal_get_dur(self.data)

	def get_start(self):
		return internal_get_start(self.data)

	def add_loops(self, loopcompat):
		self.data = internal_addloops(self.data, self.eq_connect, loopcompat)

	def remove_loops(self, out__placement_loop):
		self.data = internal_removeloops(self.data, out__placement_loop)

	def eq_content(self, pl, prev):
		if prev:
			isvalid_a = pl.custom==prev.custom
			isvalid_b = internal_eq_content(pl, prev)
			return isvalid_a & isvalid_b
		else:
			return False

	def eq_connect(self, pl, prev, loopcompat):
		if prev:
			isvalid_a = self.eq_content(pl, prev)
			isvalid_b = internal_eq_connect(pl, prev, loopcompat)
			return isvalid_a & isvalid_b
		else:
			return False

	def check(self):
		return len(self.data) != 0

	def change_seconds(self, is_seconds, bpm, ppq):
		for pl in self.data: 
			pl.time.change_seconds(is_seconds, bpm, ppq)
			pl.data.change_seconds(is_seconds, bpm, ppq)

	def calc(self, mathtype, val1, val2, val3, val4):
		for pl in self.data: pl.data.calc(mathtype, val1, val2, val3, val4)

	def funcval(self, i_function):
		for pl in self.data: pl.data.funcval(i_function)

	def change_timings(self, time_ppq):
		for pl in self.data:
			pl.time.change_timing(self.time_ppq, time_ppq)
			pl.data.change_timings(time_ppq)
		self.time_ppq = time_ppq
