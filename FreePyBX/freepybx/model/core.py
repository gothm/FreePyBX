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
from sqlalchemy import ForeignKey, Column, Table
from sqlalchemy.types import Integer, DateTime, Boolean, Unicode, UnicodeText
from sqlalchemy.orm import relation, synonym, relationship, backref
from freepybx.model import user_groups, group_permissions, admin_user_groups, admin_group_permissions, \
        company_contexts, condition_actions
from freepybx.model.meta import Base, Session as db
from freepybx.model.pbx import PbxEndpoint, PbxContext
from freepybx.model.call_center import CallCenterAgent

import logging
log = logging.getLogger(__name__)


class AdminUser(Base):
    __tablename__='admin_users'

    query = db.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(Unicode(128), unique=True, nullable=False)
    password = Column(Unicode(32), nullable=False)
    first_name =  Column(Unicode(64), nullable=True)
    last_name = Column(Unicode(64), nullable=True)
    last_login = Column(DateTime, default=datetime.now())
    remote_addr = Column(Unicode(15), nullable=True)
    session_id =  Column(Unicode(128), nullable=True)
    active = Column(Boolean, default=True)

    def __unicode__(self):
        return self.name or self.username

    @property
    def name(self):
        return self.first_name + ' ' + self.last_name

    @property
    def permissions(self):
        for g in self.admin_groups:
            perms = g.permissions
        return perms

    def __init__(self, username, password, first_name, last_name):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name

    @classmethod
    def register_login(class_, username, session, request):
        user = db.query(AdminUser).filter(AdminUser.username==username).first()
        if user:
            now = datetime.now()
            user.last_login = now
            user.session_id = session.id
            user.remote_addr = request.environ["HTTP_REMOTE_EU"]
            db.commit()
            db.flush()

        db.remove()

    def __repr__(self):
        return "<AdminUser({0},{1},{2},{3},{4},{5},{6},{7},{8})>".format(
            self.id,self.username, self.password, self.first_name,self.last_name,self.last_login,self.remote_addr,self.session_id,self.active)


class AdminGroup(Base):
    __tablename__ = 'admin_groups'

    query = db.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(64), unique=True, nullable=False)
    description = Column(UnicodeText)
    created_date = Column(DateTime, default=datetime.now)

    admin_users = relationship("AdminUser", secondary=admin_user_groups, backref='admin_groups')

    @property
    def permissions(self):
        perms = []
        for perm in self.admin_permissions:
            perms.append(perm.name)
        return perms


    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.created_date = datetime.now()

    def __repr__(self):
        return '<AdminGroup: name=%s>' % self.name

    def __unicode__(self):
        return self.name


class Provider(Base):
    __tablename__= 'providers'

    query = db.query_property()

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def __composite_values__(self):
        return [self.name, self.username]

    def __eq__(self, other):
        if isinstance(other, Provider):
            return self.name == other.name and self.username == other.username
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "<Provider({0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13}>".format(
            self.id,self.name,self.email,self.address,self.address_2,self.city,self.state,
            self.zip,self.url,self.tel,self.mobile,self.username,self.password,self.active)

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(100),nullable=False)
    email = Column(Unicode(100))
    address = Column(Unicode(100))
    address_2 = Column(Unicode(100))
    city = Column(Unicode(100))
    state = Column(Unicode(100))
    zip = Column(Unicode(15))
    url = Column(Unicode(100))
    tel = Column(Unicode(100))
    mobile = Column(Unicode(100))
    username = Column(Unicode(128), unique=True, nullable=False)
    password = Column(Unicode(32), nullable=False)
    active = Column(Boolean, default=True)
    # Allowed IP...
    ip = Column(Unicode(15))

    def _get_ip(self):
        return getattr(self, '_ip', None)

    def _set_ip(self, value):
        try:
            self._ip = unpack_ip(value)
        except:
            self._ip = value

    ip = property(_get_ip, _set_ip)


