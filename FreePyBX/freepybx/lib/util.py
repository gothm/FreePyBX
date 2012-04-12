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


import shutil, os, sys
from datetime import datetime
from pylons import request, response, session, config, tmpl_context as c, url
import time
from freepybx.model import meta
from freepybx.lib.validators import *
import formencode
from formencode import validators
from pylons.decorators import validate
from simplejson import loads, dumps
from webob import Request, Response
import simplejson as json
from itertools import chain
from freepybx.model import *
from freepybx.model.meta import Session as db
import inspect
import mimetypes


path_dir = config['app_conf']['fs_vm_dir']
smtp_server = config['smtp_server']

__all__=['escapeSpecialCharacters','has_queue','has_agent','has_tier',
         'has_agent_tier','get_agent','get_tier','get_queue','get_agent_status',
         'queue_delete','tier_delete','get_context','get_queue_directory',
         'get_campaigns','get_route_labels_ids','make_response','get_profile',
         'dir_modification_date','get_children','modification_date','convert',
         'partition_number','format_bytes','format_suffix','generateFileObject',
         'fix_date','get_default_gateway','get_type','get_talk_time','get_volume',
         'delete_extension_by_user_id','delete_extension_by_ext', 'check_for_remaining_admin',
         'delete_virtual_extension','delete_virtual_mailbox','delete_group',
         'delete_fax_ext','delete_ivr','delete_cid','delete_tts','del_blacklist',
         'delete_conf','delete_tod','delete_conditions','get_findme','is_iter_obj',
         'PbxError', 'DataInputError','PbxEncoder', 'get_presence_hosts', 'has_method',
         'get_mimetype','make_file_response']


def get_mimetype(path):
    type, encoding = mimetypes.guess_type(path)
    return type or 'application/octet-stream'

def make_file_response(path):
    res = Response(content_type=get_mimetype(path))
    res.body = open(path, 'rb').read()
    return res

def escapeSpecialCharacters (text, characters):
    for character in characters:
        text = text.replace(character, '\\' + character)
    return text

def get_presence_hosts():
    import socket
    hosts=[]
    hosts.append(socket.gethostname())
    hosts.append(socket.gethostbyname(socket.gethostname()))
    return ','.join(hosts)

def has_method(obj, name):
    v = vars(obj.__class__)
    return name in v and inspect.isroutine(v[name])

def pack_ip(ip_dot_str):
    if not ip_dot_str:
        return None
    return struct.unpack('!L', inet_aton(str(ip_dot_str)))[0]

def unpack_ip(ip_int):
    if not ip_int:
        return None
    return socket.inet_ntoa(struct.pack('!L', long(ip_int)))

def has_queue(name):
    return True if CallCenterQueue.query.filter(CallCenterQueue.name==name).filter(CallCenterQueue.context==session['context']).count()>0 else False

def has_agent(extension):
    return True if CallCenterAgent.query.filter(CallCenterAgent.extension==extension).filter(CallCenterAgent.context==session['context']).count()>0 else False

def has_tier(name):
    return True if CallCenterTier.query.join(CallCenterQueue).filter(CallCenterTier.name==name).filter(CallCenterQueue.context==session['context']).count()>0 else False

def has_agent_tier(name, agent):
    return True if CallCenterTier.query.join(CallCenterQueue).join(CallCenterAgent).\
                   filter(CallCenterTier.name==name).filter(CallCenterAgent.extension==agent).filter(CallCenterQueue.context==session['context']).count()>0 else False

def get_agent(id):
    return CallCenterAgent.query.filter(CallCenterAgent.id==id).filter(CallCenterAgent.context==session['context']).first()

def get_tier(id):
    return CallCenterTier.query.filter(CallCenterTier.id==id).filter(CallCenterTier.context==session['context']).first()

def get_queue(id):
    return CallCenterQueue.query.filter(CallCenterQueue.id==id).first()

def get_agent_status(id):
    agent = CallCenterAgent.query.filter(CallCenterAgent.id==id).filter(CallCenterAgent.context==session['context']).first()
    return FSCallCenterAgent.status.query.filter(FSCallCenterAgent.name==str(agent.extension)+"@"+session['context']).first()

def queue_delete(q):
    for queue in CallCenterQueue.query.filter(CallCenterQueue.id==q.id).filter(CallCenterQueue.context==session['context']).all():
        PbxRoute.query.filter(PbxRoute.pbx_route_type_id==10).filter(PbxRoute.pbx_to_id==queue.id).delete()
        CallCenterTier.query.filter(CallCenterTier.queue_id==queue.id).delete()
    CallCenterQueue.query.filter(CallCenterQueue.id==q.id).filter(CallCenterQueue.context==session['context']).delete()
    db.commit()
    db.flush()
    return True

