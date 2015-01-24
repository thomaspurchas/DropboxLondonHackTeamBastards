from flask import Flask, session, redirect, url_for, escape, request, render_template, g as fglobal

import os
import re

from dropbox.client import DropboxOAuth2Flow, DropboxClient
from dropbox.datastore import Datastore, DatastoreError, DatastoreManager, Date, Bytes
from dropbox.rest import ErrorResponse

app = Flask(__name__)

DEBUG = os.environ.get('DEBUG', True)
app.debug = DEBUG
app.secret_key = 'a9f3ab10-a345-11e4-89d3-123b93f75cba'

DROPBOX_APP_KEY = 'alb0kf2mp7ca1np'
DROPBOX_APP_SECRET = '1d06iyf5ixv9y54'
DROPBOX_PATH_REGEX = re.compile('.*?view/.*?/(.*)')

GOD_CLIENT = DropboxClient('qRrmAkXDDlQAAAAAAAAJTo3vU5u627YKYUwHUzTQ2t48OiJvdPHsg5dHF5HS1KyZ')
GOD_PATH = 'DBHACK/'
GOD_DS_MAN =  DatastoreManager(GOD_CLIENT)
GOD_DS = GOD_DS_MAN.open_default_datastore()

GAME_RUNNING = 'running'
GAME_WAITING = 'waiting'

WINNER_PATH = 'apps/sacradash/winnings'


def get_dropbox_client():
    client = DropboxClient(session['access_token'], locale='en_UK')

    user_info = client.account_info()
    session['user_id'] = user_info['uid']
    session['display_name'] = user_info['display_name']
    return client


def get_game_ds():
    game_ds = getattr(fglobal, '_game_ds', None)
    if game_ds:
        game_ds.commit()
        game_ds.load_deltas()
        return game_ds

    GOD_DS.load_deltas()
    main_table = GOD_DS.get_table('main')
    records = main_table.query()

    if len(records) < 1:
        # Create ds
        game_ds = GOD_DS_MAN.create_datastore()

        # Make it shared and viewable to the public
        game_ds.set_role(Datastore.PUBLIC, Datastore.VIEWER)
        game_ds.commit()

        # Store the id
        main_table.insert(game_ds_id=game_ds.get_id())
        GOD_DS.commit()
    else:
        record = records.pop()
        game_ds_id = record.get('game_ds_id')
        game_ds = DatastoreManager(GOD_CLIENT).open_datastore(game_ds_id)

    fglobal._game_ds = game_ds
    game_ds.commit()
    game_ds.load_deltas()
    return game_ds


def commit_game():
    get_game_ds().commit()


def get_team_table():
    ds = get_game_ds()

    return ds.get_table('team')


def get_status_table():
    ds = get_game_ds()

    return ds.get_table('status')


def get_game_state():
    ds = get_game_ds()

    status_table = ds.get_table('state')
    records = status_table.query()

    if len(records) < 1:
        set_game_state(GAME_WAITING)
        record = status_table.query().pop()
    else:
        record = records.pop()
    return record.get('state')


def set_game_state(state):
    ds = get_game_ds()

    status_table = ds.get_table('state')
    for record in status_table.query():
        record.delete_record()

    status_table.insert(state=state)
    ds.commit()


def reset_game():
    pass

def run_game():
    set_game_state(GAME_RUNNING)

    status_table = get_status_table()

    for record in status_table.query():
        record.delete_record()

    status_table.insert(state='running', lat='51.507990', lon='-0.128049')

    get_game_ds().commit()

def end_game():
    set_game_state(GAME_WAITING)

    get_status_table().status_table.query().pop().set('state', 'won')

    get_game_ds().commit()


def dropbox_walk_path(path):
    client = get_dropbox_client()
    items = client.metadata(path)['contents']

    file_paths = []
    for item in items:
        if item['is_dir']:
            file_paths.extend(dropbox_walk_path(item['path']))
        else:
            file_paths.append(item['path'])

    return file_paths


