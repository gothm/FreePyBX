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


import formencode
from formencode import validators 
import shutil, os, sys
from datetime import datetime
from pylons import request, response, session, tmpl_context as c, url
import time
from freepybx.model import meta
from freepybx.model.meta import *
from freepybx.lib.util import *
import formencode
from formencode import validators
from pylons.decorators import validate
from simplejson import loads, dumps
from webob import Request, Response
import simplejson as json
from zope.sqlalchemy import ZopeTransactionExtension
import transaction
from itertools import chain
from freepybx.model import *
from freepybx.model.meta import Session as db

import re


__all__=['CompanyForm', 'PbxBlacklistedForm', 'GroupForm', 'FaxForm', 'TTSForm',
         'IVRForm', 'IVREditForm','ConferenceForm', 'CIDForm', 'ExtensionForm',
         'VirtualExtensionForm', 'VirtualMailboxForm', 'TODForm', 'UserForm',
         'UserEditForm', 'ExtEditForm', 'CrmAccountForm', 'CrmCampaignForm',
         'Username', 'Login', 'get_extensions', 'get_ivr','AdminUserForm','CustUserAdminForm',
         'get_faxes','get_usernames', 'get_vextensions', 'get_vmbox', 'CompanyEditForm',
         'get_groups', 'get_conf_bridge', 'get_tod_name', 'get_tts', 'GatewayEditForm',
         'get_campaigns', 'LoginForm', 'ObjEncoder', 'UniqueQueue', 'ProfileEditForm',
         'UniqueAgent','UniqueTier', 'QueueForm', 'AgentForm', 'TierForm',
         'QueueEditForm','AgentEditForm', 'DIDForm', 'GatewayForm', 'ProfileForm',
         'ContextEditForm','ContextForm']


def get_ivr(name):
    return PbxIVR.query.filter(PbxIVR.name==name)\
                .filter(PbxIVR.context==session['context']).all()

def get_usernames(username):
    return User.query.filter_by(username=username).all()

def get_profiles(name):
    return PbxProfile.query.filter_by(name=name).all()

def get_dids(did):
    return PbxDid.query.filter_by(did=did).all()

def get_faxes(fax):
    return PbxFax.query.filter_by(extension=fax).all()

def get_extensions(extension):
    return PbxEndpoint.query.filter(PbxEndpoint.auth_id==extension)\
                .filter(PbxEndpoint.user_context==session['context']).all()

def get_vextensions(vextension):
    return PbxVirtualExtension.query.filter(PbxVirtualExtension.extension==vextension)\
            .filter(PbxVirtualExtension.context==session['context']).all()

def get_vmbox(vmbox):
    return PbxVirtualMailbox.query.filter(PbxVirtualMailbox.extension==vmbox)\
                .filter(PbxVirtualMailbox.context==session['context']).all()

def get_groups(group):
    return PbxGroup.query.filter(PbxGroup.name==group)\
                .filter(PbxGroup.context==session['context']).all()

def get_conf_bridge(ext):
    return PbxConferenceBridge.query.filter(PbxConferenceBridge.extension==ext)\
            .filter(PbxConferenceBridge.context==session['context']).all()

def get_tod_name(name):
    return PbxTODRoute.query.filter(PbxTODRoute.name==name)\
                .filter(PbxTODRoute.context==session['context']).all()

def get_tts(name):
    return PbxTTS.query.filter(PbxTTS.name==name)\
                .filter(PbxTTS.context==session['context']).all()

def get_campaigns(name):
    return CrmCampaign.name.query.filter(CrmCampaign.name==name).all()

def get_context(domain):
    return PbxContext.query.filter(PbxContext.domain==domain).all()

class UniqueUsername(formencode.FancyValidator):
     def _to_python(self, value, state):
         if len(get_usernames(value)) > 0:
             raise formencode.Invalid(
                 'That username already exists',
                 value, state)
         return value

class UniqueProfile(formencode.FancyValidator):
    def _to_python(self, value, state):
        if len(get_profiles(value)) > 0:
            raise formencode.Invalid(
                'That profile already exists',
                value, state)
        return value

class UniqueIVR(formencode.FancyValidator):
     def _to_python(self, value, state):
         if len(get_ivr(value)) > 0:
             raise formencode.Invalid(
                 'That ivr already exists',
                 value, state)
         return value

