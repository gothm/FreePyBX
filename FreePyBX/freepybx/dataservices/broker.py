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

import re
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from simplejson import loads, dumps
from freepybx.model import *
from freepybx.model import meta
from freepybx.model.meta import *

from datetime import datetime
import pyamf
import sys

Session = scoped_session(sessionmaker(autoflush=True,autocommit=True,expire_on_commit=False))
Session.configure(bind=create_engine('postgresql://pbxuser:secretpass1@127.0.0.1/pbx'))

decoder = Decoder(amf3=True)
encoder = Encoder(amf3=True)

ESL_HOST = "127.0.0.1"
ESL_PORT = "8888"
ESL_PASS = "3v3lyn888"

def make_message(type, command, context, data, ext=None):
    m = Message()
    m.type = type
    m.command = command
    m.context = context
    m.data = data
    m.ext = ext
    
class Message:
    pass


class Broker(Protocol):

    def __init__(self, users):
        self.users = users
        self.sid = None
        self.state = "UNREG"
        self.extension = None
        self.context = None
        self.name = None
        self.context = None

    def connectionLost(self, reason):
        if self.users.has_key(self.sid):
            del self.users[self.sid]

    def dataReceived(self, data):  
        if self.state == "UNREG":
            self.register_handler(data)
        else:
            self.message_handler(data)

    def register_handler(self, data):
        obj = decoder.decode(data) 
        
        if obj.has_key('type'):
            self.users['ESL'] = self
            self.state = "REGISTERED"
            print "ESL Connected..."
            return
        
        self.sid = obj['sid']
        u = Session.query(User.first_name, User.last_name, User.portal_extension, User.tel, \
                          User.company_id, Company.context).join(Company)\
                          .filter(Company.id==User.company_id).filter(User.session_id==obj['sid']).first()
        self.name = u[0]+' '+u[1]
        self.extension = u[2]
        self.context = u[5]
        self.users[self.sid] = self
        print "There are now %d connections." % len(self.users)
        self.state = "REGISTERED"
        msg = dict({"command":"REGISTERED","context": self.context, "message": str(self.name) + " connected."})
        objs = encoder.encode(msg)   
        self.broadcast(objs, self.context)

    def message_handler(self, data):        
        obj = decoder.decode(data)            
        cmd = obj['command']     
        
        if obj.has_key('type'):
            if obj['type'] == 'ESL':                    
                if cmd == 'NOTICE':
                    msg = dict({"command":"NOTICE", "message": "Call for agent " + obj['ext'] + " State: " + obj['data']})
                    objs = encoder.encode(msg)       
                    self.broadcast(objs, obj['context'])                    
                elif cmd == 'INCOMINGCALL':
                    msg = dict({"command":"INCOMINGCALL", "message": "Incoming call: You have a call from " + obj['data'], "ext": obj['ext'], "caller": obj['data']})
                    objs = encoder.encode(msg)    
                    self.broadcast(objs, obj['context'], obj['ext'])     
                elif cmd == 'CONNECT':
                    connections['ESLCONNECT'] = self    
                elif cmd == 'HEARTBEAT':
                    print "ESL Heartbeat"   
        else:
            
            if cmd == 'HEARTBEAT':
                print "Heartbeat"
            elif cmd == 'ROUTECALL':
                con = ESLconnection(ESL_HOST, ESL_PORT, ESL_PASS) 
                if con.connected:
                    uuid = str(obj['message']).split(":")[0]
                    ch = Session.execute("SELECT pbx_dids.context FROM pbx_dids INNER JOIN channels ON channels.dest = pbx_dids.did WHERE uuid=:uuid",{'uuid': uuid}).fetchone()
                    to_route = str(obj['message']).split(":")[1]
                    con.bgapi("uuid_transfer", uuid+" -both "+" "+to_route+" XML "+str(ch[0]));                                
            elif cmd == 'INSTANTMESSAGE':
                msg = dict({"command":"INCOMINGIM","message": str(obj['message']).split(":")[5], "name": str(obj['name']), "id": str(obj['id'])})
                for key in msg:
                    print "key: " + key + "  value: " + msg[key]
                objs = encoder.encode(msg)    
                self.broadcast(objs, self.context, str(obj['message']).split(":")[7])                                     
              
        return        

    def broadcast(self, obj, context, ext=None):        
        for sid, protocol in self.users.iteritems():
            if protocol.context == context and not ext:
                protocol.transport.write(obj)
            else:
                if protocol.context == context and protocol.extension == ext:
                    protocol.transport.write(obj)            
            

class BrokerFactory(Factory):
    protocol = Broker

    def __init__(self):
        self.users = {} 
        
    def buildProtocol(self, addr):
        return Broker(self.users)
    

class SocketPolicyProtocol(Protocol):

    def connectionMade(self):
        self.buffer = ''

    def dataReceived(self, data):
        self.buffer += data

        if self.buffer.startswith('<policy-file-request/>'):
            self.transport.write(self.factory.getPolicyFile(self))
            self.transport.loseConnection()


class SocketPolicyFactory(Factory):
    protocol = SocketPolicyProtocol

    def __init__(self, policy_file):
        self.policy_file = policy_file

    def getPolicyFile(self, protocol):
        return open(self.policy_file, 'rt').read()


if __name__ == '__main__':
    reactor.listenTCP(8447, BrokerFactory(), interface='0.0.0.0')
    reactor.listenTCP(843, SocketPolicyFactory('freepybx/dataservices/crossdomain.xml'),
                      interface='0.0.0.0')
    print "Server started on 8447. Accepting connections..."
    reactor.run()
    
    
    
