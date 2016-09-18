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

import config, defaults, os, visuals, time
from pprint import pprint
from lib import aquire_lock
from reporting import last_scheduled_time, SchedulePeriod
from valuespec import *
from wato import make_action_link


loaded_with_language = False
config_page = 'glpi_config.py'
schedule_file_path = defaults.var_dir + '/glpi_schedule.py'
config_file_path = defaults.var_dir + '/glpi_config.py'
errlog_file_path = defaults.var_dir + '/glpi_errors.log'


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

    config.declare_permission('general.glpi_config', _('Change GLPI settings'),
              _('Allows a user to change GLPI settings.'),
              [ 'admin' ])


def load_glpi_config():
    if not os.path.exists(config_file_path):
        load_web_plugins('glpi', globals())
        save_glpi_config(config.glpi_default_config)

    aquire_lock(config_file_path)
    return eval(file(config_file_path).read())


def load_glpi_schedule():
    if not os.path.exists(schedule_file_path):
        save_glpi_schedule({})

    aquire_lock(schedule_file_path)
    return eval(file(schedule_file_path).read())


def load_glpi_errlog():
    if not os.path.exists(errlog_file_path):
        save_glpi_errlog('')

    aquire_lock(errlog_file_path)
    return file(errlog_file_path).readlines()


def save_glpi_config(config):
    file(config_file_path, 'w').write('%s\n' % pprint.pformat(config))


def save_glpi_schedule(schedule):
    file(schedule_file_path, 'w').write('%s\n' % pprint.pformat(schedule))


def save_glpi_errlog(error):
    file(errlog_file_path, 'w').write(error)


