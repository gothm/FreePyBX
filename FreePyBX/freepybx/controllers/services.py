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
from pylons.decorators import validate, jsonify
from simplejson import loads, dumps
import simplejson as json
import os
import simplejson as json
from simplejson import loads, dumps
import cgitb; cgitb.enable()
import urllib

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

class ServicesController(BaseController):
    """ Services Controller """

    def index(self, **kw):
        return "Nothing"

    @authorize(super_user)
    def service_grid(self, **kw):
        return render("services/service_list.html")

    @authorize(super_user)
    def service_plan_grid(self, **kw):
        return render("services/service_plans.html")

    @authorize(super_user)
    def voip_profile_grid(self, **kw):
        return render("services/voip_profiles.html")

    @authorize(super_user)
    def voip_policy_grid(self, **kw):
        return render("services/voip_policies.html")

    @authorize(super_user)
    def service_add(self, **kw):
        return render("services/service_add.html")

    @authorize(super_user)
    def billing_service_types(self):
        items=[]
        for bs in BillingServiceType.query.all():
            items.append({'id': bs.id, 'name': bs.name, 'description': bs.description})

        db.remove()

        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json'),]

        return response(request.environ, self.start_response)

    @authorize(super_user)
    def services(self):
        items=[]

        for svc in BillingService.query.all():
            items.append({'id': svc.id, 'name': svc.name, 'description': svc.description, 'billing_service_type_id': svc.billing_service_type_id,
                          'service_id': svc.service_id})

        db.remove()

        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json'),]

        return response(request.environ, self.start_response)

    @authorize(super_user)
    def service_plans(self):
        items=[]

        for svc in BillingService.query.all():
            items.append({'id': svc.id, 'name': svc.name, 'description': svc.description, 'billing_service_type_id': svc.billing_service_type_id,
                          'service_id': svc.service_id})

        db.remove()

        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json'),]

        return response(request.environ, self.start_response)