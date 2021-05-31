# chu
File uploader using python, flask and uwsgi. Based on https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/

# Features
- Purges metadata (except colour profile, orientation).
- Saves ups space by losslessly compressing png and other files through [optipng](http://optipng.sourceforge.net/).
- Integrates [Dropbox's Lepton](https://github.com/dropbox/lepton) to losslessly compress JPEGs and save ~22% of space.
- Random URL/filename through temp files (unless requested otherwise; then it secures the requested filename).
- Predefined max size limit for each upload.
- Restricted to only allow certain extensions.
- Authentication required (include password in curl request).
- Returns the URL pointing to the file uploaded.

# Todo
- Remove hardcoded variables 