class UniqueExtension(formencode.FancyValidator):
     def _to_python(self, value, state):
         if len(get_vextensions(value)) > 0:
             raise formencode.Invalid(
                 'That extension already exists',
                 value, state)
         elif  len(get_extensions(value)) > 0:
             raise formencode.Invalid(
                 'That extension already exists',
                 value, state)
         elif len(get_conf_bridge(value)) > 0:
             raise formencode.Invalid(
                 'That extension already exists',
                 value, state)
         elif len(get_vmbox(value)) > 0:
             raise formencode.Invalid(
                 'That extension already exists',
                 value, state)

         return value     

class UniqueGroup(formencode.FancyValidator):
     def _to_python(self, value, state):
         if len(get_groups(value)) > 0:
             raise formencode.Invalid(
                 'That group already exists',
                 value, state)
         return value

class UniqueDID(formencode.FancyValidator):
    def _to_python(self, value, state):
        if len(get_dids(value)) > 0:
            raise formencode.Invalid(
                'That DID already exists',
                value, state)
        return value

class UniqueFax(formencode.FancyValidator):
     def _to_python(self, value, state):
         if len(get_faxes(value)) > 0:
             raise formencode.Invalid(
                 'That fax already exists',
                 value, state)
         return value     
     
     
class UniqueTTS(formencode.FancyValidator):
     def _to_python(self, value, state):
         if len(get_tts(value)) > 0:
             raise formencode.Invalid(
                 'That TTS name already exists',
                 value, state)
         return value

class UniqueTOD(formencode.FancyValidator):
     def _to_python(self, value, state):
         if len(get_tod_name(value)) > 0:
             raise formencode.Invalid(
                 'That TOD already exists',
                 value, state)
         return value
     

class UniqueCampaign(formencode.FancyValidator):
     def _to_python(self, value, state):
         if len(get_campaigns(value)) > 0:
             raise formencode.Invalid(
                 'That campaign already exists',
                 value, state)
         return value


class ObjEncoder(json.JSONEncoder):
     def default(self, obj):
         if isinstance(obj, (datetime, datetime.date)):
             return obj.ctime()
         elif isinstance(obj, datetime.time):
             return obj.isoformat()
         elif isinstance(obj, ObjectId):
             return str(obj)
         return json.JSONEncoder.default(self, obj)
     

class UniqueQueue(formencode.FancyValidator):
     def _to_python(self, value, state):
         if has_queue(value):
             raise formencode.Invalid(
                 'That Queue already exists',
                 value, state)
         return value

class UniqueContext(formencode.FancyValidator):
    def _to_python(self, value, state):
        if get_context(value):
            raise formencode.Invalid(
                'That context already exists',
                value, state)
        return value

class UniqueAgent(formencode.FancyValidator):
     def _to_python(self, value, state):
         if has_agent(value):
             raise formencode.Invalid(
                 'That agent already exists',
                 value, state)
         return value
     
class UniqueTier(formencode.FancyValidator):
     def _to_python(self, value, state):
         if has_tier(value):
             raise formencode.Invalid(
                 'That Tier already exists',
                 value, state)
         return value     

     
class SecurePassword(validators.FancyValidator):
    words_filename = '/usr/share/dict/words'

    min = 5
    non_letter = 1
    letter_regex = re.compile(r'[a-zA-Z]')

    messages = {
        'too_few': 'Your password must be longer than %(min)i '
                  'characters long',
        'non_letter': 'You must include at least %(non_letter)i '
                     'characters in your password',
        }
    def _to_python(self, value, state):
        # _to_python gets run before validate_python.  Here we
        f = open(self.words_filename)
        lower = value.strip().lower()
        for line in f:
            if line.strip().lower() == lower:
                raise formencode.Invalid(
                    'Please do not base your password on a '
                    'dictionary word.', value, state)
        return value.strip()


    def validate_python(self, value, state):
        if len(value) < self.min:
            raise formencode.Invalid(self.message("too_few", state, \
                                                  min=self.min), value, state)
        non_letters = self.letter_regex.sub('', value)

        if len(non_letters) < self.non_letter:
            raise formencode.Invalid(self.message("non_letter", state, \
                                                  non_letter=self.non_letter), value, state)
class QueueForm(formencode.Schema):
    allow_extra_fields = True
    name =  formencode.All(UniqueQueue(), validators.NotEmpty())
    strategy = validators.String(not_empty=True)


class AgentForm(formencode.Schema):
    allow_extra_fields = True
    extension =  formencode.All(UniqueAgent(), validators.NotEmpty())


