# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import xtramath
from objects import regions

#from functions.convproj_compat import fxrack2trackfx
#from functions.convproj_compat import trackfx2fxrack

from functions.convproj_compat import fxchange
from functions.convproj_compat import autopl_addrem
from functions.convproj_compat import changestretch
from functions.convproj_compat import fxrack_moveparams
from functions.convproj_compat import loops_add
from functions.convproj_compat import loops_remove
from functions.convproj_compat import removecut
from functions.convproj_compat import removelanes
from functions.convproj_compat import time_seconds
from functions.convproj_compat import timesigblocks
from functions.convproj_compat import track_pl_add
from functions.convproj_compat import track_pl_del
from functions.convproj_compat import unhybrid
from functions.convproj_compat import sep_nest_audio
from functions.convproj_compat import midi_notes
from functions.convproj_compat import setup_tempocalc
from functions.convproj_compat import arranger_region
from functions.convproj_compat import notepl_pitch

import json
import math

import logging
logger_compat = logging.getLogger('compat')

DEBUG_BEF_AFT_TRACKS = False

class song_compat:
	__slots__ = ['finished_processes','currenttime','current_dawcap','tempostore']

	def __init__(self):
		self.finished_processes = []
		self.currenttime = None
		self.current_dawcap = []
		self.tempostore = None

	def process_part(self, process_name, classname, convproj_obj, cvpj_type, in_compat, out_compat, out_type, dawvert_intent):
		cvpj_tracks = convproj_obj.tracks

		if process_name not in self.finished_processes:

			if DEBUG_BEF_AFT_TRACKS:
				print(process_name)
				for n, x in cvpj_tracks.data.items():
					x.debugtxt_placements(n)

			if classname.process(convproj_obj, in_compat, out_compat, out_type, dawvert_intent):
				logger_compat.info(process_name+' Done.')
				self.finished_processes.append(process_name)

			if DEBUG_BEF_AFT_TRACKS:
				print(process_name, 'after')
				for n, x in cvpj_tracks.data.items():
					x.debugtxt_placements(n)

	def makecompat(self, convproj_obj, cvpj_type, in_dawinfo, out_dawinfo, out_type, dawvert_intent):
		traits_obj = convproj_obj.traits

		if self.currenttime == None: self.currenttime = traits_obj.time_seconds
		if 'time_seconds' in self.finished_processes: self.currenttime = out_dawinfo.time_seconds

		self.process_part('notepl_pitch', notepl_pitch,		convproj_obj, cvpj_type, traits_obj.notepl_pitch, out_dawinfo.notepl_pitch, out_type, dawvert_intent)

		self.process_part('setup_tempocalc', setup_tempocalc,		convproj_obj, cvpj_type, traits_obj, out_dawinfo, out_type, dawvert_intent)
		self.process_part('fxchange', fxchange,						convproj_obj, cvpj_type, traits_obj, out_dawinfo, out_type, dawvert_intent)

		self.process_part('unhybrid', unhybrid,					   convproj_obj, cvpj_type, traits_obj.track_hybrid, out_dawinfo.track_hybrid, out_type, dawvert_intent)
		self.process_part('removelanes', removelanes,				 convproj_obj, cvpj_type, traits_obj.track_lanes, out_dawinfo, out_type, dawvert_intent)

		self.process_part('loops_remove', loops_remove,		   convproj_obj, cvpj_type, traits_obj.placement_loop, out_dawinfo.placement_loop, out_type, dawvert_intent)
		self.process_part('arranger_region', arranger_region,		   convproj_obj, cvpj_type, traits_obj.track_arranger, out_dawinfo.track_arranger, out_type, dawvert_intent)

		if self.currenttime == False:
			self.process_part('autopl_addrem', autopl_addrem,		 convproj_obj, cvpj_type, traits_obj.auto_types, out_dawinfo.auto_types, out_type, dawvert_intent)
			self.process_part('sep_nest_audio', sep_nest_audio,	   convproj_obj, cvpj_type, traits_obj.audio_nested, out_dawinfo.audio_nested, out_type, dawvert_intent)
			self.process_part('changestretch', changestretch,		 convproj_obj, cvpj_type, traits_obj.audio_stretch, out_dawinfo.audio_stretch, out_type, dawvert_intent)
			self.process_part('removecut', removecut,				 convproj_obj, cvpj_type, traits_obj.placement_cut, out_dawinfo.placement_cut, out_type, dawvert_intent)
			self.process_part('track_pl_add', track_pl_add,			   convproj_obj, cvpj_type, traits_obj.track_nopl, out_dawinfo.track_nopl, out_type, dawvert_intent)
			self.process_part('loops_add', loops_add,				 convproj_obj, cvpj_type, traits_obj.placement_loop, out_dawinfo.placement_loop, out_type, dawvert_intent)

		self.process_part('midi_notes', midi_notes,				convproj_obj, cvpj_type, traits_obj.notes_midi, out_dawinfo.notes_midi, out_type, dawvert_intent)

		#if self.currenttime == False:
		self.process_part('track_pl_del', track_pl_del,			   convproj_obj, cvpj_type, traits_obj.track_nopl, out_dawinfo.track_nopl, out_type, dawvert_intent)

		if cvpj_type in ['r']:
			self.process_part('time_seconds', time_seconds,			   convproj_obj, cvpj_type, traits_obj, out_dawinfo, out_type, dawvert_intent)