class Company(Base):
    __tablename__= 'companies'

    query = db.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(100),nullable=False)
    company_type_id = Column(Integer, default=1)
    pbx_profile_id = Column(Integer, ForeignKey('pbx_profiles.id', onupdate="CASCADE", ondelete="CASCADE"))
    tax_id =  Column(Unicode(100))
    start_date = Column(DateTime,default=datetime.date(datetime.now()))
    last_login = Column(DateTime,default=datetime.date(datetime.now()))
    end_date = Column(DateTime)
    email = Column(Unicode(100))
    address = Column(Unicode(100))
    address_2 = Column(Unicode(100))
    city = Column(Unicode(100))
    state = Column(Unicode(100))
    zip = Column(Unicode(15))
    url = Column(Unicode(100))
    tel = Column(Unicode(100))
    active = Column(Boolean, default=True)
    lat_lon = Column(Unicode(100), default=u"0,0")
    context = Column(Unicode(64))
    contact_phone = Column(Unicode(64))
    contact_mobile = Column(Unicode(64))
    contact_name = Column(Unicode(64))
    contact_title = Column(Unicode(64))
    contact_email = Column(Unicode(64))
    has_crm = Column(Boolean, default=False)
    has_call_center = Column(Boolean, default=False)
    max_extensions = Column(Integer, nullable=False, default=4)
    max_minutes = Column(Integer, nullable=False, default=10000)
    max_queues = Column(Integer, nullable=False, default=4)
    max_agents = Column(Integer, nullable=False, default=16)
    notes = Column(UnicodeText)
    default_gateway = Column(Unicode(64))

    company_users = relationship("User", backref="users")
    contexts = relationship("PbxContext", backref="pbx_contexts")
    e911_addresses = relationship("e911Address", backref='e911_addresses')
    company_notes = relationship("CompanyNote", backref='company_notes')
    tickets = relationship("Ticket", backref='tickets')

    company_contexts = relationship('PbxContext', secondary=company_contexts, backref='companies')


    def __init__(self, name='Acme VoIP'):
        self.name = name

    def __repr__(self):
        return "<Company({0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16}>".format(\
            self.id,self.name,self.company_type_id,self.tax_id,self.start_date,self.end_date,self.email,self.address,self.address_2,\
            self.city,self.state,self.zip,self.url,self.tel,self.active,self.lat_lon, self.company_users)
    def __str__(self):
        return self.name


