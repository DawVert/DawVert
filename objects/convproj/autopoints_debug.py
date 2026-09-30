# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
import copy
import numpy as np

verbose_blocks_gfx = [' ','▁','▂','▃','▄','▅','▆','▇','█']

class debug_display:
	def __init__(self):
		self.val_min = 0
		self.val_max = 1
		self.dur_max = 1
		self.sustain = -1
		self.vsize = 6
		self.hsize = 120
		self.color_norm = '\x1b[37;40m'
		self.color_point = '\x1b[96;44m'
		self.color_sus = '\x1b[33;41m'
		self.points = []
		self.set_size(8, 120)

	def set_size(self, vs, hs):
		self.vsize = vs
		self.hsize = hs
		self.gfxdata_vals = [0 for x in range(hs)]

	def from_points(self, autopoints_obj):
		useddata = autopoints_obj.points.get_used()
		self.points = [[x['pos'], x['value'], x['instant_mode'], x['value_end']] for x in useddata]
		if self.points:
			self.dur_max = autopoints_obj.get_dur()
			self.val_min = min(useddata['value'])
			self.val_max = max(useddata['value'])
			self.sustain =  autopoints_obj.sustain_point if autopoints_obj.sustain_on else -1
		else:
			self.val_min = 0
			self.val_max = 1
			self.dur_max = 1
			self.sustain = -1

	def gfxval_range(self, p_start, p_end, v_start, v_end):
		size = p_end-p_start
		for x in range(size):
			self.gfxdata_vals[p_start+x] = xtramath.between_from_one(v_start, v_end, x/size)

	def gfxval_flat(self, p_start, p_end, val):
		size = p_end-p_start
		for x in range(size):
			self.gfxdata_vals[p_start+x] = val

	def print(self):
		procpoints = [[p/self.dur_max, xtramath.between_to_one(self.val_min, self.val_max, v), i, xtramath.between_to_one(self.val_min, self.val_max, e)] for p,v,i,e in self.points]
		print('NUM POINTS: ',len(self.points))

		gfxdata_colors = ['\x1b[37;40m' for x in range(self.hsize)]

		debp = [[int(xtramath.clamp(x,0,1)*self.hsize), y, i, e] for x,y,i,e in procpoints]

		for n in range(len(debp)-1):
			curp = debp[n]
			nextp = debp[n+1]
			size = nextp[0]-curp[0]

			if curp[2] == 0:
				if nextp[2]==0:
					self.gfxval_range(debp[n][0], nextp[0], curp[1], nextp[1])
				elif nextp[2]==1:
					self.gfxval_flat(debp[n][0], nextp[0], curp[1])
				elif nextp[2]==2:
					self.gfxval_range(debp[n][0], nextp[0], curp[1], nextp[1])
			if curp[2] == 1:
				if nextp[2]==0:
					self.gfxval_range(debp[n][0], nextp[0], curp[1], nextp[1])
				elif nextp[2]==1:
					self.gfxval_flat(debp[n][0], nextp[0], curp[1])
				elif nextp[2]==2:
					self.gfxval_range(debp[n][0], nextp[0], curp[1], nextp[1])
			if curp[2] == 2:
				if nextp[2]==0:
					self.gfxval_range(debp[n][0], nextp[0], curp[3], nextp[1])
				elif nextp[2]==1:
					self.gfxval_flat(debp[n][0], nextp[0], curp[1])
				elif nextp[2]==2:
					self.gfxval_range(debp[n][0], nextp[0], curp[3], nextp[1])

		for n, d in enumerate(procpoints):
			p, v, i, e = d
			blocknum = int((p)*self.hsize)
			gfxdata_colors[min(blocknum, self.hsize-1)] = '\x1b[96;44m'
			sustain = self.sustain
			if sustain>=0:
				if sustain==n:
					gfxdata_colors[min(blocknum, self.hsize-1)] = '\x1b[33;41m'

		for vh in range(self.vsize, 0, -1):
			ft = [int(xtramath.clamp((x*self.vsize)-(vh-1), 0, 1)*(len(verbose_blocks_gfx)-1)) for x in self.gfxdata_vals]
			gfxdata_txt = [' ' for x in range(self.hsize)]
			for n, x in enumerate(ft): gfxdata_txt[n] = verbose_blocks_gfx[int(x)]
			for x in range(self.hsize): print(gfxdata_colors[x]+gfxdata_txt[x], end='')
			print('\033[0;0m')

def points_to_plot(plot_obj, points):
	op_pos = []
	op_val = []

	scat_pos = []
	scat_val = []

	prev_val = 0
	for n, p in enumerate(points):
		im = p['instant_mode']

		scat_pos.append(p['pos'])
		scat_val.append(p['value'])

		if im == 0:
			op_pos.append(p['pos'])
			op_val.append(p['value'])
		elif im == 1:
			if n == 0:
				op_pos.append(p['pos'])
				op_val.append(p['value'])
			else:
				op_pos.append(p['pos'])
				op_val.append(prev_val)
				op_pos.append(p['pos'])
				op_val.append(p['value'])
		elif im == 2:
			op_pos.append(p['pos'])
			op_val.append(p['value'])
			op_pos.append(p['pos'])
			op_val.append(p['value_end'])

		prev_val = p['value']

	plot_obj.plot(op_pos, op_val)
	plot_obj.scatter(scat_pos, scat_val)