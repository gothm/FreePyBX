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

import datetime
from datetime import datetime
from sqlalchemy import ForeignKey, Column
from sqlalchemy.types import Integer, DateTime, Boolean, Unicode, UnicodeText
from sqlalchemy.orm import relation, synonym, relationship, backref
from freepybx.model.meta import Session, Base




class CrmAccountStatusType(Base):
    __tablename__='crm_account_status_types'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    context = Column(Unicode(64))
    name = Column(Unicode(64))
    description = Column(Unicode(128))


class CrmGroup(Base):
    __tablename__='crm_groups'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    context = Column(Unicode(64))
    name = Column(Unicode(64))
    description = Column(Unicode(128))


class CrmCampaignGroup(Base):
    __tablename__='crm_campaign_groups'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    context = Column(Unicode(64))
    name = Column(Unicode(64))
    crm_group_id = Column(Integer, ForeignKey('crm_groups.id', onupdate="CASCADE", ondelete="CASCADE"))
    crm_campaign_id = Column(Integer, ForeignKey('crm_campaigns.id', onupdate="CASCADE", ondelete="CASCADE"))


class CrmCampaign(Base):
    __tablename__='crm_campaigns'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    context = Column(Unicode(64))
    name = Column(Unicode(64))
    description = Column(Unicode(128))


class CrmGroupMember(Base):
    __tablename__='crm_group_members'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    context = Column(Unicode(64))
    crm_group_id = Column(Integer, ForeignKey('crm_groups.id', onupdate="CASCADE", ondelete="CASCADE"))
    extension  = Column(Unicode(15))


class CrmLeadType(Base):
    __tablename__='crm_lead_types'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    context = Column(Unicode(64))
    name = Column(Unicode(64))
    description = Column(Unicode(128))


class CrmAccount(Base):
    __tablename__ = 'crm_accounts'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    first_name = Column(Unicode(64))
    last_name = Column(Unicode(64))
    customer = Column(Unicode(255))
    title = Column(Unicode(32))
    created = Column(DateTime,default=datetime.date(datetime.now()))
    last_modified = Column(DateTime,default=datetime.date(datetime.now()))
    email = Column(Unicode(128))
    address = Column(Unicode(255))
    address_2 = Column(Unicode(255))
    city = Column(Unicode(64))
    state = Column(Unicode(32))
    zip = Column(Unicode(15))
    country = Column(Unicode(64))
    url = Column(Unicode(128))
    tel = Column(Unicode(15))
    tel_ext = Column(Unicode(6))
    mobile = Column(Unicode(15))
    active = Column(Boolean, default=True)
    lat_lon = Column(Unicode(100), default=u"0,0")
    crm_campaign_id = Column(Integer, ForeignKey('crm_campaigns.id', onupdate="CASCADE"))

    user_id = Column(Integer)
    customer_id = Column(Integer, ForeignKey('customers.id', onupdate="CASCADE"))
    crm_account_status_type_id = Column(Integer, ForeignKey('crm_account_status_types.id', onupdate="CASCADE"))
    crm_lead_type_id = Column(Integer, ForeignKey('crm_lead_types.id', onupdate="CASCADE"))

    def __init__(self, _first_name=None,_last_name=None,_email=None):
        self.first_name = _first_name
        self.last_name = _last_name
        self.email = _email

    def __str__(self):
        return '<%s>' % self.__class__.__name__

    def __repr__(self):
        return '<%s %r>' % (self.__class__, self.__dict__)


class CrmLog(Base):
    __tablename__='crm_logs'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    text = Column(UnicodeText, nullable=False)
    created = Column(DateTime,default=datetime.date(datetime.now()))
    user_id = Column(Integer)


class CrmNote(Base):
    __tablename__='crm_notes'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    created = Column(DateTime,default=datetime.date(datetime.now()))
    note = Column(UnicodeText, nullable=False)
    crm_account_id = Column(Integer, ForeignKey('crm_accounts.id', onupdate="CASCADE", ondelete="CASCADE"))
