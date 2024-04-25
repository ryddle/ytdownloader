from pytube import YouTube
import os
# https://www.youtube.com/watch?v=Ckom3gf57Yw
yt = YouTube(str(input("Enter the URL of the video you want to download: \n>>")))
audio = yt.streams.filter(only_audio = True).first()
out_file = 'audio.mp4'
audio.download(output_path = '.', filename = out_file)
print("Enter the destination (leave blank for current directory)")
new_file =  yt._title + '.mp3';#str(input(">>")) or '.'
#base, ext = os.path.splitext(out_file)
#new_file = base + '.mp3'
os.rename(out_file, new_file)
print(yt.title + " has been successfully downloaded in .mp3 format.")