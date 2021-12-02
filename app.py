from flask import Flask, render_template, send_file, url_for, redirect, request
from scripts.copy_files import copy_files
from datetime import datetime, date
import os
import gphoto2 as gp
import glob
import shutil

app = Flask(__name__)

PHOTO_DIR = os.path.expanduser(os.environ.get("PHOTO_DIR"))

@app.route('/', defaults={'debug': False})
@app.route('/<path:debug>')
def index(debug):
    return render_template('index.html', today=datetime.today().strftime('%Y-%m-%d'), debug=debug)

@app.route('/pictures')
def pictures_by_date():
    selected_date = request.args.get('selected_date')
    year = selected_date.split('-')[0]
    count = int(request.args.get('count'))
    offset = count + 10
    pictures = []
    path = os.path.join(PHOTO_DIR, year, selected_date.replace('-', '_'))
    if os.path.isdir(path):
        pictures = glob.glob(path + '/**/*.JPG', recursive=True)
        pictures.sort()
    else:
        result = copy_files(selected_date)
        if result == 0:
            return render_template('no_camera.html')
        if result == 1:
            pictures = glob.glob(path + '/**/*.JPG', recursive=True)
            pictures.sort()
    
    return render_template('pictures.html', pictures=pictures[count:offset], path=path, base_path=PHOTO_DIR, count=offset, totalCount=len(pictures))

@app.route('/download/<path:filename>')
def download_file(filename):
    path = os.path.join(PHOTO_DIR, filename) 
    return send_file(path, as_attachment=True)

@app.route('/picture/<path:filename>')
def show_picture(filename):
    try:
        path = '/pictures/' + filename 
        return render_template('picture.html', filename=filename, path=path)
    except Exception as e:
        return e

@app.route('/copy')
def copy():
    folder = '2021'
    dest = os.path.join(PHOTO_DIR, folder)
    shutil.copytree(os.path.join('/home/pi/Pictures/from_camera', folder), dest, dirs_exist_ok=True)

    return

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
