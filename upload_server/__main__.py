from gevent import monkey
monkey.patch_all()
import bottle
import os
import argparse
import random
import base64
from static_server.auth import verify


STATIC_PATH = os.path.abspath('.') + os.sep


@bottle.route('/:auth_key#[a-zA-Z0-9\_\-]+#/:path#.*[^/]#')
@verify
def file(auth_key, path):
    return bottle.static_file(path, root=STATIC_PATH)


@bottle.route('/:auth_key#[a-zA-Z0-9\_\-]+#/:path#.*#')
@verify
def dir_page(auth_key, path=''):
    if not ARGS.index:
        bottle.abort(401)
    if not ARGS.dirs and path not in ('/', ''):
        bottle.abort(401)
    path = os.path.abspath(os.path.join(STATIC_PATH, path)) + os.sep
    if not path.startswith(STATIC_PATH):
        bottle.abort(401)
    rel_path = path[len(STATIC_PATH):]
    return ''.join('<a href="/%s/%s%s%s">%s</a><br>' % (auth_key, rel_path, x, '/' if os.path.isdir(os.path.join(path, x)) else '', x)
                   for x in os.listdir(path))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Serve a directory")

    # Server port
    parser.add_argument('--port', type=str, help='bottle.run webpy on this port',
                        default='8080')
    parser.add_argument('--index', action='store_true')
    parser.add_argument('--dirs', action='store_true')
    ARGS = parser.parse_args()
    bottle.run(host='0.0.0.0', port=ARGS.port, server='gevent')
