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
from freepybx.lib.validators import *
from freepybx.lib.auth import *
from freepybx.lib.util import *
from genshi import HTML
import shutil, os, sys, math, urllib, urllib2, re, imaplib
from pylons.decorators.rest import restrict
from genshi import HTML
import formencode
from formencode import validators
from decorator import decorator
from pylons.decorators.rest import restrict
import formencode
from formencode import validators
from pylons.decorators import validate
from simplejson import loads, dumps
from freepybx.model import meta
from freepybx.model.meta import *
from freepybx.model.meta import Session as db
import simplejson as json

log = logging.getLogger(__name__)
credential = HasCredential
logged_in = IsLoggedIn()

DEBUG=False

fs_vm_dir = config['app_conf']['fs_vm_dir']

class RootController(BaseController):
    def index(self, **kw):
        return self.login()

    def logout(self, **kw):
        try:
            if 'user' in session:
                session.invalidate()
                del session['user']
        except:
            pass
        return self.login()

    def login(self, **kw):
        try:
            if 'user' in session:
                session.invalidate()
                del session['user']
        except:
            pass
            session.invalidate()
        return render('login.html')

    @restrict("POST")
    def auth_user(self, **kw):
        errors = {}
        schema = LoginForm()

        try:
            form_result = schema.to_python(request.params)
            username = form_result["username"]
            password = form_result["password"]
            shift_start = form_result.get('shift_start', False)
        except:
            return AuthenticationError("")

        if authenticate(username, password):
            log.debug(session.id)
        else:
            return self.login()
        return self.main()

    @authorize(logged_in)
    def main(self, **kw):
        c.is_admin = True if session['auth_level'] < 4 else False
        c.has_crm = session['has_crm']
        c.has_call_center = session['has_call_center']            
        c.queues = get_queue_directory()    
        if c.has_crm:
            c.campaigns = get_campaigns()
        return render('main.html')  
    
    @authorize(credential('pbx_admin'))
    def user_add(self, **kw):
        c.has_crm = session['has_crm']
        c.has_call_center = session['has_call_center']
        return render('user_add.html')    
    
    @authorize(logged_in)
    def pbx_users_list(self, **kw):
        return render('pbx_users_list.html')    
    
    @authorize(logged_in)
    def broker_users(self, **kw):
        c.is_admin = True if session['auth_level'] == 1 else False
        c.has_crm = session['has_crm']
        c.has_call_center = session['has_call_center']
        c.flashvars = "sid="+session.id+"&user_id="+str(session['user_id'])+"&my_name="+session['name']
        return render('broker_users.html')      
    
    @authorize(credential('pbx_admin'))
    def ext_edit(self, **kw):
        c.has_crm  = session['has_crm']
        c.has_call_center = session['has_call_center']
        return render('ext_edit.html')

    @authorize(credential('pbx_admin'))
    def extension_add(self, **kw):
        c.has_crm  = session['has_crm']
        c.has_call_center = session['has_call_center']
        return render('extension_add.html')

    @authorize(credential('pbx_admin'))
    def user_edit(self, **kw):
        c.has_crm  = session['has_crm']
        c.has_call_center = session['has_call_center']
        return render('user_edit.html')


    




