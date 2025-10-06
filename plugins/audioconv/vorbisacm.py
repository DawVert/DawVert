# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

class input_soundfile(plugins.base):
	def is_dawvert_plugin(self):
		return 'audioconv'
	
	def get_shortname(self):
		return 'vorbisacm'
	
	def get_name(self):
		return 'VorbisACM'
	
	def get_priority(self):
		return -100
	
	def get_prop(self, in_dict): 
		in_dict['in_file_formats'] = ['wav_ogg']
		in_dict['out_file_formats'] = ['wav', 'mp3', 'flac', 'ogg']

	def usable(self): 
		import importlib.util
		usable = importlib.util.find_spec('soundfile')
		usable_meg = '"soundfile" package is not installed.' if not usable else ''
		return usable, usable_meg

	def convert_file(self, sampleref_obj, to_type, outpath):
		import soundfile
		import io
		from external.easybinrw import easybinrw
		from external.easybinrw import riff_chunks
		if sampleref_obj.fileref.file.extension == 'wav':
			input_file = sampleref_obj.fileref.get_path(None, False)
			ebrw_readstr = easybinrw.binread()
			ebrw_readstr.load_file(input_file)
			riffchunks = riff_chunks.riff_chunk()
			riffchunks.read(ebrw_readstr, 0)

			data_pos = 0
			data_end = 0
			fmt_format = 0

			for riff_part in riffchunks.iter_reader(ebrw_readstr):
				if riff_part.name == b'fmt ': 
					fmt_format = ebrw_readstr.int_u16()
				elif riff_part.name == b'data': 
					data_pos = riff_part.start
					data_end = riff_part.end

			if fmt_format in [26447, 26448, 26480, 26449]:
				ebrw_readstr.seek(data_pos)
				audiodata = ebrw_readstr.raw(data_end-data_pos)
				samples, samplerate = soundfile.read(io.BytesIO(audiodata))
				outfileref = sampleref_obj.fileref.copy()
				outfileref.set_folder(None, outpath, False)
				outfileref.file.extension = to_type
				outpath = outfileref.get_path(None, False)
				f = open(outpath, 'wb')
				soundfile.write(f, samples, samplerate)
				sampleref_obj.fileref = outfileref
				sampleref_obj.fileformat = to_type
				return True
			return False
		return False