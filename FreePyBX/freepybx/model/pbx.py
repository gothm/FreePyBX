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
from freepybx.model import company_contexts, condition_actions, user_endpoints

class PbxContext(Base):
    __tablename__='pbx_contexts'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    company_id =  Column(Integer, ForeignKey('companies.id', onupdate="CASCADE", ondelete="CASCADE"))
    domain = Column(Unicode(64), unique=True)
    profile = Column(Unicode(64))
    context = Column(Unicode(128))
    caller_id_name = Column(Unicode(64))
    caller_id_number = Column(Unicode(15))
    gateway = Column(Unicode(64), default=u'default')

    def __init__(self, company_id=None, domain=None, context=None,
                 gateway=None, profile=None, caller_id_name=None,
                 caller_id_number=None ):
        self.company_id = company_id
        self.domain = domain
        self.context = context
        self.gateway = gateway
        self.profile = profile
        self.caller_id_name = caller_id_name
        self.caller_id_number = caller_id_number

    def by_domain(self, domain=None):
        return Session.query(PbxContext).filter_by(domain=domain).first()


class PbxIVR(Base):
    __tablename__='pbx_ivrs'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id', onupdate="CASCADE", ondelete="CASCADE"))
    domain = Column(Unicode(64), default=u"sip.vwna.com")
    context = Column(Unicode(128), default=u"sip.vwna.com")
    created = Column(DateTime, default=datetime.date(datetime.now()))
    name = Column(Unicode(64))
    audio_type = Column(Integer)
    data = Column(Unicode(64))
    timeout = Column(Integer)
    direct_dial = Column(Boolean, default=True)
    timeout_destination = Column(Integer, ForeignKey('pbx_routes.id', onupdate="CASCADE", ondelete="CASCADE"))

    def __str__(self):
        return self.id


class PbxIVROption(Base):
    __tablename__='pbx_ivr_options'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    pbx_ivr_id = Column(Integer, ForeignKey('pbx_ivrs.id', onupdate="CASCADE", ondelete="CASCADE"))
    option = Column(Unicode(1))
    pbx_route_id = Column(Integer, ForeignKey('pbx_routes.id', onupdate="CASCADE", ondelete="CASCADE"))

    def __str__(self):
        return self.id


class PbxVirtualExtension(Base):
    __tablename__='pbx_virtual_extensions'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    domain = Column(Unicode(64), default=u"sip.vwna.com")
    context = Column(Unicode(128), default=u"sip.vwna.com")
    extension = Column(Unicode(4), nullable=False)
    did = Column(Unicode(15), nullable=False)

    def __str__(self):
        return self.id


class PbxCallerIDRoute(Base):
    __tablename__='pbx_caller_id_routes'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    domain = Column(Unicode(64), default=u"sip.vwna.com")
    context = Column(Unicode(128), default=u"sip.vwna.com")
    cid_number = Column(Unicode(15), nullable=False)
    pbx_route_id = Column(Integer, ForeignKey('pbx_routes.id', onupdate="CASCADE", ondelete="CASCADE"))

    def __str__(self):
        return self.id


class PbxBlacklistedNumber(Base):
    __tablename__='pbx_blacklisted_numbers'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    domain = Column(Unicode(64), default=u"sip.vwna.com")
    context = Column(Unicode(128), default=u"sip.vwna.com")
    cid_number = Column(Unicode(15), nullable=False)

    def __str__(self):
        return self.id


class PbxVirtualMailbox(Base):
    __tablename__='pbx_virtual_mailboxes'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    domain = Column(Unicode(64), default=u"sip.vwna.com")
    context = Column(Unicode(128), default=u"sip.vwna.com")
    extension = Column(Unicode(4), nullable=False)
    pin = Column(Unicode(4), nullable=False)
    skip_greeting = Column(Boolean, default=False)

    def __str__(self):
        return self.id


class PbxTTS(Base):
    __tablename__='pbx_tts'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id', onupdate="CASCADE", ondelete="CASCADE"))
    domain = Column(Unicode(64), default=u"sip.vwna.com")
    context = Column(Unicode(128), default=u"sip.vwna.com")
    created = Column(DateTime, default=datetime.date(datetime.now()))
    name = Column(Unicode(64), default=u'Unknown')
    voice = Column(Unicode(64))
    text = Column(UnicodeText)

    def __str__(self):
        return self.id


