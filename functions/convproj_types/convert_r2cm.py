# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import copy
import logging

logger_project = logging.getLogger('project')

channelcount = -1
def get_unused_chan():
	global channelcount
	channelcount += 1
	if channelcount == 9: channelcount += 1
	if channelcount == 16: channelcount = 0
	return channelcount

def convert(convproj_obj, dawvert_intent):
	logger_project.info('ProjType Convert: Regular > ClassicalMultiple')

	cvpj_tracks = convproj_obj.tracks

	max_ppq = cvpj_tracks.get_midi_max_ppq()

	if max_ppq:
		convproj_obj.change_timings(max_ppq)

		for trackid, track_obj in cvpj_tracks.iter():
			if track_obj.type == 'instrument':
				trackpl = track_obj.placements
				midievents_obj = trackpl.midievents
				midievents_obj.has_duration = True

				if track_obj.midi.out_enabled:
					channel = track_obj.midi.out_chanport.chan
				else:
					channel = get_unused_chan()

				trackpl.notelist.to_midievents(midievents_obj, channel)
				track_obj.type = 'midi'

	convproj_obj.type = 'cm'
	return 1