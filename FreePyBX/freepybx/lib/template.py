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

import os
from genshi.core import Stream
from genshi.output import encode, get_serializer
from genshi.template import Context, TemplateLoader
from pylons import request, response, session, tmpl_context as c, url
import pylons


loader = TemplateLoader(
    os.path.join(os.path.dirname(__file__), '..', 'templates/genshi'),
    auto_reload=True
)

def output(filename, method='html', encoding='utf-8', **options):
    """ decorator for html genshi stream """
    if not filename.endswith(".html"):
        filename += ".html"

    def decorate(func):
        def wrapper(*args, **kwargs):
            loader.load(filename)
            opt = options.copy()
            if method == 'html':
                opt.setdefault('doctype', 'html')
            serializer = get_serializer(method, **opt)
            stream = func(*args, **kwargs)
            if not isinstance(stream, Stream):
                return stream
            return encode(serializer(stream), method=serializer,
                          encoding=encoding)
        return wrapper
    return decorate

def render(*args, **kwargs):
    """ couple of personal tweaks from pylons default rendering  """
    globals = {}

    conf = pylons.config._current_obj()
    c = pylons.tmpl_context._current_obj()
    app_globals = conf.get('pylons.app_globals')
    pylons_vars = dict(
        c=c,
        tmpl_context=c,
        config=conf,
        app_globals=app_globals,
        h=conf.get('pylons.h'),
        request=pylons.request._current_obj(),
        response=pylons.response._current_obj(),
        url=pylons.url._current_obj(),
        translator=pylons.translator._current_obj(),
        ungettext=pylons.i18n.ungettext,
        _=pylons.i18n._,
        N_=pylons.i18n.N_
    )

    template = loader.load(args[0])

    if args:
        assert len(args) == 1, \
            'Expected exactly two argument, but got %r' % (args,)
        template = loader.load(args[0])

    globals.update(pylons_vars)
    globals.update(kwargs)
    return template.generate(g=globals, url=url, session=session)