class PbxTODRoute(Base):
    __tablename__='pbx_tod_routes'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    domain = Column(Unicode(64), default=u"sip.vwna.com")
    context = Column(Unicode(128), default=u"sip.vwna.com")
    name = Column(Unicode(64), default=u'Unknown')
    day_start = Column(Integer, default=1)
    day_end = Column(Integer, default=7)
    time_start = Column(Unicode(9), default=u'T00:00:00')
    time_end = Column(Unicode(9), default=u'T00:00:00')
    match_route_id = Column(Integer, ForeignKey('pbx_routes.id', onupdate="CASCADE", ondelete="CASCADE"))
    nomatch_route_id = Column(Integer, ForeignKey('pbx_routes.id', onupdate="CASCADE", ondelete="CASCADE"))

    def __str__(self):
        return self.id


class PbxRecording(Base):
    __tablename__='pbx_pbx_recordings'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id', onupdate="CASCADE", ondelete="CASCADE"))
    domain = Column(Unicode(64), default=u"sip.vwna.com")
    context = Column(Unicode(128), default=u"sip.vwna.com")
    created = Column(DateTime, default=datetime.date(datetime.now()))
    recording_type = Column(Integer)
    name = Column(UnicodeText)
    path = Column(Unicode(64))

    def __str__(self):
        return self.id


class PbxDid(Base):
    __tablename__='pbx_dids'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    did = Column(Unicode(20), nullable=False,  unique=True)
    active = Column(Boolean, default=True)
    domain = Column(Unicode(64), default=u"sip.vwna.com")
    context = Column(Unicode(128), default=u"sip.vwna.com")
    t38 = Column(Boolean, default=False)
    cnam = Column(Boolean, default=False)
    e911 = Column(Boolean, default=False)
    company_id = Column(Integer, ForeignKey('companies.id', onupdate="CASCADE", ondelete="CASCADE"))
    pbx_route_id = Column(Integer, default=0)

    def __init__(self, did, company_id, context, domain, t38, e911, cnam, active=True, pbx_route_id=0):
        self.did = did
        self.company_id = company_id
        self.context = context
        self.domain = domain
        self.t38 = t38
        self.e911 = e911
        self.cnam = cnam
        self.active = active
        self.pbx_route_id = pbx_route_id

    def get_domain(self):
        return self.domain

    def __str__(self):
        return self.did


class PbxProfile(Base):
    __tablename__='pbx_profiles'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(64), nullable=True)
    odbc_credentials = Column(Unicode(64), nullable=True)
    manage_presence = Column(Boolean, default=True)
    presence_db_name = Column(Unicode(64), default=u'share_presence')
    presence_hosts =  Column(UnicodeText, default=u'sip.mydomain.com')
    send_presence_on_register = Column(Boolean, default=True)
    delete_subs_on_register = Column(Boolean, default=True)
    caller_id_type = Column(Unicode(16), default=u'rpid')
    auto_jitterbuffer_msec = Column(Integer, default=120)
    apply_inbound_acl = Column(Unicode(64), default=u'gateways')
    dialplan = Column(Unicode(64), default=u'XML,enum')
    ext_rtp_ip = Column(Unicode(64), default=u"auto")
    ext_sip_ip = Column(Unicode(64), default=u"auto")
    rtp_ip = Column(Unicode(64), default=u"auto")
    sip_ip = Column(Unicode(64), default=u"auto")
    sip_port = Column(Integer, nullable=False, default=5060)
    sql_in_transactions = Column(Boolean, default=False)
    nonce_ttl = Column(Integer, default=60)
    use_rtp_timer = Column(Boolean, default=True)
    rtp_timer_name = Column(Unicode(64), default=u"soft")
    codec_prefs = Column(Unicode(255), default=u'PCMU,PCMA,G722,G726,H264,H263')
    inbound_codec_negotiation = Column(Unicode(64), default=u"generous")
    rtp_timeout_sec = Column(Integer, default=300)
    rtp_hold_timeout_sec = Column(Integer, default=1800)
    rfc2833_pt = Column(Integer, default=101)
    dtmf_duration = Column(Integer, default=100)
    dtmf_type = Column(Unicode(64), default=u'rfc2833')
    session_timeout= Column(Integer, default=1800)
    multiple_registrations = Column(Unicode(64), default=u'contact')
    vm_from_email = Column(Unicode(64), default=u'voicemail@freeswitch.org')
    accept_blind_reg = Column(Boolean, default=False)
    auth_calls = Column(Boolean, default=True)
    auth_all_packets = Column(Boolean, default=False)
    log_auth_failures = Column(Boolean, default=True)
    disable_register = Column(Boolean, default=False)
    codec_ms = Column(Integer, default=20)
    minimum_session_expires = Column(Integer, default=120)
    email_domain = Column(Unicode(64), default=u'freeswitch.org')


    def get_gateways(self):
        return Session.query(PbxGateway).filter_by(pbx_profile_id=self.id)

    def __str__(self):
        return "sip profile: %s:%s" % (self.ext_rtp_ip, self.sip_port)

    def __repr__(self):
        return  u'%r' % self.__dict__


