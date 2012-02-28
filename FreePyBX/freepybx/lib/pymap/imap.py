"""
    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.

    Software distributed under the License is distributed on an "AS IS"
    basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
    License for the specific language governing rights and limitations
    under the License.

    The Original Code is Pymp/VoiceWARE.

    The Initial Developer of the Original Code is Noel Morgan,
    Copyright (c) 2011-2012 VoiceWARE Communications, Inc. All Rights Reserved.

    http://www.vwci.com/

    You may not remove or alter the substance of any license notices (including
    copyright notices, patent notices, disclaimers of warranty, or limitations
    of liability) contained within the Source Code Form of the Covered Software,
    except that You may alter any license notices to the extent required to
    remedy known factual inaccuracies.
"""

from simplejson import loads, dumps
from webob import Request, Response
import simplejson as json
import shutil
import os, sys, re
from paste.debug.profile import *
import imaplib
import email
from email.utils import *
from email.parser import Parser
import smtplib
from email.utils import *
import base64
import urllib
from BeautifulSoup import BeautifulSoup
import logging
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
import urllib2

log = logging.getLogger(__name__)

__all__= ['Pymap', 'PymapMime', 'PymapSmtp']


class PymapSmtp():
    """This is the class that Pymap uses to contruct and send messages.
       The class implements an abstraction for STMP Pymap specifically geared
       toward Pymp."""

    def __init__(self):
        pass

    @profile_decorator(logfile='stdout')
    def __begin__(self):
        pass

