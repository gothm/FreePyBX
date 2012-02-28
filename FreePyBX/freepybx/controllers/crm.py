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
import datetime, time, md5, os, sys
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from freepybx.lib.base import BaseController, render
from freepybx.model import meta
from freepybx.model.meta import *
from genshi import HTML
import shutil, os, sys, math, urllib, urllib2, re
import shutil, os, sys, imaplib, math
from pylons.decorators.rest import restrict
from genshi import HTML
import formencode
from formencode import validators
from freepybx.lib.pymap.imap import Pymap
from freepybx.lib.auth import *
from freepybx.lib.forms import *
from freepybx.lib.util import *
from freepybx.lib.util import PbxError, DataInputError, PbxEncoder
from decorator import decorator
from pylons.decorators.rest import restrict
import formencode
from formencode import validators
from pylons.decorators import validate
from simplejson import loads, dumps
from webob import Request, Response
import simplejson as json
import pprint
import os, sys
from stat import *
from webob import Request, Response
import cgi
import simplejson as json
from simplejson import loads, dumps
import urllib, urllib2
from sqlalchemy import Date, cast, desc, asc
from sqlalchemy.orm import join
from datetime import date
import time
import shutil
import cgi
import cgitb; cgitb.enable()
from freepybx.model import meta
from freepybx.model.meta import *
from freepybx.model.meta import Session as db

logged_in = IsLoggedIn()
log = logging.getLogger(__name__)

DEBUG=False


