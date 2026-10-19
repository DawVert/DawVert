# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from objects.tracker import notestream

t_retg_alg = [['mul', 1], ['minus', 1], ['minus', 2], ['minus', 4], ['minus', 8], ['minus', 16], ['mul', 2/3], ['mul', 1/2], ['mul', 1], ['plus', 1], ['plus', 2], ['plus', 4], ['plus', 8], ['plus', 16], ['mul', 3/2], ['mul', 2]]

class cur_speed:
	def __init__(self, s_bpm, s_speed):
		self.tempo = s_bpm
		self.speed = s_speed
		self.changed = True

	def get_speed(self):
		return self.tempo*(6/(self.speed if self.speed else 1))

	def proc_data(self, idata):
		if 'speed' in idata: 
			self.speed = idata['speed']
			self.bpm_changed = True
		if 'tempo' in idata: 
			self.tempo = idata['tempo']
			self.bpm_changed = True

	def get_change(self):
		outval = (self.get_speed() if self.bpm_changed else None)
		self.bpm_changed = False
		return outval

VISUAL_ON = False
VISUAL_CELL_NL = True

def cell_visual(celldata):
	txt_note = '...'
	txt_inst = '..'
	txt_mod = '.'

	if celldata:
		if celldata.note: txt_note = str(celldata.note).rjust(3)
		if celldata.inst: txt_inst = str(celldata.inst).rjust(2)
		if celldata.fx: txt_mod = '#'

	return ' '.join([txt_note,txt_inst,txt_mod] if VISUAL_CELL_NL else [txt_note])
	
class playstream:
	def __init__(self):
		self.columns = []
		self.notestreams = []
		self.patnum = 0
		self.curpos = 0
		self.maxpos = 4
		self.stopped = True
		self.stopped_reason = None
		self.stopped_value = None
		self.cur_tempo = cur_speed(120, 6)
		self.auto_tempo = notestream.autostream()
		self.auto_mastervol = notestream.autostream()
		self.first_speed = None

	def add_channel(self, text_inst_start):
		self.columns.append(None)
		self.notestreams.append(notestream.notestream(text_inst_start))

	def init_tempo(self, s_bpm, s_speed):
		self.cur_tempo = cur_speed(s_bpm, s_speed)

	def init_patinfo(self, numrows, patnum):
		for x in self.notestreams: x.add_pl(patnum)
		self.auto_tempo.add_pl()
		self.auto_mastervol.add_pl()

		self.curpos = 0
		self.maxpos = numrows
		self.stopped = False
		self.stopped_reason = None
		self.stopped_value = None
		self.patnum = patnum

	def next_row(self):
		if self.curpos < self.maxpos: self.cur_tempo.bpm_changed = False
		else: self.stopped = True

		if not self.stopped:
			if VISUAL_ON: vistxt = str(self.patnum).rjust(3)+(' [=] ' if self.stopped else ' [>] ')
			if VISUAL_ON: vistxt += str(self.curpos).rjust(3)+'/'+str(self.maxpos).ljust(3)
			global_fx = None
			for c, x in enumerate(self.columns):
				cell_data = x.get_pos(self.curpos) if x else None
				if VISUAL_ON: vistxt += '|'+cell_visual(cell_data)
				if cell_data: 
					if cell_data.g_fx: 
						if global_fx == None: global_fx = {}
						global_fx |= cell_data.g_fx
						self.cur_tempo.proc_data(global_fx)

				if global_fx:
					if 'global_volume' in global_fx:
						self.auto_mastervol.do_point(global_fx['global_volume'])

				self.notestreams[c].do_cell_obj(cell_data,self.cur_tempo.speed)
			if VISUAL_ON: vistxt += '|'+str(self.cur_tempo.tempo).rjust(4)+(' # ' if self.cur_tempo.changed else ' - ')+str(self.cur_tempo.speed).ljust(3)
			if VISUAL_ON: vistxt += '|'

			if self.cur_tempo.changed: 
				if self.first_speed == None: self.first_speed = self.cur_tempo.get_speed()
				changedval = self.cur_tempo.get_change()
				if changedval:
					self.auto_tempo.do_point(changedval)

			self.auto_tempo.next()
			self.auto_mastervol.next()

			if VISUAL_ON: print(vistxt, global_fx)

			if global_fx:
				if 'break_to_row' in global_fx:
					self.stopped = True
					self.stopped_reason = 'break_to_row'
					self.stopped_value = global_fx['break_to_row']
				if 'skip_pattern' in global_fx:
					self.stopped = True
					self.stopped_reason = 'skip_pattern'
					self.stopped_value = global_fx['skip_pattern']
				if 'pattern_jump' in global_fx:
					self.stopped = True
					self.stopped_reason = 'pattern_jump'
					self.stopped_value = global_fx['pattern_jump']

			self.curpos += 1

		return not self.stopped

def splitparams(value, firstname, secondname):
	dualparams = {}
	dualparams[firstname], dualparams[secondname] = data_bytes.splitbyte(value)
	return dualparams

