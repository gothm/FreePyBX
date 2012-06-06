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


try:
    import twisted
except ImportError:
    raise SystemExit

from ESL import *

from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
from twisted.internet import defer
from twisted.internet.task import LoopingCall

from amfast.decoder import Decoder
from amfast.encoder import Encoder

from datetime import datetime
import sys

import socket

host = "localhost"
port = 8447

decoder = Decoder(amf3=True)
encoder = Encoder(amf3=True)



#'ESL:INCOMINGCALL:EXT:'+ext+':CONTEXT:'+context+':FROM:'+caller_id_num
def make_message(type, command, context, data, ext=None):
    m = Message()
    m.type = type
    m.command = command
    m.context = context
    m.data = data
    m.ext = ext


class Message:
    pass



class ESLBrokerNotifier(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port):

        try:
            self.sock.connect((host, port))
            print "Connected to server.\n"
        except socket.error, e:
            raise Exception("Can't connect: %s" % e[1])


    def stop(self):
        return

    def connectBroker(self):

        try:
            msg = dict({"type":"ESL","command":"CONNECT","context":"", "data": "", "ext": ""})
            objs = encoder.encode(msg)
            self.sock.send(objs)
        except socket.error, e:
            raise Exception("Can't connect: %s" % e[1])

        self.smain()


    def smain(self):
        con = ESLconnection("127.0.0.1","8888","3v3lyn888")

        if con.connected:
            con.events("plain", "all");

            while con.connected():
                e = con.recvEventTimed(1000)
                if e:
                    name = e.getHeader("Event-Name")
                    print e.serialize()

                    if name == 'CUSTOM':
                        subclass = e.getHeader("Event-Subclass")

                        if subclass == 'callcenter::info':
                            agent_context = e.getHeader("CC-Agent")
                            state = e.getHeader("CC-Agent-State")
                            if agent_context and state:
                                agent = agent_context.split("@")[0]
                                context = agent_context.split("@")[1]

                                try:
                                    #type, command, context, data, ext
                                    msg = dict({"type":"ESL","command":"NOTICE","context":context, "data": state, "ext": agent})
                                    objs = encoder.encode(msg)
                                    self.sock.send(objs)
                                    print e.serialize()
                                except:
                                    print "excepted"

                        if subclass == 'callcenter::info':
                            if e.getHeader("CC-Action") == 'agent-offering':

                                print "Agent offering..."
                                agent_context = e.getHeader("CC-Agent")

                                if len(agent_context) > 3:
                                    agent = agent_context.split("@")[0]
                                    context = agent_context.split("@")[1]

                                cid_num = e.getHeader("CC-Member-CID-Number")
                                caller_id_num = cid_num[len(cid_num)-10:]

                                try:
                                    #type, command, context, data, ext
                                    msg = dict({"type":"ESL","command":"INCOMINGCALL","context": context, "data": caller_id_num, "ext": agent})
                                    objs = encoder.encode(msg)
                                    self.sock.send(objs)
                                    print e.serialize()
                                except:
                                    print "excepted"

                    elif name == 'CHANNEL_PROGRESS':
                        ext = e.getHeader("variable_pbx_contact_user")
                        context = e.getHeader("variable_context")
                        domain = e.getHeader("variable_domain")
                        cid_num = e.getHeader("Caller-Caller-ID-Number")

                        if ext and context and domain and cid_num:
                            caller_id_num = cid_num[len(cid_num)-10:]

                            try:
                                #type, command, context, data, ext
                                msg = dict({"type":"ESL","command":"INCOMINGCALL","context": context, "data": caller_id_num, "ext": ext})
                                objs = encoder.encode(msg)
                                self.sock.send(objs)
                                print e.serialize()
                            except:
                                print "excepted"


                    elif name == 'HEARTBEAT':
                        try:
                            msg = dict({"type":"ESL","command":"HEARTBEAT","context":"", "data": "", "ext": ""})
                            objs = encoder.encode(msg)
                            self.sock.send(objs)
                        except:
                            print "excepted"



if __name__ == '__main__':

    client = ESLBrokerNotifier()
    client.connect(host, port)

    try:
        client.connectBroker()
    except KeyboardInterrupt:
        client.stop()