class Pymap():
    @profile_decorator(logfile='stdout')
    def __begin__(self):
        pass

    def __init__(self, _USERNAME=None, _PASSWORD=None, _HOST='localhost', \
            _PORT=993, _SSL=True, _KEY=None, _CERT=None):
        self.HOST = _HOST
        self.USERNAME = _USERNAME
        self.PASSWORD = _PASSWORD
        self.SSL = _SSL
        self.KEY = _KEY
        self.CERT = _CERT
        self.PORT = _PORT
        self.logged_in = False

        if _SSL:
            self.conn = imaplib.IMAP4_SSL(self.HOST, self.PORT)
        else:
            self.conn = imaplib.IMAP4(self.HOST, self.PORT)

    def auth_login(self, _email, _password):
        try:
            typ, data= self.conn.login(_email, _password)
            log.debug("auth res:"+typ+":")

            if typ.strip("\" \r\n") == "OK":
                self.conn.logout()
        except:
            log.debug("excepted at auth login imap")
            return False
        finally:
            return True

    def login(self):
        try:
            self.conn.login(session['email'], session['email_password'])
            self.logged_in = True
        except:
            self.logged_in = False

        ret = True if self.logged_in else False
        return ret

    def logout(self, _close=True):
        if _close:
            self.conn.close()

        try:
            self.conn.logout()
            self.logged_in = False
        except:
            self.logged_in = False
            return True

        return True

    def get_fields(self, header):
        message_header = {}
        hdr = header.split("\r\n")
        preval = None

        # Initialize defaults
        message_header['subject'] = "No Subject"
        message_header['from'] = "Unknown"
        message_header['to'] = "Unknown"
        message_header['received'] = "Unknown"
        message_header['size'] = "Unknown"
        message_header['message-id'] = "Unknown"
        message_header['content-type'] = "Unknown"

        for line in hdr:
            if not len(line):
                continue
            if line[0].isspace():
                if preval is not None:
                    message_header[str.lower(preval.split(":")[0])] \
                        +=  line + '\r\n'
                continue
            else:
                if len(line.split(":")) is not 0:
                    message_header[str.lower(line.split(":")[0])] \
                        = line.split(":")[1].lstrip()
                else:
                    continue

            preval = line.split(":")[0]

        return message_header

    def get_flags(self, data):
        flags = {}
        flags['deleted'] = True if str(data).upper().find('DELETED') \
            != -1 else False
        flags['seen'] = True if str(data).upper().find('SEEN') \
            != -1 else False

        return flags

    def msg_count(self, mbox='INBOX'):
        self.login()
        msg_res = self.conn.select_folder(mbox)
        msg_num = msg_res['EXISTS']
        self.logout()

        return msg_num

    def get_child_folders(self, mbox=None):
        f = []

        self.conn.select(mbox)
        folders = self.conn.list(mbox)
        log.debug(folders)

        #for fname in folders[1]:
        log.debug(folders[1])

        folders[1].sort()

        i=0

        for fldr in folders[1]:
            folder = fldr.replace('(','"')
            folder = folder.replace(')','"')
            i+=1

            log.debug(folder)
            flag, delim, fname = folder.split()

            folder_children = '' if str.find("HasNoChildren", flag.strip("\" \\"))>-1 else self.get_child_folders(fname.strip("\" "))

            tmp = dict({'folder_name': fname.strip("\" "),
                            'flags': flag.strip("\" \\"),
                            'icon': 'mailIconTrashcanFull' if fname.strip("\" ") == 'Trash' else 'mailIconFolderInbox',
                            'folders': folder_children,
                            'id': i})
            if folder_children == '':
                del tmp['folders']

            f.append(tmp)

        folders = dict({'identifier': 'folder_name', 'label': 'folder_name', 'items': f})

        return folders

    def get_folder_list(self):
        f = []
        
        if not self.login():
            return None
        
        self.conn.select()

        folders = self.conn.list()
        log.debug(folders)

        folders[1].sort()

        i=0

        for fldr in folders[1]:
            folder = fldr.replace('(','"')
            folder = folder.replace(')','"')
            i+=1

            log.debug(folder)
            flag, delim, fname = folder.split()

            log.debug(fname)


            folder_children = '' if str.find("HasNoChildren", flag.strip("\" \\"))>-1 else self.get_child_folders(fname.strip("\" "))

            tmp = dict({'folder_name': fname.strip("\" "),
                            'flags': flag.strip("\" \\"),
                            'icon': 'mailIconTrashcanFull' if fname.strip("\" ") == 'Trash' else 'mailIconFolderInbox',
                            'folders': folder_children,
                            'id': i})
            if folder_children == '':
                del tmp['folders']

            f.append(tmp)

        self.logout()
        folders = dict({'identifier': 'folder_name', 'label': 'folder_name', 'items': f})

        return folders

    def parse_headers(self,num):
        hdrs = {}

        for k in ['RFC822.SIZE', 'INTERNALDATE', 'FLAGS']:
            typ, dat = self.conn.fetch(num, '('+k+')')
            tmp = dat[0].split(k)
            hdrs[k] = tmp[1].strip(" \"\\()\w\r\n")

        return hdrs

    def parse_message(self, num):
        parts = {}

        for k in ['BODY[TEXT]', 'RFC822.HEADER']:
            typ, dat = self.conn.fetch(num, '('+k+')')
            parts[k] = dat[0][1]

        return parts


    def get_message_headers_from_buffer(self, mbox='INBOX'):
           hdrs = []
           self.login()

           self.conn.select(mbox)
           typ, data = self.conn.search(mbox, 'ALL')


           for msg_num in data[0].split():
                   typ, data = self.conn.fetch(msg_num, '(RFC822.SIZE INTERNALDATE FLAGS BODY[TEXT])')
                   parts = self.parse_message(msg_num)
                   imp_parts = self.parse_headers(msg_num)
                   fields = self.get_fields(parts['RFC822.HEADER'])
                   flags = self.get_flags(imp_parts['FLAGS'])
                   hdrs.append({'subject': fields['subject'],
                                'from': fields['from'],
                                'to': fields['to'],
                                'sent': fields['date'],
                                'received': imp_parts['INTERNALDATE'],
                                'size': imp_parts['RFC822.SIZE'],
                                'read': flags['seen'],
                                'deleted': flags['deleted'],
                                'message_id': fields['message-id'],
                                'content-type': fields['content-type'],
                                'body': parts['BODY[TEXT]'],
                                'folder': mbox,
                                'id': msg_num})

           store = dict({'identifier': 'id', 'label': 'subject', 'items': hdrs})

           self.logout(True)

           return store

    def get_message_headers(self, folder):
        hdrs = []
        hdr = {}
        self.login()

        self.conn.select(folder)
        typ, data = self.conn.search(folder, 'ALL')

        for msg_num in data[0].split():
            msg = self.get_message(msg_num, folder)
            
            headers = Parser().parsestr(str(msg), True)
            subj = headers['subject']
            msg = PymapMime(msg)

            message = msg()

            imp_parts = self.parse_headers(msg_num)
            flags = self.get_flags(self.parse_headers(msg_num))

            hdrs.append(dict({'subject': subj if subj else "No Subject",
                         'from': headers['from'] or "Unknown Sender",
                         'to': headers['to'] or "Unknown Recipients",
                         'received': str(imp_parts['INTERNALDATE']),
                         'size': str(imp_parts['RFC822.SIZE']),
                         'read': str(flags['seen']),
                         'deleted': str(flags['deleted']),
                         'message_id': str(message['message-id']),
                         'content-type': str(message['content-type']),
                         'body':  message['body_html'] or message['body_plain'],
                         'folder': folder,
                         'has_attachment': True if len(message['attachments'])>0 else False,
                         'attachments': message['att_names'],
                         'attachment_sizes': message['att_sizes'],
                         'style': 'msgRead' if flags['seen'] else 'msgUnread' + ' ' + 'hasAttachment' if len(message['attachments'])>0 else '',
                         'id': msg_num}))

        hdrs.reverse()
        store = dict({'identifier': 'id', 'label': 'subject', 'items': hdrs})
        self.logout(True)
        self.logged_in = False

        return store


    def get_message(self, uid, folder='INBOX'):

        if not self.logged_in:
            try:
                self.login()
            except:
                self.logged_in = False
                redirect("/login")
                log.debug("get message excepted")

        self.conn.select(folder)
        typ, msg = self.conn.fetch(uid, 'RFC822')

        return msg[0][1]