def getfineval(value):
	volslidesplit = data_bytes.splitbyte(value)
	volslideout = 0
	if volslidesplit[0] == 0 and volslidesplit[1] == 0: volslideout = 0
	elif volslidesplit[0] == 15 and volslidesplit[1] == 15: volslideout = volslidesplit[0]/16
	elif volslidesplit[0] == 0 and volslidesplit[1] == 15: volslideout = -15
	elif volslidesplit[0] == 0 and volslidesplit[1] != 0: volslideout = volslidesplit[1]*-1
	elif volslidesplit[0] != 0 and volslidesplit[1] == 0: volslideout = volslidesplit[0]
	elif volslidesplit[0] == 15 and volslidesplit[1] != 15: volslideout = (volslidesplit[0]*-1)/16
	elif volslidesplit[0] != 15 and volslidesplit[1] == 15: volslideout = volslidesplit[0]/16
	return volslideout

def addminusval(i_val):
	pos, neg = data_bytes.splitbyte(i_val)
	return (neg*-1) + pos

class tracker_channel:
	def __init__(self):
		self.name = None
		self.color = None
		self.insttype = None
		self.vol = 1
		self.pan = 0
		self.fx_plugins = []

class tracker_cell:
	__slots__ = ['note', 'inst', 'fx', 'g_fx']
	def __init__(self):
		self.note = None
		self.inst = None
		self.fx = None
		self.g_fx = None

	def __repr__(self):
		return ','.join([str(x) for x in [self.note,self.inst,self.fx,self.g_fx]])

