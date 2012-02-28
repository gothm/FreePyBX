from freeswitch import *
import datetime, time, md5, os, sys
from pytz import timezone

import shutil
import os, sys


class VWCI:

    def __init__(self, session):
        self.session = session        
        self.session.setInputCallback(self.on_dtmf)
        self.dtmf = ""
        self.rec = None
        self.uc = None
        self.ext = None
        self.dir = None

    
    def on_dtmf(self, session, typ, obj):

        if (typ == "dtmf"):
            self.dtmf += obj.digit
            if obj.digit == 3:
                return self.rerecord()
            if obj.digit == "*":
                self.session.speak("Hang up.  Or press 3 to ree reecord.")
                return self.rerecord()

    def rerecord(self):
        if os.path.exists(self.rec):
            shutil.rmtree(self.rec)
        self.session.speak("Begin recording after the beep. When finished, press star to end recording.") 
        self.session.streamFile("/usr/local/freeswitch/recordings/beep.wav")
        self.session.execute("sleep", "300")

        self.session.recordFile(self.rec, 240, 500, 3)        

    def main(self):
        try:
            self.ext = self.session.getVariable("sip_from_user")
            self.uc = self.session.getVariable("domain_name")
            self.dir = "/usr/local/freeswitch/htdocs/vm/"+self.uc+"/recordings/"


            if not os.path.exists(self.dir):
                os.makedirs(self.dir)

            self.session.speak("Please enter a file number followed by the pound sign.")

            self.dtmf = self.session.getDigits(5, "#", 2000, 6000);

            if not self.dtmf:
                self.session.speak("Recording failed.")
                self.session.hangup("NORMAL_CLEARING")

            self.rec = self.dir+self.ext+"-"+self.dtmf+"-recording.wav"

            if os.path.isfile(self.rec):
                shutil.rmtree(self.rec)

            self.session.speak("Begin recording after the beep. When finished, hang up or stop talking to end recording.")
            self.session.streamFile("/usr/local/freeswitch/recordings/beep.wav")
            self.session.execute("sleep", "300")


            self.session.recordFile(self.rec, 240, 500, 3)
            self.session.hangup("NORMAL_CLEARING")
        except:
            raise Exception("Broke in main...")
        finally:
            del self.session
                                           
def handler(session, args):
    try:
        session.answer()    
        session.set_tts_parms('cepstral', 'Allison')    
        VWCI = VWCI(session)
        VWCI.main()
    except:
        raise Exception("Broke in handler...")
    finally:
        del session
    
    