def page_config():
    is_admin = config.may('general.glpi_config')
    if not is_admin:
        config.need_permission('general.glpi_config')

    glpi_config = load_glpi_config()

    html.header(_('GLPI Sync'), stylesheets=['pages', 'views', 'status', 'glpi'])
    html.begin_context_buttons()
    html.context_button(_('Sync now'), make_action_link([('_sync', 'true')]), icon='glpi', hot=do_sync(True))
    html.end_context_buttons()

    errlog = load_glpi_errlog()
    html.begin_foldable_container(
        'synclog', 'synclog', False,  HTML('<b>SYNC ERRORS (%d)</b>' % len(errlog)))
    if errlog:
        html.show_error('<br>'.join(errlog))
    else:
        html.show_info('No errors')
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
              help = _('Add new hosts with these states.')
        )),
        ( 'ignored_hosts',
          ListOfStrings(
              valuespec = RegExpUnicode(),
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
            help = _('Exact match for Type from GLPI table "glpi_computertypes" to Internal ID "type".')
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


def sync_glpi(glpi_config):

    import MySQLdb
    import re
    from socket import gethostbyname_ex
    from wato import create_snapshot, ping
    from watolib import Folder, Host, check_mk_automation, log_commit_pending, load_hosttags, synchronize_site

    # check if necessary tags are present
    wato_host_tags, _ = load_hosttags()
    for check_internal_id, config_entry in [('type', 'type_matches'), ('os', 'os_matches')]:
        tag_present = False

        for internal_id, _, values in wato_host_tags:
            if internal_id == check_internal_id:
                tag_present = True

                for _, tag_id in glpi_config[config_entry]:
                    check_value = [x for x,_,_ in values if x == tag_id]
                    if not check_value:
                        return 'Add Tag ID "%s" to Internal ID "%s" in Host Tags' % (tag_id, internal_id)

        if not tag_present:
            return 'Add Internal ID "%s" to Host Tags' % internal_id

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
        AND LOWER(s.name) in (%s)
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

    activate_changes = False
    all_hosts = Host.all()
    all_hosts_no_dns_suffixes = dict((x.split('.', 1)[0],x) for x in all_hosts)
    errors = []
    folder_path = ''
    new_hosts = []
    snapshot_name = None
    ignored_hosts = [re.compile(x) for x in glpi_config['ignored_hosts']]

    for host_id, hostname, tag_criticality, type_name, os_name in db_result:
        # New hosts will be added to default sites
        cluster_nodes = None
        ipaddr = None

        # check if hostname is valid
        if not hostname:
            continue
        try:
            Hostname().validate_value(hostname, 'hostname')
        except Exception, e:
            errors += ['%s - %s' % (hostname, e)]
            continue

        # check if the hostname can be resolved to an IP address
        try:
            fqdn, _, ipaddr = gethostbyname_ex(hostname)
        except:
            errors += ['hostname %s cannot be resolved to an IP address' % hostname]
        # check dns suffix
        fqdn_split = fqdn.split('.', 1)
        if len(fqdn_split) == 2:
            dns_suffix = fqdn.split('.', 1)[1]
            if dns_suffix in glpi_config['dns_suffixes']:
                hostname = fqdn

        # prepare attributes
        attributes = {
            'tag_criticality' : tag_criticality,
        }

        if type_name:
            # exact match
            tag_type = ''.join([y for x,y in glpi_config.get('type_matches', []) if x == type_name])
            if tag_type:
                attributes['tag_type'] = tag_type

        if os_name:
            # substring match
            tag_os = ''.join([y for x,y in glpi_config.get('os_matches', []) if x in os_name])
            if tag_os:
                attributes['tag_os'] = tag_os

        if hostname not in all_hosts:
            # avoid adding duplicates
            if hostname in all_hosts_no_dns_suffixes:
                hostname = all_hosts_no_dns_suffixes[hostname]
            else:
                # add only if hosts have an IP address
                if tag_criticality in glpi_config['states_to_add'] and ipaddr:
                    # do not add the host if it is in ignored hosts
                    if [p for p in ignored_hosts if p.match(hostname)]:
                        continue
                    # add only if ICMP reply is received
                    if not ping(ipaddr[0]):
                        errors += ['cannot add hostname %s: no ICMP reply is received' % hostname]
                        continue
                    new_hosts += [(hostname, attributes, cluster_nodes)]
                    activate_changes = True
                    if not snapshot_name:
                        snapshot_name = create_snapshot()
                continue

        host = Host.host(hostname)
        # Update existing attributes
        new_attributes = host.attributes().copy()
        new_attributes.update(attributes)
        if new_attributes != host.attributes():
            if not snapshot_name:
                snapshot_name = create_snapshot()
            host.edit(new_attributes, host.cluster_nodes())
            activate_changes = True

    # Close DB connection
    cur.close()

    if new_hosts:
        Folder.folder(folder_path).create_hosts(new_hosts)

        if glpi_config['discover_services']:
            for hostname, _, _ in new_hosts:
                host = Host.host(hostname)
                host_attributes = host.effective_attributes()
                counts, failed_hosts = check_mk_automation(
                    host_attributes.get('site'), 'inventory', [ '@scan', 'new' ] + [hostname])

    # Activate changes, only for the default site
    if activate_changes:
        try:
            synchronize_site(config.site(config.default_site()), True)
        except Exception, e:
            return str(e)

        log_commit_pending()

    save_glpi_schedule({'last_run': time.time()})

    if errors:
        return '\n'.join(errors)

    return None

# This is registered as a Multisite cron job
def do_sync(WATO=False):

    glpi_config = load_glpi_config()

    if WATO and html.has_var('_sync'):
        # make sure it is not a browser reload
        if not html.check_transaction():
            return False

        error = sync_glpi(glpi_config)
        save_glpi_errlog(error)
        html.immediate_browser_redirect(1, config_page)

    elif not WATO and glpi_config['cron']:

        schedule = load_glpi_schedule()
        last_run = schedule.get('last_run', 0)
        last_time = last_scheduled_time(glpi_config)

        # Do not sync if last_time is less than last_run
        # when not run in WATO
        if last_time < last_run:
            return False

        from wato import load_plugins

        config.login(glpi_config['cron_user'])
        load_plugins(True)
        error = sync_glpi(glpi_config)
        save_glpi_errlog(error)

    return True
