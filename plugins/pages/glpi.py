#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# This file is part of Check_MK extension glpi_sync.
# Copyright (C) 2016  skunkie <skunkiem@gmail.com>
#
# glpi_sync is free software; you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2. glpi_sync is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# tails. You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

import glpi

pagehandlers.update({
    'glpi_config': glpi.page_config,
})