def tier_delete(q):
    for queue in CallCenterQueue.query.filter(CallCenterQueue.id==q.id).filter(CallCenterQueue.context==session['context']).all():
        CallCenterTier.query.filter(CallCenterTier.queue_id==queue.id).delete()
    return True

def get_context(self):
    context = PbxContext.query.filter(PbxContext.customer_id==session['customer_id']).first()
    db.remove()
    return context.context

def check_for_remaining_admin(customer_id):
    return len(Customer.query.filter(Customer.id==customer_id).all())

def get_queue_directory():
    dirs = []

    dir = path_dir+session['context']+"/queue-recordings/"
    for i in os.listdir(dir):
        dirs.append(i)

    return dirs

def get_campaigns():
    return db.execute("SELECT crm_campaigns.name FROM crm_campaigns "
                      "INNER JOIN crm_campaign_groups ON crm_campaigns.id = crm_campaign_groups.crm_campaign_id "
                      "INNER JOIN crm_group_members ON crm_group_members.crm_group_id  = crm_campaign_groups.id "
                      "WHERE crm_group_members.extension = :ext", {'ext': session['ext']}).fetchall()

def get_route_labels_ids():
    route_labels = []
    route_ids = []

    for row in db.execute("SELECT sr.id, srt.name|| ':' ||sr.name AS name "
                          "FROM pbx_routes sr "
                          "INNER JOIN pbx_route_types srt ON sr.pbx_route_type_id = srt.id "
                          "WHERE sr.context = :context", {'context': session['context']}):
        route_labels.append(row.name)
        route_ids.append(row.id)
    db.remove()
    return (route_labels,route_ids)

def make_response(obj, _content_type='application/json'):
    res = Response(content_type=_content_type)
    if _content_type=="application/json":
        res.body = dumps(obj)
    else:
        res.body = obj
    return res

def get_profile():
    ''' TODO: multiple profiles. unnecessary for now.'''
    p = PbxProfile.query.first()
    return p.name

def dir_modification_date(filename):
    t = os.path.getmtime(filename)
    return json.dumps(datetime.datetime.utcfromtimestamp(t), cls=PbxEncoder)

def get_children(top):
    children = []
    for f in os.listdir(top):
        children.append(f)
    children.sort()
    return children

def modification_date(filename):
    return time.strftime("%m/%d/%Y %I:%M:%S %p", time.localtime(os.path.getmtime(filename)))

def convert(number):
    if not number:
        return '0 Bytes'
    assert 0 < number < 1 << 110, 'number out of range'
    ordered = reversed(tuple(format_bytes(partition_number(number, 1 << 10))))
    cleaned = ', '.join(item for item in ordered if item[0] != '0')
    return cleaned

def partition_number(number, base):
    div, mod = divmod(number, base)
    yield mod
    while div:
        div, mod = divmod(div, base)
        yield mod

def format_bytes(parts):
    for power, number in enumerate(parts):
        yield '{0}'.format(number)

def format_suffix(power, number):
    PREFIX = ' k m g tera peta exa zetta yotta bronto geop'.split(' ')
    return (PREFIX[power] + 'byte').capitalize() + ('s' if number != 1 else '')

def generateFileObject(filename, dir, rootDir, expand=False, showHiddenFiles=False):
    path = dir+"/"+filename
    fullPath = rootDir+"/"+path

    fObj = {}
    fObj["name"] = filename
    fObj["parentDir"] = dir
    fObj["path"] = path
    fObj["directory"] = os.path.isdir(fullPath)
    fObj["size"] = os.path.getsize(fullPath)
    fObj["modified"] = str(modification_date(fullPath)).strip("\"")
    fObj["tpath"] = "/vm/"+session['context']+"/recordings/"+filename

    children = []
    if os.path.isdir(fullPath):
        for o in os.listdir(fullPath):
            if os.path.isdir(os.path.join(fullPath, o)):
                fullpath =  os.path.join(fullPath, o)
                path_arr = fullpath.split("/")
                pts = path_arr[:-1]
                dir = '/'.join(pts[5:])
                children.append(generateFileObject(o, dir, rootDir))
            else:
                children.append(o)
    fObj["children"] = children
    return fObj

def fix_date(t):
    if not t:
        return ""
    return t.strftime("%m/%d/%Y %I:%M:%S %p")

def get_default_gateway():
    co = Customer.query.filter_by(id=session['customer_id']).first()
    return co.default_gateway

