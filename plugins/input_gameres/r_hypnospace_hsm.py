# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
from objects import globalstore
from objects import colors

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

		traits_obj = convproj_obj.traits
		traits_obj.placement_cut = True

		project_obj = proj_hypnospace_hsm.hsm_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		globalstore.datapack.load('hypnospace_hsm', './data/datapack/app/hypnospace_hsm.dset')
		colordata = colors.colorset.from_datapack('hypnospace_hsm', 'sample', 'main')

		fileref.cvpj_fileref_global.add_prefix_extend('dawvert_external_data', 'hypnospace_hsm', ['hypnospace_hsm'])

		if project_obj.title: convproj_obj.metadata.name = project_obj.title
		if project_obj.artist: convproj_obj.metadata.author = project_obj.artist

		for tracknum in range(5):
			track_obj = convproj_obj.track__add('track_'+str(tracknum), 'instruments', 1, False)
			track_obj.visual.name = 'Track #%s' % str(tracknum+1)

		for num, sample in enumerate(project_obj.samples):
			instid = 'inst_'+str(num)
			inst_obj = convproj_obj.instrument__add(instid)
			inst_obj.visual.name = sample.path.split('\\')[-1] if sample.path else 'Unused #%s' % str(num+1)
			inst_obj.visual.color.set_int(colordata.getcolornum(num))
			inst_obj.visual.color.fx_allowed = ['saturate']
			if sample.path:
				sampleref_obj = convproj_obj.sampleref__add__prefix(sample.path, 'hypnospace_hsm', sample.path+'.ogg')
				sampleref_obj.fileref.resolve_prefix()
				plugin_obj, samplepart_obj = convproj_obj.plugin__addspec__sampler__s_obj(instid, sampleref_obj, sample.path)
				inst_obj.plugslots.set_synth(instid)

			#a_predelay, a_attack, a_hold, a_decay, a_sustain, a_release, a_amount
			plugin_obj.env_asdr_add('vol', 0, 0, 0, sample.decay/4, 1, 0, 1)

		convproj_obj.params.add('bpm', project_obj.patterns[0].header[0], 'float')

		firstpat = project_obj.patterns[0]

		for patnum, pattern_obj in enumerate(project_obj.patterns):
			tempo, steps, highlight, color = pattern_obj.header

			patnum_id = 'pat_'+str(patnum+1)
			if steps:
				scene_obj = convproj_obj.scene__add(patnum_id)
				scene_obj.visual.color.set_int( conv_color(color) )

				for n, x in enumerate(pattern_obj.notes):
					if not all([x[0]==0 for x in x]):
						trscene_obj = convproj_obj.track__add_scene('track_'+str(n), patnum_id, 'main')
						placement_obj = trscene_obj.add_notes()
						time_obj = placement_obj.time
						time_obj.set_posdur(0, steps)
						cvpj_notelist = placement_obj.notelist
						note_active = False
						for p, note in enumerate(x):
							if note[0] and note[1]<100:
								cvpj_notelist.add_m('inst_'+str(note[0]-1), p, 0, note[1]-24, note[3]/100, None)
								note_active = True

							if note[1]>99:
								note_active = False

							if note_active:
								cvpj_notelist.last_extend(1)

		curpos = 0
		for patnum in project_obj.patternorder:
			patdur = project_obj.patterns[patnum-1].header[1]
			if patdur:
				scenepl_obj = convproj_obj.scene__add_pl()
				scenepl_obj.position = curpos
				scenepl_obj.duration = patdur
				scenepl_obj.id = 'pat_'+str(patnum)
			curpos += patdur