class PbxGateway(Base):
    __tablename__='pbx_gateways'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(64), nullable=True)
    pbx_profile_id = Column(Integer, ForeignKey('pbx_profiles.id', onupdate="CASCADE", ondelete="CASCADE"))
    username = Column(Unicode(64), nullable=True)
    password = Column(Unicode(64), nullable=True)
    proxy = Column(Unicode(64), nullable=True)
    mask =  Column(Unicode(15), default=u'32')
    register = Column(Boolean, default=False)
    register_proxy = Column(Unicode(128), nullable=True)
    register_transport = Column(Unicode(64), default=u"udp")
    extension = Column(Unicode(64), nullable=True)
    realm = Column(Unicode(64), nullable=True)
    from_domain = Column(Unicode(64), nullable=True)
    from_user = Column(Unicode(32), nullable=True)
    expire_seconds = Column(Integer, nullable=False, default=600)
    retry_seconds = Column(Integer, nullable=False, default=30)
    ping = Column(Unicode(4), default=u"60")
    context = Column(Unicode(32), default=u"default")
    caller_id_in_from = Column(Boolean, default=False)
    contact_params = Column(Unicode(32), nullable=True)
    rfc5626 = Column(Boolean, default=True)
    reg_id = Column(Integer, nullable=True, default=1)

    def __str__(self):
        return self.name


class PbxAclBlacklist(Base):
    __tablename__='pbx_acl_blacklist'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(64), nullable=True)
    ip = Column(Unicode(15), nullable=False)
    mask = Column(Unicode(15), default=u'24')

    def __str__(self):
        return self.name


class PbxRoute(Base):
    __tablename__='pbx_routes'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    pbx_route_type_id = Column(Integer, ForeignKey('pbx_route_types.id', onupdate="CASCADE", ondelete="CASCADE"), default=1)
    pbx_to_id = Column(Integer)
    context = Column(Unicode(64), default=u'default')
    domain = Column(Unicode(128), default=u'sip.vwna.com')
    name = Column(Unicode(128), nullable=False)
    continue_route = Column(Boolean, default=False)
    voicemail_enabled = Column(Boolean, default=False)
    voicemail_ext = Column(Unicode(64))


class PbxRouteType(Base):
    __tablename__='pbx_route_types'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(64))
    description = Column(Unicode(255))

    def __str__(self):
        return self.id


class PbxCondition(Base):
    __tablename__='pbx_conditions'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    pbx_route_id = Column(Integer, ForeignKey('pbx_routes.id', onupdate="CASCADE", ondelete="CASCADE"))
    context = Column(Unicode(64), default=u'default')
    domain = Column(Unicode(128), default=u'sip.vwna.com')
    field = Column(Unicode(128), default=u'destination_number')
    expression = Column(Unicode(128), default=u'^(.*)$')

    condition_actions = relationship('PbxAction', secondary=condition_actions, backref='pbx_conditions')


