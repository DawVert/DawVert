# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import regions
import numpy as np
from functions import xtramath
from objects.data_bytes import dynbytearr

timesig_premake = dynbytearr.dynbytearr_premake([
		('type', np.uint8),

		('start', np.float64),
		('end', np.float64),
		('numerator', np.uint8),
		('denominator', np.uint8),

		('dur', np.float64),
	])

BLOCKID__ZERO = 100
BLOCKID__START = 101
BLOCKID__END = 102
BLOCKID__TIMESIG = 1

def add_dur_end(splitdata):
	p = None
	for n, u in enumerate(splitdata.data):
		if u['used']:
			if p:
				p['end'] = u['start']
				p['dur'] = u['start']-p['start']
			p = u


def remove_pos_clones(splitdata):
	splitdata.sort(['start'])
	prevval = -1
	for x in splitdata.data:
		if x['used']:
			if prevval-x['start'] == 0: x['used'] = 0
			prevval = x['start']
	splitdata.clean()

class timesigblocks:
	__slots__ = ['splitdata','cur_splitdata']
	def __init__(self):
		self.splitdata = timesig_premake.create()
		self.cur_splitdata = self.splitdata.create_cursor()

	def add_split_type(self, pos, num, dem, itype):
		self.cur_splitdata.add()
		self.cur_splitdata['type'] = itype
		self.cur_splitdata['start'] = pos
		self.cur_splitdata['numerator'] = num
		self.cur_splitdata['denominator'] = dem

	def add_split(self, pos, num, dem):
		self.cur_splitdata.add()
		self.cur_splitdata['start'] = pos
		self.cur_splitdata['numerator'] = num
		self.cur_splitdata['denominator'] = dem

	def create_points_cut(self, convproj_obj, splitter_mode, splitter_start):
		ppq = convproj_obj.time_ppq

		timesig_num, timesig_dem = convproj_obj.timesig
		enddur = convproj_obj.get_dur()
		self.add_split_type(0, timesig_num, timesig_dem, BLOCKID__ZERO)
		self.add_split_type(enddur, timesig_num, timesig_dem, BLOCKID__END)
		self.add_split_type(enddur+ppq, timesig_num, timesig_dem, BLOCKID__END)

		for pos, timesig in convproj_obj.timesig_auto:
			self.add_split_type(pos, timesig[0], timesig[1], BLOCKID__TIMESIG)
		
		remove_pos_clones(self.splitdata)
		add_dur_end(self.splitdata)

		startpos = 0
		if splitter_start:
			if convproj_obj.transport.loop_start:
				startpos = convproj_obj.transport.loop_start
			if not startpos:
				startpos = convproj_obj.transport.start_pos

			useddata = self.splitdata.get_used()
			poslist = useddata['start']
			if max(poslist)>startpos and startpos not in poslist:
				timesigid = np.searchsorted(poslist, startpos)
				betweenval = useddata[timesigid]
				self.add_split(startpos, betweenval['numerator'], betweenval['denominator'])

		if splitter_mode == 'timesig_num':
			for u in self.splitdata.get_used():
				psize = ppq*float(u['numerator'])
				for val in xtramath.gen_float_range(float(u['start']), float(u['end']), psize):
					self.add_split(val, u['numerator'], u['denominator'])

		if splitter_mode == 'timesig_num_x2':
			remove_pos_clones(self.splitdata)
			add_dur_end(self.splitdata)
			for u in self.splitdata.get_used():
				psize = ppq*int(u['numerator'])*2
				for val in xtramath.gen_float_range(int(u['start']), int(u['end']), psize):
					self.add_split(val, u['numerator'], u['denominator'])

		if splitter_mode == 'timesig':
			remove_pos_clones(self.splitdata)
			add_dur_end(self.splitdata)
			for u in self.splitdata.get_used():
				psize = ppq*int(u['numerator'])*int(u['denominator'])
				for val in xtramath.gen_float_range(int(u['start']), int(u['end']), psize):
					self.add_split(val, u['numerator'], u['denominator'])

		remove_pos_clones(self.splitdata)
		add_dur_end(self.splitdata)

dtype_blocks = np.dtype([
		('start', np.float64),
		('end', np.float64),
		('dur', np.float64),

		('used', np.uint8),
		('nosplit', np.uint8),
		('overflow', np.float64),
		('remaining', np.float64),
	])

useactive_premake = dynbytearr.dynbytearr_premake([
		('start', np.float64),
		('end', np.float64),
		('active', np.uint8),
		('done', np.uint8),
	])

