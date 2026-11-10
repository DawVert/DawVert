# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import getpass
username = getpass.getuser()

import platform
platform_architecture = platform.architecture()
if platform_architecture[1] == 'WindowsPE': native_os = 'win'
else: native_os = 'unix'

import copy
deepcopy = copy.deepcopy

def path_win_from_unix(pathparts):
	win_drive = 'z'
	outpath = pathparts.copy()
	if len(pathparts)>2:
		if pathparts[0] == 'cygdrive': #Cygwin
			win_drive = pathparts[1].upper()
			outpath = pathparts[2:]
	elif len(pathparts)>3:

		unix_wine_cond1 = (pathparts[0] == 'home') or (pathparts[0] == 'Users')
		unix_wine_cond2 = (pathparts[2] == '.wine') and (pathparts[3].startswith('drive_')) and (len(pathparts[3])>6)

		if pathparts[0] == 'mnt' and len(pathparts[1])==1: #WSL
			win_drive = pathparts[1].upper()
			outpath = pathparts[2:]
		elif unix_wine_cond1 and unix_wine_cond2:
			win_drive = pathparts[3][6:].upper()[0]
			outpath = pathparts[4:]
	return win_drive, outpath

def path_unix_from_win(pathparts, drive):
	wine_drive = 'drive_'+drive.lower()
	outpath = ['home',username,'.wine',wine_drive]+pathparts.copy()
	return outpath

def remove_trailing(pathparts):
	if pathparts:
		if pathparts[-1] == '': pathparts = pathparts[:-1]
	return pathparts

def pathmod(folderpath, otherfolderpath):
	folderpath = folderpath.copy()
	for x in otherfolderpath:
		if x == '..': folderpath = folderpath[0:-1]
		elif x == '.': pass
		elif x == '': pass
		else: folderpath.append(x)
	return folderpath

def splitpath_txt(in_path):
	return in_path.replace('/', '\\').replace('\\\\', '\\').split('\\')

class fileref_folder_completer:
	__slots__ = ['partial', 'full']

	def __init__(self):
		self.partial = None
		self.full = None

	def add(self, foldp_obj):
		foldp_obj = copy.deepcopy(foldp_obj)
		provtype = foldp_obj.provtype
		if provtype=='full':
			if not self.full: 
				self.full = foldp_obj
				return 0
			else: 
				return 2
		elif provtype=='part':
			if not self.partial: 
				self.partial = foldp_obj
				return 0
			else: 
				return 3
		else:
			return 1

	def comb(self):
		self.full.loc += self.partial.loc
		return self.full
# ------------------------------------ pathprov ------------------------------------

class pathprov_partial:
	provtype = 'part'
	provname = 'partial'

	def __init__(self):
		self.reset()

	def reset(self):
		self.loc = []

	def set(self, pathparts):
		self.loc = pathparts
		return True

	def get(self, filename, os_type=None):
		if not os_type: os_type = native_os
		outpath = self.loc+[filename]
		if os_type == 'win': 
			return '\\'.join(outpath)
		else: 
			return '/'.join(outpath)

class pathprov_windows:
	provtype = 'full'
	provname = 'win'

	def __init__(self):
		self.reset()

	def reset(self):
		self.loc = []
		self.win_drive = 'c'

	def set(self, pathparts):
		isset = False
		if pathparts:
			if len(pathparts[0])==2 and ':' in pathparts[0]:
				self.win_drive = pathparts[0][0].lower()
				self.loc = remove_trailing(pathparts[1:])
				isset = True
		return isset

	def get(self, filename, os_type=None):
		if not os_type: os_type = native_os
		pathparts = self.loc
		if os_type=='win':
			outpath = [self.win_drive.upper()+':']+pathparts.copy()
			return '\\'.join(outpath+[filename])
		else:
			outpath = ['']+path_unix_from_win(pathparts, self.win_drive)
			return '/'.join(outpath+[filename])

class pathprov_unix:
	provtype = 'full'
	provname = 'unix'

	def __init__(self):
		self.reset()

	def reset(self):
		self.loc = []

	def set(self, pathparts):
		isset = False
		if pathparts:
			if pathparts[0]=='':
				self.loc = remove_trailing(pathparts[1:])
				isset = True
		return isset

	def get(self, filename, os_type=None):
		if not os_type: os_type = native_os
		pathparts = self.loc
		if os_type=='win':
			win_drive, win_path = path_win_from_unix(pathparts)
			outpath = [win_drive.upper()+':']+win_path
			return '\\'.join(outpath+[filename])
		else:
			outpath = ['']+pathparts.copy()
			return '/'.join(outpath+[filename])

class pathprov_prefix:
	provtype = 'prefix'
	provname = 'prefix'

	def __init__(self):
		self.reset()

	def reset(self):
		self.name = ''
		self.loc = []

	def set(self, name, folderloc):
		self.name = name
		self.loc = []
		return True

	def get(self, filename, os_type=None):
		return ''

# ------------------------------------ classes ------------------------------------

class cvpj_folderpath:
	def __init__(self):
		self.path = pathprov_partial()

	def copy(self):
		return deepcopy(self)

	def set_win(self, pathparts):
		full_obj = pathprov_windows()
		isvalid = full_obj.set(pathparts)
		if isvalid: self.path = full_obj
		return isvalid

	def set_unix(self, pathparts):
		full_obj = pathprov_unix()
		isvalid = full_obj.set(pathparts)
		if isvalid: self.path = full_obj
		return isvalid

	def set_prefix(self, name, pathparts):
		full_obj = pathprov_prefix()
		full_obj.set(name, pathparts)
		self.path = full_obj
		return True

	def set(self, pathparts, os_src):
		isvalid = False
		if os_src=='win': isvalid = self.set_win(pathparts)
		elif os_src=='unix': isvalid = self.set_unix(pathparts)
		else:
			if self.set_win(pathparts): isvalid = True
			elif self.set_unix(pathparts): isvalid = True

		if not isvalid:
			part_obj = pathprov_partial()
			part_obj.set(pathparts)
			self.path = part_obj

	def set_str(self, pathparts, os_src):
		self.set(splitpath_txt(pathparts), os_src)
		
	def get_str(self, filename, os_type=None):
		if not os_type: os_type = native_os
		return self.path.get(filename, os_type)

	def convert_os(self, target):
		pd = self.path
		p_type = pd.provtype
		p_name = pd.provname

		if p_type=='full':
			if p_name=='unix' and target=='win':
				win_drive, win_path = path_win_from_unix(pathparts)
				new_obj = pathprov_windows()
				new_obj.win_drive = win_drive
				new_obj.folderloc = win_path
				self.path = new_obj
			elif p_name=='win' and target=='unix':
				new_obj = pathprov_unix()
				new_obj.folderloc = path_unix_from_win(pathparts, pd.win_drive)
				self.path = new_obj
