# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json	
import logging
import numpy as np
import struct

logger_project = logging.getLogger('project')

class track_chansplit_data:
	def __init__(self, newtracks_data, cvpj_tracks):
		self.newtracks_data = newtracks_data
		self.cvpj_tracks = cvpj_tracks

	def get_track(self, trackid, chan, orgtrack):
		newtrackid = 'cm2cs_%s_%i' % (trackid, chan)
		if newtrackid not in self.newtracks_data: 
			track_obj = self.cvpj_tracks.add(newtrackid, 'midi_single', 1, False)
			track_obj.midi.out_enabled = True
			track_obj.midi.out_chanport.chan = min(0, chan)
			track_obj.visual = orgtrack.visual.copy()
			channeltxt = ('Channel #'+str(chan+1)) if chan>-1 else ('Automation')
			if not track_obj.visual.name: track_obj.visual.name = channeltxt
			else: track_obj.visual.name += ' (%s)' % channeltxt
			self.newtracks_data[newtrackid] = track_obj
		return self.newtracks_data[newtrackid]

def convert(convproj_obj, dawvert_intent):
	logger_project.info('ProjType Convert: ClassicalMultiple > ClassicalSingle')
	cvpj_tracks = convproj_obj.tracks

	old_order = cvpj_tracks.order.copy()
	tracks_data = cvpj_tracks.data

	newtracks_data = {}
	chansplit_data = track_chansplit_data(newtracks_data, cvpj_tracks)

	for trackid in old_order:
		if trackid in tracks_data:
			track_obj = tracks_data[trackid]

			newtracks_data = {}


			#nopl
			midievents_obj = track_obj.placements.midievents
			channums = midievents_obj.split_midi_chans()
			for chan, data in channums.items():
				sep_track_obj = chansplit_data.get_track(trackid, chan, track_obj)
				sep_track_obj.placements.midievents = midievents_obj.copy_custom_notes(data)

			#pl
			for pl_midi in track_obj.placements.pl_midi:
				midievents_obj = pl_midi.midievents
				channums = midievents_obj.split_midi_chans()
				for chan, data in channums.items():
					sep_track_obj = chansplit_data.get_track(trackid, chan, track_obj)
					sep_pl_obj = sep_track_obj.placements.add_midi()
					sep_pl_obj.time = pl_midi.time
					sep_pl_obj.midievents = midievents_obj.copy_custom_notes(data)
					#print(len(sep_pl_obj.midievents))
				midievents_obj.clear()

			del tracks_data[trackid]
			cvpj_tracks.order.remove(trackid)

	convproj_obj.type = 'cs'
	return 1