class PbxConditionTmpl(Base):
    __tablename__='pbx_condition_tmpl'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    pbx_route_type_id = Column(Integer, ForeignKey('pbx_route_types.id', onupdate="CASCADE", ondelete="CASCADE"))
    context = Column(Unicode(64), default=u'default')
    domain = Column(Unicode(128), default=u'sip.vwna.com')
    field = Column(Unicode(128), default=u'destination_number')
    expression = Column(Unicode(128), default=u'^(.*)$')


class PbxAction(Base):
    __tablename__='pbx_actions'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    pbx_condition_id = Column(Integer, ForeignKey('pbx_conditions.id', onupdate="CASCADE", ondelete="CASCADE"))
    context = Column(Unicode(64), default=u'default')
    domain = Column(Unicode(128), default=u'sip.vwna.com')
    is_authenticated = Column(Boolean, default=False)
    precedence = Column(Integer, nullable=False, default=10)
    application = Column(Unicode(64), default=u'bridge')
    data = Column(Unicode(128), default=u'$1 XML default')

    def __repr__(self):
        return "<%r>" % self.__dict__


class PbxActionTmpl(Base):
    __tablename__='pbx_action_tmpl'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    pbx_condition_tmpl_id = Column(Integer, ForeignKey('pbx_condition_tmpl.id', onupdate="CASCADE", ondelete="CASCADE"))
    context = Column(Unicode(64), default=u'default')
    domain = Column(Unicode(128), default=u'sip.vwna.com')
    is_authenticated = Column(Boolean, default=False)
    precedence = Column(Integer, nullable=False, default=10)
    application = Column(Unicode(64), default=u'bridge')
    data = Column(Unicode(128), default=u'$1 XML default')

    def __repr__(self):
        return "<%r>" % self.__dict__


class PbxGroup(Base):
    __tablename__='pbx_groups'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    context = Column(Unicode(64), default=u'default')
    name = Column(Unicode(64))
    ring_strategy = Column(Unicode(3), default=u'sim')
    no_answer_destination = Column(Integer)
    timeout = Column(Unicode(64))

    def __repr__(self):
        return "<%r>" % self.__dict__


class PbxGroupMember(Base):
    __tablename__='pbx_group_members'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    pbx_group_id = Column(Integer, ForeignKey('pbx_groups.id', onupdate="CASCADE", ondelete="CASCADE"))
    extension  = Column(Unicode(15))

    def __repr__(self):
        return "<%r>" % self.__dict__


class PbxEndpoint(Base):
    __tablename__='pbx_endpoints'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    auth_id = Column(Unicode(64), nullable=False)
    password = Column(Unicode(64), nullable=False, default=u"O9876543$")
    outbound_caller_id_name = Column(Unicode(64), nullable=False, default=u"Anonymous")
    outbound_caller_id_number = Column(Unicode(64), nullable=False)
    internal_caller_id_name = Column(Unicode(64), nullable=False, default=u"Anonymous")
    internal_caller_id_number = Column(Unicode(64), nullable=False, default=auth_id)
    user_context = Column(Unicode(64), nullable=False, default=u"sip.vwna.com")
    force_transfer_context = Column(Unicode(64), nullable=False, default=u"sip.vwna.com")
    user_originated = Column(Unicode(64), nullable=False, default=True)
    mac = Column(Unicode(12))
    toll_allow = Column(Unicode(64), nullable=False, default=u"domestic")
    accountcode = Column(Unicode(64), nullable=False, default=u"0")
    vm_email = Column(Unicode(64), nullable=True)
    vm_password = Column(Unicode(64), nullable=True, default=password)
    vm_attach_email = Column(Boolean, default=False)
    vm_delete = Column(Boolean, default=False)
    sip_force_contact = Column(Unicode(64), nullable=False, default=u"nat-connectile-dysfunction")
    transfer_fallback_extension = Column(Unicode(64), nullable=False, default=u"operator")
    ring_strategy = Column(Unicode(32), default=u'sequential')
    find_me = Column(Boolean, default=False)
    follow_me_1 = Column(Unicode(15))
    follow_me_2 = Column(Unicode(15))
    follow_me_3 = Column(Unicode(15))
    follow_me_4 = Column(Unicode(15))
    call_timeout = Column(Integer)
    timeout_destination = Column(Integer)
    record_outbound_calls = Column(Boolean, default=False)
    record_inbound_calls = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id', onupdate="CASCADE", ondelete="CASCADE"))

    def __str__(self):
        return self.id

    def form_dict(self):
        endpoint = {}
        endpoint['id'] = self.id
        endpoint['password'] = self.password

        return endpoint


