# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def process(convproj_obj, in_compat, out_compat, out_type, dawvert_intent):
	if in_compat and not out_compat:
		bpm = convproj_obj.params.get('bpm', 120).value
		ppq = convproj_obj.time_ppq

		convproj_obj.arranger.change_seconds(convproj_obj.timemarkers.is_seconds, bpm, ppq)
		convproj_obj.timemarkers.data += convproj_obj.arranger.data
		convproj_obj.arranger.data = []
		convproj_obj.traits.track_arranger = False