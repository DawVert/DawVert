# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import globalstore
from io import BytesIO
import json
import plugins
import struct
from objects.exceptions import ProjectFileParserException

patletters = ['A','B','C','D']
patids = []
for x in patletters:
	for v in range(8):
		patids.append(x+str(v+1))

class input_petaporon(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'acidmach2'
	
	def get_name(self):
		return 'Acid Machine 2'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['native:acidmach2']
		in_dict['projtype'] = 'ri'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_drummach import acid_machine_2 as proj_acid_machine_2

		project_obj = proj_acid_machine_2.acid_amx_project()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		globalstore.datapack.load('acid_machine_2', './data/datapack/app/acid_machine_2.xml')

		convproj_obj.type = 'ri'
		convproj_obj.set_timings(4)

		traits_obj = convproj_obj.traits
		traits_obj.track_nopl = True

		proj_song = project_obj.song

		if 'tempo' in proj_song.pglobal:
			convproj_obj.params.add('bpm', proj_song.pglobal['tempo'], 'float')

		idinstnum_assoc = []
		tracks = {}
		for instid, instdata in proj_song.instruments.items():
			machineName = instdata.machineName
			track_obj = convproj_obj.track__add(instid, 'instrument', 1, True)
			track_obj.visual.from_datapack('acid_machine_2', 'plugin_inst', machineName, True)
			plugin_obj = convproj_obj.plugin__add(instid, 'native', 'acidmach2', machineName)
			plugin_obj.visual.from_datapack('acid_machine_2', 'plugin_inst', machineName, True)
			track_obj.plugslots.set_synth(instid)
			tracks[instid] = track_obj
			idinstnum_assoc.append(instid)

		for instid, patterns in proj_song.patterns.items():
			track_obj = tracks[instid]
			for patnum, pattern in patterns.items():
				nle_obj = track_obj.notelistindex__add(str(patnum))
				nle_obj.visual.name = patids[patnum] if patnum<len(patids) else 'NaN'
				cvpj_notelist = nle_obj.notelist
				for _, notes in pattern.pattern.items(): 
					for note in notes:
						if note.val is not None:
							key = note.val
							if note.octUp: key += 12
							if note.octDown: key -= 12
							cvpj_notelist.add_r(note.start, note.duration, key-60, note.veloc/127, None)

		for instid, patternList in proj_song.patternList.items():
			track_obj = tracks[instid]
			for pos, num in patternList.items():
				placement_obj = track_obj.placements.add_notes_indexed()
				time_obj = placement_obj.time
				time_obj.set_posdur(int(pos)*16, 16)
				placement_obj.fromindex = str(num)

		for instnum, fxUnits in proj_song.fxUnits.items():
			instid = idinstnum_assoc[instnum-1]
			track_obj = tracks[instid]

			for fxnum in range(2):
				slotnum = fxnum+1
				if slotnum in fxUnits:
					fxtype, fxdata = fxUnits[slotnum]
					plugin_obj, fxid = convproj_obj.plugin__add__genid('native', 'acidmach2', 'fx_'+str(fxtype))
					plugin_obj.role = 'fx'
					plugin_obj.visual.from_datapack('acid_machine_2', 'plugin_fx', str(fxtype), True)
					track_obj.plugin_autoplace(plugin_obj, fxid)

					if 'controls' in fxdata:
						fldso = globalstore.datapack.get_obj('acid_machine_2', 'plugin_fx', str(fxtype))
						for num, control in enumerate(fxdata['controls']):
							dset_param = fldso.params.get(str(num))
							if dset_param: plugin_obj.dset_param__add(str(num), control, dset_param)
							else: plugin_obj.params.add(str(num), control, 'float')

		for instnum, mixdata in enumerate(proj_song.mixer):
			if instnum<len(idinstnum_assoc):
				instid = idinstnum_assoc[instnum]
				track_obj = tracks[instid]
				track_obj.params.add('vol', mixdata[0]/127, 'float')