class TierForm(formencode.Schema):
    allow_extra_fields = True
    extension = validators.String(not_empty=True)
    name = validators.String(not_empty=True)


class QueueEditForm(formencode.Schema):
    allow_extra_fields = True
    strategy = validators.String(not_empty=True)
    
    
class AgentEditForm(formencode.Schema):
    allow_extra_fields = True
    extension = validators.String(not_empty=True)          


class CompanyForm(formencode.Schema):
    allow_extra_fields = True
    ignore_key_missing = True
    first_name = validators.String(not_empty=True)
    last_name = validators.String(not_empty=True)
    address = validators.String(not_empty=False)
    address_2 = validators.String(not_empty=False)
    city = validators.String(not_empty=False)
    state = validators.String(not_empty=False)
    zip = validators.String(not_empty=False)
    tel = validators.String(not_empty=False)
    mobile = validators.String(not_empty=False)

class CompanyEditForm(formencode.Schema):
    allow_extra_fields = True
    ignore_key_missing = True
    first_name = validators.String(not_empty=True)
    last_name = validators.String(not_empty=True)
    address = validators.String(not_empty=False)
    address_2 = validators.String(not_empty=False)
    city = validators.String(not_empty=False)
    state = validators.String(not_empty=False)
    zip = validators.String(not_empty=False)
    tel = validators.String(not_empty=False)
    mobile = validators.String(not_empty=False)


class CrmAccountForm(formencode.Schema):
    allow_extra_fields = True
    ignore_key_missing = True
    first_name = validators.String(not_empty=True)
    last_name = validators.String(not_empty=True)
    address = validators.String(not_empty=False)
    address_2 = validators.String(not_empty=False)
    city = validators.String(not_empty=False)
    state = validators.String(not_empty=False)
    zip = validators.String(not_empty=False)
    tel = validators.String(not_empty=False)
    mobile = validators.String(not_empty=False)
    
    
class CrmCampaignForm(formencode.Schema):
    allow_extra_fields = True
    ignore_key_missing = True
    campaign_name = formencode.All(UniqueCampaign(), validators.MinLength(3), \
                                validators.String(not_empty=True), \
                                validators.MaxLength(32))    
    campaign_extensions = validators.String(not_empty=True)


class ProfileForm(formencode.Schema):
    allow_extra_fields = True
    name = formencode.All(UniqueProfile(), validators.MinLength(3),\
        validators.String(not_empty=True),\
        validators.MaxLength(64))
    odbc_credentials = validators.String(not_empty=True)
    dbname = validators.String(not_empty=True)
    presence_hosts = validators.String(not_empty=True)
    caller_id_type = validators.String(not_empty=True)
    auto_jitterbuffer_msec = validators.Int(not_empty=True)
    ext_rtp_ip = validators.String(not_empty=True)
    ext_sip_ip = validators.String(not_empty=True)
    sip_ip = validators.String(not_empty=True)
    sip_ip = validators.String(not_empty=True)
    sip_port = validators.Number(not_empty=True)
    nonce_ttl = validators.Number(not_empty=True)
    rtp_timer_name = validators.String(not_empty=True)
    codec_prefs = validators.String(not_empty=True)
    inbound_codec_negotiation = validators.String(not_empty=True)
    rtp_timeout_sec = validators.Number(not_empty=True)
    rtp_hold_timeout_sec = validators.Number(not_empty=True)
    rfc2833_pt = validators.Number(not_empty=True)
    dtmf_duration = validators.Number(not_empty=True)
    dtmf_type = validators.String(not_empty=True)
    session_timeout = validators.Number(not_empty=True)
    multiple_registrations = validators.String(not_empty=True)
    vm_from_email = validators.String(not_empty=True)


class ProfileEditForm(formencode.Schema):
    allow_extra_fields = True
    ignore_key_missing = True
    odbc_credentials = validators.String(not_empty=True)
    dbname = validators.String(not_empty=True)
    presence_hosts = validators.String(not_empty=True)
    caller_id_type = validators.String(not_empty=True)
    auto_jitterbuffer_msec = validators.Number(not_empty=True)
    ext_rtp_ip = validators.String(not_empty=True)
    ext_sip_ip = validators.String(not_empty=True)
    rtp_ip = validators.String(not_empty=True)
    sip_ip = validators.String(not_empty=True)
    sip_port = validators.Number(not_empty=True)
    nonce_ttl = validators.Number(not_empty=True)
    rtp_timer_name = validators.String(not_empty=True)
    codec_prefs = validators.String(not_empty=True)
    inbound_codec_negotiation = validators.String(not_empty=True)
    rtp_timeout_sec = validators.Number(not_empty=True)
    rtp_hold_timeout_sec = validators.Number(not_empty=True)
    rfc2833_pt = validators.Number(not_empty=True)
    dtmf_duration = validators.Number(not_empty=True)
    dtmf_type = validators.String(not_empty=True)
    session_timeout = validators.Number(not_empty=True)
    multiple_registrations = validators.String(not_empty=True)
    vm_from_email = validators.String(not_empty=True)