class PbxDeviceType(Base):
    __tablename__='pbx_device_types'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(64))
    description = Column(Unicode(128))
    supported_firmware = Column(Unicode(255))
    cfg_template = Column(UnicodeText)
    notes = (Column(UnicodeText))
    is_provisionable = Column(Boolean, default=False)
    xml_directory = Column(Boolean, default=False)


class DeviceManufacturer(Base):
    __tablename__='pbx_device_manufacturers'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(64))
    description = Column(Unicode(128))
    supported = Column(Boolean, default=False)


class PbxCdr(Base):
    __tablename__='cdr'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    caller_id_name = Column(Unicode(64))
    caller_id_number = Column(Unicode(64))
    destination_number = Column(Unicode(64))
    context = Column(Unicode(64))
    start_stamp = Column(DateTime,default=datetime.now())
    answer_stamp = Column(DateTime,default=datetime.now())
    end_stamp = Column(DateTime,default=datetime.now())
    duration = Column(Integer, default=0)
    billsec = Column(Integer, default=0)
    hangup_cause = Column(Unicode(128))
    uuid = Column(Unicode(64))
    bleg_uuid = Column(Unicode(64))
    accountcode = Column(Unicode(16))
    local_ip_v4 = Column(Unicode(15))
    read_codec = Column(Unicode(128))
    write_codec = Column(Unicode(128))
    call_direction = Column(Unicode(16))
    user_id = Column(Unicode(16))
    company_id = Column(Unicode(16))
    extension = Column(Unicode(16))

    def __repr__(self):
        return "PbxCdr(%(id)s)" % self.__dict__


class PbxDNC(Base):
    __tablename__='pbx_dnc'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    context = Column(Unicode(64), nullable=False)
    domain = Column(Unicode(128), nullable=False)
    created = Column(DateTime, default=datetime.date(datetime.now()))
    did = Column(Unicode(20), nullable=False)


class PbxConferenceBridge(Base):
    __tablename__='pbx_conference_bridges'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    context = Column(Unicode(64), default=u'sip.vwna.com')
    domain = Column(Unicode(128), default=u'sip.vwna.com')
    extension = Column(Unicode(128), nullable=False)
    pin = Column(Unicode(4), default=u'7654')


class PbxFax(Base):
    __tablename__='pbx_faxes'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    context = Column(Unicode(64), default=u'sip.vwna.com')
    domain = Column(Unicode(128), default=u'sip.vwna.com')
    extension = Column(Unicode(128), nullable=False)

class PbxRegistration(Base):
    __tablename__='sip_registrations'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    call_id = Column(Unicode(255))
    sip_user = Column(Unicode(255))
    sip_host = Column(Unicode(255))
    presence_hosts = Column(Unicode(255))
    contact = Column(Unicode(1024))
    status = Column(Unicode(255))
    rpid = Column(Unicode(255))
    expires = Column(Integer)
    user_agent = Column(Unicode(255))
    server_user = Column(Unicode(255))
    server_host = Column(Unicode(255))
    profile_name = Column(Unicode(255))
    hostname = Column(Unicode(255))
    network_ip = Column(Unicode(255))
    network_port = Column(Unicode(255))
    sip_username = Column(Unicode(255))
    sip_realm = Column(Unicode(255))
    mwi_user = Column(Unicode(255))
    mwi_host = Column(Unicode(255))
    orig_server_host = Column(Unicode(255))
    orig_hostname = Column(Unicode(255))

class VoiceMail(Base):
    __tablename__='voicemail_msgs'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    created_epoch = Column(Integer, default=0)
    read_epoch = Column(Integer, default=0)
    username = Column(Unicode(255))
    domain = Column(Unicode(255))
    uuid = Column(Unicode(255))
    cid_name = Column(Unicode(255))
    cid_number = Column(Unicode(255))
    in_folder = Column(Unicode(255))
    file_path = Column(Unicode(255))
    message_len = Column(Integer, default=0)
    flags = Column(Unicode(255))
    read_flags = Column(Unicode(255))
    forwarded_by = Column(Unicode(255))


