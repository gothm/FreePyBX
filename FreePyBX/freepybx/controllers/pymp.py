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
import datetime
from pylons.templating import render_genshi as render
import transaction
from freepybx.lib.base import BaseController
from freepybx.lib.auth import *
from freepybx.model import meta
from freepybx.model.meta import User, Group, Contact
from simplejson import loads, dumps
from webob import Request, Response
import simplejson as json
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from freepybx.lib.auth import *
from freepybx.lib.validators import Username, Login
from freepybx.lib import helpers as h
import pylons
from pylons.decorators import jsonify
from freepybx.lib import template
from freepybx.model import meta
from freepybx.model.meta import *
from pylons.decorators.rest import restrict
from genshi import HTML
import formencode
from formencode import validators
import re
from freepybx.lib.pymap.imap import Pymap, PymapMime
from freepybx.lib.pymap.smtp import PymapSMTP


loggedin = IsLoggedIn()
log = logging.getLogger(__name__)


def get_attachments(id):
    import hashlib
    m = hashlib.md5()
    m.update(str(id))
    return m.hexdigest()

def get_contact(id):
    return "contact data"

def get_logs(id):
    pass

def make_response(obj, _content_type='application/json'):
    res = Response(content_type=_content_type)
    if(content_type=="application/json"):
        res.charset = 'utf8'
        res.body = dumps(obj)
    else:
        res.body = obj
    return res

def fix_date(t):
        return json.dumps(datetime.datetime.utcfromtimestamp(t), cls=PympEncoder)

class ComposeForm(formencode.Schema):
    allow_extra_fields = True
    ignore_key_missing = True
    to_email = validators.Email(resolve_domain=False)

class PympEncoder(json.JSONEncoder):
     def default(self, obj):
         if isinstance(obj, (datetime.datetime, datetime.date)):
             return obj.ctime()
         elif isinstance(obj, datetime.time):
             return obj.isoformat()
         elif isinstance(obj, ObjectId):
             return str(obj)
         return json.JSONEncoder.default(self, obj)


class PympController(BaseController):
    
    def get_message(self, uid=0, folder="INBOX"):

        p = Pymap(session['email'], session['email_password'], session['email_server'])
        msg = p.get_message(uid, folder)
        data = PymapMime(msg)

        message = data.parse_message()

        for att in message['attachments']:
            log.debug("Name: " + att.name)
            log.debug("content-type:" + att.content_type)
            log.debug(att.data)


        return message.body_html or message.body_text

    def get_attachment(self, uid=0, folder="INBOX", filename=None):

        p = Pymap(session['email'], session['email_password'], session['email_server'])
        msg = p.get_message(uid, folder)
        data = PymapMime(msg)
        message = data.parse_message()
        content_type = None
        out = ""

        for att in message['attachments']:
            if att.name==filename:
                out += str(att.data)
                content_type=att.content_type

        response = make_response(out, content_type)
        response.headers = [("Content-type", content_type),]

        return response(request.environ, self.start_response)

    @jsonify
    def get_message_headers(self, folder='INBOX'):
        p = Pymap(session['email'], session['email_password'], session['email_server'])
        return  p.get_message_headers(folder)

    def get_all_message_headers(self, folder='INBOX', **kw):

        p = Pymap(session['email'], session['email_password'], session['email_server'])
        f = p.get_folder_list()
        message_headers = {}

        for folder in f['items']:
            tmp = p.get_message_headers(folder)
            x = tmp.copy()
            message_headers.update(x)

        response = make_response(message_headers)
        response.headers = [("Content-type", 'application/json'),]

        return response(request.environ, self.start_response)

    def get_folder_list(self, **kw):
        p = Pymap(session['email'], session['email_password'], session['email_server'])
        folders = p.get_folder_list()

        response = make_response(folders)
        response.headers = [("Content-type", 'application/json'),]

        return response(request.environ, self.start_response)

    def contacts(self, **kw):
        items = []
        id=1
        log.debug(id)
        rows = meta.Session.query(Contact).filter_by(user_id=id).all()

        if rows:
            for row in rows:
                items.append({'id': row.id, 'first_name': row.first_name,  \
                          'last_name': row.last_name, 'email': row.email})

        out = dict({'identifier': 'id', 'label': 'email', 'items': items})

        response = make_response(out)
        response.headers = [("Content-type", 'application/json'),]

        return response(request.environ, self.start_response)


    @restrict("POST")
    def send_message(self, **kw):
        schema = ComposeForm()
        try:
            form_result = schema.to_python(request.params)
            to_email = form_result["to_email"]
            log.debug(to_email)
            from_email = session['email']
            #cc = form_result["cc"]
            subject = form_result["subject"]
            body = form_result["msg"]
            attachments = []

            send_msg = PymapSMTP(to_email, from_email, subject, body, attachments)
            send_msg.send_message()

        except validators.Invalid, error:
            return 'Validation Error: %s' % error

        return "OK"