class CompanyForm(formencode.Schema):
    allow_extra_fields = True
    ignore_key_missing = True
    first_name = validators.String(not_empty=True)
    last_name = validators.String(not_empty=True)
    address = validators.String(not_empty=False)
    address_2 = validators.String(not_empty=False)
    city = validators.String(not_empty=False)
    state = validators.String(not_empty=False)
    zip = validators.String(not_empty=False)
    tel = validators.String(not_empty=False)
    mobile = validators.String(not_empty=False)


class GatewayForm(formencode.Schema):
    allow_extra_fields = True
    ignore_key_missing = True
    gateway_name = validators.String(not_empty=True)
    gateway_username = validators.String(not_empty=True)
    realm = validators.String(not_empty=False)
    from_user = validators.String(not_empty=False)
    from_domain = validators.String(not_empty=False)
    password = validators.String(not_empty=False)
    extension = validators.String(not_empty=False)
    proxy = validators.String(not_empty=False)
    mobile = validators.String(not_empty=False)


class GatewayEditForm(formencode.Schema):
    allow_extra_fields = True
    ignore_key_missing = True
    gateway_name = validators.String(not_empty=True)
    gateway_username = validators.String(not_empty=True)
    realm = validators.String(not_empty=False)
    from_user = validators.String(not_empty=False)
    from_domain = validators.String(not_empty=False)
    password = validators.String(not_empty=False)
    extension = validators.String(not_empty=False)
    proxy = validators.String(not_empty=False)
    mobile = validators.String(not_empty=False)


class PbxBlacklistedForm(formencode.Schema):
    allow_extra_fields = True
    cid_number = formencode.All(validators.NotEmpty(), \
                               validators.MinLength(10), \
                               validators.String(not_empty=True), \
                               validators.MaxLength(10))
    
    
class GroupForm(formencode.Schema):
    allow_extra_fields = True
    group_name = formencode.All(UniqueGroup(), validators.MinLength(3), \
                                validators.String(not_empty=True), \
                                validators.MaxLength(32))
    group_extensions = validators.String(not_empty=True)


class DIDForm(formencode.Schema):
    allow_extra_fields = True
    did_name = formencode.All(UniqueDID(), validators.MinLength(10),\
        validators.String(not_empty=True),\
        validators.MaxLength(15))
    company_name = validators.String(not_empty=True)


class FaxForm(formencode.Schema):
    allow_extra_fields = True
    fax_name = formencode.All(UniqueFax(), validators.MinLength(3), \
                                validators.String(not_empty=True), \
                                validators.MaxLength(32))
    

class TTSForm(formencode.Schema):
    allow_extra_fields = True
    name = formencode.All(UniqueTTS(), validators.MaxLength(64))
    text = validators.String(not_empty=True)


class IVRForm(formencode.Schema):
    allow_extra_fields = True
    ivr_name = formencode.All(UniqueIVR(), validators.MaxLength(64))


class IVREditForm(formencode.Schema):
    allow_extra_fields = True
    ivr_id = validators.Number(not_empty=True)  


class ConferenceForm(formencode.Schema):
    allow_extra_fields = True
    extension = formencode.All(UniqueExtension(), validators.NotEmpty(), \
                               validators.MinLength(3), \
                               validators.String(not_empty=True), \
                               validators.MaxLength(4))
    pin = formencode.All(validators.NotEmpty(), \
                               validators.MinLength(3), \
                               validators.String(not_empty=True), \
                               validators.MaxLength(4))


class CIDForm(formencode.Schema):
    allow_extra_fields = True
    cid_number = formencode.All(validators.NotEmpty(), \
                               validators.MinLength(10), \
                               validators.String(not_empty=True), \
                               validators.MaxLength(10))
    pbx_route_id = validators.Number(not_empty=True)


