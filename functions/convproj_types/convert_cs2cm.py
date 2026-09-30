# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json	
import logging
import numpy as np
import struct

logger_project = logging.getLogger('project')

def convert(convproj_obj, dawvert_intent):
	logger_project.info('ProjType Convert: ClassicalSingle > ClassicalMultiple')
	convproj_obj.type = 'cm'
	return 1