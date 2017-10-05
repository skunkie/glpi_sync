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

import config
import cmk.paths
import os
import table
import visuals
import time
from cmk.schedule import last_scheduled_time
from lib import aquire_lock
from pprint import pprint
from valuespec import *
from wato import make_action_link

loaded_with_language = False
config_page = 'glpi_config.py'
schedule_file_path = cmk.paths.var_dir + '/glpi_schedule.py'
config_file_path = cmk.paths.var_dir + '/glpi_config.py'
errlog_file_path = cmk.paths.var_dir + '/glpi_errors.log'
snapshot_name = None


def load_plugins(force):
    global loaded_with_language
    if loaded_with_language == current_language and not force:
        return

    # Load all files below local/share/check_mk/web/plugins/glpi into
    # the global context
    load_web_plugins('glpi', globals())

    # This must be set after plugin loading to make broken plugins raise
    # exceptions all the time and not only the first time (when the plugins
    # are loaded).
    loaded_with_language = current_language

    config.declare_permission(
        'general.glpi_config',
        _('Change GLPI settings'),
        _('Allows a user to change GLPI settings.'),
        [ 'admin' ])


def load_glpi_file(file_path, default_content={}):
    if not os.path.exists(file_path):
        save_glpi_file(file_path, default_content)

    aquire_lock(file_path)
    return eval(file(file_path).read())


def save_glpi_file(file_path, content):
    file(file_path, 'w').write('%s\n' % pprint.pformat(content))


def load_glpi_config():
    if not os.path.exists(config_file_path):
        config.load_plugins(False)
        save_glpi_config(config.glpi_default_config)

    aquire_lock(config_file_path)
    return eval(file(config_file_path).read())


def load_glpi_schedule():
    return load_glpi_file(schedule_file_path)


def load_glpi_errlog():
    return load_glpi_file(errlog_file_path)


def save_glpi_config(config):
    save_glpi_file(config_file_path, config)


def save_glpi_schedule(schedule):
    save_glpi_file(schedule_file_path, schedule)


def save_glpi_errlog(error):
    save_glpi_file(errlog_file_path, error)


def page_config():
    is_admin = config.user.may('general.glpi_config')
    if not is_admin:
        config.user.need_permission('general.glpi_config')

    global glpi_config
    glpi_config = load_glpi_config()
    errlog = load_glpi_errlog()

    html.disable_request_timeout()
    html.header(_('GLPI Sync'), stylesheets=['pages', 'views', 'status', 'glpi'])
    html.begin_context_buttons()
    html.context_button(_('Sync now'), make_action_link([('_sync', 'true')]), icon='glpi', hot=do_sync(True))
    html.end_context_buttons()

    html.begin_foldable_container(
        'host_sync_errors', 'host_sync_errors', False,  HTML('<b>HOST SYNC ERRORS (%d)</b>' % len(errlog)))

    table.begin(table_id='host_sync_errors', empty_text='No errors')
    for hostname in errlog:
        table.row()
        table.cell('Hostname', hostname)
        table.cell('Error', errlog[hostname])
    table.end()

    html.end_foldable_container()

    settings = []

    settings_elements = [
        ( 'host',
          TextUnicode(
              title = _('GLPI Server'),
              allow_empty = False,
        )),
        ( 'db_name',
          TextUnicode(
              title = _('GLPI Database Name'),
              allow_empty = False,
        )),
        ( 'db_user',
          TextUnicode(
              title = _('GLPI Database User'),
              allow_empty = False,
        )),
        ( 'db_passwd',
          Password(
              title = _('GLPI Database Password'),
              allow_empty = False,
        )),
        ( 'states',
          ListChoice(
              title = _('Update hosts with these states'),
              orientation = 'horizontal',
              allow_empty = False,
              choices = [
                ('prod', _('Production system'), ),
                ('uat',  _('UAT system'), ),
                ('dev',  _('Development system'), ),
              ]
        )),
        ( 'states_to_add',
          ListChoice(
              title = _('Add new hosts with these states'),
              orientation = 'horizontal',
              choices = [
                ('prod', _('Production system'), ),
                ('uat',  _('UAT system'), ),
                ('dev',  _('Development system'), ),
              ],
              help = _('Add new hosts with these states only.')
        )),
        ( 'ignored_hosts',
          ListOfStrings(
              valuespec = RegExpUnicode(mode = RegExpUnicode.prefix),
              title = _('Do not add these hosts'),
              orientation = 'horizontal',
              elements = [],
              help = _('Do not add these hosts. Regular expressions are possible.')
        )),
        ( 'dns_suffixes',
          ListOfStrings(
              title = _('DNS suffixes to add'),
              orientation = 'horizontal',
              elements = [],
              help = _('DNS suffixes to add if hosts have them in their FQDN.')
        )),
        ( 'type_matches',
          ListOf(
            Tuple(
              show_titles = True,
              orientation = 'horizontal',
              elements = [
                TextUnicode(
                 title = _('Computer Type in GLPI'),
                 ),
                TextUnicode(
                 title = _('Internal ID type'),
                 ),
                ],
            ),
            title = _('Host Tags: Type'),
            help = _('Substring match for Type from GLPI table "glpi_computertypes" to Internal ID "type".')
        )),
        ( 'os_matches',
          ListOf(
            Tuple(
              show_titles = True,
              orientation = 'horizontal',
              elements = [
                TextUnicode(
                 title = _('OS in GLPI'),
                 ),
                TextUnicode(
                 title = _('Internal ID os'),
                 ),
                ],
            ),
            title = _('Host Tags: OS'),
            help = _('Substring match for OS from GLPI table "glpi_operatingsystems" to Internal ID "os".')
        )),
        ( 'discover_services',
          Checkbox(
              title = _('Discover services for new hosts'),
              label = _('Enable'),
        )),
        ( 'cron',
          Checkbox(
              title = _('Synchronization by Сron'),
              label = _('Enable'),
        )),
        ( 'cron_user',
          TextUnicode(
              title = _('User to run Cron job'),
              allow_empty = False,
        )),
        ( 'period',
          SchedulePeriod()
        ),
        ( 'timeofday',
          Timeofday(
              title = _('Time of day to run sync'),
        )),
    ]

    settings.append(
        ( 'general',
          Dictionary(
              title = _('Settings'),
              optional_keys = None,
              elements = settings_elements,
        ))
    )

    edit_settings = {
        'context' : visuals.pack_context_for_editing(glpi_config, None),
        'general' : glpi_config,
    }

    dict_settings = forms.edit_dictionaries(settings, edit_settings, method='POST')

    if dict_settings != None:        
        new_settings = dict_settings['general']
        save_glpi_config(new_settings)
        html.immediate_browser_redirect(1, config_page)
        html.message(_('Your settings have been saved.'))

    html.footer()


