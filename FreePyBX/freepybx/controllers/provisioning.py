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
from sqlalchemy import Date, cast, desc, asc
from sqlalchemy.orm import join
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

class ProvisioningController(BaseController):
    """ What a mess """

    def get_config(self, manufacturer=None, mac=None, model=None):

        #todo DB drive that

        snom320 = "http://provisioning.snom.com/download/fw/snom320-8.4.35-SIP-f.bin"
        snom300 = "http://provisioning.snom.com/download/fw/snom300-8.4.35-SIP-f.bin"
        snom360 = "http://provisioning.snom.com/download/fw/snom360-8.4.35-SIP-f.bin"
        snom370 = "http://provisioning.snom.com/download/fw/snom370-8.4.35-SIP-f.bin"

        if model == 300:
            c.firmware_url = snom300
        elif model == 320:
            c.firmware_url = snom320
        elif model == 360:
            c.firmware_url = snom360
        elif model == 370:
            c.firmware_url = snom370
        #todo make this multiple accounts across multiple servers
        c.ep = PbxEndpoint.query.filter_by(mac=mac).order_by(asc(PbxEndpoint.id)).first()

        return render('provisioning/'+manufacturer+'/'+model+'/default.xml')

