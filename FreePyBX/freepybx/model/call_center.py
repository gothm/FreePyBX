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


class CallCenterQueue(Base):
    __tablename__='call_center_queues'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    domain = Column(Unicode(64), default=u"sip.vwna.com")
    context = Column(Unicode(128), default=u"sip.vwna.com")
    name = Column(Unicode(64))
    audio_type = Column(Integer)
    audio_name = Column(Unicode(255))
    strategy = Column(Unicode(64), default=u'longest-idle-agent')
    moh_sound = Column(Unicode(255), default=u'local_stream://moh')
    time_base_score = Column(Unicode(32), default=u'system')
    max_wait_time = Column(Integer, default=300)
    max_wait_time_with_no_agent = Column(Integer, default=300)
    max_wait_time_with_no_agent_reached = Column(Integer, default=90)
    tier_rules_apply = Column(Boolean, default=False)
    tier_rule_wait_second = Column(Integer, default=300)
    tier_rule_wait_multiply_level = Column(Boolean, default=True)
    tier_rule_agent_no_wait = Column(Boolean, default=True)
    discard_abandoned_after = Column(Integer, default=300)
    abandoned_resume_allowed = Column(Boolean, default=False)
    failed_route_id = Column(Integer, ForeignKey('pbx_routes.id', onupdate="CASCADE", ondelete="CASCADE"))
    record_calls = Column(Boolean, default=False)
    announce_position = Column(Boolean, default=False)
    announce_sound = Column(Unicode(1024))
    announce_frequency = Column(Integer, default=60)
    approx_hold_time = Column(Integer, default=300)

    def __str__(self):
        return self.id


class CallCenterAgentLog(Base):
    __tablename__='call_center_agent_logs'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    agent = Column(Unicode(128), nullable=False)
    queue = Column(Unicode(128), nullable=False)
    log_epoch = Column(Integer, default=0)
    log_type = Column(Integer, default=0)
    data =  Column(Unicode(1024), nullable=False)
    uuid = Column(Unicode(255))


class CallCenterAgent(Base):
    __tablename__='call_center_agents'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    domain = Column(Unicode(64), default=u"sip.vwna.com")
    context = Column(Unicode(128), default=u"sip.vwna.com")
    extension = Column(Unicode(15), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id', onupdate="CASCADE", ondelete="CASCADE"))
    pbx_endpoint_id = Column(Integer, ForeignKey('pbx_endpoints.id', onupdate="CASCADE", ondelete="CASCADE"))
    timeout = Column(Integer, default=20)
    name = Column(Unicode(255))
    system = Column(Unicode(255))
    uuid = Column(Unicode(255))
    type = Column(Unicode(255))
    contact = Column(Unicode(255))
    status = Column(Unicode(255))
    state = Column(Unicode(255))
    max_no_answer = Column(Integer, default=0)
    wrap_up_time = Column(Integer, default=0)
    reject_delay_time = Column(Integer, default=0)
    busy_delay_time = Column(Integer, default=0)
    no_answer_delay_time = Column(Integer, default=0)
    last_bridge_start = Column(Integer, default=0)
    last_bridge_end = Column(Integer, default=0)
    last_offered_call = Column(Integer, default=0)
    last_status_change = Column(Integer, default=0)
    no_answer_count = Column(Integer, default=0)
    calls_answered = Column(Integer, default=0)
    talk_time = Column(Integer, default=0)
    ready_time = Column(Integer, default=0)
    record_calls = Column(Integer, default=0)


class CallCenterCaller(Base):
    __tablename__='call_center_callers'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    queue = Column(Unicode(255))
    system = Column(Unicode(255))
    uuid = Column(Unicode(255), nullable=False, default=u'')
    session_uuid = Column(Unicode(255), nullable=False, default=u'')
    cid_number = Column(Unicode(255))
    cid_name = Column(Unicode(255))
    system_epoch = Column(Integer, default=0)
    joined_epoch = Column(Integer, default=0)
    rejoined_epoch = Column(Integer, default=0)
    bridge_epoch = Column(Integer, default=0)
    abandoned_epoch = Column(Integer, default=0)
    base_score = Column(Integer, default=0)
    skill_score = Column(Integer, default=0)
    serving_agent = Column(Unicode(255))
    serving_system = Column(Unicode(255))
    state = Column(Unicode(255))


class CallCenterTier(Base):
    __tablename__='call_center_tiers'

    query = Session.query_property()

    def __init__(self, queue=None, agent=None, state='Waiting', level=None, position=None):
        self.queue = queue
        self.agent = agent
        self.state = state
        self.level = level
        self.position = position

    id = Column(Integer, autoincrement=True, primary_key=True)
    queue_id = Column(Integer, ForeignKey('call_center_queues.id', onupdate="CASCADE", ondelete="CASCADE"))
    agent_id = Column(Integer, ForeignKey('call_center_agents.id', onupdate="CASCADE", ondelete="CASCADE"))
    extension = Column(Unicode(15), nullable=True)
    queue = Column(Unicode(255))
    agent = Column(Unicode(255))
    state = Column(Unicode(255))
    level = Column(Integer)
    position = Column(Integer, nullable=False, default=0)
