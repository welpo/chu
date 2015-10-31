# coding: utf-8
# TODO: rmm app, local sends to server (just call rmm and send output like uguu, plaintext "Reminder set to ..."
# TODO: Require private key thingy/password. user (me) sends field pass=_____ and the SHA256 of that gets compared to the one stored here, so that only one key/person can use it (could do the same for remote nani, a bit more secure)
# TODO: Make local chu app allow input from nano etc., like nani can
import os
import subprocess
from tempfile import mkstemp
from flask import Flask, request, redirect, url_for
from werkzeug import secure_filename

UPLOAD_FOLDER = '/home/welpo/chu/uploads'

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webm',
                          'mp4', 'zip', 'rar', 'doc', 'docx', 'flac', 'mp3',
                          'bmp', 'pnm', 'tiff', '3gp', 'f4v', 'm4a', 'm4p',
                          'm4v', 'mov', 'psd', 'tiff', 'tif', 'mkv', 'deb',
                          'ogg', 'sh'])

OPTIPNG_EXTENSIONS = set(['png', 'bmp', 'gif', 'pnm', 'tiff'])

PURGE_EXTENSIONS = set(['3gp', 'f4v', 'm4a', 'm4p', 'pdf', 'gif', 'jpg', 'jpeg',
                        'm4v', 'mov', 'mp4', 'psd', 'tiff', 'tif', 'png'])

app = Flask(__name__)
app.debug = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # First number after equals sign is max filesize in MiB


def allowed_file(filename):
    # Allow certain extensions as well as extensionless files
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS) or not '.' in filename


def postprocess(extension, output):
    # Optimise png, tiff...
    if extension.lower() in OPTIPNG_EXTENSIONS:
        subprocess.call(["optipng", output])
    # Remove metadata from files (images and videos)
    if extension.lower() in PURGE_EXTENSIONS:
        subprocess.call(["exiftool", "-overwrite_original", "-all=", output])


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Get info from the POST request
        try:
            file = request.files['file']
        except:
            return '''<html>
<head><title>405 Not Allowed</title></head>
<body bgcolor="white">
<center><h1>405 Not Allowed</h1></center>
<hr><center>nginx</center>
</body>
</html>'''
        # Use .get('field_name') instead of 'request.form['field_name'] to make it optional: It returns
        # None instead of KeyError when the field is not sent
        custom_extension = request.form.get('custom_extension')
        preserve_filename = request.form.get('preserve_filename')
        custom_filename = request.form.get('custom_filename')

        if file and (allowed_file(file.filename) or custom_extension):
            if custom_extension in ALLOWED_EXTENSIONS:
                extension = custom_extension
            else:
                try:
                    extension = file.filename.rsplit('.', 1)[1]
                # This adds .txt extension to extensionless files
                except:
                    extension = 'txt'

            # Either create random name or keep the one sent, after securing it
            if preserve_filename or custom_filename:
                if custom_filename:
                    filename = secure_filename(custom_filename) + "." + extension
                else:
                    filename = secure_filename(file.filename)
                output = (os.path.join(app.config['UPLOAD_FOLDER'], filename))
                # If output name already exists, create a temporary file with prepending the random
                # string and using the original name as a suffix (preceded by an underscore)
                if os.path.exists(output):
                    output = mkstemp(prefix="", dir=app.config['UPLOAD_FOLDER'],
                                     suffix="_" + filename)[1]
                    file.save(output)
                    filename = os.path.basename(output)
                else:
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            elif custom_filename:
                filename = secure_filename(custom_filename)
            else:
                # Create temp file safely and store its path
                output = mkstemp(suffix="." + extension,
                                 dir=app.config['UPLOAD_FOLDER'], prefix="")[1]
                filename = os.path.basename(output)
                file.save(output)

            # Optimise png, tiff etc and remove metadata from files (images and videos)
            postprocess(extension, output)
            return redirect(url_for('uploaded_file',
                                    filename=filename))

    return '''
<!doctype html>
<link rel="icon"
type="favicon-icon"
href="https://welpo.me/sponge.ico">
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
<meta charset="utf-8">
<title>chu~</title>
<div align=center><h1>こんにちは！</h1>
<img src=/main.gif alt=3,14 /></div>
'''

from flask import send_from_directory


@app.route('/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
