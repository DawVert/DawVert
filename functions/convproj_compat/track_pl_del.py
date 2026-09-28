# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.convproj import placements
from objects import notelist_splitter

def process(convproj_obj, in__track_nopl, out__track_nopl, out_type, dawvert_intent):
	cvpj_tracks = convproj_obj.tracks

	if in__track_nopl == False and out__track_nopl == True:

		if convproj_obj.type in ['r']: 
			max_ppq = cvpj_tracks.get_midi_max_ppq()

			if max_ppq:
				for cvpj_trackid, track_obj in cvpj_tracks.iter():
					trackpl = track_obj.placements
					trackpl.midievents.change_ppq(max_ppq)
					trackpl.midievents.add_note_durs()
					for x in trackpl.pl_midi:
						pl_midievents = x.midievents
						pl_midievents.change_ppq(max_ppq)
						pl_midievents.add_note_durs()
						ppqcalc = track_obj.time_ppq/max_ppq
						pl_pos = (x.time.get_pos()/ppqcalc).__floor__()
						pl_dur = (x.time.get_dur()/ppqcalc).__ceil__()
						trackpl.midievents.merge(pl_midievents, pl_pos, pl_dur, 0)

			for cvpj_trackid, track_obj in cvpj_tracks.iter():
				trackpl = track_obj.placements
				for x in trackpl.pl_notes:
					trackpl.notelist.merge(x.notelist, x.time.get_pos())
				trackpl.pl_notes.clear()
			convproj_obj.calc_pl_tempo()
			return True

		elif convproj_obj.type in ['cs', 'cm']: 
			for cvpj_trackid, track_obj in cvpj_tracks.iter():
				trackpl = track_obj.placements
				trackpl.midievents.change_ppq(convproj_obj.time_ppq)

				for midipl_obj in trackpl.pl_midi:

					scale = convproj_obj.time_ppq/midipl_obj.midievents.ppq

					pos = int(midipl_obj.time.get_pos())
					dur = int(midipl_obj.time.get_dur())

					trackpl.midievents.merge(midipl_obj.midievents, pos, dur, 0)
					midipl_obj.midievents.change_ppq(convproj_obj.time_ppq)

				trackpl.pl_notes.clear()
				trackpl.pl_midi.clear()

			convproj_obj.calc_pl_tempo()
			return True

	return False
	