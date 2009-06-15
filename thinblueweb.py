#!/usr/bin/env python
# -*- coding: UTF-8 -*-
##########################################################################
# ThinBlueWeb writen by MarioDebian <mario.izquierdo@thinetic.es>
#
#    Python-ThinBlue
#
# Copyright (c) 2009 Mario Izquierdo <mario.izquierdo@thinetic.es>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
###########################################################################

import sys
import os
import string
import traceback
import random
from hashlib import sha1



DB="/var/lib/thinblue/database.db"
if os.path.isdir("/.dirs/dev/thinblue"):
    DB="/.dirs/dev/thinblue/database.db"

BASE="/usr/share/thinblue/"
# set BASE in git sources dir to debug
if os.path.abspath(os.curdir) == "/home/mario/thinetic/git/python-thinblue":
    BASE="/home/mario/thinetic/git/python-thinblue/webpanel/"

SESSIONS_DIR="/var/lib/thinblue/sessions"

IMAGE_EXTENSIONS=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'ppm', 'pcx', 'tiff']
MEDIA_EXTENSIONS=['jar', 'jad', '3gp', 'swf']
ALLOWED_CHARS=string.letters + string.digits + '-_.'


import thinblue.config
thinblue.config.debug=False
if "--debug" in sys.argv:
    thinblue.config.debug=True
thinblue.config.name="thinblueweb"
thinblue.config.DAEMON_PID_FILE = "/var/run/thinblueweb.pid"
import thinblue.logger as lg

# load daemonize con configure
import thinblue.daemonize
lg.old_stderr=sys.stderr
lg.old_stdout=sys.stdout
sys.stderr = lg.stderr()
sys.stdout = lg.stdout()

import web
web.config.debug = False
if "--debug" in sys.argv:
    web.config.debug=True
web.config.session_parameters.cookie_name="ThinBlue"


from web import form

def debug(txt):
    lg.debug("thinblueweb::debug(): %s" %str(txt), name=thinblue.config.name )
    #print >> sys.stderr, "DEBUG: %s" %str(txt)



# A simple user object that doesn't store passwords in plain text
# see http://en.wikipedia.org/wiki/Salt_(cryptography)
class PasswordHash(object):
    def __init__(self, password_):
        self.salt = "".join(chr(random.randint(33,127)) for x in xrange(64))
        self.saltedpw = sha1(password_ + self.salt).hexdigest()
    def check_password(self, password_):
        """checks if the password is correct"""
        return self.saltedpw == sha1(password_ + self.salt).hexdigest()

# FIXME: a secure application would never store passwords in plaintext in the source code
users = {'admin' : PasswordHash('admin') } 


urls = ('/', 'index',
        '/logout', 'logout',
        '/main', 'main',
        '/config', 'config',
        '/phones', 'phones',
        '/phones.xml', 'phones_xml',
        '/files', 'files',
        '/clear', 'clear',
        '/re-send', 'resend',
        '/download', 'download',
        '/data/([a-zA-Z.]*)', 'static')


# global app
app = web.application(urls, globals())
debug("Set templates dir to '%s'"%(BASE + 'templates/'))
render = web.template.render(BASE + 'templates/', base='layout')
db = web.database(dbn='sqlite', db=DB)

# from http://webpy.org/cookbook/session_with_reloader
# use only one session instead of debug=True
if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore(SESSIONS_DIR), {'user': 'anonymous'})
    web.config._session = session
else:
    session = web.config._session

signin_form = form.Form(form.Textbox('username',
                         form.Validator('Unknown username.', lambda x: x in users.keys()),
                         description='Usuario:'),
            form.Password('password', description='Contraseña:'),
            form.Button("submit", type="submit", description="Entrar"),
            validators = [form.Validator("El usuario o la contraseña son incorrectos.",
                          lambda x: users[x.username].check_password(x.password)) ])


class index:
    def GET(self):
        debug(session)
        my_signin = signin_form()
        if not hasattr(session, "user"):
            session.user="anonymous"
            debug("GET setting user anonymous")
        if session.user != "anonymous":
            return render.main(session, None)
        return render.index(session, my_signin)

    def POST(self):
        debug(session)
        my_signin = signin_form() 
        if not hasattr(session, "user"):
            session.user="anonymous"
            debug("POST setting user anonymous")
        if not my_signin.validates():
            debug("not login valid")
            return render.index(session, my_signin)
        else:
            session.user = my_signin['username'].value
            debug("login OK set session.user to %s" %my_signin['username'].value)
            return render.main(session, None)



class logout:
    def GET(self):
        session.user=""
        try:
            session.kill()
        except Exception, err:
            debug("Exception logout, error=%s"%err)
            traceback.print_exc(file=sys.stderr)
            pass
        raise web.seeother('/')



class main:
    def GET(self):
        debug(session)
        if session and session.user != "anonymous":
            entries = db.select('config')
            for i in entries:
                debug(i)
            return render.main(session, None)
        raise web.seeother('/')