def get_type(id):
    t = PbxRouteType.query.filter_by(id=id).first()
    return t.name

def get_talk_time(ext):
    rows =  db.execute("select coalesce(sum(billsec)/60,0) as mins from cdr where (caller_id_number=:ext or destination_number=:ext) "
                       "and start_stamp between CURRENT_DATE and CURRENT_TIMESTAMP and bleg_uuid is not null and context = :context",{'ext':ext, 'context': session['context']})
    r = rows.fetchone()
    return r.mins

def get_volume(ext):
    rows =  db.execute("select count(*) as ct "
                       "from cdr where  (caller_id_number=:ext or destination_number=:ext) "
                       "and start_stamp between CURRENT_DATE "
                       "and CURRENT_TIMESTAMP and bleg_uuid is not null and context = :context",{'ext':ext, 'context': session['context']})
    r = rows.fetchone()
    return r.ct

def delete_extension_by_user_id(user_id):
    for ext in PbxEndpoint.query.filter(PbxEndpoint.user_id==user_id).filter(PbxEndpoint.user_context==session['context']).all():
        for route in PbxRoute.query.filter(PbxRoute.pbx_route_type_id==1).\
        filter(PbxRoute.name==ext.auth_id).filter(PbxRoute.context==session['context']).all():
            for condition in PbxCondition.query.filter_by(pbx_route_id=route.id).all():
                PbxAction.query.filter_by(pbx_condition_id=condition.id).delete()
                PbxCondition.query.filter_by(pbx_route_id=route.id).delete()
            PbxRoute.query.filter(PbxRoute.pbx_route_type_id==1).\
            filter(PbxRoute.name==ext.auth_id).filter(PbxRoute.context==session['context']).delete()
        for sg in PbxGroup.query.filter_by(context=session['context']).all():
            PbxGroupMember.query.filter_by(pbx_group_id=sg.id).filter_by(extension=ext.auth_id).delete()
        PbxEndpoint.query.filter(PbxEndpoint.user_id==user_id).filter(PbxEndpoint.user_context==session['context']).delete()
        db.commit()
        db.flush()
        db.remove()
    return True

def delete_extension_by_ext(extension):
    for ext in PbxEndpoint.query.filter(PbxEndpoint.auth_id==extension).filter(PbxEndpoint.user_context==session['context']).all():
        for route in PbxRoute.query.filter(PbxRoute.pbx_route_type_id==1).\
        filter(PbxRoute.name==ext.auth_id).filter(PbxRoute.context==session['context']).all():
            for condition in PbxCondition.query.filter_by(pbx_route_id=route.id).all():
                PbxAction.query.filter_by(pbx_condition_id=condition.id).delete()
                PbxCondition.query.filter_by(pbx_route_id=route.id).delete()
            PbxRoute.query.filter(PbxRoute.pbx_route_type_id==1).\
            filter(PbxRoute.name==ext.auth_id).filter(PbxRoute.context==session['context']).delete()
        for sg in PbxGroup.query.filter_by(context=session['context']).all():
            PbxGroupMember.query.filter_by(pbx_group_id=sg.id).filter_by(extension=ext.auth_id).delete()
        PbxEndpoint.query.filter(PbxEndpoint.auth_id==extension).filter(PbxEndpoint.user_context==session['context']).delete()
        db.commit()
        db.flush()
        db.remove()
    return True

def delete_virtual_extension(extension):
    for ext in PbxVirtualExtension.query.filter(PbxVirtualExtension.extension==extension).filter(PbxVirtualExtension.context==session['context']).all():
        for route in PbxRoute.query.filter(PbxRoute.pbx_route_type_id==2).\
        filter(PbxRoute.name==ext.extension).filter(PbxRoute.context==session['context']).all():
            for condition in PbxCondition.query.filter_by(pbx_route_id=route.id).all():
                PbxAction.query.filter_by(pbx_condition_id=condition.id).delete()
                PbxCondition.query.filter_by(pbx_route_id=route.id).delete()
            PbxRoute.query.filter(PbxRoute.pbx_route_type_id==2).\
            filter(PbxRoute.name==ext.extension).filter(PbxRoute.context==session['context']).delete()
        for sg in PbxGroup.query.filter_by(context=session['context']).all():
            PbxGroupMember.query.filter_by(pbx_group_id=sg.id).filter_by(extension=extension).delete()
        PbxVirtualExtension.query.filter(PbxVirtualExtension.extension==extension).filter(PbxVirtualExtension.context==session['context']).delete()
        db.commit()
        db.flush()
        db.remove()
    return True

