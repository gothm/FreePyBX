#!/bin/bash
/bin/echo $$ > /tmp/wsgi_watch.pid

# Change development.ini to deploy.ini for production
# Noel Morgan <noel@vwci.com>
# VoiceWARE Communications, Inc.

while [ true ]
    do
    {
        /bin/sleep 120
        WSGI=`ps axu | grep -v grep | grep paster | awk '{print $2}'`
        DATE=`date`
        t=0
        FAILED="Restarted process:  $DATE";
        for p in $WSGI; do t=1; done

        if [ $t -eq 0 ] 
            then                               
            {
                echo "Restarting wsgi process..."                
                echo $FAILED >> /tmp/wsgi_watch.log
                (cd ~; source bin/activate; cd FreePyBX; paster serve --reload development.ini &)
		echo "WSGI server restarted!" | mail -s "WSGI Restarted" noel@vwna.com
            }
        else
            echo "OK..."
        fi
    }
done


