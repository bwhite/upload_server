from gevent import monkey
monkey.patch_all()
import bottle
import os
import argparse
import random
import base64
import signal
from upload_server.auth import verify

template = """<html><body>
<form action="/{{AUTH_KEY}}/" enctype="multipart/form-data" method="post">
  <input type="file" name="datafile">
  <div><input type="submit" value="Send"></div>
</form>
</body></html>"""


@bottle.post('/:auth_key#[a-zA-Z0-9\_\-]+#/')
@verify
def file(auth_key):
    for f in bottle.request.files.values():
        name = os.path.basename(f.filename)
        print('Saving [%s]' % name)
        if os.path.exists(name) and not ARGS.overwrite:
            raise OSError('File exists!')
        else:
            open(name, 'wb').write(f.value)
        if ARGS.max_uploads is not None:
            if ARGS.max_uploads <= 1:
                os.kill(os.getpid(), signal.SIGINT)
            else:
                ARGS.max_uploads -= 1


@bottle.get('/:auth_key#[a-zA-Z0-9\_\-]+#/')
@verify
def main(auth_key):
    return bottle.template(template, AUTH_KEY=auth_key)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a file to a directory")
    # Server port
    parser.add_argument('--port', type=str, help='bottle.run webpy on this port',
                        default='8080')
    parser.add_argument('--max_uploads', type=int, help='Set how many uploads to process (default unlimited)')
    parser.add_argument('--overwrite', action='store_true', help='If set then allow overwriting files')
    ARGS = parser.parse_args()
    bottle.run(host='0.0.0.0', port=ARGS.port, server='gevent')
