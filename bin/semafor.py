#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../python_modules'))
import SemaforServer as ss

# set process title so it can be killed on stop
try:
    import setproctitle
    setproctitle.setproctitle("semafor")
except:
    pass

if __name__ == '__main__':
    rssServer = ss.SemaforServer()
    try:
        rssServer.setup()
        rssServer.loop()
    except KeyboardInterrupt:
        rssServer.clear()

sys.exit(1)