def check_tags():

    from watolib import load_hosttags

    tag_errors = []
    wato_host_tags, _ = load_hosttags()
    for tag_internal_id, config_entry in [('type', 'type_matches'), ('os', 'os_matches')]:
        tag_present = False

        for internal_id, _, values in wato_host_tags:
            if internal_id == tag_internal_id:
                tag_present = True

                for _, tag_id in glpi_config[config_entry]:
                    check_value = [x for x,_,_ in values if x == tag_id]
                    if not check_value:
                        tag_errors.append('Add Tag ID "%s" to Internal ID "%s" in Host Tags' % (tag_id, internal_id))

        if not tag_present:
            tag_errors.append('Add Internal ID "%s" to Host Tags' % internal_id)

    return tag_errors


def check_snapshot():

    from watolib import lock_exclusive, unlock_exclusive
    from wato import create_snapshot

    global snapshot_name
    if not snapshot_name:
        lock_exclusive()
        snapshot_name = create_snapshot('GLPI Sync')
        unlock_exclusive()


def sync_glpi():

    import MySQLdb
    import re
    from socket import gaierror, gethostbyname_ex
    from wato import ping, prepare_git_commit
    from watolib import ActivateChangesManager, Folder, Host, check_mk_automation, default_site

    query = """
        SELECT c.id host_id,
        LOWER(c.name) hostname,
        LOWER(s.name) state,
        ct.name type,
        os.name osname
        FROM glpi_computers c
        LEFT JOIN glpi_states s
        ON c.states_id = s.id
        LEFT JOIN glpi_computertypes ct
        ON c.computertypes_id = ct.id
        LEFT JOIN glpi_operatingsystems os
        ON c.operatingsystems_id = os.id
        WHERE c.is_deleted = 0
        AND c.is_template = 0
        AND LOWER(s.name) IN (%s)
        ORDER BY hostname
    """ % ', '.join(map(lambda x: '%s', glpi_config['states']))

    try:
        db_con = MySQLdb.connect(
            user = glpi_config['db_user'],
            passwd = glpi_config['db_passwd'],
            host = glpi_config['host'],
            db = glpi_config['db_name'],
            use_unicode=True,
            charset='utf8')
        cur = db_con.cursor()
        cur.execute(query, glpi_config['states'])
        db_result = cur.fetchall()
    except MySQLdb.Error, e:
        return str(e)

    all_hosts = Host.all()
    all_hosts_no_dns_suffixes = dict((x.split('.', 1)[0],x) for x in all_hosts)
    errors = {}
    new_hosts = []
    ignored_hosts = [re.compile(x) for x in glpi_config.get('ignored_hosts', [])]

    if config.wato_use_git:
        prepare_git_commit()

    for host_id, hostname, tag_criticality, type_name, os_name in db_result:
        cluster_nodes = None  # New hosts will be added to default sites
        fqdn = ''
        ipaddr = []

        # check if hostname is valid
        try:
            Hostname().validate_value(hostname, 'hostname')
        except Exception, e:
            errors[hostname] = e
            continue

        # check if the hostname can be resolved to an IP address
        try:
            fqdn, _, ipaddr = gethostbyname_ex(hostname)
        except gaierror:
            errors[hostname] = 'cannot be resolved to an IP address'

        # check dns suffix
        fqdn_split = fqdn.split('.', 1)
        if len(fqdn_split) == 2:
            dns_suffix = fqdn.split('.', 1)[1]
            if dns_suffix in glpi_config['dns_suffixes']:
                hostname = fqdn

        # add a DNS suffix if there is an A record in two zones,
        # e.g. host1.zone1.local and host1.zone2.local, but
        # in OMD it is registered as host1.zone2.local
        hostname = all_hosts_no_dns_suffixes.get(hostname, hostname)

        # prepare attributes
        attributes = {
            'tag_criticality' : tag_criticality,
        }

        if type_name:
            # substring match
            tag_type = next((y for x, y in glpi_config.get('type_matches', []) if x in type_name), None)
            if tag_type:
                attributes['tag_type'] = tag_type

        if os_name:
            # substring match
            tag_os = next((y for x, y in glpi_config.get('os_matches', []) if x in os_name), None)
            if tag_os:
                attributes['tag_os'] = tag_os

        if hostname not in all_hosts:
            # avoid adding a duplicate host
            if hostname not in all_hosts_no_dns_suffixes:
                # add only if a host has an IP address
                if tag_criticality in glpi_config['states_to_add'] and ipaddr:
                    # do not add a host if it is in ignored hosts
                    if [p for p in ignored_hosts if p.match(hostname)]:
                        continue
                    # add only if ICMP reply is received
                    if not ping(ipaddr[0]):
                        errors[hostname] = 'cannot add, no ICMP reply is received'
                        continue
                    new_hosts += [(hostname, attributes, cluster_nodes)]
                    check_snapshot()
                continue

        host = Host.host(hostname)
        # Update existing attributes
        new_attributes = host.attributes().copy()
        new_attributes.update(attributes)
        if new_attributes != host.attributes():
            check_snapshot()
            host.edit(new_attributes, host.cluster_nodes())

    # Close DB connection
    cur.close()

    if new_hosts:
        Folder.root_folder().create_hosts(new_hosts)

        if glpi_config.get('discover_services', False):
            for hostname, _, _ in new_hosts:
                host = Host.host(hostname)
                host_attributes = host.effective_attributes()
                counts, failed_hosts = check_mk_automation(
                    host_attributes.get('site'), 'inventory', [ '@scan', 'new' ] + [hostname])

    # Activate changes, only for the default site
    manager = ActivateChangesManager()
    manager.load()
    if manager.has_changes():
        sites = [default_site()]
        manager.start(sites, comment='GLPI Sync', activate_foreign=False)
        manager.wait_for_completion()

    save_glpi_schedule({'last_run': time.time()})
    save_glpi_errlog(errors)

# This is registered as a Multisite cron job
def do_sync(WATO=False):

    if WATO and html.has_var('_sync'):
        # make sure it is not a browser reload
        if not html.check_transaction():
            return False

        tag_errors = check_tags()
        if tag_errors:
            html.show_error('\n'.join(tag_errors))
            return False

        sync_error = sync_glpi()
        if sync_error:
            html.show_error(sync_error)
            return False

        html.enable_request_timeout()
        html.immediate_browser_redirect(1, config_page)

    elif not WATO and glpi_config['cron']:

        schedule = load_glpi_schedule()
        last_run = schedule.get('last_run', 0)
        last_time = last_scheduled_time(glpi_config['period'], glpi_config['timeofday'])

        # Do not sync if last_time is less than last_run
        # when not run in WATO
        if last_time < last_run:
            return False

        tag_errors = check_tags()
        if tag_errors:
            return False

        from wato import load_plugins

        config.set_user_by_id(glpi_config['cron_user'])
        load_plugins(True)
        sync_glpi()

    return True

glpi_config = load_glpi_config()