from functions.convproj_types import convert_cs2r
from functions.convproj_types import convert_cm2rm
from functions.convproj_types import convert_cm2cs
from functions.convproj_types import convert_cs2cm
from functions.convproj_types import convert_m2mi
from functions.convproj_types import convert_m2r
from functions.convproj_types import convert_mi2m
from functions.convproj_types import convert_ms2rm
from functions.convproj_types import convert_r2cs
from functions.convproj_types import convert_r2cm
from functions.convproj_types import convert_r2m
from functions.convproj_types import convert_ri2mi
from functions.convproj_types import convert_ri2r
from functions.convproj_types import convert_rm2m
from functions.convproj_types import convert_rm2r
from functions.convproj_types import convert_rs2r
from functions.convproj_types import convert_ts2m

conv_act_class = {}
conv_act_class['cm2rm'] = convert_cm2rm.convert
conv_act_class['cs2cm'] = convert_cs2cm.convert
conv_act_class['cm2cs'] = convert_cm2cs.convert
conv_act_class['cs2r'] = convert_cs2r.convert

conv_act_class['m2mi'] = convert_m2mi.convert
conv_act_class['m2r'] = convert_m2r.convert
conv_act_class['mi2m'] = convert_mi2m.convert

conv_act_class['ms2rm'] = convert_ms2rm.convert

conv_act_class['r2cm'] = convert_r2cm.convert
conv_act_class['r2cs'] = convert_r2cs.convert
conv_act_class['r2m'] = convert_r2m.convert

conv_act_class['ri2mi'] = convert_ri2mi.convert
conv_act_class['ri2r'] = convert_ri2r.convert

conv_act_class['rm2m'] = convert_rm2m.convert
conv_act_class['rm2r'] = convert_rm2r.convert
conv_act_class['rs2r'] = convert_rs2r.convert

conv_act_class['ts2m'] = convert_ts2m.convert
conv_act_class['cm2cs'] = convert_cm2cs.convert

class compat_actions:
	__slots__ = [
		'compactclass',
		'convproj_obj',
		'in_dawinfo',
		'out_dawinfo',
		'out_type',
		'dawvert_intent',
		'vars'
	]

	def __init__(self):
		self.compactclass = song_compat()
		self.convproj_obj = None
		self.in_dawinfo = None
		self.out_dawinfo = None
		self.out_type = None
		self.dawvert_intent = None
		self.vars = {}

	def makecompat(self):
		convproj_obj = self.convproj_obj
		self.compactclass.makecompat(convproj_obj, convproj_obj.type, self.in_dawinfo, self.out_dawinfo, self.out_type, self.dawvert_intent)

	def do_cmd(self, cmd):
		if cmd in conv_act_class: conv_act_class[cmd](self.convproj_obj, self.dawvert_intent)
		elif cmd=='compat': self.makecompat()

	def get_trait_out(self, name):
		if name=='notes_midi': return self.out_dawinfo.notes_midi

	def do_cmd_order(self, cmds):
		traits_obj = self.convproj_obj.traits
		for cmd in cmds:
			if isinstance(cmd, list): 
				subcmdtype = cmd[0]
				if subcmdtype=='eq_trait_out': 
					name = cmd[1]
					inval = cmd[2]
					inval = [inval] if not isinstance(inval, list) else inval
					if self.get_trait_out(name) in inval: self.do_cmd_order(cmd[3])
			else: self.do_cmd(cmd)
