# coding: utf-8
import os
import subprocess
import re
import logging
from flask.ext.scrypt import check_password_hash
from tempfile import mkstemp
from flask import Flask, request, redirect, url_for, abort, make_response
from werkzeug import secure_filename

UPLOAD_FOLDER = '/home/welpo/chu/uploads'

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webm',
                          'mp4', 'zip', 'rar', 'doc', 'docx', 'flac', 'mp3',
                          'bmp', 'pnm', 'tiff', '3gp', 'f4v', 'm4a', 'm4p',
                          'm4v', 'mov', 'psd', 'tiff', 'tif', 'mkv', 'deb',
                          'ogg', 'sh', 'aiff', 'svg', 'dmg'])

OPTIPNG_EXTENSIONS = set(['png', 'bmp', 'gif', 'pnm', 'tiff'])

PURGE_EXTENSIONS = set(['3gp', 'f4v', 'm4a', 'm4p', 'pdf', 'gif', 'jpg', 'jpeg',
                        'm4v', 'mov', 'mp4', 'psd', 'tiff', 'tif', 'png'])

# Files that modern browsers should be able to show on the browser without the need to download them
STREAMABLE_EXTENSIONS = set(['png', 'bmp', 'gif', 'tiff', 'mov', 'mp4', '3gp',
                             'jpg', 'jpeg', 'ogg', 'mp3', 'm4a', 'pdf', 'gif',
                             'txt', 'webm'])


# Salt and password_hash generated with flask.ext.scrypt's generate_random_salt and generate_password_hash
SALT = 'ByLHJ1hT8KpidMQHilH4can0evXJ8LS0oTnDXsWLIVjls5E+N5NXm39mB/0xuchRXonasEXHRmixWV1HVADtWQ=='
PASSWORD_HASH = 'Nk/MQ85UMKSrLLzk0PgEJo6CzI+mLvKCsXeINgg69oz87BOC7qoRcmWc3tFp80b3iy7R9K/HyFgaVQLthZEzIQ=='

app = Flask(__name__)
app.debug = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # First number after equals sign is max filesize in MiB


def allowed_file(filename):
    # Allow certain extensions as well as extensionless files
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS) or not '.' in filename


def postprocess(extension, output):
    # Remove metadata from files (images and videos)
    if extension.lower() in PURGE_EXTENSIONS:
        app.logger.info('Attempting exiftool purge')
        subprocess.call(["exiftool", "-overwrite_original", "-all=", "-tagsfromfile", "@", "-Orientation",  output])

    # Optimise png, tiff...
    if extension.lower() in OPTIPNG_EXTENSIONS:
        app.logger.info('Optimising PNG size with optipng')
        subprocess.call(["optipng", output])

    # Use lepton to compress JPG files
    if extension.lower() in ('jpg', 'jpeg'):
        # We need the extensionless name to compare it to the .lep
        filename_without_extension = output.rsplit('.', 1)[0]
        app.logger.info('Compressing JPG with Lepton')
        subprocess.call(["/home/welpo/bin/lepton", output])
        # Check if .lep file was successfully created (lepton will create a 0 bit file even if it fails)
        if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], filename_without_extension + '.lep')) and os.stat(os.path.join(app.config['UPLOAD_FOLDER'], filename_without_extension + '.lep')) != 0:
            # Delete the JPG
            os.remove(output)
        else:
            app.logger.error('No matching .lep found, returning .jpg')


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check whether or not the user is allowed
        password = request.form.get('password')
        if not check_password_hash(password, PASSWORD_HASH, SALT):
            return abort(405)
        # Get info from the POST request
        file = request.files['file']
        # Use .get('field_name') instead of 'request.form['field_name'] to make it optional: It returns
        # None instead of KeyError when the field is not sent
        custom_extension = request.form.get('custom_extension')
        preserve_filename = request.form.get('preserve_filename')
        custom_filename = request.form.get('custom_filename')
        do_not_redirect = request.form.get('do_not_redirect')

        if file and (allowed_file(file.filename) or custom_extension):
            if custom_extension in ALLOWED_EXTENSIONS:
                extension = custom_extension
            else:
                if re.search(r'\..', file.filename):
                    extension = file.filename.rsplit('.', 1)[1]
                # This adds .txt extension to extensionless files
                else:
                    extension = 'txt'

            # Either create random name or keep the one sent, after securing it
            if custom_filename:
                filename = secure_filename(custom_filename) + "." + extension
            elif preserve_filename:
                filename = secure_filename(file.filename)
                output = (os.path.join(app.config['UPLOAD_FOLDER'], filename))
                # If output name already exists, create a temporary file, prepending the random
                # string and using the original name as a suffix (preceded by an underscore)
                if os.path.exists(output):
                    output = mkstemp(prefix="", dir=app.config['UPLOAD_FOLDER'],
                                     suffix="_" + filename)[1]
                    file.save(output)
                    filename = os.path.basename(output)
                else:
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                # Create temp file safely and store its path
                output = mkstemp(suffix="." + extension,
                                 dir=app.config['UPLOAD_FOLDER'], prefix="")[1]
                filename = os.path.basename(output)
                file.save(output)

            # Optimise png, tiff etc, remove metadata from files (images and videos) and compress JPGs
            postprocess(extension, output)

            if do_not_redirect:
                # Return the URL of the uploaded file in plain text
                # app.logger.info('do_not_redirect is defined')
                full_url =  str(request.base_url) + str(filename) + ''
                return full_url.replace(" ", "")
            else:
                # If a modern browser should be able to display the file, redirect to it
                # app.logger.info('do_not_redirect undefined')
                if extension.lower() in STREAMABLE_EXTENSIONS:
                    return redirect(url_for('download_file',
                                            filename=filename))
        else:
            return abort(403)

    return '''
<!doctype html>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
<meta charset="utf-8">
<link rel="icon"
type="favicon-icon"
href="https://osc.pizza/sponge.ico">
<meta name="robots" content="noindex, noimageindex, nofollow">
<title>chu~</title>
<div align=center><h1>こんにちは！</h1>
<img src=https://osc.pizza/main.gif alt=3,14 /></div>
'''

from flask import send_from_directory


@app.route('/<filename>')
def download_file(filename):
    # Get the extension of the file requested as well as the extensionless name
    extension = filename.rsplit('.', 1)[1]
    filename_without_extension = filename.rsplit('.', 1)[0]

    # If it's a jpg, try to find the .lep that matches the name and stream that into the browser
    if extension == 'jpg' or extension == 'jpeg':
        app.logger.info('JPG file requested, attempting to find matching .lep for "' +
                        filename + '"')
        # The file we will be looking for (same name, just different extension)
        matching_lep = (os.path.join(app.config['UPLOAD_FOLDER'],
                                     filename_without_extension + '.lep'))

        # See if the .lep file exists. If it does, call lepton to process it
        if os.path.isfile(matching_lep):
            app.logger.info('Found matching file: ' + matching_lep)
            args = ['/home/welpo/bin/lepton', '-']
            with open(matching_lep, 'r') as inf:
                proc = subprocess.Popen(args, stdout=subprocess.PIPE, stdin=inf)
                # output = proc.stdout.read()
                output = subprocess.Popen.communicate(proc)
                proc.wait()
                app.logger.info('Lepton finished processing ' + filename)
            response = make_response(output)
            # Set the proper JPG headers to avoid sending it as octet-stream
            response.headers.set('Content-Type', 'image/jpeg')
            return response

    return send_from_directory(app.config['UPLOAD_FOLDER'],
                           filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