def blocksdata_proc(blocksdata):
	for blockdata in blocksdata:
		remainval = 0
		for splitd in blockdata:
			splitd['remaining'] = remainval
			if remainval: splitd['used'] = 1
			remainval = max(remainval-splitd['dur'], 0)
			remainval += splitd['overflow']
			splitd['nosplit'] = 1+(remainval!=0) if splitd['used'] else 0

def blocksdata_pl_proc(blockdata):
	activedata = useactive_premake.create()
	cur_activedata = activedata.create_cursor()
	cur_activedata.add()
	for x in blockdata:
		nosplit = x['nosplit']
		if cur_activedata['done']: cur_activedata.add()
		if nosplit != 0:
			if not cur_activedata['active']:
				cur_activedata['start'] = x['start']
				cur_activedata['active'] = 1
			cur_activedata['end'] = x['end']
			if nosplit == 1:
				cur_activedata['done'] = 1
				cur_activedata['active'] = 0
		else:
			if cur_activedata['active']:
				cur_activedata['done'] = 1
	return activedata

def create_blocksdata(timesigblocks_obj, data):
	useddata = timesigblocks_obj.splitdata.get_used()
	blocksdata = np.zeros((len(data), len(useddata)), dtype=dtype_blocks)
	blocksdata['start'] = useddata['start']
	blocksdata['end'] = useddata['end']
	blocksdata['dur'] = useddata['dur']
	return useddata, blocksdata

class cvpj_midievents_splitter:
	__slots__ = ['data','ppq','timesigblocks_obj','useddata','blocksdata']
	
	def __init__(self, timesigblocks_obj, ppq):
		self.data = []
		self.ppq = ppq
		self.timesigblocks_obj = timesigblocks_obj
		self.useddata = None
		self.blocksdata = None

	def add_pldata(self, i_pl):
		self.data.append(i_pl)

	def process(self, splitter_mode):
		self.useddata, self.blocksdata = create_blocksdata(self.timesigblocks_obj, self.data)

		for plnum, pldata in enumerate(self.data):
			for blocknum, blockdata in enumerate(self.useddata):
				splitd = self.blocksdata[plnum][blocknum]
				midievents = pldata.midievents
				midievents.add_note_durs()
				splitd['used'], splitd['overflow'] = midievents.usedoverflow(blockdata['start'], blockdata['end'])

	def process_post(self, splitter_mode):
		blocksdata_proc(self.blocksdata)

		for plnum, pldata in enumerate(self.data):
			activedata = blocksdata_pl_proc(self.blocksdata[plnum])

			nopl_midievents = pldata.midievents
			if isinstance(self.ppq, int):
				flomul = 1
				for x in activedata.get_used():
					if x['done']:
						range_start = int(x['start']*flomul)
						range_end = int(x['end']*flomul)
						outevents = nopl_midievents.new_ev_start_end(range_start, range_end)

						placement_obj = pldata.add_midi()
						placement_obj.midievents = outevents
						time_obj = placement_obj.time
						time_obj.set_startend(int(x['start']), int(x['end']))
			nopl_midievents.clear()
			pldata.uses_placements = 1

class cvpj_notelist_splitter:
	__slots__ = ['data','ppq','timesigblocks_obj','useddata','blocksdata']
	def __init__(self, timesigblocks_obj, ppq):
		self.data = []
		self.ppq = ppq
		self.timesigblocks_obj = timesigblocks_obj
		self.useddata = None
		self.blocksdata = None

	def add_pldata(self, i_pl):
		self.data.append(i_pl)

	def process(self, splitter_mode):
		self.useddata, self.blocksdata = create_blocksdata(self.timesigblocks_obj, self.data)

		for plnum, pldata in enumerate(self.data):
			for blocknum, blockdata in enumerate(self.useddata):
				splitd = self.blocksdata[plnum][blocknum]
				notelist = pldata.notelist
				splitd['used'], splitd['overflow'] = notelist.usedoverflow(blockdata['start'], blockdata['end'])

	def to_blocks(self):
		for trackpl in self.blocksdata:
			for plnum in range(len(trackpl)-1):
				splitd = trackpl[plnum]
				splitd_n = trackpl[plnum+1]
				if splitd['used'] and splitd_n['used']:
					if not splitd['overflow']: splitd['overflow'] += self.ppq

	def process_post(self, splitter_mode):
		blocksdata_proc(self.blocksdata)

		for plnum, pldata in enumerate(self.data):
			activedata = blocksdata_pl_proc(self.blocksdata[plnum])
			for x in activedata.get_used():
				if x['done']:
					placement_obj = pldata.add_notes()
					placement_obj.notelist = pldata.notelist.new_nl_start_end(x['start'], x['end'])
					time_obj = placement_obj.time
					time_obj.set_startend(int(x['start']), int(x['end']))
			pldata.notelist.clear()
			pldata.uses_placements = 1