# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import logging
logger_input = logging.getLogger('input')

class reader_midifile_class():
	def load_file(self, input_file):
		from objects.midi_file.parser import MidiFile
		self.midifile = MidiFile.fromFile(input_file)

	def do_song(self, convproj_obj):
		midifile = self.midifile
		cvpj_tracks = convproj_obj.tracks
		self.ppq = midifile.ppqn
		convproj_obj.set_timings(self.ppq)
		for n, miditrack in enumerate(midifile.tracks):
			track_obj = cvpj_tracks.add(str(n), 'midi', 1, False)
			logger_input.info('Track '+str(n+1)+' of '+str(len(midifile.tracks)))
			self.do_track(miditrack.events, track_obj)
		return self.ppq

	def do_track(self, eventlist, track_obj):
		from objects.midi_file import events as MidiEvents
		events_obj = track_obj.placements.midievents
		events_obj.data.alloc(len(eventlist))
		events_obj.ppq = self.ppq

		curpos = 0
		for msg in eventlist:
			curpos += msg.deltaTime
			if type(msg) == MidiEvents.NoteOnEvent: events_obj.add_note_on(curpos, msg.channel, msg.note, msg.velocity)
			elif type(msg) == MidiEvents.NoteOffEvent: events_obj.add_note_off(curpos, msg.channel, msg.note)
			elif type(msg) == MidiEvents.TrackNameEvent: track_obj.visual.name = msg.name
			elif type(msg) == MidiEvents.CopyrightEvent: events_obj.add_copyright(msg.copyright)
			elif type(msg) == MidiEvents.PitchBendEvent: events_obj.add_pitch(curpos, msg.channel, msg.pitch)
			elif type(msg) == MidiEvents.ControllerEvent: events_obj.add_control(curpos, msg.channel, msg.controller, msg.value)
			elif type(msg) == MidiEvents.ProgramEvent: events_obj.add_program(curpos, msg.channel, msg.program)
			elif type(msg) == MidiEvents.TempoEvent: events_obj.add_tempo(curpos, 60000000/msg.tempo)
			elif type(msg) == MidiEvents.TimeSignatureEvent: events_obj.add_timesig(curpos, msg.numerator, msg.denominator**2)
			elif type(msg) == MidiEvents.TextEvent: events_obj.add_text(curpos, msg.text)
			elif type(msg) == MidiEvents.SysExEvent: events_obj.add_sysex(curpos, msg.data[0:-1])
			elif type(msg) == MidiEvents.MarkerEvent: events_obj.add_marker(curpos, msg.marker)
			elif type(msg) == MidiEvents.LyricEvent: events_obj.add_lyric(curpos, msg.lyric)
			elif type(msg) == MidiEvents.SequencerEvent: events_obj.add_seq_spec(curpos, msg.data)
			elif type(msg) == MidiEvents.MidiPortEvent: events_obj.add_port(msg.port)
			elif type(msg) == MidiEvents.EndOfTrackEvent: break

class input_midi(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'midi'
	
	def get_name(self):
		return 'MIDI'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['universal:midi']
		in_dict['projtype'] = 'cm'

	def parse(self, conversion_state, dawvert_intent):
		midiread_obj = reader_midifile_class()
		if dawvert_intent.input_mode == 'file':
			midiread_obj.load_file(dawvert_intent.input_file)
			conversion_state.project = midiread_obj
			return True

	def to_convproj(self, convproj_obj, dawvert_intent, conversion_state):
		midiread_obj = conversion_state.project
		
		convproj_obj.type = 'cm'

		midiread_obj.do_song(convproj_obj)

		traits_obj = convproj_obj.traits
		traits_obj.fxrack_params = ['vol','pan','pitch']
		traits_obj.auto_types = ['nopl_ticks']
		traits_obj.track_nopl = True

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')