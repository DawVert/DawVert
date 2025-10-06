# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.exceptions import ProjectFileParserException
from objects.inst_params import fm_opl
from external.easybinrw import easybinrw

def decode_events(ebrw_readstr):
	sop_eventdata = []
	track_numEvents = ebrw_readstr.int_u16()
	track_dataSize = ebrw_readstr.int_u32()
	for _ in range(track_numEvents):
		sop_event_pos = ebrw_readstr.int_u16()
		sop_event_code = ebrw_readstr.int_u8()
		if sop_event_code == 1: sop_eventdata.append([sop_event_pos, 'SPECIAL', ebrw_readstr.int_u8()])
		elif sop_event_code == 2: 
			note_pitch = ebrw_readstr.int_u8()
			note_length = ebrw_readstr.int_u16()
			sop_eventdata.append([sop_event_pos, 'NOTE', note_pitch, note_length])
		elif sop_event_code == 3: sop_eventdata.append([sop_event_pos, 'TEMPO', ebrw_readstr.int_u8()])
		elif sop_event_code == 4: sop_eventdata.append([sop_event_pos, 'VOL', ebrw_readstr.int_u8()])
		elif sop_event_code == 5: sop_eventdata.append([sop_event_pos, 'PITCH', ebrw_readstr.int_u8()])
		elif sop_event_code == 6: sop_eventdata.append([sop_event_pos, 'INST', ebrw_readstr.int_u8()])
		elif sop_event_code == 7: sop_eventdata.append([sop_event_pos, 'PAN', ebrw_readstr.int_u8()])
		elif sop_event_code == 8: sop_eventdata.append([sop_event_pos, 'GVOL', ebrw_readstr.int_u8()])
		else:
			print('[error] unknown event code:', sop_event_code)
			exit()
	return sop_eventdata

class adlib_sop_track:
	def __init__(self):
		self.chanmode = 0
		self.events = []

class adlib_sop_project:
	def __init__(self):
		self.tracks = []
		self.insts = []
		self.majorVersion = 0
		self.minorVersion = 1
		self.fileName = ''
		self.title = ''
		self.opl_rhythm = 1
		self.tickBeat = 8
		self.beatMeasure = 4
		self.basicTempo = 120
		self.comment = ''
		self.controltrack = []

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)

		try: 
			ebrw_readstr.magic_check(b'sopepos')
		except ValueError as t:
			raise ProjectFileParserException('adlib_sop: '+str(t))

		self.majorVersion = ebrw_readstr.int_u8()
		self.minorVersion = ebrw_readstr.int_u8()
		ebrw_readstr.skip(1)
		self.fileName = ebrw_readstr.string(13)
		self.title = ebrw_readstr.string(31)

		self.opl_rhythm = ebrw_readstr.int_u8()
		ebrw_readstr.skip(1)
		self.tickBeat = ebrw_readstr.int_u8()
		ebrw_readstr.skip(1)
		self.beatMeasure = ebrw_readstr.int_u8()
		self.basicTempo = ebrw_readstr.int_u8()

		self.comment = ebrw_readstr.string(13)
		num_tracks = ebrw_readstr.int_u8()
		num_insts = ebrw_readstr.int_u8()
		ebrw_readstr.skip(1)
		self.tracks = [adlib_sop_track() for x in range(num_tracks)]

		for n in range(num_tracks): self.tracks[n].chanmode = ebrw_readstr.int_u8()

		for _ in range(num_insts):
			insttype = ebrw_readstr.int_u8()
			opli = fm_opl.opl_inst()
			opli.name = ebrw_readstr.string(8, encoding="latin-1")
			opli.name_long = ebrw_readstr.string(19, encoding="latin-1")
			if insttype in [0]: 
				opli.ops[0].avekf(ebrw_readstr.int_u8())
				opli.ops[0].ksl_lvl(ebrw_readstr.int_u8())
				opli.ops[0].att_dec(ebrw_readstr.int_u8())
				opli.ops[0].sus_rel(ebrw_readstr.int_u8())
				opli.ops[0].waveform = ebrw_readstr.int_u8()
				opli.fmfb1(ebrw_readstr.int_u8())

				opli.ops[1].avekf(ebrw_readstr.int_u8())
				opli.ops[1].ksl_lvl(ebrw_readstr.int_u8())
				opli.ops[1].att_dec(ebrw_readstr.int_u8())
				opli.ops[1].sus_rel(ebrw_readstr.int_u8())
				opli.ops[1].waveform = ebrw_readstr.int_u8()

				opli.ops[2].avekf(ebrw_readstr.int_u8())
				opli.ops[2].ksl_lvl(ebrw_readstr.int_u8())
				opli.ops[2].att_dec(ebrw_readstr.int_u8())
				opli.ops[2].sus_rel(ebrw_readstr.int_u8())
				opli.ops[2].waveform = ebrw_readstr.int_u8()
				opli.fmfb2(ebrw_readstr.int_u8())

				opli.ops[3].avekf(ebrw_readstr.int_u8())
				opli.ops[3].ksl_lvl(ebrw_readstr.int_u8())
				opli.ops[3].att_dec(ebrw_readstr.int_u8())
				opli.ops[3].sus_rel(ebrw_readstr.int_u8())
				opli.ops[3].waveform = ebrw_readstr.int_u8()

			elif insttype in [1,6,7,8,9,10]:
				opli.set_opl2()
				if insttype>5:
					opli.perc_on = True
					opli.perc_type = insttype-5

				opli.ops[0].avekf(ebrw_readstr.int_u8())
				opli.ops[0].ksl_lvl(ebrw_readstr.int_u8())
				opli.ops[0].att_dec(ebrw_readstr.int_u8())
				opli.ops[0].sus_rel(ebrw_readstr.int_u8())
				opli.ops[0].waveform = ebrw_readstr.int_u8()
				opli.fmfb1(ebrw_readstr.int_u8())
				
				opli.ops[1].avekf(ebrw_readstr.int_u8())
				opli.ops[1].ksl_lvl(ebrw_readstr.int_u8())
				opli.ops[1].att_dec(ebrw_readstr.int_u8())
				opli.ops[1].sus_rel(ebrw_readstr.int_u8())
				opli.ops[1].waveform = ebrw_readstr.int_u8()
			self.insts.append(opli)

		for n in range(num_tracks): self.tracks[n].events = decode_events(ebrw_readstr)
		self.controltrack = decode_events(ebrw_readstr)

		return True