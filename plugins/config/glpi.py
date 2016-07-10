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

glpi_default_config = {
    'host'                   : u'glpi.example.com',
    'db_name'                : u'glpidb',
    'db_user'                : u'glpiuser',
    'db_passwd'              : 'glpipasswd',
    'states'                 : ['prod', 'uat', 'dev'],
    'states_to_add'          : ['prod'],
    'dns_suffixes'           : ['dmz.local'],
    'type_matches'           : [
                                (u'Blade Server', u'blade'),
                                (u'Physical', u'phys'),
                                (u'Rack Mount Chassis', u'phys'),
                                (u'SolarisZone', u'zone'),
                                (u'VMware ESX Server', u'esx'),
                                (u'VMware', u'virt'),
                               ],
    'os_matches'             : [
                                (u'CentOS', u'centos'),
                                (u'Red Hat Enterprise Linux Server', u'redhat'),
                                (u'SunOS', u'solaris'),
                                (u'Ubuntu Linux', u'ubuntu'),
                                (u'Windows', u'windows'),
                               ],
    'discover_services'      : False,
    'cron'                   : False,
    'cron_user'              : u'omdadmin',
    'period'                 : 'day',
    'timeofday'              : (0,0),
}
