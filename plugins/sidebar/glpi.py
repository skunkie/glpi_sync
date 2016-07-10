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

def render_glpi_config():
    import time
    from glpi import load_glpi_schedule
    from wato import make_action_link

    schedule = load_glpi_schedule()
    last_run = schedule.get('last_run', 0)

    html.write('<div class=last_glpi_sync>%s</div>' % time.strftime("%b %d %Y %H:%M", time.localtime(last_run)))
    html.write('<p>')
    iconlink(_('Edit configuration'), 'glpi_config.py', 'edit')
    html.write('</p>')


sidebar_snapins['glpi_config'] = {
    'title'       : _('GLPI Sync'),
    'description' : _('Configuration and status of GLPI Sync'),
    'refresh'     : True,
    'render'      : render_glpi_config,
    'allowed'     : [ 'admin' ],
    "styles" : """
div.last_glpi_sync {
    text-align: center;
    font-size: 10pt;
    font-weight: bold;
    /* The border needs to be substracted from the width */
    border: 1px solid #8cc;
    -moz-border-radius: 10px;
    background-color: #588;
    color: #aff;
    width: %dpx;
}
"""  % (snapin_width - 2)
}
