'''
    This Source Code Form is subject to the terms of the Mozilla Public 
    License, v. 2.0. If a copy of the MPL was not distributed with this 
    file, You can obtain one at http://mozilla.org/MPL/2.0/.

    Software distributed under the License is distributed on an "AS IS"
    basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
    License for the specific language governing rights and limitations
    under the License.

    The Original Code is FreePyBX/VoiceWARE.

    The Initial Developer of the Original Code is Noel Morgan, 
    Copyright (c) 2011-2012 VoiceWARE Communications, Inc. All Rights Reserved.

    http://www.vwci.com/ 

    You may not remove or alter the substance of any license notices (including
    copyright notices, patent notices, disclaimers of warranty, or limitations 
    of liability) contained within the Source Code Form of the Covered Software, 
    except that You may alter any license notices to the extent required to 
    remedy known factual inaccuracies.
    
'''

import logging
import pylons.test
from pylons import config
from freepybx.config.environment import load_environment
import transaction
from freepybx.model import *

log = logging.getLogger(__name__)


def setup_app(command, conf, vars):
    """Place any commands to setup freepybx here"""
    # Don't reload the app if it was loaded under the testing environment
    if not pylons.test.pylonsapp:
        load_environment(conf.global_conf, conf.local_conf)

    Base.metadata.create_all(bind=Session.bind)

    # Create the tables if they don't already exist        
    # uncomment and adjust for initial setup..
    insert_data()
    
def insert_data():

    route_types = [
        (u'Extension', None),
        (u'Virtual Extension', None),
        (u'Virtual Mailbox', None),
        (u'Group', None),
        (u'IVR', None),
        (u'Time of Day', None),
        (u'Conference Bridge', None),
        (u'Caller ID Route', None),
        (u'DID', None),
        (u'Call Center', None),
        (u'Directory', None),
        (u'Fax', None)
    ]

    for key, value in route_types:
        s = PbxRouteType()
        s.name = key
        s.description = value
        Session.add(s)

    auth_level = [(1, u'PBX Admin'),(2,u'Extension User'),(3, u'Billing & Reports')]

    for key, value in auth_level:
        al = AuthLevel()
        al.name = key
        al.description = value
        Session.add(al)

    admin_group = AdminGroup(u'system_admin',u'System administrators')
    Session.add(admin_group)
    admin = AdminUser(u'admin@freepybx.org',u'secretpass1',u'Admin',u'User')
    Session.add(admin)
    admin.admin_groups.append(admin_group)

    g = Group(u'user')
    Session.add(g)
    p = Permission(u'extension_user')
    g.group_permissions.append(p)
    Session.commit()
    Session.flush()

    ag = Group(u'admin_user')
    Session.add(ag)
    ag.group_permissions.append(Permission(u'pbx_admin'))
    ag.group_permissions.append(Permission(u'billing'))
    ag.group_permissions.append(Permission(u'reporting'))
    Session.commit()
    Session.flush()
