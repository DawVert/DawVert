# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging
import numpy as np
import struct
from objects.convproj import midievents

logger_project = logging.getLogger('project')

def convert(convproj_obj, dawvert_intent):
	import objects.midi_modernize.midi_modernize as midi_modernize

	cm2rm_split = dawvert_intent.convert_get_param('cm2rm_split', 'none')

	out_dawinfo = dawvert_intent.output_dawinfo

	if (not out_dawinfo.notes_midi) or cm2rm_split=='inst':
		convert_non_midi(convproj_obj, dawvert_intent)
	else:
		convert_midi(convproj_obj, dawvert_intent)

def convert_midi_events(convproj_obj, dawvert_intent, startpos, midievents_obj):
	cvpj_timemarkers = convproj_obj.timemarkers
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
		#print(startpos, midievents)

def convert_midi(convproj_obj, dawvert_intent):
	cvpj_tracks = convproj_obj.tracks

	markers = {}

	for n, trackid, track_obj in cvpj_tracks.iter_num():
		for pn, pl_midi in enumerate(track_obj.placements.pl_midi):
			startpos = pl_midi.time.get_pos()
			midievents_obj = pl_midi.midievents
			convert_midi_events(convproj_obj, dawvert_intent, startpos, midievents_obj)

	convproj_obj.type = 'rm'

def convert_non_midi(convproj_obj, dawvert_intent):
	cvpj_tracks = convproj_obj.tracks
	
	logger_project.info('ProjType Convert: ClassicalMultiple > RegularMultiple')

	modernize_obj = midi_modernize.midi_modernize(convproj_obj.midi.num_channels)

	for trackid, track_obj in cvpj_tracks.iter():
		modernize_obj.memory__add_count(track_obj.placements.midievents)
		for pl_midi in track_obj.placements.pl_midi:
			modernize_obj.memory__add_count(pl_midi.midievents)

	modernize_obj.memory__alloc()
	modernize_obj.from_cvpj__add_tracks(convproj_obj)

	nonmidi_tracks = []

	for n, trackid, track_obj in cvpj_tracks.iter_num():

		if track_obj.type in ['midi', 'hybrid']:
			logger_project.info('cm2rm: Track '+trackid)
			modernize_obj.init_patchchan(track_obj.midi)

			midievents_obj = track_obj.placements.midievents
			midievents_obj.add_note_durs()

			modernize_obj.add_track_visual(n, track_obj.visual)

			portnum = midievents_obj.port
			usedchans = list(midievents_obj.get_channums())

			for pn, pl_midi in enumerate(track_obj.placements.pl_midi):
				for x in pl_midi.midievents.get_channums():
					if x not in usedchans: usedchans.append(x)
				startpos = pl_midi.time.get_pos()
				durpos = pl_midi.time.get_dur()
				offset = pl_midi.time.get_offset()

				modernize_obj.do_notes(convproj_obj, pl_midi.midievents, startpos, durpos, offset, pn+1, portnum, n)

			modernize_obj.visual_chan(n, portnum, usedchans)
			modernize_obj.do_notes(convproj_obj, midievents_obj, 0, -1, 0, 0, portnum, n)

	logger_project.info('cm2rm: SysEX')
	modernize_obj.instchange_from_sysex()

	modernize_obj.sort()

	logger_project.info('cm2rm: Instruments')
	modernize_obj.do_instruments()

	logger_project.info('cm2rm: Controls and FX')
	modernize_obj.do_fx_ctrls(convproj_obj)

	logger_project.info('cm2rm: Automation')
	modernize_obj.do_automation(convproj_obj)

	logger_project.info('cm2rm: Pitch Automation')
	modernize_obj.do_pitch_automation(convproj_obj)

	logger_project.info('cm2rm: Tempo')
	modernize_obj.do_tempo(convproj_obj)

	logger_project.info('cm2rm: TimeSig')
	modernize_obj.do_timesig(convproj_obj)

	logger_project.info('cm2rm: Instruments')
	modernize_obj.to_cvpj_inst_visual(convproj_obj)

	logger_project.info('cm2rm: Out Tracks')
	modernize_obj.output_tracks(convproj_obj)

	if convproj_obj.transport.loop_start and not convproj_obj.transport.loop_end:
		convproj_obj.transport.loop_end = convproj_obj.get_dur()

	convproj_obj.type = 'rm'