class User(Base):
    __tablename__='users'

    query = db.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    company_name = Column(Unicode(255), nullable=True)
    username = Column(Unicode(128), unique=True, nullable=False)
    password = Column(Unicode(32), nullable=False)
    first_name =  Column(Unicode(64), nullable=True)
    last_name = Column(Unicode(64), nullable=True)
    address = Column(Unicode(64), nullable=True)
    address_2 = Column(Unicode(64), nullable=True)
    city = Column(Unicode(64), nullable=True)
    state = Column(Unicode(64), nullable=True)
    zip = Column(Unicode(64), nullable=True)
    tel = Column(Unicode(64), nullable=True)
    mobile = Column(Unicode(64), nullable=True)
    notes = Column(UnicodeText, nullable=True)
    created = Column(DateTime,default=datetime.now())
    updated = Column(DateTime,default=datetime.now())
    active = Column(Boolean, default=True)
    auth_level = Column(Integer, nullable=False, default=4)
    last_login = Column(DateTime, default=datetime.now())
    remote_addr = Column(Unicode(15), nullable=True)
    session_id =  Column(Unicode(128), nullable=True)
    portal_extension = Column(Unicode(15), default=u'Unknown')
    has_crm = Column(Boolean, default=False)
    company_id =  Column(Integer, ForeignKey('companies.id', onupdate="CASCADE", ondelete="CASCADE"))

    def __unicode__(self):
        return self.name or self.username

    def __init__(self, first_name=None, last_name=None, username=None,
                 password=None, auth_level=None, company_id=None, active=False):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.password = password
        self.auth_level = auth_level
        self.company_id = company_id
        self.active = active

    @property
    def permissions(self):
        for g in self.groups:
            perms = g.permissions
        return perms

    def get_name(self):
        return User.first_name + ' ' + User.last_name

    def get_gateway(self):
        gw = db.query(PbxContext.gateway).join(Company).join(User).filter(User.company_id==Company.id).first()
        return 0 if not gw else gw[0]

    def has_call_center(self):
        co = db.query(Company).filter(Company.id==self.company_id).first()
        return co.has_call_center

    def get_context(self):
        co = db.query(Company).filter(Company.id==self.company_id).first()
        return co.context

    def get_extension(self):
        r = PbxEndpoint.query.filter_by(user_id=self.id).first()
        return 0 if not r else r.auth_id

    def by_username(self, username):
        return User.query.filter_by(username==username).first()

    def get_groups(self):
        return db.query(Group.name).join(UserGroup).filter(UserGroup.user_id==self.id).all()

    def is_agent(self):
        return True if CallCenterAgent.query.filter_by(user_id=self.id).count() else False

    @classmethod
    def register_login(class_, username, session, request):
        user = User.query.filter_by(username=username).first()
        if user:
            now = datetime.now()
            user.last_login = now
            user.session_id = session.id
            user.remote_addr = request.environ["HTTP_REMOTE_EU"]
            db.commit()
            db.flush()

            if True:
                s = Shift(session.id, user.id, 1)
                db.add(s)
                db.commit()
                db.flush()
        db.remove()

    @classmethod
    def get_company_name(class_, company_id):
        company = db.query(Company).filter(Company.id==company_id).first()
        if company:
            return company.name

    def get_email_account(self):
        email = db.query(EmailAccount).filter(EmailAccount.user_id==self.id).first()
        if email:
            return email

    def __repr__(self):
        return "<User({0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16},{17},{18},{19},{20},{21})>".format(
            self.id,self.company_name, self.username, self.password,self.first_name,self.last_name,self.address,self.address_2,self.city,self.state,self.zip,self.tel,
            self.mobile,self.notes, self.created, self.updated, self.active, self.auth_level, self.last_login, self.remote_addr, self.session_id, self.company_id)


class Group(Base):
    __tablename__ = 'groups'

    query = db.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(64), unique=True, nullable=False)
    description = Column(UnicodeText)
    created_date = Column(DateTime, default=datetime.now)

    users = relationship("User", secondary=user_groups, backref='groups')

    @property
    def permissions(self):
        perms = []
        for perm in self.permissions:
            perms.append(perm.name)
        return perms

    def __init__(self, name, description=None, date=None):
        self.name = name
        self.description = description or name
        self.created_date = datetime.now()

    def __repr__(self):
        return '<Group: name=%s>' % self.name

    def __unicode__(self):
        return self.name


class Permission(Base):
    __tablename__='permissions'

    query = db.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(32), default=u'Unknown')
    description = Column(Unicode(255), default=u'Unknown')

    groups =  relationship("Group", secondary=group_permissions, backref='permissions')

    def __unicode__(self):
        return self.name

    def __init__(self, name, description=None):
        self.name = name
        self.description = description or name

    def __repr__(self):
        return '%s' % self.name


class AdminPermission(Base):
    __tablename__='admin_permissions'

    query = db.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(32), default=u'Unknown')
    description = Column(Unicode(255), default=u'Unknown')

    admin_groups =  relationship("AdminGroup", secondary=admin_group_permissions, backref='admin_permissions')

    def __unicode__(self):
        return self.name

    def __init__(self, name, description=None):
        self.name = name
        self.description = description or name

    def __repr__(self):
        return "%r" % self.__dict__


