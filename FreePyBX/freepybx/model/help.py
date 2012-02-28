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


import datetime
from datetime import datetime
from sqlalchemy import ForeignKey, Column
from sqlalchemy.types import Integer, DateTime, Boolean, Unicode, UnicodeText
from sqlalchemy.orm import relation, synonym, relationship, backref
from freepybx.model.meta import Session, Base


class HelpCategory(Base):
    __tablename__='help_categories'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(128), nullable=False)
    description = Column(UnicodeText, nullable=False, default=u'Nothing here to see folks. Please move away.')

    def __init__(self, name=None, description=None):
        self.name = name
        self.description = description


class Help(Base):
    __tablename__='pbx_help'

    query = Session.query_property()

    id = Column(Integer, autoincrement=True, primary_key=True)
    category_id = Column(Integer, ForeignKey('help_categories.id', onupdate="CASCADE"))
    data = Column(UnicodeText, nullable=False)

    help_cat = relationship("HelpCategory", order_by="HelpCategory.id")

    def __init__(self, context=None, data=None):
        self.context = context
        self.data = data