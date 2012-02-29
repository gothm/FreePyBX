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


import logging
from datetime import datetime
from pylons import request, response, session, config, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from freepybx.lib.base import BaseController, render
from freepybx.model import meta
from freepybx.model.meta import *
from freepybx.lib.util import *
from itertools import chain
from genshi import HTML
from pylons.decorators.rest import restrict
from genshi import HTML
import formencode
from formencode import validators
from freepybx.lib.pymap.imap import Pymap
from freepybx.lib.auth import *
from freepybx.lib.validators import *
from decorator import decorator
from pylons.decorators.rest import restrict
import formencode
from formencode import validators
from pylons.decorators import validate
from simplejson import loads, dumps
from webob import Request, Response
import simplejson as json
import transaction
import pprint
import os, sys
from stat import *
from webob import Request, Response
import cgi
import simplejson as json
from simplejson import loads, dumps
import os, sys
import simplejson as json
from simplejson import loads, dumps
import urllib, urllib2
from freepybx.model import meta
from freepybx.model.meta import *
from freepybx.model.meta import Session as db
import cgitb; cgitb.enable()


logged_in = IsLoggedIn()
log = logging.getLogger(__name__)

DEBUG=False

fs_vm_dir = config['app_conf']['fs_vm_dir']
ESL_HOST = config['app_conf']['esl_host']
ESL_PORT = config['app_conf']['esl_port']
ESL_PASS = config['app_conf']['esl_pass']


class DataInputError(Exception):
    message=""

    def __init__(self, message=None):
        Exception.__init__(self, message or self.message)

