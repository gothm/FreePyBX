"""
    This Source Code Form is subject to the terms of the Mozilla Public 
    License, v. 2.0. If a copy of the MPL was not distributed with this 
    file, You can obtain one at http://mozilla.org/MPL/2.0/.

    Software distributed under the License is distributed on an "AS IS"
    basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
    License for the specific language governing rights and limitations
    under the License.

    The Original Code is PythonPBX/VoiceWARE.

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
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from freepybx.lib.base import BaseController, render
from freepybx.model import meta
from freepybx.model.meta import *
from freepybx.model.meta import Session as db
from genshi import HTML
from pylons import config
from pylons.decorators.rest import restrict
import formencode
from formencode import validators
from freepybx.lib.pymap.imap import Pymap
from freepybx.lib.auth import *
from freepybx.lib.forms import *
from freepybx.lib.util import *
from freepybx.lib.util import PbxError, DataInputError, PbxEncoder
from freepybx.lib.validators import *
from decorator import decorator
from pylons.decorators.rest import restrict
import formencode
from formencode import validators
from pylons.decorators import validate
from simplejson import loads, dumps
import simplejson as json
import os
import simplejson as json
from simplejson import loads, dumps
import cgitb; cgitb.enable()

logged_in = IsLoggedIn()
super_user = IsSuperUser()
credentials = HasCredential(object)
log = logging.getLogger(__name__)

fs_vm_dir = config['app_conf']['fs_vm_dir']
fs_profile = config['app_conf']['fs_profile']


class CredentialError(Exception):
    message=""

    def __init__(self, message=None):
        Exception.__init__(self, message or self.message)

class AdminController(BaseController):
    """ this is a test of the comment system """

    @authorize(super_user)
    def index(self, **kw):
        c.sid = session.id
        c.my_name = session["name"]
        c.profiles = PbxProfile.query.all()

        return render('admin/admin.html')

    def logout(self, **kw):
        if 'user' in session:
            del session['user']
        session.clear()
        session.delete()
        return self.login()

    def login(self, **kw):
        return render('admin/login.html')

    @restrict("POST")
    def auth_admin(self, **kw):
        schema = LoginForm()
        try:
            form_result = schema.to_python(request.params)
            username = form_result.get("username")
            password = form_result.get("password")
        except:
            return AuthenticationError("Auth error...")

        if not authenticate_admin(username, password):
            return self.login()
        c.sid = session.id
        c.my_name = session["name"]
        c.profiles = PbxProfile.query.all()
        return render('admin/admin.html')

    @authorize(super_user)
    def main(self, **kw):
        c.sid = session.id
        c.my_name = session["name"]
        c.profiles = PbxProfile.query.all()

        return render('admin/admin.html')

    @authorize(super_user)
    def billing(self, **kw):
        return render('admin/billing.html')

    @authorize(super_user)
    def companies(self):
        items=[]
        for row in Company.query.all():
            items.append({'id': row.id, 'name': row.name, 'active': row.active, 'tel': row.tel})

        out = dict({'identifier': 'name', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json'),]

        return response(request.environ, self.start_response)

    @authorize(super_user)
    def companies_id(self):
        items=[]
        for row in Company.query.all():
            items.append({'id': row.id, 'name': row.name, 'active': row.active, 'tel': row.tel})

        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json'),]

        return response(request.environ, self.start_response)

    @authorize(super_user)
    def edit_company(self):

        schema = CompanyEditForm()

        try:
            form_result = schema.to_python(request.params)
            co = Company.query.filter(Company.id==form_result.get('id')).first()
            co.tel = form_result.get('tel')
            co.address = form_result.get('address')
            co.address_2 = form_result.get('address_2')
            co.city = form_result.get('city')
            co.state = form_result.get('state')
            co.zip = form_result.get('zip')
            co.url = form_result.get('url')
            co.context = form_result.get('context')
            co.email = form_result.get('contact_email')
            co.contact_name = form_result.get('contact_name')
            co.contact_phone = form_result.get('contact_phone')
            co.contact_mobile = form_result.get('contact_mobile')
            co.contact_title = form_result.get('contact_title')
            co.contact_email = form_result.get('contact_email')
            co.max_extensions = form_result.get('max_extensions')
            co.max_minutes =  form_result.get('max_minutes')
            co.max_queues =  form_result.get('max_queues')
            co.max_agents = form_result.get('max_agents')
            co.active = True if form_result.get('active')=="true" else False
            co.has_crm = True if form_result.get('has_crm')=="true" else False
            co.has_call_center = True if form_result.get('has_call_center')=="true" else False
            co.default_gateway = form_result.get('default_gateway')
            co.pbx_profile_id = form_result.get('pbx_profile_id')
            db.add(co)

            db.commit()
            db.flush()
            db.remove()

        except validators.Invalid, error:
            db.remove()
            return 'Error: %s' % error

        return "Successfully edited company."

    @authorize(super_user)
    def add_company(self):

        schema = CompanyForm()

        try:
            form_result = schema.to_python(request.params)
            co = Company()
            co.name = form_result.get('name')
            co.tel = form_result.get('tel')
            co.address = form_result.get('address')
            co.address_2 = form_result.get('address_2')
            co.city = form_result.get('city')
            co.state = form_result.get('state')
            co.zip = form_result.get('zip')
            co.url = form_result.get('url')
            co.context = form_result.get('context')
            co.email = form_result.get('contact_email')
            co.contact_name = form_result.get('contact_name')
            co.contact_phone = form_result.get('contact_phone')
            co.contact_mobile = form_result.get('contact_mobile')
            co.contact_title = form_result.get('contact_title')
            co.contact_email = form_result.get('contact_email')
            co.max_extensions = form_result.get('max_extensions')
            co.max_minutes =  form_result.get('max_minutes')
            co.max_queues =  form_result.get('max_queues')
            co.max_agents = form_result.get('max_agents')
            co.active = True if form_result.get('active')=="true" else False
            co.has_crm = True if form_result.get('has_crm')=="true" else False
            co.has_call_center = True if form_result.get('has_call_center')=="true" else False
            co.default_gateway = form_result.get('default_gateway')
            co.pbx_profile_id = form_result.get('pbx_profile_id')

            os.makedirs(fs_vm_dir+str(co.context)+'/recordings')
            os.makedirs(fs_vm_dir+str(co.context)+'/queue-recordings')
            os.makedirs(fs_vm_dir+str(co.context)+'/extension-recordings')
            os.makedirs(fs_vm_dir+str(co.context)+'/faxes')


            db.add(co)
            db.commit()

            con = PbxContext(co.id, form_result.get('domain'), form_result.get('context'), form_result.get('default_gateway'),
                co.pbx_profile_id, co.name, form_result.get('did'))

            db.add(con)
            co.company_contexts.append(con)

            db.add(PbxDid(form_result.get('did'), co.id,
                form_result.get('context'), form_result.get('domain'), form_result.get('t38', False), form_result.get('e911', False),
                form_result.get('cnam', False), True))

            db.commit()
            db.flush()
            db.remove()

        except validators.Invalid, error:
            db.remove()
            return 'Error: %s' % error

        return "Successfully created company."


    @authorize(super_user)
    def company_by_id(self, id, **kw):
        items=[]
        row = Company.query.filter(Company.id==id).first()
        items.append({'id': row.id, 'name': row.name,  'pbx_profile_id': row.pbx_profile_id, 'email': row.email, 'address': row.address, 'address_2': row.address_2,
                      'city': row.city, 'state': row.state, 'zip': row.zip, 'default_gateway': row.default_gateway,
                      'tel': row.tel, 'url': row.url, 'active': row.active, 'context': row.context, 'has_crm': row.has_crm,
                      'has_call_center': row.has_call_center, 'max_extensions': row.max_extensions, 'max_minutes': row.max_minutes,
                      'contact_name': row.contact_name, 'contact_phone': row.contact_phone, 'contact_mobile': row.contact_mobile,
                      'contact_title': row.contact_title, 'contact_email': row.contact_email, 'max_queues': row.max_queues,
                      'max_agents': row.max_agents,'notes': row.notes})

        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json'),]

        return response(request.environ, self.start_response)

    @authorize(super_user)
    def gateway_by_id(self, id, **kw):
        items=[]
        row = PbxGateway.query.filter(PbxGateway.id==id).first()
        items.append({'id': row.id, 'name': row.name, 'pbx_profile_id': row.pbx_profile_id, 'username': row.username, 'password': row.password,
                      'proxy': row.proxy, 'register': row.register, 'register_transport': row.register_transport, 'reg_id': row.reg_id, 'rfc5626': row.rfc5626,
                      'extension': row.extension, 'realm': row.realm, 'from_domain': row.from_domain, 'expire_seconds': row.expire_seconds, 'retry_seconds': row.retry_seconds,
                      'ping': row.ping, 'context': row.context, 'caller_id_in_from': row.caller_id_in_from,
                      'mask': row.mask, 'contact_params': row.contact_params})

        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json'),]

        return response(request.environ, self.start_response)

    @authorize(super_user)
    def dids(self):
        items=[]

        for row in db.query(PbxDid.id, PbxDid.did, Company.name, Company.id, Company.context, PbxDid.active, PbxDid.t38, PbxDid.cnam, PbxDid.e911)\
                            .filter(Company.id==PbxDid.company_id).order_by(PbxDid.did).all():
            items.append({'did': row[1],'company_name': row[2], 'company_id': row[3], 'context': row[4], 'active': row[5], 't38': row[6], 'cnam': row[7], 'e911': row[8]})
        db.remove()

        out = dict({'identifier': 'did', 'label': 'did', 'items': items})   #,'name': sorted(set(name)), 'id': sorted(set(id))})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(super_user)
    def add_did(self, **kw):
        schema = DIDForm()
        try:
            form_result = schema.to_python(request.params)
            co = Company.query.filter_by(name=form_result.get('company_name', None)).first()
            if co:
                db.add(PbxDid(form_result.get('did_name', None), co.id,
                            co.context, co.context, form_result.get('t38', False), form_result.get('e911', False),
                            form_result.get('cnam', False),form_result.get('active', False)))

                db.commit()
                db.flush()
            else:
                return "Error: Failed to insert DID."

        except validators.Invalid, error:
            db.remove()
            return 'Validation Error: %s' % error

        db.remove()
        return "Successfully added DID."

    @authorize(super_user)
    def update_did_grid(self, **kw):

        try:
            w = loads(urllib.unquote_plus(request.params.get("data")))

            for i in w['modified']:

                if i['company_name'].isdigit():
                    co = Company.query.filter_by(id=i['company_name']).first()
                else:
                    co = Company.query.filter_by(name=i['company_name']).first()

                sd = PbxDid.query.filter(PbxDid.did==i['did']).first()
                sd.company_id = co.id
                sd.context = co.context
                sd.domain = co.context
                sd.t38 = i['t38']
                sd.cnam = i['cnam']
                sd.e911 = i['e911']
                sd.pbx_route_id = 0
                sd.active = i['active']

                db.commit()
                db.flush()
                db.remove()

        except DataInputError, error:
            db.remove()
            return 'Error: %s' % error

        return "Successfully updated DID."

    @authorize(super_user)
    def update_company_grid(self, **kw):

        try:
            w = loads(urllib.unquote_plus(request.params.get("data")))

            for i in w['modified']:
                co = Company.query.filter_by(id=i['id']).first()
                co.active = i['active']

                db.commit()
                db.flush()
                db.remove()

        except DataInputError, error:
            db.remove()
            return 'Error: %s' % error

        return "Successfully updated Company."

    @authorize(super_user)
    def update_gw_grid(self, **kw):

        try:
            w = loads(urllib.unquote_plus(request.params.get("data")))

            for i in w['modified']:
                gw = PbxGateway.query.filter_by(id=i['id']).first()
                gw.register = i['register']
                gw.pbx_profile_id = i['profile']

                db.commit()
                db.flush()
                db.remove()

        except DataInputError, error:
            db.remove()
            return 'Error: %s' % error

        return "Successfully updated Gateway."

    @authorize(super_user)
    def update_context_grid(self, **kw):

        try:
            w = loads(urllib.unquote_plus(request.params.get("data")))

            for i in w['modified']:

                if i['profile'].isdigit():
                    pro = PbxProfile.query.filter_by(id=i['profile']).first()
                else:
                    pro = PbxProfile.query.filter_by(name=i['profile']).first()

                if i['default_gateway'].isdigit():
                    gw = PbxGateway.query.filter_by(id=int(i['default_gateway'])).first()
                else:
                    gw = PbxGateway.query.filter_by(name=i['default_gateway']).first()

                com = Company.query.filter_by(context=i['context']).first()

                con = PbxContext.query.filter_by(id=i['id']).first()
                con.pbx_profile_id = pro.id
                com.default_gateway = gw.name

                db.commit()
                db.flush()
                db.remove()

        except DataInputError, error:
            db.remove()
            return 'Error: %s' % error

        return "Successfully updated Gateway."

    @authorize(super_user)
    def profiles(self, **kw):
        items=[]
        for row in  PbxProfile.query.all():
            items.append({'name': row.name, 'ext_rtp_ip': row.ext_rtp_ip, 'ext_sip_ip': row.ext_sip_ip, 'sip_port': row.sip_port,
                      'accept_blind_reg': row.accept_blind_reg, 'auth_calls': row.auth_calls, 'email_domain': row.email_domain})

        out = dict({'identifier': 'name', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json'),]

        return response(request.environ, self.start_response)

    @authorize(super_user)
    def gateways(self, **kw):
        items=[]
        for row in PbxGateway.query.all():
            items.append({'id': row.id,'name': row.name, 'proxy': row.proxy, 'mask': row.mask, 'register': row.register,
                          'profile': row.pbx_profile_id})

        out = dict({'identifier': 'name', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json'),]

        return response(request.environ, self.start_response)

    @authorize(super_user)
    def contexts(self, **kw):
        items=[]

        for row in PbxContext.query.all():
            company = Company.query.filter(Company.id==row.company_id).first()
            items.append({'id': row.id, 'context': row.context, 'profile': row.profile, 'caller_id_name': row.caller_id_name,
                          'caller_id_number': row.caller_id_number, 'company_name': company.name, 'gateway': row.gateway})

        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json'),]

        return response(request.environ, self.start_response)

    @authorize(super_user)
    def context_by_id(self, id, **kw):
        items=[]
        row = PbxContext.query.filter(PbxContext.id==id).first()
        company = Company.query.filter(Company.id==row.company_id).first()
        items.append({'id': row.id, 'context': row.context, 'profile': row.profile, 'caller_id_name': row.caller_id_name,
                          'caller_id_number': row.caller_id_number, 'company_name': company.name, 'gateway': row.gateway})

        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json'),]

        return response(request.environ, self.start_response)

    @authorize(super_user)
    def add_gateway(self, **kw):
        schema = GatewayForm()

        try:
            form_result = schema.to_python(request.params)
            gw = PbxGateway()

            gw.name = form_result.get('name')
            gw.pbx_profile_id = form_result.get('pbx_profile_id')
            gw.username = form_result.get('gateway_username')
            gw.password = form_result.get('password')
            gw.realm = form_result.get('realm')
            gw.proxy = form_result.get('proxy')
            gw.register = form_result.get('register', False)
            gw.register_transport = form_result.get('register_transport')
            gw.extension = form_result.get('extension')
            gw.from_domain = form_result.get('from_domain')
            gw.expire_seconds = form_result.get('expire_seconds')
            gw.retry_seconds = form_result.get('retry_seconds')
            gw.ping = form_result.get('ping')
            gw.context = form_result.get('context')
            gw.caller_id_in_from = form_result.get('caller_id_in_from')
            gw.mask =  form_result.get('mask')
            gw.rfc5626 = form_result.get('rfc5626', True)
            gw.reg_id = form_result.get('reg_id', 1)
            gw.contact_params = form_result.get('contact_params', u'tport=tcp')

            db.add(gw)
            db.commit()
            db.flush()
            db.remove()

        except validators.Invalid, error:
            db.remove()
            return 'Error: %s' % error

        return "Successfully added gateway."

    @authorize(super_user)
    def edit_gateway(self):

        schema = GatewayEditForm()

        try:
            form_result = schema.to_python(request.params)

            gw = PbxGateway.query.filter(PbxGateway.id==form_result.get('gateway_id')).first()
            gw.pbx_profile_id = form_result.get('pbx_profile_id')
            gw.username = form_result.get('gateway_username')
            gw.password = form_result.get('password')
            gw.proxy = form_result.get('proxy')
            gw.register = form_result.get('register', False)
            gw.register_transport = form_result.get('register_transport')
            gw.extension = form_result.get('extension')
            gw.realm = form_result.get('realm')
            gw.from_domain = form_result.get('from_domain')
            gw.expire_seconds = form_result.get('expire_seconds')
            gw.retry_seconds = form_result.get('retry_seconds')
            gw.ping = form_result.get('ping')
            gw.context = form_result.get('context')
            gw.caller_id_in_from = form_result.get('caller_id_in_from')
            gw.mask =  form_result.get('mask')
            gw.rfc5626 = form_result.get('rfc5626', True)
            gw.reg_id = form_result.get('reg_id', 1)
            gw.contact_params = form_result.get('contact_params', u'tport=tcp')

            db.add(gw)
            db.commit()
            db.flush()
            db.remove()

        except validators.Invalid, error:
            db.remove()
            return 'Error: %s' % error

        return "Successfully edited gateway."

    @authorize(super_user)
    def add_profile(self):

        schema = ProfileForm()

        try:
            form_result = schema.to_python(request.params)
            sp = PbxProfile()
            sp.name = form_result.get('name')
            sp.odbc_credentials = form_result.get('odbc_credentials')
            sp.manage_presence = True if form_result.get('manage_presence')=="true" else False
            sp.presence_db_name = form_result.get('dbname', None)
            sp.presence_hosts = form_result.get('presence_hosts', None)
            sp.send_presence_on_register = True if form_result.get('send_presence_on_register')=="true" else False
            sp.delete_subs_on_register = True if form_result.get('delete_subs_on_register')=="true" else False
            sp.caller_id_type = form_result.get('caller_id_type', u'rpid')
            sp.auto_jitterbuffer_msec = form_result.get('auto_jitterbuffer_msec', 120)
            sp.dialplan = form_result.get('dialplan', u'XML,enum')
            sp.ext_rtp_ip = form_result.get('ext_rtp_ip', None)
            sp.ext_sip_ip = form_result.get('ext_sip_ip', None)
            sp.rtp_ip = form_result.get('rtp_ip', None)
            sp.sip_ip = form_result.get('sip_ip', None)
            sp.sip_port = form_result.get('sip_port', 5060)
            sp.nonce_ttl = form_result.get('nonce_ttl', 60)
            sp.sql_in_transactions = True if form_result.get('sql_in_transactions')=="true" else False
            sp.use_rtp_timer = True if form_result.get('use_rtp_timer')=="true" else False
            sp.rtp_timer_name =  form_result.get('rtp_timer_name', u'soft')
            sp.codec_prefs = form_result.get('codec_prefs', u'PCMU,PCMA,G722,G726,H264,H263')
            sp.inbound_codec_negotiation = form_result.get('inbound_codec_negotiation', u'generous')
            sp.codec_ms = form_result.get('codec_ms', 20)
            sp.rtp_timeout_sec = form_result.get('rtp_timeout_sec', 300)
            sp.rtp_hold_timeout_sec = form_result.get('rtp_hold_timeout_sec', 1800)
            sp.rfc2833_pt = form_result.get('rfc2833_pt', 101)
            sp.dtmf_duration = form_result.get('dtmf_duration', 100)
            sp.dtmf_type = form_result.get('dtmf_type', u'rfc2833')
            sp.session_timeout = form_result.get('session_timeout', 1800)
            sp.multiple_registrations = form_result.get('multiple_registrations', u'contact')
            sp.vm_from_email = form_result.get('vm_from_email', u'voicemail@freeswitch')
            sp.accept_blind_reg = True if form_result.get('accept_blind_reg')=="true" else False
            sp.auth_calls = True if form_result.get('auth_calls')=="true" else False
            sp.email_domain = form_result.get('email_domain', u'freeswitch.org')
            sp.auth_all_packets = True if form_result.get('auth_all_packets')=="true" else False
            sp.log_auth_failures = True if form_result.get('log_auth_failures')=="true" else False
            sp.disable_register = True if form_result.get('disable_register')=="true" else False
            sp.minimum_session_expires = form_result.get('minimum_session_expires', 120)

            db.add(sp)
            db.commit()
            db.flush()

        except validators.Invalid, error:
            db.remove()
            return 'Validation Error: %s' % error

        db.remove()

        return "Successfully added profile."

    @authorize(super_user)
    def profiles(self, **kw):
        items=[]
        for row in  PbxProfile.query.all():
            items.append({'id': row.id, 'name': row.name, 'ext_rtp_ip': row.ext_rtp_ip, 'ext_sip_ip': row.ext_sip_ip, 'sip_port': row.sip_port})

        out = dict({'identifier': 'name', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json'),]

        return response(request.environ, self.start_response)

    @authorize(super_user)
    def profiles_id(self, **kw):
        items=[]
        for row in  PbxProfile.query.all():
            items.append({'id': row.id, 'name': row.name, 'ext_rtp_ip': row.ext_rtp_ip, 'ext_sip_ip': row.ext_sip_ip, 'sip_port': row.sip_port})

        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json'),]

        return response(request.environ, self.start_response)

    @authorize(super_user)
    def edit_profile(self):

        schema = ProfileEditForm()

        try:
            form_result = schema.to_python(request.params)
            sp = PbxProfile.query.filter_by(id=form_result.get('id',0)).first()
            sp.odbc_credentials = form_result.get('odbc_credentials')
            sp.manage_presence = True if form_result.get('manage_presence')=="true" else False
            sp.presence_db_name = form_result.get('dbname', None)
            sp.presence_hosts = form_result.get('presence_hosts', None)
            sp.send_presence_on_register = True if form_result.get('send_presence_on_register')=="true" else False
            sp.delete_subs_on_register = True if form_result.get('delete_subs_on_register')=="true" else False
            sp.caller_id_type = form_result.get('caller_id_type', u'rpid')
            sp.auto_jitterbuffer_msec = form_result.get('auto_jitterbuffer_msec', 120)
            sp.dialplan = form_result.get('dialplan', u'XML,enum')
            sp.ext_rtp_ip = form_result.get('ext_rtp_ip', None)
            sp.ext_sip_ip = form_result.get('ext_sip_ip', None)
            sp.rtp_ip = form_result.get('rtp_ip', None)
            sp.sip_ip = form_result.get('sip_ip', None)
            sp.sip_port = form_result.get('sip_port', 5060)
            sp.nonce_ttl = form_result.get('nonce_ttl', 60)
            sp.sql_in_transactions = True if form_result.get('sql_in_transactions')=="true" else False
            sp.use_rtp_timer = True if form_result.get('use_rtp_timer')=="true" else False
            sp.rtp_timer_name =  form_result.get('rtp_timer_name', u'soft')
            sp.codec_prefs = form_result.get('codec_prefs', u'PCMU,PCMA,G722,G726,H264,H263')
            sp.inbound_codec_negotiation = form_result.get('inbound_codec_negotiation', u'generous')
            sp.codec_ms = form_result.get('codec_ms', 20)
            sp.rtp_timeout_sec = form_result.get('rtp_timeout_sec', 300)
            sp.rtp_hold_timeout_sec = form_result.get('rtp_hold_timeout_sec', 1800)
            sp.rfc2833_pt = form_result.get('rfc2833_pt', 101)
            sp.dtmf_duration = form_result.get('dtmf_duration', 100)
            sp.dtmf_type = form_result.get('dtmf_type', u'rfc2833')
            sp.session_timeout = form_result.get('session_timeout', 1800)
            sp.multiple_registrations = form_result.get('multiple_registrations', u'contact')
            sp.vm_from_email = form_result.get('vm_from_email', u'voicemail@freeswitch')
            sp.accept_blind_reg = True if form_result.get('accept_blind_reg')=="true" else False
            sp.auth_calls = True if form_result.get('auth_calls')=="true" else False
            sp.email_domain = form_result.get('email_domain', u'freeswitch.org')
            sp.auth_all_packets = True if form_result.get('auth_all_packets')=="true" else False
            sp.log_auth_failures = True if form_result.get('log_auth_failures')=="true" else False
            sp.disable_register = True if form_result.get('disable_register')=="true" else False
            sp.minimum_session_expires = form_result.get('minimum_session_expires', 120)

            db.add(sp)
            db.commit()
            db.flush()

        except validators.Invalid, error:
            db.remove()
            return 'Validation Error: %s' % error

        db.remove()
        return "Successfully updated profile."

    @authorize(super_user)
    def get_profile_by_id(self, id, **kw):
        items=[]
        row = PbxProfile.query.filter_by(id=id).first()
        items.append({'id': row.id, 'name': row.name, 'odbc_credentials': row.odbc_credentials, 'manage_presence': row.manage_presence, 'presence_hosts': row.presence_hosts,
                      'send_presence_on_register': row.send_presence_on_register, 'delete_subs_on_register': row.delete_subs_on_register, 'caller_id_type': row.caller_id_type,
                      'auto_jitterbuffer_msec': row.auto_jitterbuffer_msec, 'dialplan': row.dialplan, 'ext_rtp_ip': row.ext_rtp_ip, 'ext_sip_ip': row.ext_sip_ip, 'rtp_ip': row.rtp_ip,
                      'sip_ip': row.sip_ip, 'sip_port': row.sip_port, 'nonce_ttl': row.nonce_ttl, 'sql_in_transactions': row.sql_in_transactions, 'use_rtp_timer': row.use_rtp_timer,
                      'codec_prefs': row.codec_prefs, 'inbound_codec_negotiation': row.inbound_codec_negotiation, 'rtp_timeout_sec': row.rtp_timeout_sec, 'rfc2833_pt': row.rfc2833_pt,
                      'dtmf_duration': row.dtmf_duration, 'dtmf_type': row.dtmf_type, 'session_timeout': row.session_timeout, 'multiple_registrations': row.multiple_registrations,
                      'vm_from_email': row.vm_from_email, 'accept_blind_reg': row.accept_blind_reg, 'auth_calls': row.auth_calls, 'email_domain': row.email_domain,
                      'rtp_timer_name': row.rtp_timer_name, 'presence_db_name': row.presence_db_name, 'codec_ms': row.codec_ms, 'disable_register': row.disable_register,
                      'log_auth_failures': row.log_auth_failures, 'auth_all_packets':row.auth_all_packets, 'minimum_session_expires': row.minimum_session_expires})

        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json'),]

        return response(request.environ, self.start_response)

    @authorize(super_user)
    def admins(self, **kw):
        items=[]
        for row in  AdminUser.query.all():
            for r in row.permissions:
                log.debug("%s" % r)
            items.append({'id': row.id, 'name': row.first_name+' '+row.last_name, 'username': row.username, 'password': row.password, 'active': row.active})

        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json'),]

        return response(request.environ, self.start_response)

    @authorize(super_user)
    def admin_by_id(self, id, **kw):
        items=[]
        row = AdminUser.query.filter(AdminUser.id==id).first()
        items.append({'id': row.id, 'first_name': row.first_name, 'last_name': row.last_name, 'username': row.username, 'password': row.password})

        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json'),]

        return response(request.environ, self.start_response)

    @authorize(super_user)
    def cust_admins(self, **kw):
        items=[]
        perms=[]
        for row in User.query.filter(User.auth_level==1).all():
            for i in row.permissions:
                perms.append(str(i))
            items.append({'id': row.id, 'company_name': row.get_company_name(row.company_id), 'active': row.active, 'perms': ','.join(perms), 'name': row.first_name+' '+row.last_name, 'first_name': row.first_name, 'last_name': row.last_name, 'username': row.username, 'password': row.password})

        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json'),]

        return response(request.environ, self.start_response)

    @authorize(super_user)
    def cust_admin_by_id(self, id, **kw):
        items=[]
        for row in User.query.filter_by(id=id).filter(User.auth_level==2).all():
            items.append({'id': row.id, 'name': row.first_name+' '+row.last_name, 'username': row.username, 'password': row.password, 'active': row.active})

        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json'),]

        return response(request.environ, self.start_response)


    @authorize(super_user)
    def add_admin(self, **kw):
        schema = AdminUserForm()

        try:
            form_result = schema.to_python(request.params)
            username = form_result.get('username')
            password = form_result.get('password')
            first_name = form_result.get('first_name')
            last_name = form_result.get('last_name')

            admin_group = AdminGroup.query.filter(AdminGroup.id==1).first()
            au = AdminUser(username, password, first_name, last_name)
            db.add(au)
            au.admin_groups.append(admin_group)

            db.commit()
            db.flush()
            db.remove()

        except validators.Invalid, error:
            db.remove()
            return 'Error: %s' % error

        return "Successfully added admin user."

    @authorize(super_user)
    def edit_admin(self, **kw):
        schema = AdminEditUserForm()

        try:
            form_result = schema.to_python(request.params)
            user = AdminUser.query.filter(AdminUser.id==form_result.get('id')).first()
            user.password = form_result.get('password')
            user.first_name = form_result.get('first_name')
            user.last_name = form_result.get('last_name')

            db.commit()
            db.flush()
            db.remove()

        except validators.Invalid, error:
            db.remove()
            return 'Error: %s' % error

        return "Successfully edited admin user."


    @authorize(super_user)
    def add_cust_admin(self, **kw):
        schema = CustUserAdminForm()

        try:
            form_result = schema.to_python(request.params)
            username = form_result.get('username')
            password = form_result.get('password')
            first_name = form_result.get('first_name')
            last_name = form_result.get('last_name')

            co = Company.query.filter_by(name=form_result.get('company_id')).first()
            u = User(first_name, last_name, username, password, 1, co.id, True)
            db.add(u)
            g = Group.query.filter(Group.name=='admin_user').first()
            u.user_groups.append(g)

            db.commit()
            db.flush()
            db.remove()

        except validators.Invalid, error:
            db.remove()
            return 'Error: %s' % error

        return "Successfully added admin user."


    @authorize(super_user)
    def cust_admin_by_id(self, id, **kw):
        items=[]
        row = User.query.filter_by(id=id).first()

        lev = ['SUPER','PBX Admin','Extension User','Billing & Reports']

        items.append({'id': row.id, 'company_name': row.get_company_name(row.company_id), 'auth_level': lev[row.auth_level], 'first_name': row.first_name, 'last_name': row.last_name, 'username': row.username, 'password': row.password, 'company_id': row.company_id})

        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json'),]

        return response(request.environ, self.start_response)

    @authorize(super_user)
    def edit_cust_admin(self, **kw):
        schema = AdminUserForm()

        lev = ['SUPER','PBX Admin','Extension User','Billing & Reports']

        try:
            form_result = schema.to_python(request.params)
            user = User.query.filter(User.id==form_result.get('id')).first()
            user.password = form_result.get('password')
            user.first_name = form_result.get('first_name')
            user.last_name = form_result.get('last_name')

            if int(lev.index(form_result.get('auth_level')))>1:
                if check_for_remaining_admin(user.company_id)==1:
                    return "Error: You are the last admin. Please make a new one before you lower "+user.username+"'s security level."

            user.auth_level = int(lev.index(form_result.get('auth_level')))

            db.commit()
            db.flush()
            db.remove()

        except validators.Invalid, error:
            db.remove()
            return 'Error: %s' % error

        return "Successfully edited admin user."

    @authorize(super_user)
    def update_cust_admin_grid(self, **kw):

        try:
            w = loads(urllib.unquote_plus(request.params.get("data")))

            for i in w['modified']:
                u = User.query.filter_by(id=i['id']).first()
                u.active = i['active']

                db.commit()
                db.flush()
                db.remove()

        except DataInputError, error:
            db.remove()
            return 'Error: %s' % error

        return "Successfully updated admin."

    @authorize(super_user)
    def update_admin_grid(self, **kw):

        try:
            w = loads(urllib.unquote_plus(request.params.get("data")))

            for i in w['modified']:
                u = AdminUser.query.filter_by(id=i['id']).first()
                u.active = i['active']

                db.commit()
                db.flush()
                db.remove()

        except DataInputError, error:
            db.remove()
            return 'Error: %s' % error

        return "Successfully updated admin."

    @authorize(super_user)
    def add_context(self, **kw):
        schema = ContextForm()

        try:
            form_result = schema.to_python(request.params)

            sc = PbxContext()

            sc.company_id = form_result.get('company_id')
            sc.profile = form_result.get('profile')
            sc.domain = form_result.get('context')
            sc.context = form_result.get('context')
            sc.caller_id_name = form_result.get('caller_id_name')
            sc.caller_id_number = form_result.get('caller_id_number')
            sc.gateway = u'default'

            db.add(sc)
            db.commit()
            db.flush()
            db.remove()

        except validators.Invalid, error:
            db.remove()
            return 'Error: %s' % error

        return "Successfully added context."

    @authorize(super_user)
    def edit_context(self, **kw):
        schema = ContextEditForm()

        try:
            form_result = schema.to_python(request.params)

            sc = PbxContext.query.filter(PbxContext.id==form_result.get('id')).first()

            sc.company_id = form_result.get('company_id')
            sc.profile = form_result.get('pbx_profile_id')
            sc.caller_id_name = form_result.get('caller_id_name')
            sc.caller_id_number = form_result.get('caller_id_number')
            sc.gateway = u'default'

            db.add(sc)
            db.commit()
            db.flush()
            db.remove()

        except validators.Invalid, error:
            db.remove()
            return 'Error: %s' % error

        return "Successfully edited context."

    @restrict("GET")
    @authorize(super_user)
    def del_admin(self, **kw):

        if not len(AdminUser.query.all())>1:
            return "You only have one admin! Create another, then delete this one."

        try:
            AdminUser.query.filter(User.id==request.params.get('id', 0)).delete()
            db.commit()
            db.flush()
        except:
            db.remove()
            return "Error deleting admin."

        db.remove()
        return  "Successfully deleted admin."