class PbxDialog(Base):
    __tablename__='sip_dialogs'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    call_id = Column(Unicode(255))
    uuid = Column(Unicode(255))
    sip_to_user = Column(Unicode(255))
    sip_to_host = Column(Unicode(255))
    sip_from_user = Column(Unicode(255))
    sip_from_host = Column(Unicode(255))
    contact_user = Column(Unicode(255))
    contact_host = Column(Unicode(255))
    state = Column(Unicode(255))
    direction = Column(Unicode(255))
    user_agent = Column(Unicode(255))
    profile_name = Column(Unicode(255))
    hostname = Column(Unicode(255))
    contact = Column(Unicode(255))
    presence_id = Column(Unicode(255))
    presence_data = Column(Unicode(255))
    call_info = Column(Unicode(255))
    call_info_state = Column(Unicode(255))
    expires = Column(Integer, default=0)
    status = Column(Unicode(255))
    rpid = Column(Unicode(255))
    sip_to_tag = Column(Unicode(255))
    sip_from_tag = Column(Unicode(255))
    rcd = Column(Integer, default=0)


class PbxChannel(Base):
    __tablename__='channels'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    uuid = Column(Unicode(255))
    direction = Column(Unicode(32))
    created = Column(Unicode(128))
    created_epoch = Column(Integer, nullable=False, default=0)
    name = Column(Unicode(1024))
    state = Column(Unicode(64))
    cid_name = Column(Unicode(1024))
    cid_num = Column(Unicode(255))
    ip_addr = Column(Unicode(255))
    dest = Column(Unicode(1024))
    application = Column(Unicode(128))
    application_data = Column(Unicode(4096))
    dialplan = Column(Unicode(128))
    context = Column(Unicode(128))
    read_codec = Column(Unicode(128))
    read_rate = Column(Unicode(32))
    read_bit_rate = Column(Unicode(32))
    write_codec = Column(Unicode(128))
    write_rate = Column(Unicode(32))
    write_bit_rate = Column(Unicode(32))
    secure = Column(Unicode(32))
    hostname = Column(Unicode(255))
    presence_id = Column(Unicode(4096))
    presence_data = Column(Unicode(4096))
    callstate = Column(Unicode(64))
    callee_name = Column(Unicode(1024))
    callee_num = Column(Unicode(255))
    callee_direction = Column(Unicode(15))
    call_uuid = Column(Unicode(255))
    sent_callee_name = Column(Unicode(1024))
    sent_callee_num = Column(Unicode(255))


class e911Address(Base):
    __tablename__='e911_addresses'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    company_id =  Column(Integer, ForeignKey('companies.id', onupdate="CASCADE", ondelete="CASCADE"))
    house_num = Column(Unicode(32))
    house_num_suffix = Column(Unicode(32))
    prefix_directional = Column(Integer, ForeignKey('e911_directional_types.id', onupdate="CASCADE", ondelete="CASCADE"))
    street_name = Column(Unicode(32))
    street_suffix = Column(Integer, ForeignKey('e911_street_types.id', onupdate="CASCADE", ondelete="CASCADE"))
    post_directional = Column(Integer, ForeignKey('e911_directional_types.id', onupdate="CASCADE", ondelete="CASCADE"))
    msag_community = Column(Unicode(32))
    state_province = Column(Unicode(32))
    county_id = Column(Unicode(32))
    country = Column(Unicode(32))
    tar_code = Column(Unicode(32))
    postal_code = Column(Unicode(32))
    building = Column(Unicode(32))
    floor = Column(Unicode(32))
    unit_num = Column(Unicode(32))
    unit_type = Column(Integer, ForeignKey('e911_unit_types.id', onupdate="CASCADE", ondelete="CASCADE"))
    location_description = Column(UnicodeText)
    editable = Column(Boolean, default=True)


class e911DirectionalType(Base):
    __tablename__='e911_directional_types'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(32))


class e911UnitType(Base):
    __tablename__='e911_unit_types'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(32))


class e911StreetType(Base):
    __tablename__='e911_street_types'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(32))
