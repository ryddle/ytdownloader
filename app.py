from flask import Flask, redirect, url_for, request, render_template, session, send_file, make_response
from flask_cors import CORS
from pytube import YouTube, Playlist
from ytd.YtdlpYtd import YtdlpYtd
from werkzeug.utils import secure_filename
import os, json

import requests

# Url video example: https://www.youtube.com/watch?v=Ckom3gf57Yw
# Url playlist example: https://www.youtube.com/playlist?list=PL9Pc5j186PM52HmjSIMRH2jU-Z21cOblb
# flask run or flask --app app.py --debug run

app = Flask(__name__)
CORS(app)
deleteFiles = False # if True delete files after download. By default dont delete files.

@app.route("/", methods=["GET"])
def index():
    error_message = request.args.get('error_message')
    if error_message==None:
        error_message = ""
    
    if deleteFiles & os.path.exists('download'):
        files_path = [os.path.abspath('download/'+x).replace("\\","/") for x in os.listdir("./download/")]
        print(files_path)
        for file in files_path:
            if os.path.exists(file) & file.endswith(".mp3"):
                os.remove(file)
    
    return render_template("index.html", error_message=error_message)


@app.route("/", methods=["POST"])
def index_post():
    yturls = list(map(str.strip, request.form["text"].split(',')))
    filesObj, errors = downloadUrls(yturls)
    return render_template('results.html', filesObj=filesObj)

@app.route("/api/ytdown", methods=["POST"])
def api_index_post():
    res_obj = {}
    yturls = list(map(str.strip, request.form["videos_urls"].split(',')))
    dir_path = request.form.get("dir_path")
    filesObj, errors = downloadUrls(yturls, dir_path)
    res_obj['status'] = 'success'
    res_obj['data'] = filesObj
    res_obj['errors'] = errors
    res = make_response(json.JSONEncoder().encode(res_obj), 200)
    res.headers.add('Content-type', 'application/json')
    return res

@app.route("/playlist/", methods=["POST"])
def playlist():
    playlist_url = request.form.get("playlist_url")
    dir_path = "download"
    print(playlist_url)
    if not playlist_url:
        return "Empty playlist URL", 400
    try:
        """ playlist = Playlist(playlist_url)
        videos = []
        for url in playlist.video_urls:
            print(url)
            videos.append(url)
        if not videos:
            return redirect(url_for('index', error_message="Playlist is empty"))
        yturls = ",".join(videos)
        print(yturls)
        filesObj, errors = downloadUrls(videos)  """
        ytd = YtdlpYtd(playlist_url)
        filesObj, errors = ytd.downloadAudioPlaylist(playlist_url, dir_path)
        if len(filesObj) == 0 and len(errors) == 0:
            return redirect(url_for('index', error_message="Playlist is empty"))
        print(filesObj)
        print(errors)
        return render_template('results.html', filesObj=filesObj, errors=errors)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return str(e), 500

@app.route("/api/playlist", methods=["POST"])
def api_playlist():
    res_obj = {}
    playlist_url = request.form.get("playlist_url")
    dir_path = request.form.get("dir_path")
    print(playlist_url)
    if not playlist_url:
        res_obj['status'] = 'error'
        res_obj['msg'] = "Empty playlist URL"
        res = make_response(json.JSONEncoder().encode(res_obj), 400)
        res.headers.add('Content-type', 'application/json')
        return res
    try:
        """ playlist = Playlist(playlist_url)
        videos = []
        for url in playlist.video_urls:
            print(url)
            videos.append(url)
        if not videos:
            res_obj['status'] = 'error'
            res_obj['msg'] = "Playlist is empty"
            res = make_response(json.JSONEncoder().encode(res_obj), 400)
            res.headers.add('Content-type', 'application/json')
            return res
        yturls = ",".join(videos)
        print(yturls)
        filesObj, errors = downloadUrls(videos, dir_path)  """
        ytd = YtdlpYtd(playlist_url)
        filesObj, errors = ytd.downloadAudioPlaylist(playlist_url, dir_path)
        if len(filesObj) == 0 and len(errors) == 0:
            return redirect(url_for('index', error_message="Playlist is empty"))
        print(filesObj)
        print(errors)
        res_obj['status'] = 'success'
        res_obj['data'] = filesObj
        res_obj['errors'] = errors
        res = make_response(json.JSONEncoder().encode(res_obj), 200)
        res.headers.add('Content-type', 'application/json')
        return res
    except Exception as e:
        import traceback
        traceback.print_exc()
        res_obj['status'] = 'error'
        res_obj['msg'] = traceback.format_exc()
        res = make_response(json.JSONEncoder().encode(res_obj), 500)
        res.headers.add('Content-type', 'application/json')
        return res
    

@app.route('/return-files/')
def return_files():
    filepath = request.args.get('filepath')
    filename = request.args.get('filename')
    try:
        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        return str(e)
    
def downloadUrls(yturls, dir_path = "download"):
    filesObj = {}
    errors = []
    for yturl in yturls:
        if yturl == '':
            continue
        try:
            """ yt = YouTube(yturl)
            audio = yt.streams.filter(only_audio=True).first()
            file_name = secure_filename(yt._title) + ".mp3"
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)            
            out_file = dir_path +"/" + file_name
            audio.download(output_path=".", filename=out_file, skip_existing=False)
            file_name = yt._title + ".mp3"
            filesObj[file_name] = out_file """
            ytd = YtdlpYtd(yturl)
            filesObj, errors = ytd.downloadAudioFiles([yturl], dir_path)
        except Exception as e:
            errors.append(yturl)
            continue

    return filesObj, errors

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3001)