class ExtensionForm(formencode.Schema):
    allow_extra_fields = True
    extension = formencode.All(UniqueExtension(), validators.NotEmpty(), \
                               validators.MinLength(3), \
                               validators.String(not_empty=True), \
                               validators.MaxLength(4))
    password = validators.String(not_empty=True)

class AdminUserForm(formencode.Schema):
    allow_extra_fields = True
    ignore_key_missing = True
    first_name = validators.String(not_empty=True)
    last_name = validators.String(not_empty=True)
    username = formencode.All(UniqueUsername())
    password = SecurePassword()

class VirtualExtensionForm(formencode.Schema):
    allow_extra_fields = True
    vextension_number = formencode.All(UniqueExtension(), \
                               validators.NotEmpty(), \
                               validators.MinLength(3), \
                               validators.String(not_empty=True), \
                               validators.MaxLength(4))
    vextension_did = validators.Number(not_empty=True)    
    
    
class VirtualMailboxForm(formencode.Schema):
    allow_extra_fields = True
    vmbox_number = formencode.All(UniqueExtension(), validators.NotEmpty(), \
                               validators.MinLength(3), \
                               validators.String(not_empty=True), \
                               validators.MaxLength(4))
    vmbox_pin = validators.Number(not_empty=True)      
    
    
class TODForm(formencode.Schema):
    allow_extra_fields = True
    name =  formencode.All(UniqueTOD(), validators.NotEmpty())
    day_start = validators.String(not_empty=True)
    day_end = validators.String(not_empty=True)
    time_start = validators.String(not_empty=True)
    time_end = validators.String(not_empty=True)        
    match_route_id = validators.String(not_empty=True)
    nomatch_route_id = validators.String(not_empty=True)
    
    
class UserForm(formencode.Schema):
    allow_extra_fields = True
    ignore_key_missing = True
    first_name = validators.String(not_empty=True)
    last_name = validators.String(not_empty=True)
    username = formencode.All(UniqueUsername())
    password = SecurePassword()
    address = validators.String(not_empty=False)
    address_2 = validators.String(not_empty=False)
    city = validators.String(not_empty=False)
    state = validators.String(not_empty=False)
    zip = validators.String(not_empty=False)
    tel = validators.String(not_empty=False)
    mobile = validators.String(not_empty=False)


class CustUserAdminForm(formencode.Schema):
    allow_extra_fields = True
    ignore_key_missing = True
    first_name = validators.String(not_empty=True)
    last_name = validators.String(not_empty=True)
    username = formencode.All(UniqueUsername())
    password = SecurePassword()

class UserEditForm(formencode.Schema):
    allow_extra_fields = True
    ignore_key_missing = True
    id = validators.String(not_empty=True)
    first_name = validators.String(not_empty=True)
    last_name = validators.String(not_empty=True)
    username = validators.String(not_empty=True)
    password = SecurePassword()
    address = validators.String(not_empty=False)
    address_2 = validators.String(not_empty=False)
    city = validators.String(not_empty=False)
    state = validators.String(not_empty=False)
    zip = validators.String(not_empty=False)
    tel = validators.String(not_empty=False)
    mobile = validators.String(not_empty=False)


class ExtEditForm(formencode.Schema):
    allow_extra_fields = True
    ignore_key_missing = True
    id = validators.String(not_empty=True)
    password = validators.String(not_empty=True)
    vm_password = validators.String(not_empty=True)

class ContextForm(formencode.Schema):
    allow_extra_fields = True
    ignore_key_missing = True
    profile = validators.String(not_empty=True)
    context = validators.String(not_empty=True)
    company_id = validators.Number(not_empty=True)

class ContextEditForm(formencode.Schema):
    allow_extra_fields = True
    ignore_key_missing = True
    id = validators.String(not_empty=True)
    profile = validators.String(not_empty=True)
    context = validators.String(not_empty=True)
    company_id = validators.Number(not_empty=True)

class Username(validators.Regex):
    regex = R"^(a)?[\w.-]+(@[\w.-]+)?$"
    strip = True
    accept_python = True

    messages = {"invalid": '''Alphanumeric characters, "_", "-", "." and "@" are allowed.'''}

class LoginForm(formencode.Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    username = formencode.validators.Email(not_empty=True)
    password = formencode.validators.String(not_empty=True)

class Login(formencode.Schema):
    allow_extra_fields = True
    strip = True

    username = Username(not_empty=True)
    password = validators.String(not_empty=True)
    