class config:
    def GET(self):
        if session and session.user != "anonymous":
            entries = db.select('config')
            conf=entries[0]
            if conf.debug == 1:
                conf.debugtxt="checked"
            else:
                conf.debugtxt=""
            return render.config(session, conf)
        raise web.seeother('/')
        
    def POST(self):
        if session and session.user != "anonymous":
            userdata=web.input(debug=0, concurrent=8, timeout=4)
            debug(userdata)
            _debug = userdata.debug
            _timeout = userdata.timeout
            _concurrent = userdata.concurrent
            debug("debug=%s  timeout=%s  concurrent=%s"%(_debug, _timeout, _concurrent) )
            try:
                # set stop=2 to reload conf from daemon
                db.query("UPDATE config set debug='%s', timeout='%s', concurrent='%s', stop='2'" %(_debug, _timeout, _concurrent))
            except Exception, err:
                debug("Exception save config, error=%s"%err)
                traceback.print_exc(file=sys.stderr)
            return web.seeother('/config')
        raise web.seeother('/')



class phones:
    def GET(self):
        if session and session.user != "anonymous":
            entries = db.select('phones')
            return render.phones(session, entries)
        raise web.seeother('/')



class phones_xml:
    def GET(self):
        # local render engine (not use layout.html)
        lrender = web.template.render(BASE + 'templates')
        web.header('Content-Type', 'text/xml')
        if session and session.user != "anonymous":
            entries = db.select('phones')
            return lrender.phones_xml(entries)
        else:
            # return empty XML if no auth
            return lrender.phones_xml([])



class FileData(object):
    def __init__(self):
        entries = db.select('config')[0]
        self.absname=os.path.join( entries.file_path , entries.sendfile)
        self.fname=entries.sendfile
        self.b64=""
        self.isimage=False
        self.ext=self.fname.split('.')[-1]
        if self.ext in IMAGE_EXTENSIONS:
            self.isimage=True
            import base64
            if os.path.isfile(self.absname):
                self.b64=base64.b64encode( open(self.absname, 'r').read() )

    def download(self):
        web.header('Content-Type', 'image/%s' %(self.ext) )
        return open(self.absname, 'r').read()



class FileUpload(object):
    def __init__(self, _form):
        self.raw=_form['myfile'].value
        self.filename=_form['myfile'].filename
        for c in range(len(self.filename)):
            print "c=%s   self.filename[c]=%s" %(c, self.filename[c])
            if self.filename[c] not in ALLOWED_CHARS:
                self.filename=self.filename.replace(self.filename[c],'_')

    def isallowed(self):
        if self.filename.split('.')[-1] in IMAGE_EXTENSIONS:
            return True
        elif self.filename.split('.')[-1] in MEDIA_EXTENSIONS:
            return True
        return False

    def save(self):
        entries = db.select('config')[0]
        self.absname=os.path.join( entries.file_path , self.filename)
        try:
            f=open(self.absname, 'wb')
            f.write(self.raw)
            f.close()
            return True
        except Exception, err:
            debug("Exception save config, error=%s"%err)
            traceback.print_exc(file=sys.stderr)
            return False



class files:
    def GET(self):
        if session and session.user != "anonymous":
            return render.files(session, FileData() )
        raise web.seeother('/')

    def POST(self):
        if session and session.user != "anonymous":
            upload = FileUpload( web.input(myfile={}) )
            
            if not upload.isallowed():
                # extension not allowed
                return render.files(session, FileData() )
            if upload.save():
                # configure database
                db.query("UPDATE config set sendfile='%s', stop='2'" %(upload.filename))
            
            return render.files(session, FileData() )
        raise web.seeother('/')



class download:
    def GET(self):
        if session and session.user != "anonymous":
            data=FileData()
            return data.download()
        raise web.seeother('/')



class clear:
    def GET(self):
        if session and session.user != "anonymous":
            # clear phone table
            try:
                db.query("DELETE from phones")
            except Exception, err:
                debug("Exception clear, error=%s"%err)
                traceback.print_exc(file=sys.stderr)
            raise web.seeother('/phones')
        raise web.seeother('/')



class resend:
    def GET(self):
        if session and session.user != "anonymous":
            # set 'seen1' to all
            try:
                db.query("UPDATE phones set status='seen1', date_send=''")
            except Exception, err:
                debug("Exception resend, error=%s"%err)
                traceback.print_exc(file=sys.stderr)
            raise web.seeother('/phones')
        raise web.seeother('/')


class static:
    def GET(self, sfile):
        #debug(os.path.join(BASE, 'static' , sfile))
        if not os.path.isfile( os.path.join(BASE, 'static' , sfile) ):
            # return 404
            return web.notfound()

        # set headers (javascript, css, or images)
        extension = sfile.split('.')[-1]
        if extension == "css":
            web.header("Content-Type","text/css; charset=utf-8")
        elif extension == "js":
            web.header("Content-Type","text/javascript; charset=utf-8")
        elif extension in IMAGE_EXTENSIONS:
            web.header('Content-Type', 'image/%s' %(extension) )
        return open(os.path.join(BASE, 'static', sfile)).read()


if __name__ == "__main__":
    args=[]
    for arg in sys.argv[1:]:
        args.append(arg)
    sys.argv=[sys.argv[0], '9090']
    debug("main() sys.argv=%s args=%s" %(sys.argv,args) )
    if "--start" in args:
        debug("daemonize....")
        thinblue.daemonize.start_server()
        app.run()
    
    elif "--stop" in args:
        thinblue.daemonize.stop_server(sys.argv[0], wait = True)
    
    else:
        print >> lg.old_stderr , """
thinblueweb:
        --start    - start web daemon
        --stop     - stop daemon

    You can access interface in http://localhost:9090
"""