def delete_virtual_mailbox(extension):
    for ext in PbxVirtualMailbox.query.filter(PbxVirtualMailbox.extension==extension)\
    .filter(PbxVirtualMailbox.context==session['context']).all():
        for route in PbxRoute.query.filter(PbxRoute.pbx_route_type_id==3).\
        filter(PbxRoute.name==ext.extension).filter(PbxRoute.context==session['context']).all():
            for condition in PbxCondition.query.filter_by(pbx_route_id=route.id).all():
                PbxAction.query.filter_by(pbx_condition_id=condition.id).delete()
                PbxCondition.query.filter_by(pbx_route_id=route.id).delete()
            PbxRoute.query.filter(PbxRoute.pbx_route_type_id==3).\
            filter(PbxRoute.name==ext.extension).filter(PbxRoute.context==session['context']).delete()
        for sg in PbxGroup.query.filter_by(context=session['context']).all():
            PbxGroupMember.query.filter_by(pbx_group_id=sg.id).filter_by(extension=extension).delete()
        PbxVirtualMailbox.query.filter(PbxVirtualMailbox.extension==extension).filter(PbxVirtualMailbox.context==session['context']).delete()
        db.commit()
        db.flush()
        db.remove()
    return True

def delete_group(name):
    for group in PbxGroup.query.filter(PbxGroup.name==name).filter(PbxGroup.context==session['context']).all():
        for route in PbxRoute.query.filter(PbxRoute.pbx_route_type_id==4).\
        filter(PbxRoute.name==group.name).filter(PbxRoute.context==session['context']).all():
            PbxRoute.query.filter(PbxRoute.pbx_route_type_id==4).\
            filter(PbxRoute.name==group.name).filter(PbxRoute.context==session['context']).delete()
        PbxGroup.query.filter(PbxGroup.name==name).filter(PbxGroup.context==session['context']).delete()
        db.commit()
        db.flush()
        db.remove()
    return True

def delete_fax_ext(extension):
    for ext in PbxFax.query.filter(PbxFax.extension==extension).filter(PbxFax.context==session['context']).all():
        for route in PbxRoute.query.filter(PbxRoute.pbx_route_type_id==12).\
        filter(PbxRoute.name==ext.extension).filter(PbxRoute.context==session['context']).all():
            PbxRoute.query.filter(PbxRoute.pbx_route_type_id==12).\
            filter(PbxRoute.name==ext.extension).filter(PbxRoute.context==session['context']).delete()
        PbxFax.query.filter(PbxFax.extension==extension).filter(PbxFax.context==session['context']).delete()
        db.commit()
        db.flush()
        db.remove()
    return True

def delete_ivr(name):
    for ivr in PbxIVR.query.filter_by(name=name).filter_by(context=session['context']).all():

        r = PbxRoute.query.filter(PbxRoute.pbx_route_type_id==5).\
        filter(PbxRoute.name==ivr.name).filter(PbxRoute.context==session['context']).first()
        did = PbxDid.did.query.filter(PbxDid.pbx_route_id==r.id).first()

        if did:
            msg = "Error: IVR is in use by Inbound DID: "+str(did.did)+"!"

        tod = db.execute("select * from pbx_tod_routes where match_route_id = :id or nomatch_route_id = :id", {'id': r.id}).first()

        if tod:
            msg = "Error: IVR is in a TOD route!"

        ivr_opt = PbxIVROption.query.filter(PbxIVROption.pbx_route_id==r.id).first()

        if ivr_opt:
            msg = "Error: IVR belongs to another IVR Option."


        if not did and not ivr_opt and not tod:
            PbxRoute.query.filter(PbxRoute.pbx_route_type_id==5).\
            filter(PbxRoute.name==ivr.name).filter(PbxRoute.context==session['context']).delete()
            PbxIVROption.query.filter(PbxIVROption.pbx_ivr_id==ivr.id).delete()
            PbxIVR.query.filter(PbxIVR.name==name).filter(PbxIVR.context==session['context']).delete()
            db.commit()
            db.flush()
            db.remove()
        else:
            return msg

        db.remove()
        return "Successfully deleted IVR: "+name+"."


def delete_cid(cid_number):
    PbxCallerIDRoute.query.filter(PbxCallerIDRoute.cid_number==cid_number)\
    .filter(PbxCallerIDRoute.context==session['context']).delete()
    db.commit()
    db.flush()
    db.remove()
    return True

