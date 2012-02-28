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
from pylons import request, response, session, tmpl_context as c, url
from pylons import config
from pylons.controllers.util import abort, redirect
from freepybx.lib.base import BaseController, render
from freepybx.model import meta
from freepybx.model.meta import *
from genshi import HTML
from pylons.decorators.rest import restrict
import formencode
from formencode import validators
from freepybx.lib.pymap.imap import Pymap
from freepybx.lib.auth import *
from freepybx.lib.forms import *
from freepybx.lib.util import *
from freepybx.lib.validators import *
from decorator import decorator
from pylons.decorators.rest import restrict
import formencode
from formencode import validators
from pylons.decorators import validate
from simplejson import loads, dumps
import simplejson as json
from freepybx.model import meta
from freepybx.model.meta import *
from freepybx.model.meta import Session as db
import simplejson as json
from simplejson import loads, dumps
import urllib
from sqlalchemy import Date, cast, desc, asc
from sqlalchemy.orm import join
import time
import shutil
import cgi
import cgitb; cgitb.enable()
from ESL import *
from sqlalchemy.sql import func

logged_in = IsLoggedIn()
log = logging.getLogger(__name__)

DEBUG=False

fs_vm_dir = config['app_conf']['fs_vm_dir']
fs_dir = config['app_conf']['fs_dir']
ESL_HOST = config['app_conf']['esl_host']
ESL_PORT = config['app_conf']['esl_port']
ESL_PASS = config['app_conf']['esl_pass']



class HelpController(BaseController):

    def index(self, category):
        return  db.query(Help)
