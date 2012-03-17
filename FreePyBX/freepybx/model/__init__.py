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


__all__ = ['Customer','User', 'AdminUser', 'Group', 'EmailAccount','Shift','PbxContext','PbxIVR','PbxIVROption',
           'PbxVirtualExtension','PbxCallerIDRoute','PbxBlacklistedNumber','PbxVirtualMailbox','PbxTTS',
           'PbxTODRoute','PbxRecording','PbxDid','PbxProfile','PbxGateway','PbxRoute','PbxRouteType','PbxCondition',
           'PbxConditionTmpl','PbxAction','PbxActionTmpl','PbxGroup','PbxGroupMember','PbxEndpoint','Contact','CrmAccount',
           'CrmNote','CrmLog','PbxCdr','HelpCategory','Help','PbxConferenceBridge','PbxRegistration','PbxFax',
           'CallCenterQueue', 'CallCenterAgent', 'CallCenterTier', 'CallCenterCaller', 'VoiceMail', 'PbxChannel', 'PbxDialog',
           'CrmAccountStatusType', 'CrmGroup', 'CrmGroupMember', 'CrmCampaign','CrmLeadType', 'CrmCampaignGroup','CrmAccount',
           'Base', 'Session', 'PbxAclBlacklist', 'Provider', 'e911Address', 'e911DirectionalType', 'admin_user_groups','admin_group_permissions',
           'e911UnitType', 'e911StreetType', 'CustomerNote', 'Ticket', 'TicketPriority', 'TicketType', 'AdminGroup',
           'user_groups', 'group_permissions', 'Permission', 'AdminPermission', 'customer_contexts','condition_actions',
           'PbxDeviceType', 'PbxDeviceManufacturer', 'BillingServiceType', 'VoipServiceType', 'BillingService',
           'VoipService', 'VoipServicePolicy', 'VoipExtensionServiceProfile', 'VoipTrunkServiceProfile', 'VoipPbxServiceProfile',
           'BillingServiceFee', 'BillingServiceFeeType', 'BillingCycleType', 'ProviderBillingProfile', 'VoipServicePlan',
           'ProviderBillingGateway', 'ProviderBillingApiType', 'AuthorizeNetAccount', 'Invoice', 'InvoiceItem', 'Payment',
           'PaymentType', 'BillingProduct', 'BillingProductType', 'BillingProductFee']



user_groups = Table('user_groups', metadata,
    Column('user_id', Integer, ForeignKey('users.id', onupdate="CASCADE", ondelete="CASCADE")),
    Column('group_id', Integer, ForeignKey('groups.id', onupdate="CASCADE", ondelete="CASCADE"))
)

group_permissions = Table('group_permissions', metadata,
    Column('group_id', Integer, ForeignKey('groups.id', onupdate="CASCADE", ondelete="CASCADE")),
    Column('permission_id', Integer, ForeignKey('permissions.id', onupdate="CASCADE", ondelete="CASCADE"))
)

admin_user_groups = Table('admin_user_groups', metadata,
    Column('admin_id', Integer, ForeignKey('admin_users.id', onupdate="CASCADE", ondelete="CASCADE")),
    Column('admin_group_id', Integer, ForeignKey('admin_groups.id', onupdate="CASCADE", ondelete="CASCADE"))
)

admin_group_permissions = Table('admin_group_permissions', metadata,
    Column('admin_group_id', Integer, ForeignKey('admin_groups.id', onupdate="CASCADE", ondelete="CASCADE")),
    Column('admin_permission_id', Integer, ForeignKey('admin_permissions.id', onupdate="CASCADE", ondelete="CASCADE"))
)

customer_contexts = Table('customer_contexts', metadata,
    Column('customer_id', Integer, ForeignKey('customers.id', onupdate="CASCADE", ondelete="CASCADE")),
    Column('pbx_context_id', Integer, ForeignKey('pbx_contexts.id'))
)

condition_actions = Table('condition_actions', metadata,
    Column('pbx_condition_id', Integer, ForeignKey('pbx_conditions.id', onupdate="CASCADE", ondelete="CASCADE")),
    Column('pbx_action_id', Integer, ForeignKey('pbx_actions.id'))
)


from freepybx.model.core import AdminUser, AdminGroup, Provider, Customer, User, Group, Permission, \
    AdminPermission, EmailAccount, Contact, CustomerNote, Ticket, TicketPriority, TicketType, Shift

from freepybx.model.pbx import PbxContext, PbxIVR, PbxIVROption, PbxVirtualExtension,\
    PbxCallerIDRoute, PbxBlacklistedNumber, PbxVirtualMailbox, PbxTTS, PbxTODRoute,\
    PbxRecording, PbxDid, PbxProfile, PbxGateway, PbxAclBlacklist, PbxRoute,\
    PbxRouteType, PbxCondition, PbxConditionTmpl, PbxAction, PbxActionTmpl, PbxGroup,\
    PbxGroupMember, PbxEndpoint, PbxDeviceType, PbxDeviceManufacturer, PbxCdr,\
    PbxDNC, PbxConferenceBridge, PbxFax, PbxRegistration, VoiceMail, PbxDialog,\
    PbxChannel, e911Address, e911DirectionalType, e911UnitType, e911StreetType

from freepybx.model.call_center import CallCenterAgent, CallCenterAgentLog,\
    CallCenterCaller, CallCenterQueue, CallCenterTier

from freepybx.model.crm import CrmAccountStatusType, CrmGroup, CrmCampaignGroup,\
    CrmCampaign, CrmGroupMember, CrmLeadType, CrmAccount, CrmLog, CrmNote

from freepybx.model.help import Help, HelpCategory

from freepybx.model.billing import BillingService, BillingServiceType, VoipServiceType, VoipServicePlan, \
    VoipService, VoipServicePolicy, VoipExtensionServiceProfile, VoipTrunkServiceProfile, VoipPbxServiceProfile, \
    BillingServiceFee, BillingServiceFeeType, BillingCycleType, ProviderBillingProfile, \
    ProviderBillingGateway, ProviderBillingApiType, AuthorizeNetAccount, Invoice, InvoiceItem, Payment, \
    PaymentType, BillingProduct, BillingProductType, BillingProductFee