def steal_file(path):
    client = get_dropbox_client()
    user_id = session['user_id']

    # Copy file to GODBOX
    file_ref = client.create_copy_ref(path)
    GOD_CLIENT.add_copy_ref(file_ref['copy_ref'], GOD_PATH + '%s/%s' % (user_id, path))

    # Delete original
    client.file_delete(path)


def return_file(path):
    client = get_dropbox_client()
    user_id = session['user_id']

    # Copy file to GODBOX
    file_ref = GOD_CLIENT.create_copy_ref(path)
    client.add_copy_ref(file_ref['copy_ref'], WINNER_PATH + path)

    # Delete original
    GOD_CLIENT.file_delete(path)


def return_files():
    client = get_dropbox_client()
    user_id = session['user_id']

    for rfile in dropbox_walk_path(GOD_PATH):
        return_file(rfile)


def get_dropbox_auth_flow():
    if DEBUG:
        redirect_uri = "http://localhost:5000/dropbox-auth-finish"
    else:
        redirect_uri = "https://https://sacradash.herokuapp.com/dropbox-auth-finish"
    return DropboxOAuth2Flow(DROPBOX_APP_KEY, DROPBOX_APP_SECRET, redirect_uri,
                             session, "dropbox-auth-csrf-token")

# URL handler for /dropbox-auth-start
@app.route('/dropbox-auth-start')
def dropbox_auth_start():
    authorize_url = get_dropbox_auth_flow().start()
    print authorize_url
    return redirect(authorize_url)

# URL handler for /dropbox-auth-finish
@app.route('/dropbox-auth-finish')
def dropbox_auth_finish():
    try:
        access_token, user_id, url_state = \
            get_dropbox_auth_flow().finish(request.args)
    except DropboxOAuth2Flow.BadRequestException, e:
        return render_template('400.html', 400)
    except DropboxOAuth2Flow.BadStateException, e:
        # Start the auth flow again.
        return redirect(url_for('dropbox_auth_start'))
    except DropboxOAuth2Flow.CsrfException, e:
        return render_template('403.html', 403)
    except DropboxOAuth2Flow.NotApprovedException, e:
        return redirect_to(url_for('index'))
    except DropboxOAuth2Flow.ProviderException, e:
        #logger.log("Auth error: %s" % (e,))
        return render_template('403.html', 403)

    session['access_token'] = access_token

    return redirect(url_for('index'))


@app.route('/chosen-one/<path:link>')
def get_link(link):
    # show the post with the given id, the id is an integer
    match = DROPBOX_PATH_REGEX.match(link)
    if match:
        link = match.group(1)
    else:
        return render_template('400.html', 400)

    steal_file(link)
    return link


@app.route('/access_token/')
def access_token():
    return session['access_token']


@app.route('/datastore_id/')
def datastore_id():
    return get_game_ds().get_id()


@app.route('/start/')
def start_game():
    run_game()
    return 'Running'


@app.route('/stop/')
def stop_game():
    return_files()
    reset_game()

    return 'Nice One!'


@app.route('/position/')
def set_user_position():
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    get_dropbox_client()
    team_table = get_team_table()

    records = team_table.query(user_id = session['user_id'])
    if len(records) >= 1:
        for record in records:
            record.delete_record()

        team_table.insert(user_id=session['user_id'], display_name=session['display_name'], lat=lat, lon=lon)
    else:
        if get_game_state() == GAME_WAITING:
            team_table.insert(user_id=session['user_id'], display_name=session['display_name'], lat=lat, lon=lon)

    get_game_ds().commit()

    return 'Wooo!'


@app.route('/')
def index():
    if session.get('access_token') is None:
        return redirect(url_for('dropbox_auth_start'))
    try:
        client = get_dropbox_client()
    except ErrorResponse as e:
        return redirect(url_for('dropbox_auth_start'))

    return redirect('/static/chooser/index.html')
'''
@app.route('auth'):
	#Should be 301 Redirect to Dropbox app authentication
	return "auth"
'''

if __name__ == "__main__":
    app.run()