class PymapMime():
    message = {}

    def __call__(self, *args, **kwargs):
        # TODO: add more cool stuff
        msg = self.parse_message()
        return msg

    def __init__(self, _msg):
        self.msg = _msg
        self.message['multipart'] = False
        self.message['msg'] = _msg
        self.message['body_plain'] = None
        self.message['body_html'] = None
        self.message['attachments'] = []
        self.message['att_names'] = []
        self.message['att_sizes'] = []

    def parse_message(self):
        self.msg = email.message_from_string(self.msg)

        for k in self.msg.keys():
            self.message[str(k).lower()] = str(self.msg[k])

        if not self.msg.is_multipart():
            self.message['body_plain'] = str(self.msg.get_payload(decode=True))
        else:
            for part in self.msg.walk():
                self.message[part.get_content_type().lower().strip()] = part.get_payload()
                print part.get_content_type()

                disposition = part.get('Content-Disposition', None)

                if part.get_content_type().lower().strip() == "text/html":
                    self.message['body_html'] = str(part.get_payload(decode=True))
                if part.get_content_type().lower().strip() == "text/plain":
                    self.message['body_text'] = str(part.get_payload(decode=True))
                if disposition:
                    for disp in disposition.strip().split(';'):
                        if disp.lower().strip() == "attachment":
                            log.debug(disp)
                            patt = PymapAttachment(part)
                            log.debug(patt.name)
                            self.message['attachments'].append(patt)
                            self.message['att_names'].append(str(patt.name))
                            self.message['att_sizes'].append(str(patt.size))

        return self.message


class PymapAttachment():
    def __init__(self, _part=None):
        self.content_type = None
        self.name = None
        self.size = None
        self.data = None
        self.get_file_info(_part)

    def get_file_info(self, msg):
        self.data = msg.get_payload(decode=True)
        self.content_type = msg.get_content_type()
        self.size = len(msg)
        k,v = msg['Content-Disposition'].split(";")[1].split("=")
        self.name = v.strip("\"") if k.strip().lower() == "filename" else "No Name"

        return self