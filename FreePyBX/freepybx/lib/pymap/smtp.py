"""
    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.

    Software distributed under the License is distributed on an "AS IS"
    basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
    License for the specific language governing rights and limitations
    under the License.

    The Original Code is Pymp/Pymap/VoiceWARE.

    The Initial Developer of the Original Code is Noel Morgan,
    Copyright (c) 2011-2012 VoiceWARE Communications, Inc. All Rights Reserved.

    http://www.vwci.com/

    You may not remove or alter the substance of any license notices (including
    copyright notices, patent notices, disclaimers of warranty, or limitations
    of liability) contained within the Source Code Form of the Covered Software,
    except that You may alter any license notices to the extent required to
    remedy known factual inaccuracies.
"""


import smtplib

import HTMLParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



class PymapSMTP():
    def __init__(self, _to_email, _from_email, _subject=None, _msg_body=None, _msg_attachments=[]):
        self.to_email = _to_email
#        self.from_name = _from_name
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
        part2 = MIMEText(body_html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        # Send the message via local SMTP server.
        s = smtplib.SMTP('localhost')
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        s.sendmail(msg['From'], msg['To'], msg.as_string())
        s.quit()
        