# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def process(convproj_obj, in__midi_notes, out__midi_notes, out_type, dawvert_intent):

	if convproj_obj.type == 'r': 

		if in__midi_notes == True and out__midi_notes == False and out_type not in ['cm', 'cs']:
			for cvpj_trackid, track_obj in convproj_obj.track__iter(): 
				for midpl in track_obj.placements.pl_midi:
					midievents_obj = midpl.midievents
					midievents_obj.add_note_durs()
					notes_pl = track_obj.placements.pl_notes.make_base_from_midi(midpl)
					notelist_obj = notes_pl.notelist
					notelist_obj.time_ppq = midievents_obj.ppq
					auto_data_cc = {}
					auto_data_pitch = {}
					auto_data_pressure = {}
					auto_data_program = {}

					for x in midievents_obj.iter_events():
						etype = x[1]
						if etype == 'NOTE_DUR':
							channel = int(x[2])
							notelist_obj.add_r(int(x['pos']), int(x['val3']), int(x['val1'])-60, int(x['val2'])/127, None)
							notelist_obj.last_add_vol_off(float(x['off_vel'])/127)
							notelist_obj.last_add_channel(channel)
						elif etype == 'CONTROL':
							if x['val1'] not in auto_data_cc: auto_data_cc[x['val1']] = {}
							auto_data_cc[x['val1']][x['pos']] = x['val2']
						elif etype == 'PRESSURE':
							auto_data_pressure[x['pos']] = x['val1']
						elif etype == 'PITCH':
							auto_data_pitch[x['pos']] = x['val1']
						elif etype == 'PROGRAM':
							auto_data_program[x['pos']] = x['val1']

					for ccnum, data in auto_data_cc.items():
						autoticks = notes_pl.add_autoticks_ppq('midi_cc_'+str(int(ccnum)), midievents_obj.ppq)
						for pos, val in data.items(): autoticks.add_point(int(pos), int(val))

					if auto_data_pitch:
						autoticks = notes_pl.add_autoticks_ppq('midi_pitch', midievents_obj.ppq)
						for pos, val in auto_data_pitch.items(): autoticks.add_point(int(pos), int(val))

					if auto_data_pressure:
						autoticks = notes_pl.add_autoticks_ppq('midi_pressure', midievents_obj.ppq)
						for pos, val in auto_data_pressure.items(): autoticks.add_point(int(pos), int(val))

					if auto_data_program:
						autoticks = notes_pl.add_autoticks_ppq('midi_program', midievents_obj.ppq)
						for pos, val in auto_data_program.items(): autoticks.add_point(int(pos), int(val))

					notes_pl.change_timings_internal(convproj_obj.time_ppq)

				track_obj.placements.pl_midi.data = []

			return True

		elif in__midi_notes == False and out__midi_notes == True and out_type not in ['rm']:
			for cvpj_trackid, track_obj in convproj_obj.track__iter(): 

				pll = [track_obj.placements]+[x[1].placements for x in track_obj.lanes.items()]

				for tpl in pll:
					for notespl_obj in tpl.pl_notes:
						notespl_obj.notelist.mod_limit(-60, 67)
						notespl_obj.notelist.change_timings(960)
						midi_pl = tpl.pl_midi.make_base_from_notes(notespl_obj)
						midievents_obj = midi_pl.midievents
						midievents_obj.ppq = 960
						for t_pos, t_dur, t_keys, t_vol, t_vol_off, t_chan, t_inst, t_extra, t_autopack in notespl_obj.notelist.iter_midispec():
							for t_key in t_keys:
								midievents_obj.add_note_dur_off_vel(t_pos, t_chan, t_key+60, min(127, t_vol*127), t_dur, min(127, t_vol_off*127))
						for autoid, autodata in notespl_obj.auto_ticks.items():
							autodata.change_timings(960)
							if autoid.startswith('midi_cc_'):
								try:
									ccnum = int(autoid[8:])
									for p, v in autodata: midievents_obj.add_control(p, 0, ccnum, v)
								except: pass
							if autoid == 'midi_pitch':
								for p, v in autodata: midievents_obj.add_pitch(p, 0, v)
							if autoid == 'midi_pressure':
								for p, v in autodata: midievents_obj.add_chan_pressure(p, 0, v)
							if autoid == 'midi_program':
								for p, v in autodata: midievents_obj.add_program(p, 0, v)
						midievents_obj.has_duration = True
						midievents_obj.del_note_durs()
					tpl.pl_notes.data = []
			return True

		else: 
			return False

	else: return False
	