class CrmController(BaseController):
        
    def debug(self, **kw):
        result = []
        environ = request.environ
        keys = environ.keys()
        keys.sort()
        for key in keys:
            result.append("%s: %r"%(key, environ[key]))
        return '<pre>' + '\n'.join(result) + '</pre>'
    
    @authorize(logged_in)
    def campaigns(self):
        items=[]
        members = []
        for campaign in CrmCampaign.query.filter(context=session['context']).all():
            for member in CrmGroupMember.query.join(CrmGroup).join(CrmCampaignGroup).filter(CrmCampaignGroup.crm_campaign_id==campaign.id).all():
                members.append(member.extension)            
            items.append({'id': campaign.id, 'name': campaign.name, 'members': ",".join(members)})
            members = []
        
        db.remove()
        headers = [("Content-type", 'application/json'),]
        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def accounts(self):
        items=[]
        for account in CrmAccount.query.filter(company_id=session['company_id']).filter(user_id=session['user_id']).all():
            items.append({'id': account.id, 'name': str(account.first_name)+" "+str(account.last_name), 'address': account.address, \
                          'city': account.city, 'state': account.state, 'zip': account.zip, 'tel': account.tel, 'mobile': account.mobile, \
                          'email': account.email, 'crm_campaign_id': account.crm_campaign_id})        
        db.remove()
        headers = [("Content-type", 'application/json'),]
        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)

        return response(request.environ, self.start_response)
    
    @authorize(logged_in)
    def accounts_by_campaign(self, id):
        items=[]
        for account in CrmAccount.query.join(CrmCampaign).filter(CrmAccount.company_id==session['company_id'])\
                    .filter(CrmAccount.user_id==session['user_id']).filter(CrmCampaign.name==id).all():        
            items.append({'id': account.id, 'name': str(account.first_name)+" "+str(account.last_name), 'address': account.address, \
                          'city': account.city, 'state': account.state, 'zip': account.zip, 'tel': account.tel, 'mobile': account.mobile, \
                          'email': account.email, 'crm_campaign_id': account.crm_campaign_id})        
        db.remove()
        headers = [("Content-type", 'application/json'),]
        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)

        return response(request.environ, self.start_response)    
    
    @authorize(logged_in)
    def account_by_id(self, id):
        items=[]
        for account in CrmAccount.query.join(CrmCampaign).filter(CrmAccount.company_id==session['company_id'])\
                    .filter(CrmAccount.user_id==session['user_id']).filter(CrmCampaign.name==id).all():        
            items.append({'id': account.id, 'name': str(account.first_name)+" "+str(account.last_name), 'address': account.address, \
                          'city': account.city, 'state': account.state, 'zip': account.zip, 'tel': account.tel, 'mobile': account.mobile, \
                          'email': account.email, 'crm_campaign_id': account.crm_campaign_id})        
        db.remove()
        headers = [("Content-type", 'application/json'),]
        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)

        return response(request.environ, self.start_response)        
    
    @authorize(logged_in)
    def campaigns_ids(self):
        names=[]
        ids=[]
        for row in CrmCampaign.query.filter(context=session['context']).all():
            names.append(row.name)
            ids.append(row.id)
        db.remove()
        headers = [("Content-type", 'application/json'),]
        out = dict({'names': names, 'ids': ids})
        response = make_response(out)

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def account_add(self, **kw):
        schema = CrmAccountForm()
        try:
            form_result = schema.to_python(request.params)
            ca = CrmAccount()
            ca.first_name = form_result.get("first_name", "Unknown")
            ca.last_name = form_result.get("last_name", "Unknown")
            ca.company = form_result.get("company")
            ca.title = form_result.get("title")
            ca.email = form_result.get("email")
            ca.address = form_result.get("address")
            ca.address_2 = form_result.get("address_2")
            ca.city = form_result.get("city")
            ca.state = form_result.get("state")
            ca.zip = form_result.get("zip")
            ca.tel = form_result.get("tel")
            ca.tel_ext = form_result.get("tel_ext")
            ca.mobile = form_result.get("mobile")
            if request.params.has_key('active'):
                ca.active = True 
            else:
                ca.active = False              
            ca.company_id = session["company_id"]
            ca.user_id = session["user_id"]
            ca.crm_campaign_id = form_result.get("crm_campaign_name")
            ca.crm_account_status_type_id = form_result.get("status_type_name")
            ca.crm_lead_type_id = form_result.get("crm_lead_type_name")
            
            db.add(ca)
            db.commit()
            db.flush()
        except validators.Invalid, error:
             return 'Error: %s' % error
        
        return "Successfully added CRM account."        

    @authorize(logged_in)
    def edit_crm_account(self, **kw):
        schema = CrmAccountForm()
        try:
            form_result = schema.to_python(request.params)
            ca = CrmAccount.query.filter(id=form_result['id']).filter(company_id=session['company_id']).first()
            ca.first_name = form_result.get("first_name", "Unknown")
            ca.last_name = form_result.get("last_name", "Unknown")
            ca.company = form_result.get("company")
            ca.title = form_result.get("title")
            ca.email = form_result.get("email")
            ca.address = form_result.get("address")
            ca.address_2 = form_result.get("address_2")
            ca.city = form_result.get("city")
            ca.state = form_result.get("state")
            ca.zip = form_result.get("zip")
            ca.tel = form_result.get("tel")
            ca.tel_ext = form_result.get("tel_ext")
            ca.mobile = form_result.get("mobile")
            if request.params.has_key('active'):
                ca.active = True 
            else:
                ca.active = False              
            ca.company_id = session["company_id"]
            ca.user_id = session["user_id"]
            ca.crm_campaign_id = form_result.get("crm_campaign_name")
            ca.crm_account_status_type_id = form_result.get("status_type_name")
            ca.crm_lead_type_id = form_result.get("crm_lead_type_name")
            
            db.add(ca)
            db.commit()
            db.flush()
        except validators.Invalid, error:
             return 'Error: %s' % error
        
        return "Successfully edited CRM account."     
      
    
    @authorize(logged_in)
    def account_status_types(self):
        items=[]
        for act in CrmAccountStatusType.query.filter(context=session['context']).all():
            items.append({'id': act.id, 'name': act.name, 'desc': act.description})
        db.remove()
        headers = [("Content-type", 'application/json'),]
        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)

        return response(request.environ, self.start_response)
    
    @authorize(logged_in)
    def account_lead_types(self):
        items=[]
        for act in CrmLeadType.query.filter(context=session['context']).all():
            items.append({'id': act.id, 'name': act.name, 'desc': act.description})
        db.remove()
        headers = [("Content-type", 'application/json'),]
        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)

        return response(request.environ, self.start_response)
    
    
    @authorize(logged_in)
    def campaign_add(self, **kw):
        schema = CrmCampaignForm()
        try:
            form_result = schema.to_python(request.params)
            cc = CrmCampaign()
            cc.name = form_result.get('campaign_name')
            cc.context = session['context']

            db.add(cc)
            db.commit()
            db.flush()          
            
            cg = CrmGroup()  
            cg.name = form_result.get('campaign_name')
            db.add(cg)
            db.commit()
            db.flush()          
            
            ccg = CrmCampaignGroup()  
            ccg.name = form_result.get('campaign_name')
            ccg.crm_group_id = cg.id
            ccg.crm_campaign_id = cc.id
            ccg.context = session['context']
            db.add(ccg)
            db.commit()
            db.flush()       
            
            for i in form_result.get('campaign_extensions').split(","):
                if not i.isdigit():
                    continue
                gm = CrmGroupMember()
                gm.crm_group_id = cg.id
                gm.context = session['context']
                gm.extension = i

                db.add(gm)
                db.commit()
                db.flush()
                        
        except validators.Invalid, error:
            db.remove()
            return 'Error: %s' % error

        db.remove()   
        return "Successfully added CRM Campaign." 

    @authorize(logged_in)
    def update_campaign_grid(self, **kw):
        
        w = loads(urllib.unquote_plus(request.params.get("data")))

        try:
            for i in w['modified']:
                sg = CrmCampaignGroup.query.filter(CrmCampaignGroup.crm_campaign_id==i['id']).filter(CrmCampaignGroup.context==session['context']).first()
                CrmGroupMember.query.filter(CrmGroupMember.crm_group_id==sg.crm_group_id).delete()
                
                for gm in i['members'].split(","):
                    if not gm.strip().isdigit():
                        continue
                    sm = CrmGroupMember()
                    sm.crm_group_id = sg.crm_group_id
                    sm.extension = gm.strip()
                    sm.context = session['context']                    
    
                    db.add(sm)
                    db.commit()
                    db.flush()    
        except:    
            db.remove()        
            return "Error updating campaign."
            
        return "Successfully updated campaign."    
    
    @authorize(logged_in)
    def account_by_id(self, id, **kw):
        items=[]        
        for crm in CrmAccount.query.filter(CrmAccount.company_id==session['company_id']).filter(CrmAccount.id==id).all():
            items.append({'id': crm.id, 'first_name': crm.first_name, 'last_name': crm.last_name, 'address': crm.address, 'address_2': crm.address_2, \
                          'city': crm.city, 'state': crm.state, 'zip': crm.zip, 'title': crm.title, 'tel': crm.tel, 'mobile': crm.mobile, \
                          'tel_ext': crm.tel_ext, 'company': crm.company, 'email': crm.email, 'url': crm.url, 'crm_account_status_type_id': crm.crm_account_status_type_id, \
                          'crm_lead_type_id': crm.crm_lead_type_id, 'crm_campaign_id': crm.crm_campaign_id, 'created': crm.created.strftime("%m/%d/%Y %I:%M:%S %p"), \
                          'last_modified': crm.last_modified.strftime("%m/%d/%Y %I:%M:%S %p"), 'active': crm.active})
        db.remove()
        headers = [("Content-type", 'application/json'),]
        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)

        return response(request.environ, self.start_response)
    
    @authorize(logged_in)
    def account_notes_by_id(self, id, **kw):
        items=[]        
        for note in CrmNote.query.filter(CrmNote.crm_account_id==id).all():
            items.append({'id': note.id, 'created': note.created.strftime("%m/%d/%Y %I:%M:%S %p"), 'note': note.note , 'crm_account_id': note.crm_account_id})
        db.remove()
        headers = [("Content-type", 'application/json'),]
        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)

        return response(request.environ, self.start_response)     

    @authorize(logged_in)
    def add_crm_account_note(self, **kw):

        try:
            cn = CrmNote()
            cn.note = request.params.get('crm_note')
            cn.crm_account_id = request.params.get('crm_acct_id')
            cn.created = datetime.now()

            db.add(cn)
            db.commit()
            db.flush()          
            
        except validators.Invalid, error:
            db.remove()
            return 'Error: %s' % error

        db.remove()   
        return "Successfully added CRM notes."     
                   
    
    