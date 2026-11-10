# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import copy
import os

from objects.convproj import fileref_folder
from objects.convproj import fileref_file
from objects import globalstore

cvpj_folderpath = fileref_folder.cvpj_folderpath
cvpj_filename = fileref_file.cvpj_filename
fileref_folder_completer = fileref_folder.fileref_folder_completer

get_path_type = globalstore.os_info_target.get_path_type

def splitpath_txt(in_path):
	return in_path.replace('/', '\\').replace('\\\\', '\\').split('\\')

def folderfile(in_path, isfile):
	pathd = splitpath_txt(in_path)
	outfolder = []
	outfile = None
	while pathd:
		if pathd[0] == '.': pathd = pathd[1:]
		else: break
	if pathd:
		if isfile>=0:
			if '.' in pathd[-1]: 
				outfolder = pathd[0:-1]
				outfile = pathd[-1]
			else:
				outfolder = pathd
			#else: pathd[0:-1], None
		elif isfile==1:
			outfolder = pathd[0:-1]
			outfile = pathd[-1]
		else:
			outfolder = pathd
	return outfolder, outfile

# ------------------------------------ classes ------------------------------------

class cvpj_fileref_state:
	def __init__(self, fileref):
		self.file = copy.deepcopy(fileref.file)
		self.folder = copy.deepcopy(fileref.folder)
		self.is_file = fileref.is_file

	def restore(self, fileref):
		fileref.file = self.file
		fileref.folder = self.folder
		fileref.is_file = self.is_file

class cvpj_fileref:
	def __init__(self, convproj_obj):
		self.convproj_obj = convproj_obj
		self.reset()

	def reset(self):
		self.file = cvpj_filename()
		self.folder = cvpj_folderpath()
		self.is_file = False

	def copy(self):
		return copy.deepcopy(self)

	def set(self, in_path, os_type=None):
		o_folder, o_file = folderfile(in_path, 0)
		self.folder.set(o_folder, os_type)
		self.is_file = self.file.set(o_file)

	def set_file(self, in_path, os_type=None):
		o_folder, o_file = folderfile(in_path, 1)
		self.folder.set(o_folder, os_type)
		self.is_file = self.file.set(o_file)

	def set_folder(self, in_path, os_type=None):
		o_folder, o_file = folderfile(in_path, -1)
		self.folder.set(o_folder, os_type)
		self.is_file = self.file.set(o_file)

	def set_folderbase(self, in_path, os_type=None):
		o_folder, o_file = folderfile(in_path, 0)
		self.folder.set(o_folder, os_type)

	def add_dir(self, other):
		main = self.copy()
		other = other.copy()
		compl_obj = fileref_folder_completer()
		compl_obj.add(main.folder.path)
		if compl_obj.add(other.folder.path): return None
		main.folder.path = compl_obj.comb()
		return main
		
	def get(self, os_type=None):
		return self.folder.get_str(str(self.file), os_type)

	def get_filename(self):
		return self.file.get()

	def get_basename(self):
		return self.file.filename

	def get_fileext(self):
		return self.file.extension.lower()

	def create_state(self):
		state_obj = cvpj_fileref_state()
		state_obj.folder = copy.deepcopy(self.folder)
		state_obj.file = copy.deepcopy(self.file)
		state_obj.is_file = self.is_file
		return state_obj

	def restore_state(self, state_obj):
		self.folder = copy.deepcopy(state_obj.folder)
		self.file = state_obj.file
		self.is_file = state_obj.is_file

	def set_folder_obj(self, other_fileref):
		self.folder = copy.deepcopy(other_fileref.folder)

	def exists(self):
		filepath = self.get()
		if os.path.exists(filepath): 
			return os.path.isfile(filepath)
		else: return False

	def apply_prefix(self, prefixname):
		folder_prefixes = self.convproj_obj.folder_prefixes

		if prefixname in folder_prefixes and self.folder.path.provtype == 'part':
			prefixdata = folder_prefixes[prefixname]
			for _, r in prefixdata.items():
				combref = self.add_dir(r)
				if combref.exists(): 
					self.file = combref.file
					self.folder = combref.folder
					self.is_file = combref.is_file
					return True
		return False