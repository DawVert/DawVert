# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json

def conv_color(b_color):
	color = b_color.to_bytes(4, "little")
	return [color[0],color[1],color[2]]

class input_hypnospace_hsm(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'hypnospace_hsm'
	
	def get_name(self):
		return 'Hypnospace HSM'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['projtype'] = 'ms'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_vgm import hypnospace_hsm as proj_hypnospace_hsm
		from objects.convproj import fileref

		convproj_obj.type = 'ms'
		convproj_obj.set_timings(4)

		project_obj = proj_hypnospace_hsm.hsm_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		if project_obj.title: convproj_obj.metadata.name = project_obj.title
		if project_obj.artist: convproj_obj.metadata.author = project_obj.artist

		for tracknum in range(5):
			track_obj = convproj_obj.track__add('track_'+str(tracknum), 'instruments', 1, False)
			track_obj.visual.name = 'Track #%s' % str(tracknum+1)

		for num, sample in enumerate(project_obj.samples):
			inst_obj = convproj_obj.instrument__add('inst_'+str(num))
			inst_obj.visual.name = sample.path.split('\\')[-1] if sample.path else 'Unused #%s' % str(num+1)

		for patnum, pattern_obj in enumerate(project_obj.patterns):
			something, steps, highlight, color = pattern_obj.header
			patnum_id = 'pat_'+str(patnum+1)
			if steps:
				scene_obj = convproj_obj.scene__add(patnum_id)
				scene_obj.visual.color.set_int( conv_color(color) )

				for n, x in enumerate(pattern_obj.notes):
					trscene_obj = convproj_obj.track__add_scene('track_'+str(n), patnum_id, 'main')
					placement_obj = trscene_obj.add_notes()
					time_obj = placement_obj.time
					time_obj.set_posdur(0, steps)
					cvpj_notelist = placement_obj.notelist
					for p, note in enumerate(x):
						if note[0]:
							cvpj_notelist.add_m('inst_'+str(note[0]-1), p, 1, note[1]-36, note[3]/100, None)


		curpos = 0
		for patnum in project_obj.patternorder:
			patdur = project_obj.patterns[patnum-1].header[1]
			if patdur:
				scenepl_obj = convproj_obj.scene__add_pl()
				scenepl_obj.position = curpos
				scenepl_obj.duration = patdur
				scenepl_obj.id = 'pat_'+str(patnum)
			curpos += patdur