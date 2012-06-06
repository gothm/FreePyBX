""" This Source Code Form is subject to the terms of the Mozilla Public
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
    remedy known factual inaccuracies."""

import logging
from freepybx.lib import helpers as h
from datetime import datetime
import pyamf
from pyamf import amf3
import pylons
from pylons.decorators import jsonify
from pylons import config
from freepybx.lib import template
from freepybx.model import *
from freepybx import model
from freepybx.model import meta
from freepybx.model.meta import *
from freepybx.model.meta import Session as db
from ESL import *

from amfast.decoder import Decoder
from amfast.encoder import Encoder

decoder = Decoder(amf3=True)
encoder = Encoder(amf3=True)

amf3.use_proxies_default = True

log = logging.getLogger(__name__)

ESL_HOST = "127.0.0.1"
ESL_PORT = "8021"
ESL_PASS = "ClueCon"

namespace = 'com.vwci.charting.model'
pyamf.register_package(model, namespace)


def fix_date(t):
    if not t:
        return ""
    return t.strftime("%m/%d/%Y %I:%M:%S %p")

def get_talk_time(ext, context):
    rows =  db.execute("SELECT coalesce(sum(billsec)/60,0) AS mins FROM cdr "
                       "WHERE (caller_id_number=:ext OR destination_number=:ext) "
                       "AND start_stamp BETWEEN CURRENT_DATE AND CURRENT_TIMESTAMP "
                       "AND bleg_uuid IS NOT NULL AND context = :context",
            {'ext':ext, 'context': context})
    r = rows.fetchone()
    db.remove()
    return r.mins

def get_volume(ext, context):
    rows =  db.execute("SELECT count(*) AS ct "
                       "FROM cdr "
                       "WHERE  (caller_id_number=:ext OR destination_number=:ext) "
                       "AND start_stamp BETWEEN CURRENT_DATE "
                       "AND CURRENT_TIMESTAMP AND bleg_uuid IS NOT NULL "
                       "AND context = :context",
            {'ext':ext, 'context': context})
    r = rows.fetchone()
    db.remove()
    return r.ct

def make_agent(name=None,volume=0,talk_time=0):
    a = Agent()
    a.agent_name = name
    a.volume = volume
    a.talk_time = talk_time

    return a

def make_broker_user(name, id, customer_id, email, tel, mobile, ext, uuid, is_online):
    b = BrokerUser()
    b.name = name
    b.id = id
    b.customer_id = customer_id
    b.email = email
    b.mobile = mobile
    b.tel = tel
    b.ext = ext
    b.uuid = uuid
    b.is_online = is_online

    return b

def make_caller(dest, cid_name, cid_num, direction, created, time_in_queue, to_user, uuid, status):
    c = Caller()
    c.dest = dest
    c.cid_name = cid_name
    c.cid_num = cid_num
    c.direction = direction
    c.created = created
    c.time_in_queue = time_in_queue
    c.to_user = to_user
    c.uuid = uuid
    c.status = status

    return c

def make_res_message(msg):
    m = ResMessage()
    m.msg = msg

    return m

class BrokerUser:
    pass

class Agent:
    pass

class Caller:
    pass

class ResMessage:
    pass

pyamf.register_class(Agent, 'com.vwci.charting.model.Agent')
pyamf.register_class(BrokerUser, 'com.vwci.broker.model.BrokerUser')
pyamf.register_class(Caller, 'com.vwci.queue.model.Caller')
pyamf.register_class(ResMessage, 'com.vwci.broker.model.ResMessage')