class CallCenterController(BaseController):

    @authorize(logged_in)
    def queues(self):
        items=[]
        for queue in CallCenterQueue.query.filter_by(context=session['context']).all(): 
            items.append({'id': queue.id, 'name': queue.name})

        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)     
    
    @authorize(logged_in)
    def ccq_add(self):
        schema = QueueForm()
        try:
            form_result = schema.to_python(request.params)
            ccq = CallCenterQueue()
            ccq.name = form_result['name']
            ccq.context = session['context']
            ccq.domain = session['context']
            ccq.audio_type = form_result.get('audio_name').split(",")[0]
            ccq.audio_name = form_result.get('audio_name').split(",")[1]
            ccq.moh_sound = form_result.get('moh_sound', 'local_stream://moh')
            ccq.time_base_score = form_result.get('time_base_score', 'system')
            ccq.max_wait_time = form_result.get('max_wait_time', 0)
            ccq.max_wait_time_with_no_agent = form_result.get('max_wait_time_with_no_agent', 0)
            ccq.max_wait_time_with_no_agent_reached = form_result.get('max_wait_time_with_no_agent_reached', 5)
            ccq.tier_rules_apply = form_result.get('tier_rules_apply', False)
            ccq.tier_rule_wait_second = form_result.get('tier_rule_wait_second', 300)
            ccq.tier_rule_wait_multiply_level = form_result.get('tier_rule_wait_multiply_level', False)
            ccq.tier_rule_agent_no_wait = form_result.get('tier_rule_agent_no_wait', False)
            ccq.discard_abandoned_after = form_result.get('discard_abandoned_after', 1800)
            ccq.abandoned_resume_allowed = form_result.get('abandoned_resume_allowed', False)
            ccq.strategy = form_result.get('strategy', 'callback')
            ccq.failed_route_id = form_result.get('failed_route_id', 0)
            ccq.record_calls = form_result.get('record_calls', False)
            ccq.announce_position = form_result.get('announce_position', False)    
            ccq.announce_sound = form_result.get('announce_sound').split(",")[1]
            ccq.announce_frequency = form_result.get('announce_frequency')                  
            
            db.add(ccq)
            db.commit()
            db.flush()           
            
            dir = fs_vm_dir+session['context']+"/queue-recordings/"+ccq.name
            
            if not os.path.exists(dir):
                os.makedirs(dir)                
                        
        except validators.Invalid, error:
            db.remove()
            return 'Error: %s.' % error
        
        r = PbxRoute()
        r.context = session['context']
        r.domain = session['context']
        r.name = form_result['name']
        r.continue_route = True
        r.voicemail_enable = True
        r.voicemail_ext = form_result['name']
        r.pbx_route_type_id = 10
        r.pbx_to_id = ccq.id
                    
        db.add(r)
        db.commit()
        db.flush()      
        db.remove() 
          
        return "Successfully added Call Center queue "+form_result['name']+"."
    
    @authorize(logged_in)
    def ccq_edit(self):
        schema = QueueEditForm()
        try:
            form_result = schema.to_python(request.params)
            ccq =  CallCenterQueue.query.filter_by(context=session['context']).filter_by(id=form_result.get('ccq_id')).first()
            ccq.context = session['context']
            ccq.domain = session['context']
            ccq.audio_type = form_result.get('audio_name').split(",")[0]
            ccq.audio_name = form_result.get('audio_name').split(",")[1]
            ccq.moh_sound = form_result.get('moh_sound', 'local_stream://moh')
            ccq.time_base_score = form_result.get('time_base_score', 'system')
            ccq.max_wait_time = form_result.get('max_wait_time', 0)
            ccq.max_wait_time_with_no_agent = form_result.get('max_wait_time_with_no_agent', 0)
            ccq.max_wait_time_with_no_agent_reached = form_result.get('max_wait_time_with_no_agent_reached', 5)
            ccq.tier_rules_apply = form_result.get('tier_rules_apply', False)
            ccq.tier_rule_wait_second = form_result.get('tier_rule_wait_second', 300)
            ccq.tier_rule_wait_multiply_level = form_result.get('tier_rule_wait_multiply_level', False)
            ccq.tier_rule_agent_no_wait = form_result.get('tier_rule_agent_no_wait', False)
            ccq.discard_abandoned_after = form_result.get('discard_abandoned_after', 1800)
            ccq.abandoned_resume_allowed = form_result.get('abandoned_resume_allowed', False)
            ccq.strategy = form_result.get('strategy')
            ccq.failed_route_id = form_result.get('failed_route_id', 0)
            ccq.record_calls = form_result.get('record_calls', False)
            ccq.announce_position = form_result.get('announce_position', False)
            ccq.announce_sound = form_result.get('announce_sound').split(",")[1]
            ccq.announce_frequency = form_result.get('announce_frequency')                  
            
            db.commit()
            db.flush()           
                        
        except validators.Invalid, error:
            db.remove()
            return 'Error: %s.' % error
        
        db.remove()
        return "Successfully updated Call Center queue "+ccq.name+"."    
    
    def ccq_by_id(self, id, **kw):
        items=[]
        for ccq in CallCenterQueue.query.filter_by(context=session['context']).filter_by(id=id).all():
            items.append({'id': ccq.id, 'name': ccq.name, 'audio_type': ccq.audio_type, 'audio_name': str(ccq.audio_type)+","+str(ccq.audio_name),
                          'moh_sound': ccq.moh_sound, 'time_base_score': ccq.time_base_score, 'max_wait_time': ccq.max_wait_time,
                          'max_wait_time_with_no_agent': ccq.max_wait_time_with_no_agent, 'max_wait_time_with_no_agent_reached': ccq.max_wait_time_with_no_agent_reached,
                          'tier_rules_apply': ccq.tier_rules_apply, 'tier_rule_wait_second': ccq.tier_rule_wait_second, 'tier_rule_wait_multiply_level': ccq.tier_rule_wait_multiply_level,
                          'tier_rule_agent_no_wait': ccq.tier_rule_agent_no_wait, 'discard_abandoned_after': ccq.discard_abandoned_after,
                          'abandoned_resume_allowed': ccq.abandoned_resume_allowed, 'strategy': ccq.strategy, 'failed_route_id': ccq.failed_route_id,
                          'record_calls': ccq.record_calls, 'announce_position': ccq.announce_position, 'announce_sound': "1,"+ccq.announce_sound,
                          'announce_frequency': ccq.announce_frequency})
        
        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)            

    @authorize(logged_in)
    def ccq_audio(self):
        items = []
        dir = fs_vm_dir+session['context']+"/recordings/"
        for i in os.listdir(dir):
            fo = generateFileObject(i, "",  dir)            
            items.append({'id': '1,'+fo["name"], 'name': 'Recording: '+fo["name"] , 'data': fo["path"], 'type': 1, 'real_id': ""})
            
        items.append({'id': '0,local_stream://moh', 'name': 'Default Music on Hold' , 'data': 'local_stream://moh', 'type': 1, 'real_id': ""})
        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)  

    @authorize(logged_in)    
    def delete_queue(self, **kw):
        
        id = request.params.get('id', None)
        q = CallCenterQueue.query.filter(CallCenterQueue.id==id).filter(CallCenterQueue.context==session['context']).first()

        queue = CallCenterQueue.query.filter(CallCenterQueue.id==q.id).first()
        CallCenterTier.query.filter(CallCenterTier.queue_id==queue.id).delete() 
        CallCenterQueue.query.filter(CallCenterQueue.id==q.id).delete()
        
        db.commit()
        db.flush()    
        db.remove()
        
        return "Successfully removed queue."                                
    
    @authorize(logged_in)
    def agents(self):
        items=[]
        for agent in CallCenterAgent.query.filter_by(context=session['context']).all(): 
            items.append({'id': agent.id, 'extension': agent.extension, 'status': agent.status})

        
        out = dict({'identifier': 'id', 'label': 'extension', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)          
        
    @authorize(logged_in)
    def agent_avail_endpoints(self):
        items=[]
        ext = request.params.get('ext', None)
        if ext:
            items.append({'id': 0, 'extension': ext})
        for row in PbxEndpoint.query.filter_by(user_context=session['context']).order_by(PbxEndpoint.auth_id).all():
            if CallCenterAgent.query.filter_by(extension=row.auth_id).filter_by(context=session['context']).count()>0:
                    continue
            

            items.append({'id': row.id, 'extension': row.auth_id})
        
        out = dict({'identifier': 'extension', 'label': 'extension', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)           
       
    @authorize(logged_in)
    def agent_endpoints(self):
        items=[]
        for row in PbxEndpoint.query.filter_by(user_context=session['context']).order_by(PbxEndpoint.auth_id).all():
            items.append({'id': row.id, 'extension': row.auth_id})
        
        out = dict({'identifier': 'extension', 'label': 'extension', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)             
        
    @authorize(logged_in)
    def agent_add(self):
        schema = AgentForm()
        try:
            form_result = schema.to_python(request.params)
            cca = CallCenterAgent()
            cca.extension = form_result.get('extension')            
            e = PbxEndpoint.query.filter_by(user_context=session['context']).filter(PbxEndpoint.auth_id==cca.extension).first()
            cca.context = session['context']
            cca.domain = session['context']
            cca.type = 'callback'
            cca.system = 'single_box'
            cca.name = cca.extension+"@"+session['context']
            cca.timeout = form_result.get('timeout', 30)
            cca.contact = "[call_timeout="+cca.timeout+"]user/"+cca.name
            cca.max_no_answer = form_result.get('max_no_answer', 3)
            cca.wrap_up_time = form_result.get('wrap_up_time', 30)
            cca.reject_delay_time = form_result.get('reject_delay_time', 30)
            cca.busy_delay_time = form_result.get('busy_delay_time', 0)
            cca.no_answer_delay_time = form_result.get('no_answer_delay_time', 5)
            cca.record_calls = form_result.get('record_calls', 0)
            cca.status = 'Available'
            cca.state = 'Waiting'
            cca.user_id = e.user_id
            cca.pbx_endpoint_id = e.id
            
            db.add(cca)
            db.commit()
            db.flush()    
                        
        except validators.Invalid, error:
            db.remove()
            return 'Error: %s.' % error

        db.remove()
        return "Successfully added agent."
        
    @authorize(logged_in)
    def agent_edit(self):
        schema = AgentEditForm()
        try:
            form_result = schema.to_python(request.params)
            cca = CallCenterAgent.query.filter_by(context=session['context']).filter(CallCenterAgent.id==form_result.get('agent_id')).first()
            cca.extension = form_result.get('extension')            
            e = PbxEndpoint.query.filter_by(user_context=session['context']).filter(PbxEndpoint.auth_id==cca.extension).first()
            cca.context = session['context']
            cca.domain = session['context']
            cca.type = 'callback'
            cca.record_calls = form_result.get('record_calls', 0)
            cca.timeout = form_result.get('timeout', 30)
            cca.max_no_answer = form_result.get('max_no_answer', 3)
            cca.wrap_up_time = form_result.get('wrap_up_time', 30)
            cca.reject_delay_time = form_result.get('reject_delay_time', 30)
            cca.busy_delay_time = form_result.get('busy_delay_time', 0)
            cca.no_answer_delay_time = form_result.get('no_answer_delay_time', 5)
            cca.user_id = e.user_id
            cca.pbx_endpoint_id = e.id

            db.commit()
            db.flush()           
            
        except validators.Invalid, error:
            db.remove()
            return 'Error: %s.' % error

        db.remove()
        return "Successfully edited agent."
                
        
    def cca_by_id(self, id, **kw):
        items=[]
        for cca in CallCenterAgent.query.filter_by(context=session['context']).filter_by(id=id).all():
            items.append({'id': cca.id, 'extension': cca.extension, 'type': cca.type, 'timeout': cca.timeout,
                          'max_no_answer': cca.max_no_answer, 'wrap_up_time': cca.wrap_up_time, 'reject_delay_time': cca.reject_delay_time,
                          'busy_delay_time': cca.busy_delay_time, 'no_answer_delay_time': cca.no_answer_delay_time, 'record_calls': cca.record_calls})
        
        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)           

    @authorize(logged_in)
    def update_agent_grid(self):
        
        try:
            w = loads(urllib.unquote_plus(request.params.get("data")))
            
            for i in w['modified']:  
                log.debug(w['modified'])                
                fsa = CallCenterAgent.query.filter(CallCenterAgent.name==str(i['extension'])+"@"+str(session['context'])).first()
                fsa.status = i['status']                
             
                db.commit()
                db.flush()                
                db.remove()         
                   
        except DataInputError, error:
            return 'Error: %s' % error
            
        return "Successfully update agent."           
        
        
    @authorize(logged_in)
    def tiers(self):
        items=[]
        
        for tier in CallCenterTier.query.join(CallCenterQueue).filter(CallCenterQueue.context==session['context']).all():
            agent = get_agent(tier.agent_id)
            queue = get_queue(tier.queue_id)
            items.append({'id': tier.id, 'agent': agent.extension, 'queue': queue.name, 'level': tier.level, 'position': tier.position, 'state': tier.state})

        
        out = dict({'identifier': 'id', 'label': 'agent', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)


    @authorize(logged_in)
    def tier_add(self):
        schema = TierForm()
        try:
            form_result = schema.to_python(request.params)

            cca = CallCenterAgent.query.filter_by(id=form_result.get('extension')).filter_by(context=session['context']).first()
            cur_cct = CallCenterTier.query.filter_by(agent=cca.name).first()
            ccq = CallCenterQueue.query.filter_by(name=form_result.get('name'))

            if cur_cct:
                return "Agent in tier already exists!"

            cct = CallCenterTier()

            cct.extension = cca.extension
            cct.queue_id = ccq.id
            cct.agent_id = cca.id
            cct.queue = str(ccq.name)+"@"+session['context']
            cct.agent = str(cca.extension)+"@"+session['context']
            cct.level = form_result.get('level', 1)
            cct.state = 'Ready'
            cct.position = form_result.get('position', 1)
            cct.context = session['context']
            cct.domain = session['context']

            db.add(cct)
            db.commit()
            db.flush()

        except validators.Invalid, error:
            db.remove()
            return 'Error: %s.' % error

        db.remove()
        return "Successfully created tier agent."
        
    @authorize(logged_in)
    def update_tier_grid(self):
        
        try:
            w = loads(urllib.unquote_plus(request.params.get("data")))
            
            for i in w['modified']:  
                log.debug(w['modified'])
                tier = CallCenterTier.query.filter_by(id=i['id']).first()
                
                tier.state = i['state']
                tier.level = i['level']
                tier.position = i['position']
                
                db.commit()
                db.flush()            
                db.remove()         
                   
        except DataInputError, error:
            return 'Error: %s' % error
            
        return "Sucessfully updated agent tiers."          
        
    def cc_cdr_stats(self):
        pass
    
    def get_queue_calls(self):
        log.debug(request.params.get("sid"))
        user = User.query.filter_by(session_id=request.params.get("sid")).first()
        if user:
            context = user.get_context()
        else:
            return ""
        items = []
        sql = "SELECT * FROM call_center_callers WHERE queue like '%@{0}'".format(context)
        
        for call in db.execute(sql): 
            items.append({'queue': call.queue.split("@")[0], 'cid_name': call.cid_name, 'cid_number': call.cid_number, 'agent': call.serving_agent.split("@")[0], 'state': call.state, 'uuid': call.uuid})
        
        if not len(items) == 0:
            return ""
        
        
        out = items
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)    
    
    @restrict("POST")
    @authorize(logged_in)
    def delete_queue_recording(self, **params):
        
        try:
            path = request.params.get("data")
            queue = request.params.get("queue_name")
            file_name = path.split("/")[len(path.split("/"))-1]
            dir = fs_vm_dir+session['context']+"/queue-recordings/"+queue+"/"
            os.remove(os.path.join(dir, file_name))
                        
        except:
            return "Error..."
        
        return "Deleted queue recording."

    @authorize(logged_in) 
    def get_queue_recordings(self):
        files = []
        queue = request.params.get("queue_name")
        
        dir = fs_vm_dir+session['context']+"/queue-recordings/"+queue
        for i in os.listdir(dir):
            path = dir+"/"+i
            id = i.split(".")[3].strip()
            row = PbxCdr.query.filter(PbxCdr.uuid==id).first()
            agent = PbxCdr.query.filter(PbxCdr.uuid==row.bleg_uuid).first()
            
            tpath = "/vm/" +session['context']+"/queue-recordings/"+queue+"/"+i
            received = str(modification_date(path)).strip("\"")
            fsize = str(os.path.getsize(path))
            caller = row.caller_id_number[len(row.caller_id_number)-10:]
            files.append({'name': caller, 'queue': queue, 'destination': row.destination_number, 'agent': agent.destination_number, 'path': tpath, 'received': received, 'size': fsize})

        db.remove()
        out = dict({'identifier': 'path', 'label': 'name', 'items': files})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)        

    @authorize(logged_in)
    def ad_audio(self):
        items = []
        dir = fs_vm_dir+session['context']+"/recordings/"
        try:
            for i in os.listdir(dir):
                fo = generateFileObject(i, "",  dir)
                items.append({'id': '1,'+fo["name"], 'name': 'Recording: '+fo["name"] , 'data': fo["path"], 'type': 1, 'real_id': ""})

            db.remove()
        except:
            pass
        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)   
    
    @restrict("GET")
    @authorize(logged_in)
    def del_agent(self, **kw):
        
        try:
            del_agent(request.params['id'])                            
        except:
            return "Error deleting agent."
        
        return  "Successfully deleted agent." 
        
    @restrict("GET")
    @authorize(logged_in)
    def del_tier(self, **kw):
        
        try:
            CallCenterTier.query.filter_by(id=request.params.get('id', 0)).delete()
            db.commit()
            db.flush()
            db.remove()

        except:
            return "Error deleting tier agent."
        
        return  "Successfully deleted tier agent."
        

        
        
        
        
        
    
    
    