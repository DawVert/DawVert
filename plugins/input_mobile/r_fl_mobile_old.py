# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import xtramath
from objects.convproj import fileref
from objects import globalstore
import os

INST_ENABLED = 1

class input_fl_mobile_old(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'fl_mobile_old'
	
	def get_name(self):
		return 'FL Studio Mobile 1.1 (2011)'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['']
		in_dict['projtype'] = 'r'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_mobile import fl_mobile_xew
		from objects import audio_data

		project_obj = fl_mobile_xew.oldflm_song()

		convproj_obj.type = 'r'

		traits_obj = convproj_obj.traits
		traits_obj.track_nopl = True

		convproj_obj.set_timings(48)

		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		convproj_obj.params.add('bpm', project_obj.bpm, 'float')
		
		instplugs = {}

		for xe_tr in project_obj.tracks:
			idval = 'track'+str(xe_tr.numid)
			track_obj = convproj_obj.track__add(idval, 'instrument', 0, False)

			track_obj.params.add('vol', xe_tr.vol, 'float')
			track_obj.params.add('pan', xe_tr.pan, 'float')

			cvpj_notelist = track_obj.placements.notelist
			tracknotes = xe_tr.notes

			for n in tracknotes:
				cvpj_notelist.add_r(int(n.pos), int(n.dur), n.key-60, n.vol/127, None)

				noteauto = n.auto
				if noteauto:
					pp = noteauto[0][0]
					for p, v in noteauto:
						val = ((v-8192)/8192)*24
						if (p-pp)>5:
							cvpj_notelist.last_add_auto_instant('pitch', p, val)
						else:
							cvpj_notelist.last_add_auto('pitch', p, val)
						pp = p
						if n.dur<p: break

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')