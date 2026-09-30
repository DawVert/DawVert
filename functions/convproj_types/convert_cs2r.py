# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging
import numpy as np
import struct
from objects.convproj import midievents
import objects.midi_modernize.midi_modernize as midi_modernize

logger_project = logging.getLogger('project')

from functions.convproj_types import convert_cm2rm

def convert(convproj_obj, dawvert_intent):
	logger_project.info('ProjType Convert: ClassicalSingle > Regular')
	cm2rm_split = dawvert_intent.convert_get_param('cs2r_split', 'none')
	out_dawinfo = dawvert_intent.output_dawinfo
	if (not out_dawinfo.notes_midi) or cm2rm_split=='inst':
		convert_non_midi(convproj_obj, dawvert_intent)
	else:
		convert_midi(convproj_obj, dawvert_intent)
	return 1

def convert_midi_events(convproj_obj, dawvert_intent, startpos, midievents_obj):
	cvpj_timemarkers = convproj_obj.timemarkers
	cvpj_automation = convproj_obj.automation
	for x in midievents_obj:
		curpos = int(x['pos'])+startpos
		if x['type'] == midievents.EVENTID__TIMESIG:
			convproj_obj.timesig_auto.add_point(curpos, [int(x['value']), int(x['value2'])])
			x['used'] = 0
		elif x['type'] == midievents.EVENTID__MARKER:
			marker_data = midievents_obj.markers[x['uhival']]
			timemarker_obj = cvpj_timemarkers.add()
			timemarker_obj.time.set_pos(curpos)
			if marker_data: timemarker_obj.visual.name = marker_data
			x['used'] = 0
		elif x['type'] == midievents.EVENTID__TEMPO:
			bpm = struct.unpack('f', struct.pack('I', x['uhival']))[0]
			cvpj_automation.add_autotick(['main', 'bpm'], 'float', curpos, bpm)
			x['used'] = 0
		#print(startpos, midievents)

def convert_midi(convproj_obj, dawvert_intent):
	cvpj_tracks = convproj_obj.tracks

	markers = {}

	for n, trackid, track_obj in cvpj_tracks.iter_num():
		for pn, pl_midi in enumerate(track_obj.placements.pl_midi):
			startpos = pl_midi.time.get_pos()
			midievents_obj = pl_midi.midievents
			convert_midi_events(convproj_obj, dawvert_intent, startpos, midievents_obj)

	convproj_obj.type = 'r'

def convert_non_midi(convproj_obj, dawvert_intent):
	cvpj_tracks = convproj_obj.tracks
	
	modernize_obj = midi_modernize.midi_modernize(convproj_obj.midi.num_channels)

	for trackid, track_obj in cvpj_tracks.iter():
		modernize_obj.memory__add_count(track_obj.placements.midievents)
		for pl_midi in track_obj.placements.pl_midi:
			modernize_obj.memory__add_count(pl_midi.midievents)

	modernize_obj.memory__alloc()
	modernize_obj.from_cvpj__add_tracks(convproj_obj)

	nonmidi_tracks = []

	for tracknum, trackid, track_obj in cvpj_tracks.iter_num():
		if track_obj.type in ['midi', 'midi_single', 'hybrid']:
			modernize_obj.add_track_data(convproj_obj, tracknum, trackid, track_obj)

	modernize_obj.instchange_from_sysex()
	modernize_obj.memory__sort()
	modernize_obj.do_instruments()
	modernize_obj.do_tempo(convproj_obj)
	modernize_obj.do_timesig(convproj_obj)
	modernize_obj.instrument_visual(convproj_obj)

	modernize_obj.r__output_tracks(convproj_obj)
	modernize_obj.r__do_fx_ctrls(convproj_obj)
	modernize_obj.r__output_groups(convproj_obj)