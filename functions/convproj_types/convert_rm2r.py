# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import xtramath

import json
import logging

logger_project = logging.getLogger('project')

def convert(convproj_obj):
	logger_project.info('ProjType Convert: RegularMultiple > Regular')

	fxrack_obj = convproj_obj.fxrack
	cvpj_tracks = convproj_obj.tracks
	cvpj_insts = convproj_obj.instruments
	useable_plugins = convproj_obj.plugins

	convproj_obj.plugins = {}

	used_plugins = []


	old_track_order = cvpj_tracks.order.copy()

	for _, track_obj in cvpj_tracks.iter():
		for x in track_obj.plugslots.slots_audio:
			if x not in used_plugins: used_plugins.append(x)

	for x in convproj_obj.track_master.plugslots.slots_audio:
		if x not in used_plugins: used_plugins.append(x)

	nonmultitrack = []
	splitted_trks = {}
	for trackid, track_obj in cvpj_tracks.iter():

		if track_obj.type == 'instruments':
			splitted_pl = track_obj.placements.inst_split()
			splitted_nl = track_obj.placements.notelist.inst_split()

			comb_split = {}
			for i, d in splitted_pl.items():
				if i not in comb_split: comb_split[i] = [None, None]
				comb_split[i][0] = d

			for i, d in splitted_nl.items():
				if i not in comb_split: comb_split[i] = [None, None]
				comb_split[i][1] = d

			for i, d in comb_split.items():
				pls, nl = d
				if i not in splitted_trks: splitted_trks[i] = []
				if i in cvpj_insts:
					inst_obj = cvpj_insts[i]
	
					new_track_obj = track_obj.make_base_inst(inst_obj)
					new_track_obj.is_drum = inst_obj.is_drum
					new_track_obj.group = inst_obj.group
					used_plugins.append(new_track_obj.plugslots.synth)
					for x in new_track_obj.plugslots.slots_audio:
						if x not in used_plugins: used_plugins.append(x)
	
					if new_track_obj.fxrack_channel == -1: new_track_obj.fxrack_channel = track_obj.fxrack_channel
	
					if new_track_obj.visual.name and inst_obj.visual.name: new_track_obj.visual.name = inst_obj.visual.name+' ('+new_track_obj.visual.name+')'
					else: new_track_obj.visual.name = inst_obj.visual.name
					if not new_track_obj.visual.color: new_track_obj.visual.color = inst_obj.visual.color
				else:
					new_track_obj = track_obj.make_base()
					if new_track_obj.visual.name:
						new_track_obj.visual.name = i+' ('+new_track_obj.visual.name+')'
					else:
						new_track_obj.visual.name = i
	
				splitted_trks[i].append([trackid, new_track_obj, pls, nl])
		else:
			nonmultitrack.append([trackid, track_obj])

	for x in old_track_order:
		cvpj_tracks.order.remove(x)
		del cvpj_tracks.data[x]

	for xc, trackdata in splitted_trks.items():

		for oldtrackid, track_obj, track_pls, track_nl in trackdata:

			cvpj_trackid = 'rm2r_'+xc+'_'+oldtrackid
			track_obj.type = 'instrument'
			if track_pls: track_obj.placements.pl_notes.data = track_pls
			if track_nl: track_obj.placements.notelist = track_nl

			cvpj_tracks.data[cvpj_trackid] = track_obj
			cvpj_tracks.order.append(cvpj_trackid)

	for trackid, track_obj in nonmultitrack:
		cvpj_tracks.data[trackid] = track_obj
		cvpj_tracks.order.append(trackid)

		for fxid in track_obj.plugslots.slots_audio:
			used_plugins.append(fxid)

	for num, fxchannel_obj in fxrack_obj.items():
		used_plugins += fxchannel_obj.plugslots.slots_audio

	used_plugins = set(used_plugins)
	if '' in used_plugins: used_plugins.remove('')

	for plugid in set(used_plugins):
		if plugid in useable_plugins:
			convproj_obj.plugins[plugid] = useable_plugins[plugid]

	cvpj_insts.clear()
	convproj_obj.type = 'r'
