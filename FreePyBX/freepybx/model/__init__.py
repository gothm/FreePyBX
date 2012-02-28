"""
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
"""

from sqlalchemy import ForeignKey, Column, Table
from sqlalchemy.types import Integer
from freepybx.model.meta import Session, Base, metadata

def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    Session.configure(bind=engine)

    """Call me before using any of the tables or classes in the model"""
    Session.configure(bind=engine, expire_on_commit=False )
    Base.query = Session.query_property()
    metadata = Base.metadata


__all__ = ['Company','User', 'AdminUser', 'Group', 'EmailAccount','Shift','PbxContext','PbxIVR','PbxIVROption',
           'PbxVirtualExtension','PbxCallerIDRoute','PbxBlacklistedNumber','PbxVirtualMailbox','PbxTTS', 'AuthLevel',
           'PbxTODRoute','PbxRecording','PbxDid','PbxProfile','PbxGateway','PbxRoute','PbxRouteType','PbxCondition',
           'PbxConditionTmpl','PbxAction','PbxActionTmpl','PbxGroup','PbxGroupMember','PbxEndpoint','Contact','CrmAccount',
           'CrmNote','CrmLog','PbxCdr','HelpCategory','Help','PbxConferenceBridge','PbxRegistration','PbxFax',
           'CallCenterQueue', 'CallCenterAgent', 'CallCenterTier', 'CallCenterCaller', 'VoiceMail', 'PbxChannel', 'PbxDialog',
           'CrmAccountStatusType', 'CrmGroup', 'CrmGroupMember', 'CrmCampaign','CrmLeadType', 'CrmCampaignGroup','CrmAccount',
           'Base', 'Session', 'PbxAclBlacklist', 'Provider', 'e911Address', 'e911DirectionalType', 'company_contexts', 'condition_actions',
           'e911UnitType', 'e911StreetType', 'CompanyNote', 'Ticket', 'TicketPriority', 'TicketType', 'AdminGroup','admin_user_groups',
           'user_groups', 'group_permissions', 'Permission', 'AdminPermission', 'user_endpoints', 'user_contacts']


admin_user_groups = Table('admin_user_groups', metadata,
    Column('admin_id', Integer, ForeignKey('admin_users.id')),
    Column('admin_group_id', Integer, ForeignKey('admin_groups.id'))
)

admin_group_permissions = Table('admin_group_permissions', metadata,
    Column('admin_group_id', Integer, ForeignKey('admin_groups.id')),
    Column('admin_permission_id', Integer, ForeignKey('admin_permissions.id'))
)

user_groups = Table('user_groups', metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('group_id', Integer, ForeignKey('groups.id'))
)

group_permissions = Table('group_permissions', metadata,
    Column('group_id', Integer, ForeignKey('groups.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id'))
)

company_contexts = Table('company_contexts', metadata,
    Column('company_id', Integer, ForeignKey('companies.id')),
    Column('pbx_context_id', Integer, ForeignKey('pbx_contexts.id'))
)

condition_actions = Table('condition_actions', metadata,
    Column('pbx_condition_id', Integer, ForeignKey('pbx_conditions.id')),
    Column('pbx_action_id', Integer, ForeignKey('pbx_actions.id'))
)

user_endpoints = Table('user_endpoints', metadata,
    Column('endpoint_id', Integer, ForeignKey('pbx_endpoints.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)

user_contacts = Table('user_contacts', metadata,
    Column('contact_id', Integer, ForeignKey('contacts.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)



from freepybx.model.core import AdminUser, AdminGroup, Provider, Company, \
    User, Group, Permission, AdminPermission, EmailAccount, Contact, CompanyNote, \
    Ticket, TicketPriority, TicketType, Shift, AuthLevel

from freepybx.model.pbx import PbxContext, PbxIVR, PbxIVROption, PbxVirtualExtension, \
    PbxCallerIDRoute, PbxBlacklistedNumber, PbxVirtualMailbox, PbxTTS, PbxTODRoute, \
    PbxRecording, PbxDid, PbxProfile, PbxGateway, PbxAclBlacklist, PbxRoute, \
    PbxRouteType, PbxCondition, PbxConditionTmpl,PbxAction, PbxActionTmpl, PbxGroup, \
    PbxGroupMember, PbxEndpoint, PbxDeviceType, DeviceManufacturer, PbxCdr, \
    PbxDNC, PbxConferenceBridge, PbxFax, PbxRegistration, VoiceMail, PbxDialog, \
    PbxChannel, e911Address, e911DirectionalType, e911UnitType, e911StreetType

from freepybx.model.call_center import CallCenterAgent, CallCenterAgentLog, \
    CallCenterCaller, CallCenterQueue, CallCenterTier

from freepybx.model.crm import CrmAccountStatusType, CrmGroup, CrmCampaignGroup, \
    CrmCampaign, CrmGroupMember, CrmLeadType, CrmAccount, CrmLog, CrmNote

from freepybx.model.help import Help, HelpCategory