def delete_tts(name):
    tts = PbxTTS.query.filter(PbxTTS.name==name)\
    .filter(PbxTTS.context==session['context']).first()
    ivr = PbxIVR.query.filter(PbxIVR.audio_type==2)\
    .filter(PbxIVR.data==str(tts.id)).first()
    db.commit()
    db.flush()
    db.remove()
    if ivr:
        return "Error: That TTS is in use by the IVR named "+ivr.name+"!"
    else:
        PbxTTS.query.filter(PbxTTS.name==name)\
        .filter(PbxTTS.context==session['context']).delete()
        db.commit()
        db.flush()
        db.remove()
    return "Successfully deleted TTS."

def del_blacklist(cid_number):
    PbxBlacklistedNumber.query.filter(PbxBlacklistedNumber.cid_number==cid_number)\
    .filter(PbxBlacklistedNumber.context==session['context']).delete()
    db.commit()
    db.flush()
    db.remove()
    return True


def delete_conf(extension):
    PbxRoute.query.filter(PbxRoute.pbx_route_type_id==7)\
    .filter(PbxRoute.name==extension).filter(PbxRoute.context==session['context']).delete()
    PbxConferenceBridge.query.filter(PbxConferenceBridge.extension==extension).delete()
    db.commit()
    db.flush()
    db.remove()
    return True

def delete_tod(name):
    for tod in PbxTODRoute.query.filter(PbxTODRoute.name==name)\
    .filter(PbxTODRoute.context==session['context']).all():
        for route in PbxRoute.query.filter(PbxRoute.pbx_route_type_id==6)\
        .filter(PbxRoute.name==tod.name).filter(PbxRoute.context==session['context']).all():
            PbxRoute.query.filter(PbxRoute.pbx_route_type_id==6).\
            filter(PbxRoute.name==tod.name).filter(PbxRoute.context==session['context']).delete()
        PbxTODRoute.query.filter(PbxTODRoute.name==name)\
        .filter(PbxTODRoute.context==session['context']).delete()
        db.commit()
        db.flush()
        db.remove()
    return True

def delete_conditions(route_id):
    for route in PbxRoute.query.filter(PbxRoute.pbx_route_type_id==1).\
    filter(PbxRoute.id==route_id).filter(PbxRoute.context==session['context']).all():
        for condition in PbxCondition.query.filter_by(pbx_route_id=route.id).all():
            PbxAction.query.filter_by(pbx_condition_id=condition.id).delete()
            PbxCondition.query.filter_by(pbx_route_id=route.id).delete()
    db.commit()
    db.flush()
    db.remove()

def get_findme(name, context):
    e = PbxEndpoint.query.filter_by(user_context=context).filter_by(auth_id=name).first()
    ds = None
    if e.find_me:
        ds = u"sofia/gateway/"+str(get_default_gateway())+"/{0}".format(e.follow_me_1)
        if len(e.follow_me_2) == 10:
            ds+= u",sofia/gateway/"+str(get_default_gateway())+"/{0}".format(e.follow_me_2)
        if len(e.follow_me_3) == 10:
            ds+= u",sofia/gateway/"+str(get_default_gateway())+"/{0}".format(e.follow_me_3)
        if len(e.follow_me_4) == 10:
            ds+= u",sofia/gateway/"+str(get_default_gateway())+"/{0}".format(e.follow_me_4)
    return ds

def is_iter_obj(obj):
    itr = iter(obj)
    try:
        item = itr.next()
    except:
        return None
    return chain((item,), itr)


class PbxError(Exception):
    message=""

    def __init__(self, message=None):
        Exception.__init__(self, message or self.message)


class DataInputError(Exception):
    message=""

    def __init__(self, message=None):
        Exception.__init__(self, message or self.message)


class PbxEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, datetime.date)):
            return obj.ctime()
        elif isinstance(obj, datetime.time):
            return obj.isoformat()
        elif isinstance(obj, ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


class PbxSMTP():
    def __init__(self, _to_email, _from_email, _subject=None, _msg_body=None, _msg_attachments=[]):
        self.to_email = _to_email
        self.from_email = _from_email
        self.subject = _subject
        self.msg_body = _msg_body
        self.msg_attachments = _msg_attachments


    def send_message(self):
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        html_parser = HTMLParser.HTMLParser()
        body_plain = html_parser.unescape(self.msg_body)
        body_html = self.msg_body

        msg['Subject'] = self.subject
        msg['From'] = self.from_email
        msg['To'] = self.to_email

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(body_plain, 'plain')
        #        part2 = MIMEText(body_html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        #        msg.attach(part2)

        # Send the message via local SMTP server.
        s = smtplib.SMTP('108.60.221.2')
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        s.sendmail(msg['From'], msg['To'], msg.as_string())
        s.quit()