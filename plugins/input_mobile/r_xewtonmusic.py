# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import xtramath
from objects.convproj import fileref

class input_xewton(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'xewton_music'
	
	def get_name(self):
		return 'Xewton Music Studio'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['']
		in_dict['projtype'] = 'r'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_mobile import xewtonmusic

		project_obj = xewtonmusic.xewtonmusic_file()

		convproj_obj.type = 'r'

		traits_obj = convproj_obj.traits
		traits_obj.fxrack_params = ['vol','pan','pitch']
		traits_obj.auto_types = ['nopl_ticks']
		traits_obj.track_nopl = True

		convproj_obj.set_timings(48)

		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		convproj_obj.params.add('bpm', project_obj.header.tempo, 'float')
		convproj_obj.timesig = [project_obj.header.timesig1, project_obj.header.timesig2]
		

		for tracknim, xe_tr in project_obj.tracks.items():
			idval = 'track'+str(tracknim)
			track_obj = convproj_obj.track__add(idval, 'instrument', 0, False)

			track_obj.params.add('vol', xe_tr.volume, 'float')
			track_obj.params.add('pan', xe_tr.pan, 'float')

			visual_obj = track_obj.visual
			if xe_tr.color is not None: 
				cr = xe_tr.color[2]
				cg = xe_tr.color[1]
				cb = xe_tr.color[0]
				visual_obj.color.set_int([cr, cg, cb])

			cvpj_notelist = track_obj.placements.notelist

			tracknotes = xe_tr.notes.notes
			for n in tracknotes:
				cvpj_notelist.add_r(int(n.pos), int(n.dur), n.key-60, n.vol/127, None)

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')