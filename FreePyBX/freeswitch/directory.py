from freeswitch import *
import datetime, time, md5, os, sys
from pytz import timezone
from sqlalchemy.orm import scoped_session, sessionmaker, mapper
from sqlalchemy.ext.declarative import declarative_base
import datetime
from datetime import datetime
from sqlalchemy import MetaData
from sqlalchemy import Table, ForeignKey, Column
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.types import String, Integer, DateTime, Text, Boolean, Float, Time, TIMESTAMP, LargeBinary, Enum, Date, Unicode, UnicodeText
from sqlalchemy.orm import relation, synonym, relationship, backref
from datetime import datetime
import transaction
from sqlalchemy.orm import mapper
import sqlalchemy
from freepybx.model import meta
from freepybx.model.core import *
from freepybx.model.pbx import *
from freepybx.model.call_center import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine('postgresql://pbxuser:secretpass1@127.0.0.1/pbx')

Session = sessionmaker(bind=engine)
s = Session()


class VWCI:

    def __init__(self, session, context=None):
        self.session = session
        self.session.setInputCallback(self.input_callback)
        self.session.setHangupHook(self.hangup_hook)
        self.context=context
        self.ivr_obj = None

    def hangup_hook(self, session):
        del self.session
        return

    def input_callback(self, session, what, obj):
        if (what == "dtmf"):
            dtmf = obj.digit
            dtmf += self.session.getDigits(2, "", 3000, 8000);
        else:
            consoleLog( "info", what + " " + obj.serialize() + "\n" )

    def main(self):

        try:
            inbound = self.session.getVariable("sip_to_user")
            consoleLog("INFO", inbound+"\n\n")
            self.called_number = inbound[len(inbound)-10:]

            row = s.execute("SELECT pbx_routes.*, pbx_dids.customer_id "
                            "from pbx_routes "
                            "inner join pbx_dids "
                            "on pbx_routes.id = pbx_dids.pbx_route_id "
                            "where pbx_dids.did = :destination_number",\
                    {'destination_number': self.called_number})

            self.r = row.fetchone()

            self.context = self.r.context
            self.customer_id = self.r.customer_id

            alphabet = "abcdefghijklmnopqrstuvwxyz"
            numbers = "22233344455566677778889999"

            code_to_name = {}
            code = ""

            names = {}
            for name in s.query(User).filter_by(customer_id=self.r.customer_id).all():
                names[name.first_name.lower()+' '+name.last_name.lower()]=name.portal_extension

            def sayname(fullname):
                console_log("alert", "Now saying: " + fullname + "\n")
                self.session.execute("phrase", "spell," + fullname)

            for name in names:
                name3char = name[0:3]
                code = ""
                for char in name3char:
                    code = code + numbers[alphabet.index(char)]
                if not code in code_to_name:
                    code_to_name[code] = [name]
                else:
                    code_to_name[code].append(name)

            self.session.sleep(3000)
            digits_keyed = self.session.playAndGetDigits(3, 3, 10, 5000, "*#", "phrase:directory_welcome", "", "");

            if digits_keyed == "1":
                self.session.transfer(str(extension), "XML", "default")
            else:
                if digits_keyed == "*":
                    self.session.streamFile("${base_dir}/sounds/en/us/callie/directory/8000/dir-no_matching_results.wav")

                else:
                    for item in code_to_name[digits_keyed]:
                        extension = str(names[item])
                        recorded_name = False #checkforgreeting(extension)
                        if recorded_name:
                            self.session.streamFile(str(recorded_name[0]))
                        else:
                            sayname(str(item))
                        self.session.execute("phrase", "spell," + str(extension));
                        self.session.execute( "sleep", "1000" )
                        digits_keyed = self.session.playAndGetDigits(1, 1, 3, 2000, "#", "phrase:directory_match", "", "1|\*");
                        if digits_keyed == "1":
                            self.session.execute( "set", "contact_available=${sofia_contact("+str(self.context)+"/"+str(extension)+"@"+str(self.context)+")}" )
                            contact_available = self.session.getVariable("contact_available")

                            if contact_available.find("error") != -1:
                                self.session.speak("I am sorry, that person is unavailable.")
                                self.session.execute("voicemail", str(self.context)+" "+str(self.context)+" "+str(extension))
                            else:
                                self.session.execute("playback", "ivr/ivr-hold_connect_call.wav")
                                self.session.execute("set", "transfer_ringback=${hold_music}")
                                self.session.transfer(str(extension),"XML", str(self.context))

                    self.session.streamFile("${base_dir}/sounds/en/us/callie/directory/8000/dir-no_matching_results.wav")
        except:
            Exception("Blowed up real good...")
        finally:
            del self.session
            return

def handler(session, args):
    session.answer()
    session.set_tts_parms('cepstral', 'Allison')
    vwci = VWCI(session)
    vwci.main()
    vwci.hangup_hook(session)