class VoiceWareService(object):
    '''This is the controller that acts as a broker and object serialization
    between the flash components and FreeSWITCH.'''

    def __init__(self, sid=None):
        self.sid = sid

    def getAgents(self, sid):
        agents = []
        user = User.query.filter_by(session_id=sid).first()
        if user:
            context = user.get_context()
        else:
            raise Exception("No user in session...")

        for row in User.query.filter(User.customer_id==user.customer_id).all():
            if not len(row.portal_extension):
                continue
            else:
                extension = row.portal_extension

            agent = make_agent(row.first_name+' '+row.last_name,  get_volume(extension, context), get_talk_time(extension, context))
            agents.append(agent)
        db.remove()
        return agents

    def getUsers(self, sid):
        users = []
        ep_stats = []
        user = User.query.filter_by(session_id=sid).first()

        if user:
            context = user.get_context()
        else:
            raise Exception("No session id in db matching the user calling this method.")

        for r in db.execute("SELECT DISTINCT users.first_name, users.last_name, users.id, users.customer_id, "
                            "customers.context AS context, users.portal_extension, "
                            "users.tel, users.mobile, users.username, sip_dialogs.uuid AS uuid "
                            "FROM users "
                            "INNER JOIN customers ON users.customer_id = customers.id "
                            "LEFT JOIN sip_dialogs ON sip_dialogs.presence_id = users.portal_extension || '@' || customers.context "
                            "WHERE customers.context = :context ORDER BY users.id", {'context': context}):

            for pbx_reg in PbxRegistration.query.filter(PbxRegistration.sip_realm==context).filter(PbxRegistration.sip_user==r[5]).all():
                ep_stats.append({'ip': pbx_reg.network_ip, 'port':pbx_reg.network_port})

            is_online = True if len(ep_stats) > 0 else False
            ep_stats = []

            # make_broker_user(name, id, customer_id, email, tel, mobile, ext, uuid, is_online):
            users.append(make_broker_user(r[0]+' '+r[1], r[2], r[3], r[8], r[6], r[7], r[5], r[9], is_online))

        db.remove()
        return users

    def getCallers(self, sid):
        callers = []
        user = User.query.filter_by(session_id=sid).first()
        if user:
            context = user.get_context()

        for row in PbxDid.query.filter(PbxDid.context==context).all():
            for cal in db.execute("SELECT * FROM channels WHERE dest like :did", {'did': "%"+row.did}).fetchall():
                #PbxChannel.query.filter(PbxChannel.dest.like('%'+row.did).all():
                l =  PbxChannel.query.filter_by(uuid=cal.uuid).first()
                if l:
                    to_user = l.dest
                    status = l.callstate
                else:
                    to_user = ""
                    status = ""
                direction = "inbound"
                if len(cal.cid_num) > 10:
                    cid_num = cal.cid_num[len(cal.cid_num)-10:]
                else:
                    cid_num = cal.cid_num

                time_in_queue = db.execute("SELECT now() FROM channels WHERE uuid = :uuid", {'uuid': cal.uuid}).fetchone()
                callers.append(make_caller(cal.dest, cal.cid_name,cid_num, direction, cal.created, time_in_queue[0], to_user, cal.uuid, status))

        for cal in PbxChannel.query.filter_by(context=context).distinct(PbxChannel.call_uuid).all():
            if len(cal.presence_id)>3:
                if cal.presence_id.split("@")[1] == context:
                    time_in_queue = db.execute("SELECT now() FROM channels WHERE uuid = :uuid", {'uuid': cal.uuid}).fetchone()
            callers.append(make_caller(cal.dest, cal.cid_name, cal.cid_num, "outbound", cal.created, "", cal.dest, cal.uuid, cal.callstate))

        db.remove()
        return callers

    def callExtension(self, sid, ext):
        user = User.query.filter_by(session_id=sid).first()
        if user and ext.isdigit():
            context = user.get_context()
        else:
            return

        con = ESLconnection(ESL_HOST, ESL_PORT, ESL_PASS)
        if con.connected:
            con.api("originate", "{origination_caller_id_name=Click-To-Call,ringback=\'%(2000,4000,440.0,480.0)\'}user/"+str(user.portal_extension)+"@"+str(context)+"  &transfer('"+str(ext)+" XML sbc10.vwna.com')")

    def callOutbound(self, sid, did):
        user = User.query.filter_by(session_id=sid).first()
        if user:
            context = user.get_context()
        else:
            return

        ep = db.execute("SELECT pbx_endpoints.outbound_caller_id_number AS pbx_endpoints_outbound_caller_id_number, customers.tel AS customers_tel "
                        "FROM pbx_endpoints "
                        "INNER JOIN customers on customers.context  = pbx_endpoints.user_context "
                        "WHERE customers.context = :context AND customers.id = :customer_id AND pbx_endpoints.auth_id = :auth_id",
                        {'context': context,'customer_id': user.customer_id, 'auth_id': user.portal_extension}).fetchone()

        if len(ep[0])==10:
            origination_caller_id_number = ep[0]
        else:
            origination_caller_id_number = ep[1]

        con = ESLconnection(ESL_HOST, ESL_PORT, ESL_PASS)
        if con.connected:
            con.bgapi("originate", "{ringback=\'%(2000,4000,440.0,480.0)\',origination_caller_id_name=Click-To-Call,effective_caller_id_number="+str(origination_caller_id_number)+"}user/"+str(user.portal_extension)+"@"+str(context)+" &bridge(sofia/gateway/"+str(user.get_gateway())+"/"+str(did)+")")

    def reloadCallCenter(self, sid):
        user = User.query.filter_by(session_id=sid).first()
        if user:
            if user.group_id>1:
                return
        else:
            return

        con = ESLconnection(ESL_HOST, ESL_PORT, ESL_PASS)
        if con.connected:
            con.events("plain", "all")
            msg = con.api("reload", "mod_callcenter")
        else:
            msg = "Failed!"
        return msg.getBody()

    def reloadXML(self, sid):
        user = User.query.filter_by(session_id=sid).first()
        if user:
            if user.group_id>1:
                return

        con = ESLconnection(ESL_HOST, ESL_PORT, ESL_PASS)
        if con.connected:
            con.events("plain", "all")
            msg = con.api("reloadxml")
        else:
            msg = "Failed!"
        return msg.getBody()

    def reloadProfile(self, sid, profile=None):
        user = User.query.filter_by(session_id=sid).first()
        if user:
            if user.group_id>1:
                return

        con = ESLconnection(ESL_HOST, ESL_PORT, ESL_PASS)
        if con.connected:
            con.events("plain", "all")
            msg = con.api("sofia profile "+str(profile)+" rescan reloadxml")
        else:
            msg = "Failed!"
        return msg.getBody()

    def reloadACL(self, sid):
        user = User.query.filter_by(session_id=sid).first()
        if user:
            if user.group_id>1:
                return

        con = ESLconnection(ESL_HOST, ESL_PORT, ESL_PASS)
        if con.connected:
            con.events("plain", "all")
            msg = con.api("reloadxml")
        else:
            msg = "Failed!"
        return msg.getBody()

    def showGateways(self, sid, profile=None):
        user = User.query.filter_by(session_id=sid).first()
        if user:
            if user.group_id>1:
                return

        con = ESLconnection(ESL_HOST, ESL_PORT, ESL_PASS)
        if con.connected:
            con.events("plain", "all")
            msg = con.api("sofia profile "+str(profile)+" gwlist up")
        else:
            msg = "Failed!"
        return msg.getBody()

    def sofiaStatus(self, sid):
        user = User.query.filter_by(session_id=sid).first()
        if user:
            if user.group_id>3:
                return

        con = ESLconnection(ESL_HOST, ESL_PORT, ESL_PASS)
        if con.connected:
            con.events("plain", "all")
            msg = con.api("sofia status")
        else:
            msg = "Failed!"
        return msg.getBody()

    def showRegUsers(self, sid, profile=None):
        user = User.query.filter_by(session_id=sid).first()
        if user:
            if user.group_id>3:
                return

        con = ESLconnection(ESL_HOST, ESL_PORT, ESL_PASS)
        if con.connected:
            con.events("plain", "all")
            msg = con.api("sofia status profile "+str(profile)+ " reg")
        else:
            msg = "Failed!"
        return msg.getBody()





services = {
    'VoiceWareService': VoiceWareService
}



FlashGatewayController = h.WSGIGateway(services, logger=log, debug=True)