class EmailAccount(Base):
    __tablename__='email_accounts'

    query = db.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id =  Column(Integer, ForeignKey('users.id', onupdate="CASCADE", ondelete="CASCADE"))
    company_id =  Column(Integer, ForeignKey('companies.id', onupdate="CASCADE", ondelete="CASCADE"))
    email = Column(Unicode(64), unique=True, nullable=False)
    password = Column(Unicode(255), nullable=False)
    mail_server = Column(Unicode(64), nullable=False)


class Contact(Base):
    __tablename__ = 'contacts'

    query = db.query_property()

    def __init__(self, _first_name=None,_last_name=None,_email=None):
        self.first_name = _first_name
        self.last_name = _last_name
        self.email = _email

    id = Column(Integer, autoincrement=True, primary_key=True)
    first_name = Column(Unicode(64), unique=True, nullable=False)
    last_name = Column(Unicode(64), unique=True, nullable=False)
    email = Column(Unicode(64), unique=True, nullable=False)
    created = Column(DateTime,default=datetime.date(datetime.now()))
    last_modified = Column(DateTime,default=datetime.date(datetime.now()))
    email = Column(Unicode(100))
    address = Column(Unicode(100))
    address_2 = Column(Unicode(100))
    city = Column(Unicode(100))
    state = Column(Unicode(100))
    zip = Column(Unicode(15))
    url = Column(Unicode(100))
    tel = Column(Unicode(32))
    tel_ext = Column(Unicode(32))
    mobile = Column(Unicode(32))
    active = Column(Boolean, default=True)
    status = Column(Integer, default=1)
    lat_lon = Column(Unicode(100), default=u"0,0")
    user_id = Column(Integer, ForeignKey('users.id', onupdate="CASCADE"))

    def __str__(self):
        return '<%s>' % self.__class__.__name__

    def __repr__(self):
        return '<%s %r>' % (self.__class__, self.__dict__)


class CompanyNote(Base):
    __tablename__='company_notes'

    query = db.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    company_id =  Column(Integer, ForeignKey('companies.id', onupdate="CASCADE", ondelete="CASCADE"))
    created = Column(DateTime,default=datetime.date(datetime.now()))
    subject  =  Column(Unicode(128), nullable=True)
    note = Column(UnicodeText, nullable=False)


class Ticket(Base):
    __tablename__='tickets'

    query = db.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    company_id =  Column(Integer, ForeignKey('companies.id', onupdate="CASCADE", ondelete="CASCADE"))
    ticket_priority_id =  Column(Integer, ForeignKey('ticket_priorities.id', onupdate="CASCADE", ondelete="CASCADE"))
    ticket_type =  Column(Integer, ForeignKey('ticket_types.id', onupdate="CASCADE", ondelete="CASCADE"))
    created = Column(DateTime,default=datetime.date(datetime.now()))
    expected_resolve_date = Column(DateTime,default=datetime.date(datetime.now()))
    is_resolved = Column(Boolean, default=False)
    subject  =  Column(Unicode(128), nullable=True)
    description = Column(UnicodeText, nullable=False)


class TicketPriority(Base):
    __tablename__='ticket_priorities'

    query = db.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(32), default=u'Unknown')
    description = Column(Unicode(255), default=u'Unknown')


class TicketType(Base):
    __tablename__='ticket_types'

    query = db.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(32), default=u'Unknown')
    type = Column(Integer, default=1)


class Shift(Base):
    __tablename__='shifts'

    query = db.query_property()

    def __init__(self, session_id=None, user_id=None, type_id=1):
        self.session_id = session_id
        self.user_id = user_id
        self.start = datetime.now()
        self.type_id = type_id

    id = Column(Integer, autoincrement=True, primary_key=True)
    session_id = Column(Unicode(128))
    start = Column(DateTime, default=datetime.now())
    end = Column(DateTime)
    user_id = Column(Integer, nullable=False)
    type_id = Column(Integer, default=1)


class AuthLevel(Base):
    __tablename__='auth_levels'

    query = db.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(64))
    description = Column(Unicode(128))

