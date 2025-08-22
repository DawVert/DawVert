# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def process(convproj_obj, in__notepl_pitch, out__notepl_pitch, out_type, dawvert_intent):

	if convproj_obj.type == 'r': 
		if in__notepl_pitch == True and out__notepl_pitch == False:
			for cvpj_trackid, track_obj in convproj_obj.track__iter(): 
				for midi_pl in track_obj.placements.pl_midi:
					if midi_pl.pitch:
						midievents_obj = midi_pl.midievents
						midievents_obj.mod_transpose(midi_pl.pitch)
						midi_pl.pitch = 0
				for notes_pl in track_obj.placements.pl_notes:
					if notes_pl.pitch:
						notelist_obj = notes_pl.notelist
						notelist_obj.mod_transpose(notes_pl.pitch)
						notes_pl.pitch = 0
			return True

	else: return False
	