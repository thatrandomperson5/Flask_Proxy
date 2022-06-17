from flask import Flask, send_from_directory, redirect, abort, session, request
from browserbook import brbook
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import os
from datetime import timedelta
from time import sleep
from letterCode import Encode, Decode
import threading
app = Flask(__name__)
app.secret_key = os.environ.get('sct')
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=7)
book = brbook('brbookProxy')
def timeout(time, b):
  print('Timing Out')
  sleep(time)
  book.EndSession(b)
  print("Timed out")
@app.route('/')
def index():
    return redirect('/proxyaccess')
@app.route('/proxyaccess', methods=["GET","POST"])
def f():
  if request.method == "POST":
    url = request.form['url']
    url = urlparse(url)
    if url.path == '':
      abort(401)
    if 'id' in session:
        return redirect(f'/proxy/{Encode(url.hostname)}/{Encode(url.path)}?q={Encode(url.query)}')
    session['id'] = book.sessionStart()
    t = threading.Thread(target=timeout, args=(420, session["id"],))
    t.start()
    return redirect(f'/proxy/{Encode(url.hostname)}/{Encode(url.path)}?q={Encode(url.query)}')
  return '''
  <style>
.center-screen {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  min-height: 80vh;
}
  </style>
  <form method="post">
  <div class ="center-screen">
  <h1 style="font-size: 75px; font-style: italic; font-family: 'Montserrat', sans-serif;">Flask Proxy</h1>
  <p><input type=url placeholder=url value="https://www.google.com/" name=url style="height: 55px; font-size: 35px; width: 1000px;">
  <input type = "submit" value = "GO!" style="font-size: 40px;"></p>
  <h9>Powered by <a href="https://www.python.org/">Python</a> <a href="https://flask.palletsprojects.com/">Flask</a>, <a href="https://pypi.org/project/browserbook/">BrowserBook</a> and <a href="https://www.crummy.com/software/BeautifulSoup/">BS4</a></h9>
  <p style="color: red;">⚠This is a proxy and is not phishing⚠</p>

  </div>
  </form>
  '''
@app.route('/proxy/<host>/<path:path>')
def proxy(host, path):
  if 'id' in session:
    
    bsession = book.getSessionObject(book.name, session['id'])
    host = Decode(host)
    path = Decode(path)
    q = Decode(request.args.get('q'))
    bsession.localize = True
    try:
      bsession.dump()
    except:
      print("firsttime")
    print("https://"+host+path+'?'+q)
    bsession.Get("https://"+host+path+'?'+q)
    oldpath = path
    path = f'{os.getcwd()}/brbookProxy/sessions/{bsession.id}/source/index.html'
    with open(path, 'r') as readme:
      r = readme.read()
    soup = BeautifulSoup(r)
    
    jsScript = soup.new_tag('script')
    jsScript['type'] = "text/javascript"
    jsScript.string = '''
    function closepopup() {
      var elm = document.getElementById("overlay")
      elm.remove()
    
    }
    function proxypopup () {
    var d = document.body
    d.innerHTML += `
<style>
.overlay {
  position: fixed;
  display: block; 
  width: 100%; 
  height: 30px; 
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,5,0.5); 
  z-index: 2;
  cursor: pointer;
  
}
.urlbox {

      border: 3px solid black;
      
      
    }
</style>
<div class=overlay id=overlay>
<div>
<b style="font-style: italic; font-family: 'Montserrat', sans-serif; font-size: 30px;">Flask Proxy ''' + f'''<b style="font-size: 20px; font-style: normal; display: inline-block; border: 3px solid black; vertical-align: middle; background-color: white; max-width: 500px; max-height: 30px; overflow: hidden; white-space: nowrap;"> URL: <b class=urlbox >&nbsphttps://{host+oldpath+"?"+q}</b></b><button type="button" style="vertical-align: middle; font-size: 18px;" onclick="closepopup()">❌</button>
</div>
</div>
`'''+'}'
    activator = soup.new_tag('script')
    activator.string = 'proxypopup()'
    soup.html.head.append(jsScript)
    soup.html.body.append(activator)
    for s in soup.find_all(attrs={'src': True}):
      if s['src'].startswith('/'):
        new = f'/m/get/brbookProxy/sessions/{bsession.id}/source{s["src"]}'
        s['src'] = new
      else:
        p = urlparse(s['src'])
        new = f'/m/get/brbookProxy/sessions/{bsession.id}/externalSRC{p.path}'
    with open(path, 'w') as w:
      w.write(str(soup))
    return soup.prettify()
      
  return redirect('/proxyaccess')
@app.route('/m/get/<path:proxypath>')
def get(proxypath):
  try:
    return send_from_directory(os.getcwd(), proxypath)
  except FileNotFoundError:
    abort(404)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=81)
