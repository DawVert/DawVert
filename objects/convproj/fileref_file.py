# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

# ------------------------------------ classes ------------------------------------

class cvpj_filename:
	def __init__(self):
		self.reset()

	def reset(self):
		self.used = False
		self.basename = None
		self.extension = ''
		self.filename = None

	def set(self, basename):
		if basename is not None:
			self.used = True
			self.basename = basename
			filenamesplit = self.basename.rsplit('.', 1)
			self.filename = filenamesplit[0]
			if len(filenamesplit) > 1: 
				self.extension = filenamesplit[1]
				return True
		else: self.reset()

	def get_str(self):
		return (self.filename+'.'+self.extension if self.extension else self.filename) if self.used else ''

	def __str__(self):
		return self.get_str()
