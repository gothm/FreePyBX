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


from pylons import request, response, session, tmpl_context as c, url


class Flash(object):
    """ unused since the notice js implementation  """
    def __call__(self, message=None, style='notice'):
        session["flash"] = message
        session["flash.style"] = style
        session.save()

    def pop_message(self):
        message = session.pop("flash", None)
        session['flash'] = None
        session.save()
        if not message:
            return None
        return message


    def style(self):
        return session.pop("flash.style", 'notice')

    def _has_message(self):
        if len(session['flash']) > 0 and session['flash'] is not None:
            return True
        return False



flash = Flash()