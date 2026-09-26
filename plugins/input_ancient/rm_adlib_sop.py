# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

endtxt = ['', '4OP', '2OP']
panvals = [1, 0, -1]
maincolor = [0.39, 0.16, 0.78]

class input_sop(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'adlib_sop'
	
	def get_name(self):
		return 'Sopepos Note Sequencer'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['chip:fm:opl2','chip:fm:opl3']
		in_dict['projtype'] = 'rm'

	def get_configdef(self, configdef):
		cfgpart = configdef.add_float('panlvl', 1.0, 'Pan Amount')
		cfgpart.set_range(-1, 1)
		configdef.set_group('visual', 'Visual')
		cfgpart = configdef.add_bool('endtxt_on', True, 'Add OP Type to Track name')

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_adlib import sop as proj_adlib_sop
		
		project_obj = proj_adlib_sop.adlib_sop_project()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		# ---------- convproj params ----------
		endtxt_on = dawvert_intent.input_get_param('endtxt_on', True)
		panlvl = dawvert_intent.input_get_param('panlvl', 1.0)

		# ---------- convproj objects ----------
		cvpj_tracks = convproj_obj.tracks
		cvpj_insts = convproj_obj.instruments
		cvpj_automation = convproj_obj.automation
		
		# ---------- convproj init ----------
		convproj_obj.set_timings(project_obj.tickBeat)
		convproj_obj.type = 'rm'
		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')

		traits_obj = convproj_obj.traits
		traits_obj.auto_types = ['nopl_ticks']
		traits_obj.track_nopl = True

		# ---------- metadata ----------
		convproj_obj.metadata.name = project_obj.title
		convproj_obj.metadata.comment_text = project_obj.comment

		# ---------- transport ----------
		convproj_obj.params.add('bpm', project_obj.basicTempo, 'float')
		convproj_obj.timesig = [project_obj.beatMeasure, 4]

		# ---------- insts ----------
		inst_comments = []

		for instnum, sopinst in enumerate(project_obj.insts):
			insttype, opli = sopinst
			if insttype!=12:
				cvpj_instname = str(instnum)
				inst_obj = cvpj_insts.add(cvpj_instname)
				inst_obj.plugslots.set_synth(cvpj_instname)
				outname = opli.name_long if opli.name_long else opli.name
				if outname: inst_obj.visual.name = outname
				inst_obj.visual.color.set_float(maincolor)
				inst_obj.is_drum = opli.perc_type!=0
				opli.to_cvpj(convproj_obj, cvpj_instname)
			else:
				inst_comments.append(opli.name_long)

		inst_comments = '\n'.join(inst_comments).lstrip('\n').rstrip('\n')
		if convproj_obj.metadata.comment_text:
			convproj_obj.metadata.comment_text += '\n'

		convproj_obj.metadata.comment_text += inst_comments

		# ---------- tracks ----------
		for tracknum, soptrack in enumerate(project_obj.tracks):
			cvpj_trackid = str(tracknum)
			track_obj = cvpj_tracks.add(cvpj_trackid, 'instruments', 0, False)
			track_obj.visual.name = '#'+str(cvpj_trackid)
			track_obj.visual.color.set_float(maincolor)

			if endtxt_on:
				trackname_endtext = endtxt[soptrack.chanmode]
				track_obj.visual.name += ' '+str()+trackname_endtext

			cvpj_notelist = track_obj.placements.notelist
			
			curtick = 0
			instpos = []
			for event in soptrack.events:
				curtick += event[0]
				if event[1] == 'VOL': 
					cvpj_automation.add_autotick(['track', cvpj_trackid, 'vol'], 'float', curtick, event[2]/127)

				elif event[1] == 'PAN': 
					cvpj_automation.add_autotick(['track', cvpj_trackid, 'pan'], 'float', curtick, panvals[event[2]%3]*panlvl)

				elif event[1] == 'INST': 
					instpos.append([curtick, str(event[2])])

				elif event[1] == 'NOTE': 
					cvpj_notelist.add_m(None, curtick, event[3], event[2]-60, 1, None)

				#else:
				#	print(event)

			cvpj_notelist.add_instpos(instpos)

		# ---------- control track ----------
		for event in project_obj.controltrack:
			curtick += event[0]
			if event[1] == 'TEMPO': 
				cvpj_automation.add_autotick(['main', 'bpm'], 'float', curtick, event[2])
			if event[1] == 'GVOL': 
				cvpj_automation.add_autotick(['master', 'vol'], 'float', curtick, event[2]/127)