class tracker_column:
	def __init__(self):
		self.data = {}

	def get_pos(self, row_num):
		return self.data[row_num] if row_num in self.data else None

	def auto_cell(self, row_num):
		if row_num not in self.data: self.data[row_num] = tracker_cell()
		return self.data[row_num]

	def cell_note(self, row_num, note, inst):
		row = self.auto_cell(row_num)
		row.note = note
		row.inst = inst

	def cell_param(self, row_num, p_name, p_val):
		row = self.auto_cell(row_num)
		if row.fx == None: row.fx = {}
		row.fx[p_name] = p_val

	def cell_g_param(self, row_num, p_name, p_val):
		row = self.auto_cell(row_num)
		if row.g_fx == None: row.g_fx = {}
		row.g_fx[p_name] = p_val

	def cell_fx_mod(self, row_num, fx_type, fx_value):
		if fx_type == 1: self.cell_param(row_num, 'std_slide_up', fx_value)
		if fx_type == 2: self.cell_param(row_num, 'std_slide_down', fx_value)
		if fx_type == 3: self.cell_param(row_num, 'std_slide_to_note', fx_value)
		if fx_type == 4: self.cell_param(row_num, 'vibrato', splitparams(fx_value, 'speed', 'depth'))
		if fx_type == 6: self.cell_param(row_num, 'vol_slide', addminusval(fx_value))
		if fx_type == 7: self.cell_param(row_num, 'tremolo', splitparams(fx_value, 'speed', 'depth'))
		if fx_type == 8: self.cell_param(row_num, 'pan', (fx_value-128)/128)
		if fx_type == 9: self.cell_param(row_num, 'sample_offset', fx_value*256)
		if fx_type == 10: self.cell_param(row_num, 'vol_slide', addminusval(fx_value))

		if fx_type == 0 and fx_value != 0:
			arpeggio_first, arpeggio_second = data_bytes.splitbyte(fx_value)
			self.cell_param(row_num, 'arp', [arpeggio_first, arpeggio_second])

		if fx_type == 5:
			valueout = addminusval(fx_value) 
			self.cell_param(row_num, 'vol_slide', valueout)
			self.cell_param(row_num, 'slide_to_note', valueout)

		if fx_type == 14: 
			ext_type, ext_value = data_bytes.splitbyte(fx_value)
			if ext_type == 0: self.cell_param(row_num, 'filter_amiga_led', ext_value)
			if ext_type == 1: self.cell_param(row_num, 'fine_slide_up', ext_value)
			if ext_type == 2: self.cell_param(row_num, 'fine_slide_down', ext_value)
			if ext_type == 3: self.cell_param(row_num, 'glissando_control', ext_value)
			if ext_type == 4: self.cell_param(row_num, 'vibrato_waveform', ext_value)
			if ext_type == 5: self.cell_param(row_num, 'set_finetune', ext_value)
			if ext_type == 6: self.cell_param(row_num, 'pattern_loop', ext_value)
			if ext_type == 7: self.cell_param(row_num, 'tremolo_waveform', ext_value)
			if ext_type == 8: self.cell_param(row_num, 'set_pan', ext_value)
			if ext_type == 9: self.cell_param(row_num, 'retrigger_note', ext_value)
			if ext_type == 10: self.cell_param(row_num, 'fine_vol_slide_up', ext_value)
			if ext_type == 11: self.cell_param(row_num, 'fine_vol_slide_down', ext_value)
			if ext_type == 12: self.cell_param(row_num, 'note_cut', ext_value)
			if ext_type == 13: self.cell_param(row_num, 'note_delay', ext_value)
			if ext_type == 14: self.cell_param(row_num, 'pattern_delay', ext_value)
			if ext_type == 15: self.cell_param(row_num, 'invert_loop', ext_value)

	def cell_fx_s3m(self, row_num, fx_type, fx_value):
		if fx_type == 1: self.cell_g_param(row_num, 'speed', fx_value)
		if fx_type == 2: self.cell_g_param(row_num, 'pattern_jump', fx_value)
		if fx_type == 3: self.cell_g_param(row_num, 'break_to_row', fx_value)
		if fx_type == 4: self.cell_param(row_num, 'vol_slide', getfineval(fx_value))
		if fx_type == 5: 
			if 240 <= fx_value:		 self.cell_param(row_num, 'fine_slide_down', (fx_value-240)/8)
			elif 224 <= fx_value <= 239:  self.cell_param(row_num, 'fine_slide_down', (fx_value-224)/16)
			else:					   self.cell_param(row_num, 'std_slide_down', fx_value)
		if fx_type == 6: 
			if 240 <= fx_value:		 self.cell_param(row_num, 'fine_slide_up', (fx_value-240)/8)
			elif 224 <= fx_value <= 239:  self.cell_param(row_num, 'fine_slide_up', (fx_value-224)/16)
			else:					   self.cell_param(row_num, 'std_slide_up', fx_value)
		if fx_type == 7: self.cell_param(row_num, 'std_slide_to_note', fx_value)
		if fx_type == 8: self.cell_param(row_num, 'vibrato', splitparams(fx_value, 'speed', 'depth'))
		if fx_type == 9: self.cell_param(row_num, 'tremor', splitparams(fx_value, 'ontime', 'offtime'))
		if fx_type == 11: self.cell_param(row_num, 'vol_slide', getfineval(fx_value))
		if fx_type == 13: self.cell_param(row_num, 'channel_vol', fx_value/64)
		if fx_type == 14: self.cell_param(row_num, 'channel_vol_slide', getfineval(fx_value))
		if fx_type == 15: self.cell_param(row_num, 'sample_offset', fx_value*256)
		if fx_type == 16: self.cell_param(row_num, 'pan_slide', getfineval(fx_value)*-1)
		if fx_type == 18: self.cell_param(row_num, 'tremolo', splitparams(fx_value, 'speed', 'depth'))
		if fx_type == 22: self.cell_g_param(row_num, 'global_volume', fx_value/64)
		if fx_type == 23: self.cell_g_param(row_num, 'global_volume_slide', getfineval(fx_value))
		if fx_type == 24: self.cell_param(row_num, 'set_pan', fx_value/255)
		if fx_type == 25: self.cell_param(row_num, 'panbrello', splitparams(fx_value, 'speed', 'depth'))

		if fx_type == 10:
			arpeggio_first, arpeggio_second = data_bytes.splitbyte(fx_value)
			self.cell_param(row_num, 'arp', [arpeggio_first, arpeggio_second])

		if fx_type == 12:
			self.cell_param(row_num, 'vol_slide', getfineval(fx_value))
			self.cell_param(row_num, 'slide_to_note', getfineval(fx_value))

		if fx_type == 17:
			retrigger_params = {}
			retrigger_alg, retrigger_params['speed'] = data_bytes.splitbyte(fx_value)
			retrigger_params['alg'], retrigger_params['val'] = t_retg_alg[retrigger_alg]
			self.cell_param(row_num, 'retrigger', retrigger_params)
	
		if fx_type == 19: 
			ext_type, ext_value = data_bytes.splitbyte(fx_value)
			if ext_type == 1: self.cell_param(row_num, 'glissando_control', ext_value)
			if ext_type == 3: self.cell_param(row_num, 'vibrato_waveform', ext_value)
			if ext_type == 4: self.cell_param(row_num, 'tremolo_waveform', ext_value)
			if ext_type == 5: self.cell_param(row_num, 'panbrello_waveform', ext_value)
			if ext_type == 6: self.cell_param(row_num, 'fine_pattern_delay', ext_value)
			if ext_type == 7: self.cell_param(row_num, 'it_inst_control', ext_value)
			if ext_type == 8: self.cell_param(row_num, 'set_pan', ext_value/16)
			if ext_type == 9: self.cell_param(row_num, 'it_sound_control', ext_value)
			if ext_type == 10: self.cell_param(row_num, 'sample_offset_high', ext_value*65536)
			if ext_type == 11: self.cell_param(row_num, 'loop_start', ext_value)
			if ext_type == 12: self.cell_param(row_num, 'note_cut', ext_value)
			if ext_type == 13: self.cell_param(row_num, 'note_delay', ext_value)
			if ext_type == 14: self.cell_param(row_num, 'pattern_delay', ext_value)
			if ext_type == 15: self.cell_param(row_num, 'it_active_macro', ext_value)
