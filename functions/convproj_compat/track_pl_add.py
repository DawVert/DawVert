# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.convproj import placements
from objects import notelist_splitter

def process_pl(timesigblocks_obj, convproj_obj, npsplit, splitter_mode, splitter_start):
	cvpj_tracks = convproj_obj.tracks

	match splitter_mode:
		case 'num': timesigblocks_obj.create_points_cut(convproj_obj, 'timesig_num', splitter_start)
		case 'num2': timesigblocks_obj.create_points_cut(convproj_obj, 'timesig_num_x2', splitter_start)
		case 'timesig': timesigblocks_obj.create_points_cut(convproj_obj, 'timesig', splitter_start)

		case 'blocks_num': timesigblocks_obj.create_points_cut(convproj_obj, 'timesig_num', splitter_start)
		case 'blocks_num2': timesigblocks_obj.create_points_cut(convproj_obj, 'timesig_num_x2', splitter_start)
		case 'blocks_timesig': timesigblocks_obj.create_points_cut(convproj_obj, 'timesig', splitter_start)

	for cvpj_trackid, track_obj in cvpj_tracks.iter(): npsplit.add_pldata(track_obj.placements)
	npsplit.process(splitter_mode)

	if splitter_mode in ['blocks_num','blocks_num2','blocks_timesig']: npsplit.to_blocks()

	npsplit.process_post(splitter_mode)

def process(convproj_obj, in__track_nopl, out__track_nopl, out_type, dawvert_intent):
	cvpj_tracks = convproj_obj.tracks

	if in__track_nopl == True and out__track_nopl == False:

		splitter_mode = dawvert_intent.splitter_mode if dawvert_intent else 'timesig'
		splitter_start = dawvert_intent.splitter_detect_start if dawvert_intent else 0

		if convproj_obj.type in ['cm', 'cs']: 
			if ('do_singlenotelistcut' in convproj_obj.do_actions) or splitter_mode=='none':
				timesigblocks_obj = notelist_splitter.timesigblocks()
				npsplit = notelist_splitter.cvpj_midievents_splitter(timesigblocks_obj, convproj_obj.time_ppq)
				process_pl(timesigblocks_obj, convproj_obj, npsplit, splitter_mode, splitter_start)
				return True
			else:
				for cvpj_trackid, track_obj in cvpj_tracks.iter(): 
					midievents = track_obj.placements.midievents
					if len(midievents):
						placement_obj = track_obj.placements.add_midi()
						placement_obj.midievents = midievents.__copy__()
						placement_obj.time.set_dur(int(midievents.get_dur_all()))
						midievents.clear()
				return True

		if convproj_obj.type in (['r'] if 'r' in out_type else ['r', 'rm']): 
			if ('do_singlenotelistcut' in convproj_obj.do_actions) or splitter_mode=='none':
				timesigblocks_obj = notelist_splitter.timesigblocks()
				npsplit = notelist_splitter.cvpj_notelist_splitter(timesigblocks_obj, convproj_obj.time_ppq)
				process_pl(timesigblocks_obj, convproj_obj, npsplit, splitter_mode, splitter_start)
				convproj_obj.calc_pl_tempo()
				return True
			else:
				for cvpj_trackid, track_obj in cvpj_tracks.iter(): 
					if track_obj.placements.notelist.count():
						placement_obj = track_obj.placements.add_notes()
						placement_obj.notelist = track_obj.placements.notelist.__copy__()
						placement_obj.time.set_dur(int(track_obj.placements.notelist.get_dur()))
						track_obj.placements.notelist.clear()
				convproj_obj.calc_pl_tempo()
				return True
		else: 
			return False

	else: return False
	