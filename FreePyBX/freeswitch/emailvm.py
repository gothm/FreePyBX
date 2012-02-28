#!/usr/bin/python
#

"""
Copyright (c) 2009, ChronosTelecom, LLC
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the <organization> nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY <copyright holder> ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <copyright holder> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""


import smtplib
import sys
import MimeWriter
import mimetools
import mimetypes
import os
import StringIO
import re
import shutil
import time
import os.path
from optparse import OptionParser

SERVER = ''
PORT = 587
USER = ''
PASSWORD = ''
attach = ""

# Write data to a file given the filename.  Make a backup of the file FIRST!
def write_file(filename,data):
    fh = ""
    cur_time = time.time()
    if not fh:
        if not os.path.exists(filename):
            fh = open(filename,'w')
        else:
            #print "WARNING: %s exists!  Moving it to %s.bak.%s" % (filename,filename,cur_time)
            shutil.move(filename,"%s.bak.%s" % (filename,cur_time))
            fh = open(filename,'w')
    
    fh.write(data)
    fh.close()

# send the mail
def send(sender,to,message,verbose=False):
    smtp = smtplib.SMTP(SERVER, PORT)
    if verbose:
        smtp.set_debuglevel(1)
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(USER,PASSWORD)
    smtp.sendmail(sender, to, message)
    smtp.quit()
    
    
def mail(sender='', to='', subject='', text='', attachments=None, verbose=False):
    """
    Usage:
        mail()
    Params:
        sender: sender's email address
        to: receipient email address
        subject: subject line
        text: Email message body main part.
        attachments: list of files to attach
    """
    message = StringIO.StringIO()
    writer = MimeWriter.MimeWriter(message)
    writer.addheader('To', to)
    writer.addheader('From', sender)
    writer.addheader('Subject', subject)
    writer.addheader('MIME-Version', '1.0')
    
    writer.startmultipartbody('mixed')
    
    # start with a text/plain part
    part = writer.nextpart()
    body = part.startbody('text/plain')
    part.flushheaders()
    body.write(text)

    # now add the attachments
    if attachments is not None:
        for a in attachments:
            filename = os.path.basename(a)
            ctype, encoding = mimetypes.guess_type(a)
            if ctype is None:
                ctype = 'application/octet-stream'
                encoding = 'base64'
            elif ctype == 'text/plain':
                encoding = 'quoted-printable'
            else:
                encoding = 'base64'
                
            part = writer.nextpart()
            part.addheader('Content-Transfer-Encoding', encoding)
            body = part.startbody("%s; name=%s" % (ctype, filename))
            print filename
            mimetools.encode(open(a, 'rb'), body, encoding)

    # that's all folks
    writer.lastpart()

    send(sender,to,message.getvalue(),verbose)
    
def validate_email(fromAddress):
    email_addr = re.compile(r'(([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?))')
    return bool(email_addr.search(fromAddress))


if __name__ == "__main__":
    fromAddress = ""
    to = ""
    subject = ""
    infile = ""
    body = ""
    translate = ""
    tempfile = ""
    usestdin = False
    verbose = False
    delete = False
    log = False
    
    parser = OptionParser()
    parser.add_option('-f', dest='fromAddress', metavar='FROMADDRESS',help="The from address for the email")
    parser.add_option('-t', dest='toAddress', metavar='TOADDRESS',help="The to address for the email")
    parser.add_option('-s', dest='subject', metavar='SUBJECT',help="The subject for the email")
    parser.add_option('-a', dest='attachment', metavar='ATTACHMENT',help="The file to attach to the email")
    parser.add_option('-b', dest='body', metavar='BODY',help="The body of the email")
    parser.add_option('-x', dest='translate', metavar='TRANSLATE',help="Translate the attachment using a translator program.\ntiff2pdf is the only supported option at this time.")
    parser.add_option('-i', dest='use_stdin', action="store_true", default=False,help="Use standard in as the input for the email message.")
    parser.add_option('-d', dest='delete', action="store_true", default=False,help="Delete the attachments when done processing.")
    parser.add_option('-v', dest='verbose', action="store_true", default=False,help="Verbose output for debugging.")
    parser.add_option('-l', dest='log', action="store_true", default=False,help="Log the message to a file stored in /tmp/sendemail.log")

    (options, args) = parser.parse_args()

    if options.fromAddress:
        fromAddress = options.fromAddress
        if not validate_email(fromAddress):
            print "Invalid From email address.  Please try again."
            exit(1)
    if options.toAddress:
        to = options.toAddress
        if not validate_email(to):
            print "Invalid To email address.  Please try again."
            exit(1)
    if options.subject: subject = options.subject
    if options.attachment: infile = options.attachment
    if options.body: body = options.body
    if options.translate: translate = options.translate
    if options.use_stdin: usestdin = options.use_stdin
    if options.verbose: verbose = options.verbose
    if options.delete: delete = options.delete
    if options.log: log = options.log

    if usestdin is True:
        message = ""
        attachment = infile
        for line in sys.stdin:
            message += line
        to_field = re.compile(r'To: <(([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?))>')
        if to_field.search(message):
            to_match = to_field.search(message)
            to = str(to_match.group(1))
        if log:
            write_file('/tmp/sendemail.log',message)
        send(fromAddress,to,message,verbose)
    else:
        if translate == 'tiff2pdf':
            tempfile = "/tmp/%s.pdf" % os.path.basename(infile)
            command = "tiff2pdf %s -o %s" % (infile, tempfile)
            os.system(command)
            attachment = tempfile
        else:
            attachment = infile
        
        attach=[attachment]

        mail(sender=fromAddress, to=to, subject=subject, text=body, attachments=attach, verbose=verbose)
    
    # delete our temporary file - it's up to the caller to delete the attachments, if they want
    if tempfile:
        os.unlink(tempfile)
    if delete and attachment:
        os.unlink(attachment)
