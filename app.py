from flask import Flask, redirect, url_for, request, render_template, session, send_file
from pytube import YouTube, Playlist
import os

import requests

# Url video example: https://www.youtube.com/watch?v=Ckom3gf57Yw
# Url playlist example: https://www.youtube.com/playlist?list=PL9Pc5j186PM52HmjSIMRH2jU-Z21cOblb
# flask run or flask --app app.py --debug run

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    error_message = request.args.get('error_message')
    if error_message==None:
        error_message = "" 
    return render_template("index.html", error_message=error_message)


@app.route("/", methods=["POST"])
def index_post():
    yturls = list(map(str.strip, request.form["text"].split(',')))
    filesObj = downloadUrls(yturls)
    return render_template('results.html', filesObj=filesObj)

@app.route("/playlist/", methods=["POST"])
def playlist():
    playlist_url = request.form.get("playlist_url")
    print(playlist_url)
    if not playlist_url:
        return "Empty playlist URL", 400
    try:
        playlist = Playlist(playlist_url)
        videos = []
        for url in playlist.video_urls:
            print(url)
            videos.append(url)
        if not videos:
            return redirect(url_for('index', error_message="Playlist is empty"))
        yturls = ",".join(videos)
        print(yturls)
        filesObj, errors = downloadUrls(videos) 
        print(filesObj)
        print(errors)
        return render_template('results.html', filesObj=filesObj, errors=errors)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return str(e), 500
    

@app.route('/return-files/')
def return_files():
    filepath = request.args.get('filepath')
    filename = request.args.get('filename')
    try:
        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        return str(e)
    
def downloadUrls(yturls):
    filesObj = {}
    errors = []
    for yturl in yturls:
        if yturl == '':
            continue
        try:
            yt = YouTube(yturl)
            audio = yt.streams.filter(only_audio=True).first()
            file_name = yt._title + ".mp3"
            if not os.path.exists('download'):
                os.makedirs('download')            
            out_file = "download/" + file_name
            audio.download(output_path=".", filename=out_file, skip_existing=False)
            file_name = yt._title + ".mp3"
            filesObj[file_name] = out_file
        except Exception as e:
            errors.append(yturl)
            continue

    return filesObj, errors