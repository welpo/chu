# chu
A file uploader built with Python, Flask, and uWSGI, based on https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/

## Features
- Metadata Purging: Removes metadata from uploaded files (except color profile and orientation).
- Space Optimization: Losslessly compresses PNG and other file formats using [optipng](http://optipng.sourceforge.net/).
- JPEG Compression: Integrates [Dropbox's Lepton](https://github.com/dropbox/lepton) for lossless JPEG compression, saving approximately 22% of space.
- Filename Handling: Generates random URL/filenames using temporary files, or secures user-requested filenames if provided.
- Upload Size Limit: Enforces a predefined maximum size limit for each uploaded file.
- Extension Control: Restricts uploads to only allow specific file extensions.
- Authentication: Requires a password to be included in the cURL request for uploading files.
- URL Response: Returns the URL pointing to the successfully uploaded file.

## Dependencies

- Python 3
- Flask
- uWSGI
- [optipng](https://optipng.sourceforge.net/)
- [Dropbox's Lepton](https://github.com/dropbox/lepton)

## License

This code is licensed under the GNU General Public License version 3.
