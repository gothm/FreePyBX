""" This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.

    Software distributed under the License is distributed on an "AS IS"
    basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
    License for the specific language governing rights and limitations
    under the License.

    The Original Code is FreePyBX/VoiceWARE. noel@vwci.com

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
from datetime import datetime
from pylons import request, response, session, tmpl_context as c, url
from pylons import config
from pylons.controllers.util import abort, redirect
from freepybx.lib.base import BaseController, render
from freepybx.model import meta
from freepybx.model.meta import *
from freepybx.model.meta import Session as db
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
import os, sys
from subprocess import call
from stat import *
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
import re
import csv


logged_in = IsLoggedIn()
credential = HasCredential

log = logging.getLogger(__name__)

DEBUG=False

fs_vm_dir = config['app_conf']['fs_vm_dir']
fs_dir = config['app_conf']['fs_dir']
ESL_HOST = config['app_conf']['esl_host']
ESL_PORT = config['app_conf']['esl_port']
ESL_PASS = config['app_conf']['esl_pass']


class PbxController(BaseController):
    """ This is the main controller for the config of the pbx. FreeSWITCH
        makes requests from the curl xml interface when the configuration
        is requested from FreeSWITCH. More testing."""

    def index(self):
        return "This space was intentionally left blank."

    def sofiaconf(self):
        c.domains = []
        c.odbc_credentials = config['app_conf']['odbc_credentials']
        c.pbx_profiles = PbxProfile.query.all()
        c.pbx_gateways = PbxGateway.query.all()
        c.pbx_acl_blacklist = PbxAclBlacklist.query.all()
        for domain in PbxContext.query.filter_by(profile=c.pbx_profiles[0].name).all():
            c.domains.append(domain.domain)

        return render('xml/sofia.conf.xml')

    def switchconf(self):
        c.odbc_credentials = config['app_conf']['odbc_credentials']
        return render('xml/switch.conf.xml')

    def aclconf(self):
        c.pbx_gateways = PbxGateway.query.all()
        c.pbx_acl_blacklist = PbxAclBlacklist.query.all()
        c.odbc_credentials = config['app_conf']['odbc_credentials']
        return render('xml/switch.conf.xml')

    def callcenterconf(self):
        c.odbc_credentials = config['app_conf']['odbc_credentials']
        c.domains = []
        c.call_center_queues = []
        c.call_center_agents = []
        c.call_center_tiers = []

        try:
            for domain in PbxContext.query.distinct(PbxContext.domain).all():
                c.domains.append(domain.domain)

            for context in PbxContext.query.distinct(PbxContext.context):
                for queue in CallCenterQueue.query.filter_by(context=context.context).all():
                    c.call_center_queues.append(
                             {'name': queue.name, 'domain': queue.domain, 'moh_sound': queue.moh_sound.split(",")[1],
                             'time_base_score': queue.time_base_score,
                             'max_wait_time': queue.max_wait_time,
                             'max_wait_time_with_no_agent': queue.max_wait_time_with_no_agent,
                             'max_wait_time_with_no_agent_reached': queue.max_wait_time_with_no_agent_reached,
                             'tier_rules_apply': queue.tier_rules_apply,
                             'tier_rule_wait_second': queue.tier_rule_wait_second,
                             'tier_rule_wait_multiply_level': queue.tier_rule_wait_multiply_level,
                             'record_calls': queue.record_calls,
                             'tier_rule_agent_no_wait': queue.tier_rule_agent_no_wait,
                             'discard_abandoned_after': queue.discard_abandoned_after,
                             'abandoned_resume_allowed': queue.abandoned_resume_allowed, 'strategy': queue.strategy,
                             'announce_sound': queue.announce_sound,
                             'announce_frequency': queue.announce_frequency})
                    for agent in CallCenterAgent.query.filter_by(context=context.context).all():
                        c.call_center_agents.append({'name': agent.name, 'domain': queue.domain, 'type': agent.type,
                                                     'max_no_answer': agent.max_no_answer, 'extension': agent.extension,
                                                     'wrap_up_time': agent.wrap_up_time,
                                                     'reject_delay_time': agent.reject_delay_time,
                                                     'busy_delay_time': agent.busy_delay_time,
                                                     'timeout': agent.timeout})
                    for tier in CallCenterTier.query.all():
                        c.call_center_tiers.append({'agent': tier.agent, 'domain': queue.domain, 'queue': tier.queue,
                                                    'level': tier.level, 'position': tier.position})
        except:
            return render('xml/notfound.xml')

        return render('xml/callcenter.conf.xml')

    def cdr_pg_csvconf(self):
        return render('xml/cdr_pg_csv.conf.xml')

    def dbconf(self):
        c.odbc_credentials = config['app_conf']['odbc_credentials']
        return render('xml/db.conf.xml')

    def faxconf(self):
        return render('xml/fax.conf.xml')

    def fifoconf(self):
        c.domains=[]
        for domain in PbxContext.query.distinct(PbxContext.domain).all():
            c.domains.append(domain.domain)
        c.odbc_credentials = config['app_conf']['odbc_credentials']
        return render('xml/fifo.conf.xml')

    def presence_mapconf(self):
        c.domains = []
        for domain in PbxContext.query.filter_by(profile=c.pbx_profiles[0].name).all():
            c.domains.append(domain.domain)
        return render('xml/presence_map.conf.xml')

    def voicemailconf(self):
        c.odbc_credentials = config['app_conf']['odbc_credentials']
        c.pbx_profiles = PbxProfile.query.all()
        return render('xml/voicemail.conf.xml')

    def configuration(self, **kw):

        conf = re.sub('[^A-Za-z0-9]+', '', request.params.get('key_value', "Nothing"))

        if has_method(self, conf):
            return getattr(self, conf)()
        else:
            return render('xml/notfound.xml')

    def directory(self, **kw):
        """ The directory method is called when FreeSWITCH needs information
            about the users endpoints and for things like gateways for the 
            profile, group pointers, as well as our custom stuff like virtual
            mailbox extensions. All specific to XML. Needed for registrations 
            and XML. """

        try:
            if request.params.has_key('purpose'):
                if request.params["purpose"] == "gateways":
                    gateway = db.execute("SELECT pbx_gateways.* FROM pbx_gateways "
                                         "INNER JOIN pbx_profiles "
                                         "ON pbx_profiles.id = pbx_gateways.pbx_profile_id "
                                         "WHERE pbx_profiles.name = :profile_name",
                                         {'profile_name': str(request.params["profile"])})
                    c.gateway = {'name': str(request.params["profile"]), 'gateway': gateway}
                    db.remove()
                    return render('xml/gateways.xml')

            domain = request.params['domain']
            c.groups = []
            c.voicemailboxes = []

            for group in PbxGroup.query.filter_by(context=domain).all():
                exts = []
                for ext in PbxGroupMember.query.filter_by(pbx_group_id=group.id).all():
                    exts.append({'ext': ext.extension})
                c.groups.append({'name': group.name, 'extensions': exts})

            vmext = []
            for vmext in PbxVirtualMailbox.query.filter_by(context=domain).all():
                c.voicemailboxes.append({'extension': vmext.extension, 'pin': vmext.pin})

            if not request.params.has_key('user'):
                c.endpoints = []
                c.domain = domain
                c.endpoints = PbxEndpoint.query.filter_by(user_context = domain).all()
                db.remove()
                return render('xml/directory.xml')
            else:
                user = request.params['user']
                c.endpoints = PbxEndpoint.query.filter_by(user_context = domain).all()

                if not len(c.endpoints):
                    return render('xml/notfound.xml')

                c.domain = domain
                db.remove()
                return render('xml/directory.xml')
        except:
            return render('xml/notfound.xml')
        finally:
            db.remove()

    def dialplan(self, **kw):
        """ This is a recursion engine that creates several objects of nested
            dictionaries and arrays and that are subsequently passed into the
            template context of pylons and interpolated into the xml template
            stream by genshi to create XML dynamically for FreeSWITCH.

            We create this for call control as well as use lua for setting
            inbound routes by context from the default context, since we are
            using only one profile for all sip traffic. Both the XML and lua
            call control are needed. It helps you be lazy and hardcode trash
            into the dialplan that you will eventually forget about.

            :param c.profile: request parameter posted from FreeSWITCH
            :type c.profile: type description

            :returns context object
            :rtype: serialized Dict

            :returns dids object
            :rtype: serialized Dict


            Renders:  ``xml/dialplan.xml``

            I'll highlight the important stuff.

            Pull all of the dids from the db to setup call control for lua
            from the default context on incoming calls from outside the switch.

            Iterate over the contexts and create objects for the xml stream engine.
            These objects are passed to dialplan.xml in the templates/xml directory.

            Retrieve all of the routes.

            Only concerned with what is needed for transfers to the xml context.

            More to do in xml with virtual extensions for things like continue on fail
            timeouts to local voicemail boxes.

            After we check and make sure that our route object is iterable,
            we grab the conditions and actions for the route. We have a template
            meta class and default set of conditions/actions for orphaned routes.
            Not really needed, but it will help you when you make mistakes your
            users will still get dialplan.

            Retrieve the route conditions and actions for the conditions.

            Serialize into context template and pass objects to xml rendering stream.
        """

        c.contexts = []
        routes =  []
        conditions = []
        actions = []

        c.profile = request.params.get('variable_sofia_profile_name','default')

        try:
            c.dids = PbxDid.query.all()
            for context in PbxContext.query.distinct(PbxContext.context):
                conference_bridges = PbxConferenceBridge.query.filter_by(context=context.context).all()
                voicemailboxes = PbxVirtualMailbox.query.filter_by(context=context.context).all()
                faxes = PbxFax.query.filter_by(context=context.context).all()
                gateway = PbxGateway.query.join(PbxProfile).filter(PbxProfile.name==c.profile).first()

                for route in PbxRoute.query.filter_by(context=context.context).all():
                    if route.pbx_route_type_id not in range(1,3):
                        continue
                    if route.pbx_route_type_id == 2:
                        continue
                    route_conditions = is_iter_obj(PbxCondition.query.filter_by(pbx_route_id=route.id).all())
                    if route.pbx_route_type_id == 1:
                        ep = PbxEndpoint.query.filter_by(id=route.pbx_to_id).first()
                        rec = ep.record_inbound_calls
                    else:
                        rec = None
                    if route_conditions is not None:
                        for condition in route_conditions:
                            for action in PbxAction.query.filter_by(pbx_condition_id=condition.id).order_by(PbxAction.precedence).all():
                                actions.append({'application': action.application, 'data': action.data})
                            ds = get_findme(route.name, context.context)
                            if ds:
                                actions.append({'application': "bridge", 'data': ds})
                            conditions.append({'field': condition.field, 'expression': condition.expression, 'actions': actions})
                            actions  = []
                    else:
                        for action in PbxActionTmpl.query.join(PbxConditionTmpl).filter(PbxConditionTmpl.pbx_route_type_id==route.pbx_route_type_id).order_by(PbxActionTmpl.precedence).all():
                            actions.append({'application': action.application, 'data': action.data})

                        actions.append({'application': "bridge", 'data': "sofia/"+str(get_profile())+"/$1"+"%"+context.context})
                        conditions.append({'field': "destination_number", 'expression': "^("+route.name+")", 'actions': actions})
                        actions  = []

                    routes.append({'name': route.name, 'continue_route': str(route.continue_route).lower(), 'conditions': conditions,
                                   'voicemail_enabled': str(route.voicemail_enabled).lower(), 'voicemail_ext': route.voicemail_ext, 'record_inbound_calls': rec})
                    conditions = []

                c.contexts.append({'domain': context.domain, 'context': context.context, 'routes': routes, 'effective_caller_id_name': context.caller_id_name,
                                   'effective_caller_id_number': context.caller_id_number, 'origination_caller_id_name': context.caller_id_name,
                                   'origination_caller_id_number': context.caller_id_number, 'gateway': gateway.name, 'conference_bridges': conference_bridges,
                                   'voicemailboxes': voicemailboxes, 'faxes': faxes})

                routes = []
            db.remove()
            return render('xml/dialplan.xml')

        except Exception, e:
            log.debug("Unexpected error: %s" % e)
            return render('xml/notfound.xml')
        finally:
            db.remove()


    def doc_pbx_json(self):
        """ Below is the JSON data called for the pbx by dojo and/or the template
            context. The json decorators do not work because postgres scary date
            objects are not serializable, so they have to be string formatted or
            worse, passed to the json encoder class and serialized by type
            reference. The encoder is imported from the lib.util.

            Lots of work needs to be done like meta class init functions for
            inserts, but as I rollout subsequent versions, stored procedures
            will eventually replace much of the way sqlalchemy handles the data
            and I prefer not to do it more than once ;p"""

    @authorize(logged_in)
    def users(self):
        items=[]
        exts = []
        for row in User.query.filter(User.company_id==session['company_id']).order_by(asc(User.id)).all():
            for ext in PbxEndpoint.query.filter(PbxEndpoint.user_id==row.id).filter_by(user_context=session['context']).all():
                exts.append(ext.auth_id)
            if not len(exts) > 0:
                extension = "No Extension"
            else:
                extension = ",".join(exts)
            items.append({'id': row.id, 'extension': extension, 'username': row.username, 'password': row.password, 'first_name': row.first_name,
                          'last_name': row.last_name, 'address': row.address, 'address_2': row.address_2, 'city': row.city, 'state': row.state, 'zip': row.zip,
                          'tel': row.tel, 'mobile': row.mobile, 'notes': row.notes, 'created': row.created.strftime("%m/%d/%Y %I:%M:%S %p"), 'updated': row.updated.strftime("%m/%d/%Y %I:%M:%S %p"), 'active': row.active,
                          'auth_level': row.auth_level, 'last_login': row.last_login.strftime("%m/%d/%Y %I:%M:%S %p"), 'remote_addr': row.remote_addr, 'session_id': row.session_id, 'company_id': row.company_id})
            exts = []
        db.remove()

        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def tod_routes(self):
        items=[]
        for tod in PbxTODRoute.query.filter_by(context=session['context']).all():
            route_match = db.query(PbxRoute.id, PbxRouteType.name, PbxRoute.name) \
                    .join(PbxRouteType).filter(PbxRoute.context==session['context']).filter(PbxRoute.id==tod.match_route_id).first()
            route_nomatch = db.query(PbxRoute.id, PbxRouteType.name, PbxRoute.name)\
                    .join(PbxRouteType).filter(PbxRoute.context==session['context']).filter(PbxRoute.id==tod.nomatch_route_id).first()

            items.append({'id': tod.id, 'name': tod.name, 'day_start': tod.day_start, 'day_end': tod.day_end, 'time_start': tod.time_start[1:len(tod.time_start)-3], 'time_end': tod.time_end[1:len(tod.time_end)-3],
                          'match_route_id': tod.match_route_id, 'nomatch_route_id': tod.nomatch_route_id, 'match_name': route_match[1]+': '+route_match[2],
                          'match_id': route_match[0], 'nomatch_name': route_nomatch[1]+': '+route_nomatch[2], 'nomatch_id': route_nomatch[0]})
        db.remove()
        out = dict({'identifier': 'id', 'label': 'extension', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def help(self, id, **kw):
        help = PbxHelp.query.filter(PbxHelp.category_id==id).first()

        if help:
            data = help.data
        else:
            data = "No help to display in this category."

        db.remove()

        out = dict({'help': data})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def user_by_id(self, id, **kw):
        items=[]
        exts = []
        for row in User.query.filter(User.company_id==session['company_id']).filter(User.id==id).order_by(asc(User.id)).all():
            for ext in PbxEndpoint.query.filter(PbxEndpoint.user_id==row.id).all():
                exts.append(ext.auth_id)
            if not len(exts) > 0:
                extension = "No Extension"
            else:
                extension = ",".join(exts)
            items.append({'id': row.id, 'extension': extension, 'username': row.username, 'password': row.password, 'first_name': row.first_name, 'portal_extension': row.portal_extension,
                          'last_name': row.last_name, 'address': row.address, 'address_2': row.address_2, 'city': row.city, 'state': row.state, 'zip': row.zip,
                          'tel': row.tel, 'mobile': row.mobile, 'notes': row.notes, 'created': row.created.strftime("%m/%d/%Y %I:%M:%S %p"), 'updated': row.updated.strftime("%m/%d/%Y %I:%M:%S %p"), 'active': row.active,
                          'auth_level': row.auth_level, 'last_login': row.last_login.strftime("%m/%d/%Y %I:%M:%S %p"), 'remote_addr': row.remote_addr, 'session_id': row.session_id, 'company_id': row.company_id})
            exts = []
        db.remove()
        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def extensions(self):
        items=[]
        ep_stats = []
        for endpoint in PbxEndpoint.query.filter(PbxEndpoint.user_context==session['context']).all():
            for pbx_reg in PbxRegistration.query.filter(PbxRegistration.sip_realm==session['context']).filter(PbxRegistration.sip_user==endpoint.auth_id).all():
                ep_stats.append({'ip': pbx_reg.network_ip, 'port': pbx_reg.network_port})
            is_online = True if len(ep_stats) > 0 else False
            if is_online:
                ip = ep_stats[0]["ip"]
                port = ep_stats[0]["port"]
            else:
                ip = "Unregistered"
                port = "N/A"

            for user in User.query.filter_by(id=endpoint.user_id).all():
                items.append({'id': endpoint.id, 'name': str(user.first_name)+' '+str(user.last_name), 'extension': endpoint.auth_id, 'password': endpoint.password,
                              'outbound_caller_id_name': endpoint.outbound_caller_id_name, 'outbound_caller_id_number': endpoint.outbound_caller_id_number,
                              'internal_caller_id_name': endpoint.internal_caller_id_name, 'internal_caller_id_number': endpoint.internal_caller_id_number,
                              'vm_email': endpoint.vm_email, 'vm_password': endpoint.vm_password, 'vm_attach_email': endpoint.vm_attach_email, 'vm_delete': endpoint.vm_delete,
                              'transfer_fallback_extension': endpoint.transfer_fallback_extension, 'is_online': is_online, 'ip': ip, 'port': port})
            ep_stats = []

        db.remove()

        out = dict({'identifier': 'extension', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def extension_by_id(self, id, **kw):
        items=[]
        for endpoint in PbxEndpoint.query.filter(PbxEndpoint.user_context==session['context']).filter(PbxEndpoint.id==id).all():
            for user in User.query.filter_by(id=endpoint.user_id).all():
                items.append({'id': endpoint.id, 'name': str(user.first_name)+' '+str(user.last_name), 'extension': endpoint.auth_id, 'password': endpoint.password,
                              'outbound_caller_id_name': endpoint.outbound_caller_id_name, 'outbound_caller_id_number': endpoint.outbound_caller_id_number,
                              'internal_caller_id_name': endpoint.internal_caller_id_name, 'internal_caller_id_number': endpoint.internal_caller_id_number,
                              'vm_email': endpoint.vm_email, 'vm_password': endpoint.vm_password, 'vm_attach_email': endpoint.vm_attach_email, 'vm_delete': endpoint.vm_delete,
                              'transfer_fallback_extension': endpoint.transfer_fallback_extension, 'find_me': endpoint.find_me, 'follow_me_1': endpoint.follow_me_1,
                              'follow_me_2': endpoint.follow_me_2, 'follow_me_3': endpoint.follow_me_3, 'follow_me_4': endpoint.follow_me_4, 'call_timeout': endpoint.call_timeout,
                              'timeout_destination': endpoint.timeout_destination, 'record_inbound_calls': endpoint.record_inbound_calls, 'record_outbound_calls': endpoint.record_outbound_calls})
        db.remove()

        out = dict({'identifier': 'extension', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def names_user_ids(self):
        names=[]
        user_ids=[]
        for row in User.query.filter_by(company_id=session['company_id']).all():
            names.append(row.first_name+' '+row.last_name)
            user_ids.append(row.id)

        db.remove()

        out = dict({'names': names, 'user_ids': user_ids})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def destinations(self):
        items=[]
        for row in PbxEndpoint.query.filter_by(user_context=session['context']).all():
            items.append({'id': row.id, 'ext': row.auth_id})

        db.remove()

        out = dict({'identifier': 'ext', 'label': 'ext', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def cdr(self):
        items=[]
        for row in PbxCdr.query.filter_by(context=session['context']).order_by(desc(PbxCdr.id)).all():
            num = row.caller_id_number if len(row.caller_id_number)<=10 else row.caller_id_number[len(row.caller_id_number)-10:]
            items.append({'id': row.id, 'caller_id_name': row.caller_id_name, 'caller_id_number': num,
                          'destination_number': row.destination_number, 'start_stamp': fix_date(row.start_stamp), 'answer_stamp': fix_date(row.answer_stamp),
                          'end_stamp': fix_date(row.end_stamp), 'duration': row.duration, 'billsec':row.billsec, 'hangup_cause': row.hangup_cause})
        db.remove()

        out = dict({'identifier': 'id', 'label': 'caller_id_number', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def cdr_ext_summary(self):
        items=[]
        sdate = request.params.get("sdate", 'TIMESTAMP')
        edate = request.params.get("edate", 'CURRENT_TIMESTAMP')

        sdate = "TIMESTAMP '"+sdate+"'" if sdate != 'TIMESTAMP' else "TIMESTAMP '"+datetime.today().strftime("%m/%d/%Y 12:00:00 AM")+"'"
        edate = "TIMESTAMP '"+edate+"' + interval '1 day'" if edate != 'CURRENT_TIMESTAMP' else 'CURRENT_TIMESTAMP'

        for row in db.execute("SELECT DISTINCT users.id, users.first_name ||' '|| users.last_name AS agent, users.portal_extension as extension, "
                              "(SELECT COUNT(uuid) FROM cdr WHERE (cdr.caller_id_number = users.portal_extension or cdr.destination_number = users.portal_extension) "
                              "AND cdr.start_stamp > "+sdate+" AND cdr.end_stamp < "+edate+" AND call_direction = 'inbound' AND cdr.context = companies.context) AS call_count_in, "
                              "(SELECT COUNT(uuid) FROM cdr WHERE (cdr.caller_id_number = users.portal_extension or cdr.destination_number = users.portal_extension) "
                              "AND cdr.start_stamp > "+sdate+" AND cdr.end_stamp < "+edate+" AND call_direction = 'outbound' AND cdr.context =  companies.context) AS call_count_out, "
                              "(SELECT coalesce(sum(billsec),0) FROM cdr WHERE  (cdr.caller_id_number = users.portal_extension or cdr.destination_number = users.portal_extension) "
                              "AND cdr.start_stamp > "+sdate+" AND cdr.end_stamp < "+edate+" AND call_direction = 'inbound' AND cdr.context =  companies.context) AS time_on_call_in, "
                              "(SELECT coalesce(sum(billsec),0) FROM cdr WHERE  (cdr.caller_id_number = users.portal_extension or cdr.destination_number = users.portal_extension) "
                              "AND cdr.start_stamp > "+sdate+" AND cdr.end_stamp < "+edate+" AND call_direction = 'outbound' AND cdr.context =  companies.context) AS time_on_call_out "
                              "FROM users "
                              "INNER JOIN companies ON companies.id = users.company_id "
                              "WHERE companies.id = :company_id "
                              "ORDER BY extension", {'company_id': session['company_id']}).fetchall():

            m, s = divmod(row.time_on_call_in, 60)
            h, m = divmod(m, 60)
            toci = "%dh:%02dm:%02ds" % (h, m, s)

            m, s = divmod(row.time_on_call_out, 60)
            h, m = divmod(m, 60)
            toco = "%dh:%02dm:%02ds" % (h, m, s)

            items.append({'id': row.id, 'agent': row.agent, 'extension': row.extension, 'call_count_in': row.call_count_in,
                          'qstring': '?ext='+row.extension+'&sdate='+request.params.get("sdate", 'TIMESTAMP')+'&edate='+request.params.get("edate", 'CURRENT_TIMESTAMP'),
                          'call_count_out': row.call_count_out, 'time_on_call_in': toci, 'time_on_call_out': toco,
                          'from': request.params.get("sdate", 'TIMESTAMP') if request.params.get("sdate", 'TIMESTAMP') != 'TIMESTAMP' else datetime.today().strftime("%m/%d/%Y"),
                          'to': request.params.get("edate", 'CURRENT_TIMESTAMP') if request.params.get("edate", 'CURRENT_TIMESTAMP') != 'CURRENT_TIMESTAMP' else datetime.today().strftime("%m/%d/%Y")})

        db.remove()

        out = dict({'identifier': 'id', 'label': 'agent', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    def cdr_ext(self):
        items=[]

        sdate = request.params.get("sdate", 'TIMESTAMP')
        edate = request.params.get("edate", 'CURRENT_TIMESTAMP')

        ext = request.params.get("ext")

        sdate = "TIMESTAMP '"+sdate+"'" if sdate != 'TIMESTAMP' else "TIMESTAMP '"+datetime.today().strftime("%m/%d/%Y 12:00:00 AM")+"'"
        edate = "TIMESTAMP '"+edate+"' + interval '1 day'" if edate != 'CURRENT_TIMESTAMP' else 'CURRENT_TIMESTAMP'

        for row in db.execute("SELECT  cdr.id AS id, caller_id_name, caller_id_number, destination_number, start_stamp, answer_stamp, "
                              "end_stamp, duration, billsec, hangup_cause "
                              "FROM cdr "
                              "INNER JOIN companies ON cdr.context = companies.context "
                              "WHERE companies.id = :company_id "
                              "AND cdr.start_stamp > "+sdate+" AND cdr.end_stamp < "+edate+" "
                              "AND cdr.call_direction IS NOT NULL "
                              "AND (cdr.caller_id_number = :extension or cdr.destination_number = :extension) "
                              "ORDER BY id", {'company_id': session['company_id'], 'extension': ext}).fetchall():

            num = row.caller_id_number if len(row.caller_id_number)<=10 else row.caller_id_number[len(row.caller_id_number)-10:]

            items.append({'id': row.id, 'caller_id_name': row.caller_id_name, 'caller_id_number': num,
                          'destination_number': row.destination_number, 'start_stamp': fix_date(row.start_stamp), 'answer_stamp': fix_date(row.answer_stamp),
                          'end_stamp': fix_date(row.end_stamp), 'duration': row.duration, 'billsec':row.billsec, 'hangup_cause': row.hangup_cause})

        db.remove()

        out = dict({'identifier': 'id', 'label': 'caller_id_number', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def cdr_ext_download(self):
        items=[]

        start = request.params.get("sdate")
        end = request.params.get("edate")

        sdate = request.params.get("sdate", 'TIMESTAMP')
        edate = request.params.get("edate", 'CURRENT_TIMESTAMP')

        ext = request.params.get("ext")

        sdate = "TIMESTAMP '"+sdate+"'" if sdate != 'TIMESTAMP' else "TIMESTAMP '"+datetime.today().strftime("%m/%d/%Y 12:00:00 AM")+"'"
        edate = "TIMESTAMP '"+edate+"' + interval '1 day'" if edate != 'CURRENT_TIMESTAMP' else 'CURRENT_TIMESTAMP'

        for row in db.execute("SELECT  cdr.id AS id, caller_id_name, caller_id_number, destination_number, start_stamp, answer_stamp, "
                              "end_stamp, duration, billsec, hangup_cause "
                              "FROM cdr "
                              "INNER JOIN companies ON cdr.context = companies.context "
                              "WHERE companies.id = :company_id "
                              "AND cdr.start_stamp > "+sdate+" AND cdr.end_stamp < "+edate+" "
                              "AND cdr.call_direction IS NOT NULL "
                              "AND (cdr.caller_id_number = :extension or cdr.destination_number = :extension) "
                              "ORDER BY id", {'company_id': session['company_id'], 'extension': ext}).fetchall():

            num = row.caller_id_number if len(row.caller_id_number)<=10 else row.caller_id_number[len(row.caller_id_number)-10:]

            items.append({'id': row.id, 'caller_id_name': row.caller_id_name, 'caller_id_number': num,
                          'destination_number': row.destination_number, 'start_stamp': fix_date(row.start_stamp), 'answer_stamp': fix_date(row.answer_stamp),
                          'end_stamp': fix_date(row.end_stamp), 'duration': row.duration, 'billsec':row.billsec, 'hangup_cause': row.hangup_cause})

        db.remove()

        f = open("/tmp/Report_ext"+ext+".csv", "wb+")
        csv_file = csv.writer(f)

        #f=csv.writer(open("/tmp/Report_ext"+ext+".csv",'wb+'))
        csv_file.writerow(["Name","Number","Destination","Start Time","End Time", "Duration Seconds","Hangup Cause"])

        for csv_items in items:
            csv_file.writerow([csv_items['caller_id_name'], csv_items['caller_id_number'], csv_items['destination_number'], csv_items['start_stamp'], csv_items['duration'], csv_items['hangup_cause']])

        f.close()

        size = os.path.getsize("/tmp/Report_ext"+ext+".csv")

        response = make_file_response("/tmp/Report_ext"+ext+".csv")
        response.headers = [("Content-type", "application/octet-stream"),
                            ("Content-Disposition", "attachment; filename="+"Report_ext"+ext+".csv"),
                            ("Content-length", str(size)),]

        return response(request.environ, self.start_response)


    @authorize(logged_in)
    def avail_findme_endpoints(self):
        items=[]
        for row in PbxEndpoint.query.filter_by(user_context=session['context']).order_by(PbxEndpoint.auth_id).all():
            if PbxFindMeRoute.query.filter_by(pbx_endpoint_id=row.id).count()>0:
                continue
            items.append({'id': row.id, 'auth_id': row.auth_id})
        db.remove()

        out = dict({'identifier': 'id', 'label': 'auth_id', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def inuse_findme_endpoints(self):
        items=[]
        for row in db.query(PbxFindMeRoute.id, PbxEndpoint.auth_id) \
                .select_from(join(PbxFindMeRoute, PbxEndpoint, PbxEndpoint.pbx_find_me)) \
                .filter(PbxEndpoint.user_context==session['context']).all():
            items.append({'id': row.id, 'auth_id': row.auth_id})

        db.remove()

        out = dict({'identifier': 'id', 'label': 'auth_id', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def routes(self):
        items=[]
        for row in db.execute("SELECT sr.id, sr.name AS data, sr.pbx_to_id AS to_id, sr.pbx_route_type_id AS type_id, srt.name|| ': ' ||sr.name AS name "
                              "FROM pbx_routes sr "
                              "INNER JOIN pbx_route_types srt ON sr.pbx_route_type_id = srt.id "
                              "WHERE sr.context = :context", {'context': session['context']}):
            items.append({'id': row.id, 'data': row.data, 'to_id': row.to_id, 'type_id': row.type_id, 'name': row.name})
        db.remove()

        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def dids(self):
        items=[]

        for did in PbxDid.query.filter_by(context=session['context']).all():
            route = db.query(PbxRoute.id, PbxRouteType.name, PbxRoute.name) \
                    .join(PbxRouteType).filter(PbxRoute.context==session['context']).filter(PbxRoute.id==did.pbx_route_id).first()
            if route:
                items.append({'id': did.id, 'did': did.did, 'route_name': route[1]+': '+route[2], 'pbx_route_id': route.id})
            else:
                items.append({'id': did.id, 'did': did.did, 'route_name': "Broken Route!", 'pbx_route_id': 0})

        lbid = get_route_labels_ids()
        db.remove()

        out = dict({'identifier': 'id', 'label': 'name', 'items': items,'did_labels': lbid[0], 'did_ids': lbid[1]})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def vextensions(self):
        items=[]
        for extension in PbxVirtualExtension.query.filter_by(context=session['context']).all():
            items.append({'id': extension.id, 'extension': extension.extension, 'did': extension.did})

        db.remove()

        out = dict({'identifier': 'id', 'label': 'extension', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def tts(self):
        items=[]
        for row in PbxTTS.query.filter_by(context=session['context']).all():
            items.append({'id': row.id, 'name': row.name, 'text': row.text})

        db.remove()

        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def vmboxes(self):
        items=[]
        for extension in PbxVirtualMailbox.query.filter_by(context=session['context']).all():
            items.append({'id': extension.id, 'extension': extension.extension, 'pin': extension.pin})

        db.remove()

        out = dict({'identifier': 'id', 'label': 'extension', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def groups(self):
        items=[]
        members = []
        for group in PbxGroup.query.filter_by(context=session['context']).all():
            for extension in PbxGroupMember.query.filter_by(pbx_group_id=group.id).all():
                members.append(extension.extension)
            items.append({'id': group.id, 'name': group.name, 'ring_strategy': group.ring_strategy, 'members': ",".join(members)})
            members = []

        db.remove()

        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def conferences(self):
        items=[]
        for conf in PbxConferenceBridge.query.filter_by(context=session['context']).all():
            items.append({'id': conf.id, 'extension': conf.extension, 'pin': conf.pin})
            members = []

        db.remove()

        out = dict({'identifier': 'id', 'label': 'extension', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def cid_routes(self):
        items=[]
        for cid in PbxCallerIDRoute.query.filter_by(context=session['context']).all():
            route = db.query(PbxRoute.id, PbxRouteType.name, PbxRoute.name) \
                    .join(PbxRouteType).filter(PbxRoute.context==session['context']).filter(PbxRoute.id==cid.pbx_route_id).first()
            items.append({'id': cid.id, 'cid_number': cid.cid_number, 'pbx_route_id': cid.pbx_route_id, 'pbx_route_name': route[1]+': '+route[2]})
            members = []

        db.remove()

        out = dict({'identifier': 'id', 'label': 'cid_number', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def blacklisted(self):
        items=[]
        for cid in PbxBlacklistedNumber.query.filter_by(context=session['context']).all():
            items.append({'id': cid.id, 'cid_number': cid.cid_number})
            members = []

        db.remove()

        out = dict({'identifier': 'id', 'label': 'cid_number', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def ivr(self):
        items=[]
        for ivr in PbxIVR.query.filter_by(context=session['context']).all():
            items.append({'id': ivr.id, 'name': ivr.name})
            members = []

        db.remove()

        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def ivr_by_id(self, id, **kw):
        items=[]
        for ivr in PbxIVR.query.filter_by(context=session['context']).filter_by(id=id).all():
            options=[]
            for opt in PbxIVROption.query.filter_by(pbx_ivr_id=ivr.id).all():
                options.append({'option': opt.option, 'pbx_route_id': opt.pbx_route_id})

            items.append({'id': ivr.id, 'name': ivr.name,'timeout': ivr.timeout, 'direct_dial': ivr.direct_dial, 'data': ivr.data, \
                          'audio_name': str(ivr.audio_type)+','+str(ivr.data), 'timeout_destination': ivr.timeout_destination, 'options': options})

        db.remove()

        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def vmbox_add(self, **kw):
        schema = VirtualMailboxForm()
        try:
            form_result = schema.to_python(request.params)
            svm = PbxVirtualMailbox()
            svm.extension = form_result.get('vmbox_number')
            svm.pin = form_result.get('vmbox_pin')
            svm.context = session['context']

            db.add(svm)
            db.commit()
            db.flush()

            r = PbxRoute()
            r.context = session['context']
            r.domain = session['context']
            r.name = form_result.get('vmbox_number')
            r.continue_route = True
            r.voicemail_enable = True
            r.voicemail_ext = form_result.get('vmbox_number')
            r.pbx_route_type_id = 3
            r.pbx_to_id = svm.id

            db.add(r)
            db.commit()
            db.flush()
            db.remove()

        except validators.Invalid, error:
            msg='Validation Error: %s' % error

        finally:
            if len(msg)>0:
                return msg
            else:
                return "Successfully added extension %s" % form_result.get('extension')
            db.remove()

    @authorize(logged_in)
    def group_add(self, **kw):
        schema = GroupForm()
        try:
            form_result = schema.to_python(request.params)
            sg = PbxGroup()
            sg.name = form_result.get('group_name')
            sg.context = session['context']
            sg.ring_strategy = form_result.get('group_ring_strategy', 'sim')
            sg.no_answer_destination = form_result.get('no_answer_destination', None)
            sg.timeout = form_result.get('timeout', 13)

            db.add(sg)
            db.commit()
            db.flush()

            for i in form_result.get('group_extensions').split(","):
                if not i.isdigit():
                    continue
                sm = PbxGroupMember()
                sm.pbx_group_id = sg.id
                sm.extension = i

                db.add(sm)
                db.commit()
                db.flush()

        except validators.Invalid, error:
            db.remove()
            return 'Validation Error: %s' % error

        r = PbxRoute()
        r.context = session['context']
        r.domain = session['context']
        r.name = form_result.get('group_name')
        r.continue_route = True
        r.voicemail_enable = True
        r.voicemail_ext = form_result.get('group_name')
        r.pbx_route_type_id = 4
        r.pbx_to_id = sg.id

        db.add(r)
        db.commit()
        db.flush()

        db.remove()
        return "OK"

    @authorize(logged_in)
    def ivr_add(self, **kw):
        schema = IVRForm()
        try:
            form_result = schema.to_python(request.params)
            s = PbxIVR()
            s.name = form_result.get('ivr_name')

            s.audio_type = form_result.get('audio_name').split(",")[0].strip()
            s.data = form_result.get('audio_name').split(",")[1].strip()
            s.domain = session['context']
            s.context = session['context']
            s.timeout = form_result.get('timeout')
            s.timeout_destination = form_result.get('timeout_destination')

            if request.params.has_key('direct_dial'):
                s.direct_dial = True
            else:
                s.direct_dial = False

            db.add(s)
            db.commit()
            db.flush()

            if len(form_result.get('option_1'))>0:
                i = PbxIVROption()
                i.option=1
                i.pbx_ivr_id = s.id
                i.pbx_route_id = form_result.get('option_1')

                db.add(i)
                db.commit()
                db.flush()

            if len(form_result.get('option_2'))>0:
                i = PbxIVROption()
                i.option=2
                i.pbx_ivr_id = s.id
                i.pbx_route_id = form_result.get('option_2')

                db.add(i)
                db.commit()
                db.flush()

            if len(form_result.get('option_3'))>0:
                i = PbxIVROption()
                i.option=3
                i.pbx_ivr_id = s.id
                i.pbx_route_id = form_result.get('option_3')

                db.add(i)
                db.commit()
                db.flush()

            if len(form_result.get('option_4'))>0:
                i = PbxIVROption()
                i.option=4
                i.pbx_ivr_id = s.id
                i.pbx_route_id = form_result.get('option_4')

                db.add(i)
                db.commit()
                db.flush()

            if len(form_result.get('option_5'))>0:
                i = PbxIVROption()
                i.option=5
                i.pbx_ivr_id = s.id
                i.pbx_route_id = form_result.get('option_5')

                db.add(i)
                db.commit()
                db.flush()

            if len(form_result.get('option_6'))>0:
                i = PbxIVROption()
                i.option=6
                i.pbx_ivr_id = s.id
                i.pbx_route_id = form_result.get('option_6')

                db.add(i)
                db.commit()
                db.flush()

            if len(form_result.get('option_7'))>0:
                i = PbxIVROption()
                i.option=7
                i.pbx_ivr_id = s.id
                i.pbx_route_id = form_result.get('option_7')

                db.add(i)
                db.commit()
                db.flush()

            if len(form_result.get('option_8'))>0:
                i = PbxIVROption()
                i.option=8
                i.pbx_ivr_id = s.id
                i.pbx_route_id = form_result.get('option_8')

                db.add(i)
                db.commit()
                db.flush()

            if len(form_result.get('option_9'))>0:
                i = PbxIVROption()
                i.option=9
                i.pbx_ivr_id = s.id
                i.pbx_route_id = form_result.get('option_9')

                db.add(i)
                db.commit()
                db.flush()

            if len(form_result.get('option_0'))>0:
                i = PbxIVROption()
                i.option=0
                i.pbx_ivr_id = s.id
                i.pbx_route_id = form_result.get('option_0')

                db.add(i)
                db.commit()
                db.flush()

        except validators.Invalid, error:
            db.remove()
            return 'Validation Error: Please correct form inputs and resubmit.'

        r = PbxRoute()
        r.context = session['context']
        r.domain = session['context']
        r.name = form_result.get('ivr_name')
        r.continue_route = True
        r.voicemail_enable = True
        r.voicemail_ext = form_result.get('ivr_name')
        r.pbx_route_type_id = 5
        r.pbx_to_id = s.id

        db.add(r)
        db.commit()
        db.flush()

        db.remove()
        return "OK"

    @authorize(logged_in)
    def ivr_edit(self, **kw):
        schema = IVREditForm()
        try:
            form_result = schema.to_python(request.params)
            s = PbxIVR.query.filter_by(id=form_result.get('ivr_id')).filter_by(context=session['context']).first()
            s.audio_type = form_result.get('audio_name').split(",")[0].strip()
            s.data = form_result.get('audio_name').split(",")[1].strip()
            s.domain = session['context']
            s.context = session['context']
            s.timeout = form_result.get('timeout')
            s.timeout_destination=form_result.get('timeout_destination')

            if request.params.has_key('direct_dial'):
                s.direct_dial=True
            else:
                s.direct_dial=False

            db.commit()
            db.flush()

            PbxIVROption.query.filter_by(pbx_ivr_id=s.id).delete()
            db.commit()
            db.flush()

            if len(form_result.get('option_1'))>0:
                i = PbxIVROption()
                i.option=1
                i.pbx_ivr_id=s.id
                i.pbx_route_id=form_result.get('option_1')

                db.add(i)
                db.commit()
                db.flush()

            if len(form_result.get('option_2'))>0:
                i = PbxIVROption()
                i.option=2
                i.pbx_ivr_id=s.id
                i.pbx_route_id=form_result.get('option_2')

                db.add(i)
                db.commit()
                db.flush()

            if len(form_result.get('option_3'))>0:
                i = PbxIVROption()
                i.option=3
                i.pbx_ivr_id=s.id
                i.pbx_route_id=form_result.get('option_3')

                db.add(i)
                db.commit()
                db.flush()

            if len(form_result.get('option_4'))>0:
                i = PbxIVROption()
                i.option=4
                i.pbx_ivr_id=s.id
                i.pbx_route_id=form_result.get('option_4')

                db.add(i)
                db.commit()
                db.flush()

            if len(form_result.get('option_5'))>0:
                i = PbxIVROption()
                i.option=5
                i.pbx_ivr_id=s.id
                i.pbx_route_id=form_result.get('option_5')

                db.add(i)
                db.commit()
                db.flush()

            if len(form_result.get('option_6'))>0:
                i = PbxIVROption()
                i.option=6
                i.pbx_ivr_id=s.id
                i.pbx_route_id=form_result.get('option_6')

                db.add(i)
                db.commit()
                db.flush()

            if len(form_result.get('option_7'))>0:
                i = PbxIVROption()
                i.option=7
                i.pbx_ivr_id=s.id
                i.pbx_route_id=form_result.get('option_7')

                db.add(i)
                db.commit()
                db.flush()

            if len(form_result.get('option_8'))>0:
                i = PbxIVROption()
                i.option=8
                i.pbx_ivr_id=s.id
                i.pbx_route_id=form_result.get('option_8')

                db.add(i)
                db.commit()
                db.flush()

            if len(form_result.get('option_9'))>0:
                i = PbxIVROption()
                i.option=9
                i.pbx_ivr_id=s.id
                i.pbx_route_id=form_result.get('option_9')

                db.add(i)
                db.commit()
                db.flush()

            if len(form_result.get('option_0'))>0:
                i = PbxIVROption()
                i.option=0
                i.pbx_ivr_id=s.id
                i.pbx_route_id=form_result.get('option_0')

                db.add(i)
                db.commit()
                db.flush()

        except validators.Invalid, error:
            db.remove()
            return 'Validation Error: Please correct form inputs and resubmit.'

        db.remove()
        return "Successfully updated IVR."

    @authorize(logged_in)
    def conf_add(self, **kw):
        schema = ConferenceForm()
        try:
            form_result = schema.to_python(request.params)
            sc = PbxConferenceBridge()
            sc.extension = form_result.get('extension')
            sc.pin = form_result.get('pin')
            sc.context = session['context']
            sc.domain = session['context']

            db.add(sc)
            db.commit()
            db.flush()

        except validators.Invalid, error:
            db.remove()
            return 'Validation Error: %s' % error

        r = PbxRoute()
        r.context = session['context']
        r.domain = session['context']
        r.name = form_result.get('extension')
        r.continue_route = False
        r.voicemail_enable = False
        r.voicemail_ext = form_result.get('extension')
        r.pbx_route_type_id = 7
        r.pbx_to_id = sc.id

        db.add(r)
        db.commit()
        db.flush()

        db.remove()
        return "Successfully added conference bridge."

    @authorize(logged_in)
    def cid_add(self, **kw):
        schema = CIDForm()
        try:
            form_result = schema.to_python(request.params)
            sc = PbxCallerIDRoute()
            sc.cid_number = form_result.get('cid_number')
            sc.pbx_route_id = form_result.get('pbx_route_id')
            sc.context = session['context']
            sc.domain = session['context']

            db.add(sc)
            db.commit()
            db.flush()

        except validators.Invalid, error:
            db.remove()
            return 'Validation Error: %s' % error

        db.remove()
        return "Successfully added Caller ID Route."

    @authorize(logged_in)
    def tts_add(self, **kw):
        schema = TTSForm()
        try:
            form_result = schema.to_python(request.params)
            t = PbxTTS()
            t.name = form_result.get('name')
            t.text = form_result.get('text')
            t.context = session['context']
            t.domain = session['context']
            t.voice = u'Allison'

            db.add(t)
            db.commit()
            db.flush()

        except validators.Invalid, error:
            db.remove()
            return 'Validation Error: %s' % error

        db.remove()
        return "Successfully added Text to Speech entry."

    @authorize(logged_in)
    def blacklist_add(self, **kw):
        schema = PbxBlacklistedForm()
        try:
            form_result = schema.to_python(request.params)
            sc = PbxBlacklistedNumber()
            sc.cid_number = form_result.get('cid_number')
            sc.context = session['context']
            sc.domain = session['context']

            db.add(sc)
            db.commit()
            db.flush()

        except validators.Invalid, error:
            db.remove()
            return 'Validation Error: %s' % error

        db.remove()
        return "Successfully added to blacklist."

    @authorize(logged_in)
    def vextension_add(self, **kw):
        schema = VirtualExtensionForm()
        try:
            form_result = schema.to_python(request.params)
            sve = PbxVirtualExtension()
            sve.extension = form_result.get('vextension_number')
            sve.did = form_result.get('vextension_did')
            sve.context = session['context']

            db.add(sve)
            db.commit()
            db.flush()

            r = PbxRoute()
            r.context = session['context']
            r.domain = session['context']
            r.name = form_result.get('vextension_number')
            r.continue_route = True
            r.voicemail_enable = True
            r.voicemail_ext = form_result.get('vextension_number')
            r.pbx_route_type_id = 2
            r.pbx_to_id = sve.id

            db.add(r)
            db.commit()
            db.flush()

        except validators.Invalid, error:
            return 'Validation Error: %s' % error

        db.remove()
        return "Successfully created virtual extension."

    @authorize(logged_in)
    def vmbox_add(self, **kw):
        schema = VirtualMailboxForm()
        try:
            form_result = schema.to_python(request.params)
            svm = PbxVirtualMailbox()
            svm.extension = form_result.get('vmbox_number')
            svm.pin = form_result.get('vmbox_pin')
            svm.context = session['context']

            db.add(svm)
            db.commit()
            db.flush()

            r = PbxRoute()
            r.context = session['context']
            r.domain = session['context']
            r.name = form_result.get('vmbox_number')
            r.continue_route = True
            r.voicemail_enable = True
            r.voicemail_ext = form_result.get('vmbox_number')
            r.pbx_route_type_id = 3
            r.pbx_to_id = svm.id

            db.add(r)
            db.commit()
            db.flush()

        except validators.Invalid, error:
            return 'Validation Error: %s' % error

        finally:
            db.remove()
            return "OK"

    @authorize(logged_in)
    def tod_route_add(self, **kw):
        schema = TODForm()
        try:
            form_result = schema.to_python(request.params)
            t = PbxTODRoute()
            t.domain = session['context']
            t.context = session['context']
            t.name = form_result.get('name')
            t.day_start = form_result.get('day_start')
            t.day_end = form_result.get('day_end')
            t.time_start = form_result.get('time_start')
            t.time_end = form_result.get('time_end')
            t.match_route_id = form_result.get('match_route_id')
            t.nomatch_route_id = form_result.get('nomatch_route_id')

            db.add(t)
            db.commit()
            db.flush()

            r = PbxRoute()
            r.context = session['context']
            r.domain = session['context']
            r.name = form_result.get('name')
            r.continue_route = True
            r.voicemail_enable = True
            r.voicemail_ext = form_result.get('name')
            r.pbx_route_type_id = 6
            r.pbx_to_id = t.id

            db.add(r)
            db.commit()
            db.flush()

        except validators.Invalid, error:
            return 'Error: %s' % error

        db.remove()
        return "OK"

    @authorize(logged_in)
    def extension_add(self):
        schema = ExtensionForm()
        msg=""
        co = Company.query.filter(Company.id==session['company_id']).first()

        try:
            form_result = schema.to_python(request.params)
            e = PbxEndpoint()
            e.auth_id = form_result.get('extension')
            e.password = form_result.get('password')
            e.outbound_caller_id_name = form_result.get('outbound_caller_id_name')
            e.outbound_caller_id_number = form_result.get('outbound_caller_id_number')
            e.internal_caller_id_name = form_result.get('internal_caller_id_name')
            e.internal_caller_id_number = form_result.get('internal_caller_id_number')
            e.vm_email = form_result.get('vm_email')
            e.vm_password = form_result.get('vm_password')
            e.transfer_fallback_extension = form_result.get('transfer_fallback_extension')
            e.accountcode = co.tel
            e.follow_me_1 = form_result.get('follow_me_1')
            e.follow_me_2 = form_result.get('follow_me_2')
            e.follow_me_3 = form_result.get('follow_me_3')
            e.follow_me_4 = form_result.get('follow_me_4')
            e.call_timeout = form_result.get('call_timeout', 20)
            time_dest = form_result.get('timeout_destination')
            e.timeout_destination = time_dest if time_dest.isdigit() else None
            e.record_inbound_calls = form_result.get('record_inbound_calls', False)
            e.record_outbound_calls = form_result.get('record_outbound_calls', False)
            e.user_id = int(session['user_id'])
            e.user_context = session['context']
            e.force_transfer_context = session['context']
            e.user_originated = u'true'
            e.toll_allow = u'domestic'
            e.accountcode = co.tel

            if request.params.has_key('find_me'):
                e.find_me = True
            else:
                e.find_me = False

            if len(form_result.get('vm_email')) > 0:
                e.vw_attach_email = True

            db.add(e)
            db.commit()
            db.flush()

            r = PbxRoute()
            r.context = session['context']
            r.domain = session['context']
            r.name = form_result.get("extension")
            r.continue_route = True
            r.voicemail_enable = True
            r.voicemail_ext = form_result.get("extension")
            r.pbx_route_type_id = 1
            r.pbx_to_id = e.id

            db.add(r)
            db.commit()
            db.flush()

            con = PbxCondition()
            con.context = session['context']
            con.domain = session['context']
            con.field = u'destination_number'
            con.expression = u'^('+form_result.get("extension")+')$'
            con.pbx_route_id = r.id

            db.add(con)
            db.commit()
            db.flush()

            s = PbxAction()
            s.pbx_condition_id = con.id
            s.context = session['context']
            s.domain = session['context']
            s.precedence = 1
            s.application = u'set'
            s.data = u'hangup_after_bridge=true'

            db.add(s)
            db.commit()
            db.flush()

            s = PbxAction()
            s.pbx_condition_id = con.id
            s.context = session['context']
            s.domain = session['context']
            s.precedence = 1
            s.application = u'set'
            s.data = u'continue_on_fail=true'

            db.add(s)
            db.commit()
            db.flush()

            s = PbxAction()
            s.pbx_condition_id = con.id
            s.context = session['context']
            s.domain = session['context']
            s.precedence = 2
            s.application = u'set'
            s.data = u'call_timeout='+form_result.get('call_timeout', 20)

            db.add(s)
            db.commit()
            db.flush()

            s = PbxAction()
            s.pbx_condition_id = con.id
            s.context = session['context']
            s.domain = session['context']
            s.precedence = 3
            s.application = u'bridge'
            s.data = u'{force_transfer_context='+session['context']+'}sofia/'\
                     +str(get_profile())+'/'+form_result.get("extension")+'%'+session['context']

            db.add(s)
            db.commit()
            db.flush()

        except validators.Invalid, error:
            msg='Validation Error: %s' % error

        finally:
            if len(msg)>0:
                return msg
            else:
                return "Successfully added extension %s" % form_result.get('extension')
            db.remove()

    @authorize(logged_in)
    def call_stats(self):
        items=[]
        volume=[]
        ttime=[]
        minimumt = 0
        maximumt = 0
        minimumv = 0
        maximumv = 10
        for row in User.query.filter(User.company_id==session['company_id']).all():
            if not len(row.portal_extension):
                continue
            else:
                extension = row.portal_extension
            vol =  get_volume(extension)
            tt = get_talk_time(extension)
            if vol > maximumv:
                maximumv = vol
            if tt > maximumt:
                maximumt = tt
            volume.append({'x': row.first_name+' '+row.last_name, 'y': vol})
            ttime.append({'x': row.first_name+' '+row.last_name, 'y': tt})
            items.append({'id': row.id, 'extension': extension, 'name': row.first_name+' '+row.last_name, 'volume': vol, 'talk_time': tt})

        db.remove()

        out = dict({'identifier': 'id', 'label': 'name', 'items': items, 'mint': minimumt,
                    'maxt': maximumt, 'minv': minimumv, 'maxv': maximumv, 'volume': volume, 'talk_time': ttime})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def recordings(self):
        files = []
        dir = fs_vm_dir+session['context']+"/recordings/"

        try:
            for i in os.listdir(dir):
                files.append(generateFileObject(i, "",  dir))
        except:
            os.makedirs(dir)

        out = dict({'identifier': 'name', 'label': 'name', 'items': files})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def ivr_audio(self):
        items = []
        dir = fs_vm_dir+session['context']+"/recordings/"

        try:
            for i in os.listdir(dir):
                fo = generateFileObject(i, "",  dir)
                items.append({'id': '1,'+fo["name"], 'name': 'Recording: '+fo["name"] , 'data': fo["path"], 'type': 1, 'real_id': ""})
        except:
            os.makedirs(dir)

        for row in PbxTTS.query.filter_by(context=session['context']).all():
            items.append({'id': '2,'+str(row.id), 'name': 'TTS: '+row.name, 'data': row.text, 'type': 2, 'real_id': row.id})

        db.remove()
        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def voicemail_from_file_system(self):
        files = []

        dir = fs_vm_dir+session['context']+"/"+session['ext']

        try:
            for i in os.listdir(dir):
                if i.startswith("greeting_"):
                    continue
                id = i.split("_")[1].split(".")[0].strip()
                row = PbxCdr.query.filter(PbxCdr.uuid==id).first()
                path = dir+"/"+i
                tpath = "/vm/"+session['context']+"/"+session['ext']+"/"+i
                received = str(modification_date(path)).strip("\"")
                fsize = str(os.path.getsize(path))
                caller = row.caller_id_number[len(row.caller_id_number)-10:]
                files.append({'name': caller, 'path': tpath, 'received': received, 'size': fsize})
        except:
            os.makedirs(dir)

        out = dict({'identifier': 'path', 'label': 'name', 'items': files})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def voicemail(self):
        items=[]
        path = []
        i = 4
        if session['auth_level'] == 4:
            rows = VoiceMail.query.filter_by(domain=session['context']).filter(VoiceMail.username==session['ext']).all()
        else:
            rows = VoiceMail.query.filter_by(domain=session['context']).all()

        for row in rows:
            received = time.strftime("%a, %d %b %Y %H:%M", time.localtime(row.created_epoch))
            name = row.cid_number[len(row.cid_number)-10:]
            fname = row.file_path.split("/")[len(row.file_path.split("/"))-1]
            for x in range(1,5):
                path.append(row.file_path.split("/")[len(row.file_path.split("/"))-i])
                i=i-1
            fpath = "/"+"/".join(path)
            items.append({'name': name, 'received': received, 'path': fpath, 'size': row.message_len})

        db.remove()
        out = dict({'identifier': 'path', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @restrict("POST")
    @authorize(logged_in)
    def delete_voicemail(self, **kw):

        path = request.params['data']
        file_name = path.split("/")[len(path.split("/"))-1]
        uuid = file_name.split("_")[1].split(".")[0].strip()

        try:
            VoiceMail.query.filter(VoiceMail.uuid==uuid).filter(VoiceMail.username==session['ext']).delete()
            dir = fs_vm_dir+"/"+session['context']+"/"+session['ext']
            os.remove(os.path.join(dir, file_name))
        except:
            return "Error: OS Path problem."

        return "Deleted voicemail."

    @authorize(logged_in)
    def recording_name(self, **kw):
        files = []
        dir = fs_vm_dir+session['context']+"/recordings/"
        old_name = request.params['old_name']
        new_name = request.params['new_name']
        src = dir+old_name
        dst = dir+new_name

        if not new_name.endswith(".wav"):
            dst +=".wav"

        os.rename(src, dst)

        return "OK"

    """ Trash... unused. """
    @authorize(logged_in)
    def update_user_ext(self, **kw):
        id = request.params['id']
        username = request.params['username']
        extension = request.params['extension']

        a = PbxAccount.query.filter(PbxAccount.user_id==request.params["id"]).first()
        e = PbxEndpoint.query.filter(PbxEndpoint.auth_id==request.params['extension']).first()
        r = PbxRoute.query.filter(PbxRoute.name==request.params["extension"]).first()
        e.pbx_account_id = a.id
        r.pbx_account_id = a.id
        db.commit()
        db.flush()
        db.remove()
        return "OK"

    @authorize(logged_in)
    def update_ivr_grid(self, **kw):

        w = loads(urllib.unquote_plus(request.params.get("data")))

        for i in w['modified']:
            ivr = PbxIVR.query.filter_by(context=session['context']).filter(PbxIVR.id==int(i['id'])).first()
            ivr.name = i['name']

            route = PbxRoute.query.filter_by(context=session['context']). \
                filter(PbxRoute.pbx_route_type_id==5).filter(PbxRoute.pbx_to_id==int(i['id'])).first()
            route.name = i['name']

            db.commit()
            db.flush()
            db.remove()

        return "Successfully updated."

    @authorize(logged_in)
    def update_ext_grid(self, **kw):

        w = loads(urllib.unquote_plus(request.params.get("data")))

        for i in w['modified']:
            if i['name'].isdigit():
                id = i['name']
            else:
                id = i['id']
            u = User.query.filter(User.id==int(id)).filter_by(company_id=session['company_id']).first()
            e = PbxEndpoint.query.filter(PbxEndpoint.auth_id==i['extension']).filter_by(user_context=session['context']).first()
            e.user_id = u.id
            e.password = i['password']

            db.commit()
            db.flush()
            db.remove()

        return "Successfully updated."

    @authorize(logged_in)
    def update_users_grid(self, **kw):

        w = loads(urllib.unquote_plus(request.params.get("data")))

        for i in w['modified']:
            u = User.query.filter_by(company_id=session['company_id']).filter_by(id=i['id']).first()
            u.first_name = i['first_name']
            u.last_name = i['last_name']
            u.username = i['username']
            u.password = i['password']

            db.commit()
            db.flush()
            db.remove()

        return "Successfully updated."

    @authorize(logged_in)
    def get_find_me_edit(self, id, **kw):
        c.findme = db.query(PbxFindMeRoute.id,PbxFindMeRoute.ring_strategy, PbxFindMeRoute.destination_1, PbxFindMeRoute.destination_2 \
                                      , PbxFindMeRoute.destination_3, PbxFindMeRoute.destination_4, PbxEndpoint.auth_id) \
                .select_from(join(PbxFindMeRoute, PbxEndpoint, PbxEndpoint.pbx_find_me)) \
                .filter(PbxEndpoint.user_context==session['context']) \
                .filter_by(id=id).first()
        db.remove()
        return render('find_me_edit.html')

    @authorize(credential('pbx_admin'))
    def permissions(self, id, **kw):
        c.findme = db.query(PbxFindMeRoute.id,PbxFindMeRoute.ring_strategy, PbxFindMeRoute.destination_1, PbxFindMeRoute.destination_2\
            , PbxFindMeRoute.destination_3, PbxFindMeRoute.destination_4, PbxEndpoint.auth_id)\
        .select_from(join(PbxFindMeRoute, PbxEndpoint, PbxEndpoint.pbx_find_me))\
        .filter(PbxEndpoint.user_context==session['context'])\
        .filter_by(id=id).first()
        db.remove()
        return render('find_me_edit.html')


    @authorize(logged_in)
    def update_vext_grid(self, **kw):

        try:
            w = loads(urllib.unquote_plus(request.params.get("data")))

            for i in w['modified']:
                if not len(i['did']) == 10 or not str(i['did']).strip().isdigit():
                    return "A virtual extension needs to be exactly 10 digits."
                ve = PbxVirtualExtension.query.filter_by(id=i['id']).filter_by(context=session['context']).first()
                ve.did = i['did'].strip()
                db.commit()
                db.flush()
                db.remove()

        except DataInputError, error:
            db.remove()
            return 'Error: %s' % error

        return "Successfully updated."

    @authorize(logged_in)
    def update_tts_grid(self, **kw):

        try:
            w = loads(urllib.unquote_plus(request.params.get("data")))

            for i in w['modified']:
                t = PbxTTS.query.filter_by(id=i['id']).filter_by(context=session['context']).first()
                t.name = i['name'].strip()
                t.text = i['text'].strip()

                db.commit()
                db.flush()
                db.remove()

        except DataInputError, error:
            db.remove()
            return 'Error: %s' % error

        return "Successfully updated TTS entry."

    @authorize(logged_in)
    def update_vmbox_grid(self, **kw):

        try:
            w = loads(urllib.unquote_plus(request.params.get("data")))

            for i in w['modified']:
                if not str(i['extension']).strip().isdigit() or not str(i['pin']).strip().isdigit():
                    return "A virtual mailbox and pin needs to be exactly 3 or 4 numbers."
                vm = PbxVirtualMailbox.query.filter_by(id=i['id']).filter_by(context=session['context']).first()
                vm.pin = i['pin'].strip()
                db.commit()
                db.flush()
                db.remove()

        except DataInputError, error:
            db.remove()
            return 'Error: %s' % error

        return "Successfully updated."

    @authorize(logged_in)
    def update_group_grid(self, **kw):

        w = loads(urllib.unquote_plus(request.params.get("data")))

        try:
            for i in w['modified']:
                sg = PbxGroup.query.filter(PbxGroupMember.pbx_group_id==sg.id).delete()

                for gm in i['members'].split(","):
                    if not gm.strip().isdigit():
                        continue
                    sm = PbxGroupMember()
                    sm.pbx_group_id = sg.id
                    sm.extension = gm.strip()

                    db.add(sm)
                    db.commit()
                    db.flush()
                    db.remove()
        except:
            db.remove()
            return "Error updating group."

        return "Successfully updated."

    @authorize(logged_in)
    def update_did_grid(self, **kw):

        w = loads(urllib.unquote_plus(request.params.get("data")))

        try:
            for i in w['modified']:
                sd = PbxDid.query.filter_by(id=i['id']).filter_by(context=session['context']).first()
                sd.pbx_route_id = i['route_name']
                db.commit()
                db.flush()
                db.remove()
        except:
            db.remove()
            return "Error updating DID."

        return "Successfully updated DID."

    @restrict("POST")
    @authorize(logged_in)
    def add_user(self, **kw):
        schema = UserForm()
        try:
            form_result = schema.to_python(request.params)
            u = User()
            u.username = form_result.get("username")
            u.password = form_result.get("password")
            u.first_name = form_result.get("first_name")
            u.last_name = form_result.get("last_name")
            u.address = form_result.get("address")
            u.address_2 = form_result.get("address_2")
            u.city = form_result.get("city")
            u.state = form_result.get("state")
            u.zip = form_result.get("zip")
            u.tel = form_result.get("tel")
            u.mobile = form_result.get("mobile")
            u.active = form_result.get("active")
            u.company_id = session["company_id"]
            u.notes = form_result.get("notes")
            u.portal_extension = form_result.get("extension")

            db.add(u)
            db.commit()
            db.flush()

            context = PbxContext.query.filter(PbxContext.company_id==session['company_id']).first()

            em = EmailAccount()
            e = PbxEndpoint()
            r = PbxRoute()
            c = PbxCondition()
            s = PbxAction()

            if(session['has_crm']):
                if len(form_result.get("email"))>0 and len(form_result.get("email_password"))>0 and len(form_result.get("email_server"))>0:
                    em = EmailAccount()
                    em.user_id = u.id
                    em.company_id = session['company_id']
                    em.email = form_result.get("email")
                    em.password = form_result.get("email_password")
                    em.mail_server = form_result.get("email_server")
                    email = form_result.get("email", None)

                    db.add(em)
                    db.commit()
                    db.flush()
            else:
                email = ""

            if request.params.has_key('extension'):
                ext = form_result.get("extension").strip()
                if ext.isdigit():
                    if (len(get_extensions(ext))>0):
                        raise Exception("Extension already exists!")
                        ext_failed = True
                    else:
                        ext_failed = False
                else:
                    ext_failed = True
            else:
                ext_failed = True

            if not ext_failed:
                e = PbxEndpoint()
                e.auth_id = form_result.get("extension")
                e.password = form_result.get("extension_password")
                e.outbound_caller_id_name = context.origination_caller_id_name
                e.outbound_caller_id_number = context.origination_caller_id_number
                e.internal_caller_id_name = u.first_name + ' ' + u.last_name
                e.internal_caller_id_number = form_result.get("extension")
                e.user_context = context.context
                e.force_transfer_context = context.context
                e.user_originated = u'true'
                e.toll_allow = u'domestic'
                e.call_timeout = form_result.get("call_timeout", 20)
                e.accountcode = context.origination_caller_id_number
                e.pbx_force_contact =  form_result.get("pbx_force_contact", u'nat-connectile-dysfunction')
                e.vm_email = form_result.get("vm_email")
                e.vm_password = form_result.get("vm_password")
                e.vm_attach_email = True if form_result.get("vm_email", None) is not None else False
                e.vm_delete = False
                e.user_id = u.id

                db.add(e)
                db.commit()
                db.flush()

                r = PbxRoute()
                r.context = context.context
                r.domain = context.context
                r.name = form_result.get("extension")
                r.continue_route = True
                r.voicemail_enable = True
                r.voicemail_ext = form_result.get("extension")
                r.pbx_route_type_id = 1
                r.pbx_to_id = e.id

                db.add(r)
                db.commit()
                db.flush()

                con = PbxCondition()
                con.context = context.context
                con.domain = context.context
                con.field = u'destination_number'
                con.expression = u'^('+form_result.get("extension")+')$'
                con.pbx_route_id = r.id

                db.add(c)
                db.commit()
                db.flush()

                s = PbxAction()
                s.pbx_condition_id = con.id
                s.context = context.context
                s.domain = context.context
                s.precedence = 1
                s.application = u'set'
                s.data = u'hangup_after_bridge=true'

                db.add(s)
                db.commit()
                db.flush()

                s = PbxAction()
                s.pbx_condition_id = con.id
                s.context = context.context
                s.domain = context.context
                s.precedence = 2
                s.application = u'set'
                s.data = u'call_timeout=20'

                db.add(s)
                db.commit()
                db.flush()

                s = PbxAction()
                s.pbx_condition_id = con.id
                s.context = context.context
                s.domain = context.context
                s.precedence = 3
                s.application = u'bridge'
                s.data = u'{force_transfer_context='+context.context+'}sofia/'+str(get_profile())+'/'+form_result.get("extension")+'%'+context.context

                db.add(s)
                db.commit()
                db.flush()

        except validators.Invalid, error:
            db.remove()
            return 'Validation Error: %s' % error


        db.remove()
        return "Sucessfully added user."

    @restrict("POST")
    @authorize(logged_in)
    def edit_user(self, **kw):

        schema = UserEditForm()

        try:
            form_result = schema.to_python(request.params)
            u = User.query.filter(User.id==form_result.get("id")).filter(User.company_id==session['company_id']).first()
            u.password = form_result.get("password")
            u.first_name = form_result.get("first_name")
            u.last_name = form_result.get("last_name")
            u.address = form_result.get("address")
            u.address_2 = form_result.get("address_2")
            u.city = form_result.get("city")
            u.state = form_result.get("state")
            u.zip = form_result.get("zip")
            u.tel = form_result.get("tel")
            u.mobile = form_result.get("mobile")
            u.portal_extension = form_result.get('extension', 0)
            u.auth_level = form_result.get('auth_level', 0)
            u.active = True if form_result.get("active", None) is not None else False
            u.company_id = session["company_id"]
            u.notes = form_result.get("notes")

            db.commit()
            db.flush()
            db.remove()

        except validators.Invalid, error:
            return 'Error updating user. Please contact support.'

        return "User successfully updated."


    @restrict("GET")
    @authorize(logged_in)
    def del_user(self, **kw):

        u = User.query.filter(User.id==request.params['id']).filter(User.company_id==session['company_id']).first()
        delete_extension_by_user_id(u.id)

        try:
            id = request.params['id']
            if not id.isdigit():
                raise Exception("YOUR IP: "+str(request.params["HTTP_REMOTE_DUDE"])+" INFO WAS SENT TO THE ADMIN FOR BLOCKING.")
            User.query.filter(User.id==id).filter(User.company_id==session['company_id']).delete()
            db.commit()
            db.flush()
        except:
            db.remove()
            return "Error deleting user."

        db.remove()
        return  "Successfully deleted user."

    @restrict("GET")
    @authorize(logged_in)
    def del_ext(self, **kw):

        try:
            delete_extension_by_ext(request.params['extension'])
        except:
            return "Error deleting extension."

        return  "Successfully deleted extension."


    @restrict("GET")
    @authorize(logged_in)
    def del_vext(self, **kw):

        try:
            delete_virtual_extension(request.params['extension'])
        except:
            return "Error deleting virtual extension."

        return  "Successfully deleted virtual extension."


    @restrict("GET")
    @authorize(logged_in)
    def del_vmbox(self, **kw):

        try:
            delete_virtual_mailbox(request.params['extension'])
        except:
            return "Error deleting virtual mailbox."

        return  "Successfully deleted virtual mailbox."

    @restrict("GET")
    @authorize(logged_in)
    def del_group(self, **kw):

        try:
            delete_group(request.params['name'])
        except:
            return "Error"

        return  "Successfully deleted group."

    @restrict("GET")
    @authorize(logged_in)
    def del_tod(self, **kw):
        try:
            t = PbxTODRoute.query.filter(PbxTODRoute.id==request.params['id']).first()
            delete_tod(t.name)
        except:
            return "Error deleting Time of Day Route"

        return  "Successfully deleted Time of Day Route."

    @restrict("POST")
    @authorize(logged_in)
    def delete_recording(self, **kw):

        t = PbxIVR.query.filter(PbxIVR.data==request.params['name']).filter(PbxIVR.context==session['context']).first()

        if t:
            return "Error: Recording "+request.params['name']+" is in use by IVR named "+t.name+"!"

        try:
            dir = fs_vm_dir+session['context']+"/recordings/"+request.params['name']
            os.remove(dir)
        except:
            db.remove()
            return "Error deleting recording."
        db.remove()
        return "Deleted recording."

    @restrict("GET")
    @authorize(logged_in)
    def del_conf(self, **kw):

        try:
            delete_conf(request.params['extension'])
        except:
            return "Error deleting conference bridge."

        return  "Successfully deleted conference bridge."

    @restrict("GET")
    @authorize(logged_in)
    def del_cid(self, **kw):

        try:
            delete_cid(request.params['cid_number'])
        except:
            return "Error deleting CallerID Route."

        return  "Successfully deleted CallerID route."

    @restrict("GET")
    @authorize(logged_in)
    def del_bl(self, **kw):

        try:
            del_blacklist(request.params['cid_number'])
        except:
            return "Error deleting blacklisted number."

        return  "Successfully deleted blacklisted number."

    @restrict("GET")
    @authorize(logged_in)
    def del_tts(self, **kw):
        return  delete_tts(request.params['name'])

    @restrict("GET")
    @authorize(logged_in)
    def del_ivr(self, **kw):
        return  delete_ivr(request.params['name'])


    @restrict("POST")
    @authorize(logged_in)
    def ext_edit(self, **kw):
        schema = ExtEditForm()
        msg=""
        try:
            form_result = schema.to_python(request.params)
            e = PbxEndpoint.query.filter(PbxEndpoint.id==form_result.get('extension_id')).filter(PbxEndpoint.user_context==session['context']).first()
            e.password = form_result.get('password')
            e.outbound_caller_id_name = form_result.get('outbound_caller_id_name')
            e.outbound_caller_id_number = form_result.get('outbound_caller_id_number')
            e.internal_caller_id_name = form_result.get('internal_caller_id_name')
            e.internal_caller_id_number = form_result.get('outbound_caller_id_number')
            e.vm_email = form_result.get('vm_email')
            e.vm_password = form_result.get('vm_password')
            e.transfer_fallback_extension = form_result.get('transfer_fallback_extension')
            e.follow_me_1 = form_result.get('follow_me_1')
            e.follow_me_2 = form_result.get('follow_me_2')
            e.follow_me_3 = form_result.get('follow_me_3')
            e.follow_me_4 = form_result.get('follow_me_4')
            e.call_timeout = form_result.get('call_timeout')
            time_dest = form_result.get('timeout_destination')
            e.timeout_destination = time_dest if time_dest.isdigit() else None
            e.record_inbound_calls = form_result.get('record_inbound_calls', False)
            e.record_outbound_calls = form_result.get('record_outbound_calls', False)

            if request.params.has_key('find_me'):
                e.find_me = True
            else:
                e.find_me = False

            if len(form_result.get('vm_email')) > 0:
                e.vw_attach_email = True

            db.add(e)
            db.commit()
            db.flush()

            r = PbxRoute.query.filter(PbxRoute.pbx_route_type_id==1). \
                filter(PbxRoute.name==e.auth_id).filter(PbxRoute.context==session['context']).first()

            delete_conditions(r.id)

            con = PbxCondition()
            con.context = session['context']
            con.domain = session['context']
            con.field = u'destination_number'
            con.expression = u'^('+e.auth_id+')$'
            con.pbx_route_id = r.id

            db.add(con)
            db.commit()
            db.flush()

            s = PbxAction()
            s.pbx_condition_id = con.id
            s.context = session['context']
            s.domain = session['context']
            s.precedence = 1
            s.application = u'set'
            s.data = u'hangup_after_bridge=true'

            db.add(s)
            db.commit()
            db.flush()

            s = PbxAction()
            s.pbx_condition_id = con.id
            s.context = session['context']
            s.domain = session['context']
            s.precedence = 1
            s.application = u'set'
            s.data = u'continue_on_fail=true'

            db.add(s)
            db.commit()
            db.flush()

            s = PbxAction()
            s.pbx_condition_id = con.id
            s.context = session['context']
            s.domain = session['context']
            s.precedence = 2
            s.application = u'set'
            s.data = u'call_timeout=20'

            db.add(s)
            db.commit()
            db.flush()

            s = PbxAction()
            s.pbx_condition_id = con.id
            s.context = session['context']
            s.domain = session['context']
            s.precedence = 3
            s.application = u'bridge'
            s.data = u'{force_transfer_context='+session['context']+'}sofia/'+str(get_profile())+'/'+e.auth_id+'%'+session['context']

            db.add(s)
            db.commit()
            db.flush()

            db.remove()

        except validators.Invalid, error:
            msg='Validation Error: %s' % error

        finally:
            if len(msg)>0:
                return msg
            else:
                return "Successfully edited extension %s" % e.auth_id
            db.remove()

    def debug(self, **kw):
        result = []
        environ = request.environ
        keys = environ.keys()
        keys.sort()
        for key in keys:
            result.append("%s: %r"%(key, environ[key]))
        return '<pre>' + '\n'.join(result) + '</pre>'

    @authorize(logged_in)
    def upload_recording(self):

        myfile = request.params['uploadedfiles[]']

        if not myfile.filename.endswith(".wav"):
            return "Error uploading file. File must have .wav extension."

        try:
            dir = fs_vm_dir + "/"+session['context']+"/recordings/"
            permanent_file = open(os.path.join(dir,myfile.filename.lstrip(os.sep)), 'w')
            shutil.copyfileobj(myfile.file, permanent_file)
            myfile.file.close()
            permanent_file.close()
        except:
            return "Error uploading file. The administrator has been contacted."

        return "Successfully uploaded recording."

    @authorize(logged_in)
    def login_ext(self, id):
        items=[]
        for row in PbxEndpoint.query.filter_by(user_context=session['context']). \
                filter_by(user_id=id).order_by(PbxEndpoint.auth_id).all():
            items.append({'id': row.id, 'extension': row.auth_id})
        db.remove()

        out = dict({'identifier': 'extension', 'label': 'extension', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def company_by_id(self, **kw):
        items=[]
        row = Company.query.filter(Company.id==session['company_id']).first()
        items.append({'id': row.id, 'name': row.name, 'email': row.email, 'address': row.address, 'address_2': row.address_2,
                          'city': row.city, 'state': row.state, 'zip': row.zip,
                          'tel': row.tel, 'url': row.url, 'active': row.active, 'context': row.context, 'has_crm': row.has_crm,
                          'has_call_center': row.has_call_center, 'max_extensions': row.max_extensions, 'max_minutes': row.max_minutes,
                          'contact_name': row.contact_name, 'contact_phone': row.contact_phone, 'contact_mobile': row.contact_mobile,
                          'contact_title': row.contact_title, 'contact_email': row.contact_email, 'max_queues': row.max_queues,
                          'max_agents': row.max_agents,'notes': row.notes})

        out = dict({'identifier': 'id', 'label': 'name', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def edit_company(self):
        schema = CompanyForm()
        try:
            form_result = schema.to_python(request.params)
            co = Company.query.filter(Company.id==session['company_id']).first()
            co.tel = form_result.get('tel')
            co.address = form_result.get('address')
            co.address_2 = form_result.get('address_2')
            co.city = form_result.get('city')
            co.state = form_result.get('state')
            co.zip = form_result.get('zip')
            co.url = form_result.get('url')
            co.email = form_result.get('email')
            co.contact_name = form_result.get('contact_name')
            co.contact_phone = form_result.get('contact_phone')
            co.contact_mobile = form_result.get('contact_mobile')
            co.contact_title = form_result.get('contact_title')
            co.contact_email = form_result.get('contact_email')

            db.commit()
            db.flush()

        except validators.Invalid, error:
            db.remove()
            return 'Error: %s' % error

        return "Successfully edited company."

    @authorize(logged_in)
    def faxes(self):
        files = []
        dir = fs_vm_dir+session['context']+"/faxes"

        try:
            for i in os.listdir(dir):
                if not i.endswith(".png"):
                    continue
                path = dir+"/"+i
                uuid = i.split("_")[0].strip()
                name = i.split("_")[1].strip().split(".")[0]
                if name.find("-") == -1:
                    page_num = "Single Page"
                else:
                    page_num = name.split("-")[1].split(".")[0].strip()
                    name = name.split("-")[0].strip()
                    page_num = int(page_num)+1

                tpath = "/vm/" +session['context']+"/faxes/"+i
                received = str(modification_date(path)).strip("\"")
                fsize = str(os.path.getsize(path))
                row = PbxCdr.query.filter(PbxCdr.uuid==uuid).first()
                if row:
                    caller = row.caller_id_number[len(row.caller_id_number)-10:]
                else:
                    caller = "Unknown"
                files.append({'uuid': uuid, 'name': name, 'caller_id': caller, 'path': tpath, 'received': received, 'size': fsize, 'page_num': page_num})
        except:
            os.makedirs(dir)

        db.remove()
        out = dict({'identifier': 'path', 'label': 'name', 'items': files})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def fax_add(self, **kw):
        schema = FaxForm()
        try:
            form_result = schema.to_python(request.params)
            sf = PbxFax()
            sf.extension = form_result.get('fax_name')
            sf.context = session['context']

            db.add(sf)
            db.commit()
            db.flush()

            r = PbxRoute()
            r.context = session['context']
            r.domain = session['context']
            r.name = form_result.get('fax_name')
            r.continue_route = False
            r.voicemail_enable = False
            r.voicemail_ext = form_result.get('fax_name')
            r.pbx_route_type_id = 12
            r.pbx_to_id = sf.id

            db.add(r)
            db.commit()
            db.flush()

        except validators.Invalid, error:
            db.remove()
            return 'Validation Error: Please correct form inputs and resubmit.'

    @authorize(logged_in)
    def fax_ext(self):
        items=[]
        for ext in PbxFax.query.filter_by(context=session['context']).all():
            items.append({'id': ext.id, 'extension': ext.extension})

        db.remove()

        out = dict({'identifier': 'id', 'label': 'extension', 'items': items})
        response = make_response(out)
        response.headers = [("Content-type", 'application/json; charset=UTF-8'),]

        return response(request.environ, self.start_response)

    @authorize(logged_in)
    def fax_send(self, **kw):
        form = cgi.FieldStorage()

        user = User.query.filter_by(session_id=session.id).first()
        if not user:
            return

        ep = db.execute("SELECT pbx_dids.did FROM pbx_dids "
                                  "INNER JOIN pbx_routes on pbx_dids.pbx_route_id = pbx_routes.id "
                                  "WHERE pbx_routes.pbx_route_type_id=12").fetchone()

        if ep:
            if len(ep[0])==10:
                origination_caller_id_number = ep[0]
            else:
                origination_caller_id_number = ep[1]
        else:
            origination_caller_id_number = "0000000000"

        myfile = request.params['uploadedfiles[]']

        fname = myfile.filename.lstrip(os.sep)
        ext = fname.split(".")[len(fname.split("."))-1]
        if not ext:
            return  "Error no file type found."
        fname = re.sub('[^A-Za-z0-9]+', '', fname)
        fname = fname+"."+ext

        try:
            dir = "/tmp/"
            permanent_file = open(os.path.join(dir,fname), 'w')
            shutil.copyfileobj(myfile.file, permanent_file)
            myfile.file.close()
            permanent_file.close()
        except:
            return "Error uploading file. The administrator has been contacted."

        converted = fname.split(".")[0]+".tiff"
        call("convert -density 204x98 -units PixelsPerInch -resize 1728x1186\! -monochrome -compress Fax /tmp/"+fname+" /tmp/"+converted, shell=True)
        os.remove("/tmp/"+fname)

        con = ESLconnection(ESL_HOST, ESL_PORT, ESL_PASS)
        if con.connected:
            con.bgapi("originate", "{fax_ident='PythonPBX Web Fax',fax_header="+str(origination_caller_id_number)+",fax_enable_t38=true,origination_caller_id_number="+str(origination_caller_id_number)+"}sofia/gateway/voipinnovations/"+str(request.params["fax_recipient"])+" &txfax(/tmp/"+str(converted)+")")

    @restrict("GET")
    @authorize(logged_in)
    def del_fax(self, **kw):
        """For security, we check the input, then put them into their own context"""

        file_name = request.params['name'].split("/")[len(request.params['name'].split("/"))-1]

        try:
            dir = fs_vm_dir+session['context']+"/faxes/"+file_name
            os.remove(dir)
        except:
            return "Error deleting fax."
        return "Deleted fax."

    @authorize(logged_in)
    def del_fax_ext(self, **kw):

        try:
            delete_fax_ext(request.params['name'])
        except:
            return "Error deleting fax extension."

        return  "Successfully deleted fax extension."
    
    
    
        