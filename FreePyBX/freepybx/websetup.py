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

    # Add initial admin with admin login rights
    admin_user = AdminUser(u'admin@freepybx.org',u'secretpass1',u'Admin',u'User')
    Session.add(admin_user)

    admin_group = AdminGroup(u'system_admin',u'System administrators')
    admin_group.admin_users.append(admin_user)
    Session.add(admin_group)

    admin_perm = AdminPermission(u'superuser',u'all access')
    admin_perm.admin_groups.append(admin_group)
    Session.add(admin_perm)

    pba = Group(u'pbx_admin', u'PBX Admins')
    pba.permissions.append(Permission(u'pbx_admin'))
    Session.add(pba)

    pbe = Group(u'pbx_extension', u'PBX Extension Users')
    pbe.permissions.append(Permission(u'pbx_extension'))
    Session.add(pbe)

    pbb = Group(u'billing', u'Billing Administrators')
    pbb.permissions.append(Permission(u'pbx_admin'))
    Session.add(pbb)

    # Setup the default VoIP services as an example to get you started on the concept.
    Session.add(BillingServiceType(u'VoIP Service', u'Voice over Internet Protocol Service'))
    Session.add(VoipServiceType(u'VoIP PBX Service', u'Private Branch Exchange Service'))
    Session.add(VoipServiceType(u'VoIP Extension Service', u'VoIP Extension'))
    Session.add(VoipServiceType(u'VoIP Trunk Service', u'Voip Trunk'))
    Session.add(VoipServiceType(u'DID', u'Direct Inward Dial Number'))
    Session.add(VoipServiceType(u'8XX', u'8XX Number'))

    Session.add(BillingProductType(u'Voip Telephones'))
    Session.add(BillingProductType(u'Voip ATA'))

    Session.add(BillingServiceFeeType(u'Tax', u'Local taxes'))
    Session.add(BillingServiceFeeType(u'USF Fee', u'Local taxes'))

    Session.add(ProviderBillingApiType(u'Credit Card Gateway', u'Charge customer card via credit card processing gateway.'))
    Session.add(BillingCycleType(u'Monthly', u'Monthly Service'))
    Session.add(BillingCycleType(u'Annual', u'Annual Service'))
    Session.add(BillingCycleType(u'Prepay Pool', u'Prepay Service Deducted from account funds.'))
    Session.add(PaymentType(u'Credit Card Auto Bill', u'Charged credit card via merchant gateway automatically.'))
    Session.add(PaymentType(u'Credit Card By Employee', u'Manually charged credit card via merchant gateway by employee.'))

    Session.commit()
    Session.flush()




