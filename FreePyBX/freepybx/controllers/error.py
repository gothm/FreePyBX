import cgi

from paste.urlparser import PkgResourcesParser
from pylons import request, response, session, config, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.middleware import error_document_template
from webhelpers.html.builder import literal
from freepybx.lib.base import BaseController, render
import HTMLParser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

smtp_server = config['smtp_server']

class ErrorController(BaseController):
    """Generates error documents as and when they are required.

    The ErrorDocuments middleware forwards to ErrorController when error
    related status codes are returned from the application.

    This behaviour can be altered by changing the parameters to the
    ErrorDocuments middleware in your config/middleware.py file.
    """

    def document(self):
        """Render the error document"""
        '''Change below for your liking!'''
        #abort(500, 'Internal Server Error')
        request = self._py_object.request
        resp = request.environ.get('pylons.original_response')
        script = request.environ.get('PATH_INFO', '')
        error_code=cgi.escape(request.GET.get('code', str(resp.status_int)))
        content = literal(resp.body) or cgi.escape(request.GET.get('message', ''))
        remote_ip = request.environ.get("HTTP_REMOTE_EU", "No IP?")
        c.status_code = str(resp.status_int)
        if c.status_code == "404":
            c.message = "The document you are looking or was not found. The administrator has been notified of this event."
        elif c.status_code == "500":
            c.message = "An internal server error has occurred. The administrator has been notified of this event."
        else:
            c.message = "Sorry, an error has occurred. The administrator has been notified of this event."

        from_email = "errors@vwci.com"
        to_email = 'noel@vwci.com'
        subject = "Error code "+error_code+" has happened from "+remote_ip
        message = content+"\n\n"
        from_name = "Errors"

        msg = from_name+"Error was:\n\n"+"Script: "+script+"\n\nMessage:"+message

        p = PbxSMTP(to_email, from_email, subject, msg)
        p.send_message()

        try:
            if 'user' in session:
                session.invalidate()
                del session['user']
        except:
            pass

        return render("errors/error.html")

    def img(self, id):
        """Serve Pylons' stock images"""
        return self._serve_file('/'.join(['media/img', id]))

    def style(self, id):
        """Serve Pylons' stock stylesheets"""
        return self._serve_file('/'.join(['media/style', id]))

    def _serve_file(self, path):
        """Call Paste's FileApp (a WSGI application) to serve the file
        at the specified path
        """
        request = self._py_object.request
        request.environ['PATH_INFO'] = '/%s' % path
        return PkgResourcesParser('pylons', 'pylons')(request.environ, self.start_response)


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
        #body_html = self.msg_body

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
        s = smtplib.SMTP(smtp_server)
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        s.sendmail(msg['From'], msg['To'], msg.as_string())
        s.quit()