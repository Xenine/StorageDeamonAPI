import os
import hashlib
from flask import Flask 
from flask import request, make_response, send_from_directory

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16mb max of uploaded files
uploads_dir = os.path.join(app.instance_path, 'store')
os.makedirs(uploads_dir, exist_ok=True)

@app.route('/', methods=['POST'])
def upload_file():
# Can be checked in the terminal with cURL e.g.:
# curl -X POST --form file=@path-to-file http://localhost:5000/
    file = request.files['file']
    filename = file.filename
    hash_object = hashlib.sha1(filename.encode())
    filename_hash = hash_object.hexdigest()
    extra_uploads_dir = os.path.join(uploads_dir, filename_hash[0:2])
    os.makedirs(extra_uploads_dir, exist_ok=True)
    file.save(os.path.join(extra_uploads_dir, filename_hash))
    # If you need to save files with extensions so that you can easily open them (insteed of previos line):
    # extension = filename.rsplit('.', 1)[1] 
    # file.save(os.path.join(extra_uploads_dir, f"{filename_hash}.{extension}"))
    return make_response(filename_hash)


@app.route('/<filename>', methods=['GET'])
def download_file(filename):
# Can be checked in the terminal with cURL e.g.:
# curl -X GET -O http://localhost:5000/hash-filename
    download_path_file = os.path.join(uploads_dir, filename[0:2])
    if os.path.exists(os.path.join(download_path_file, filename)):
        return send_from_directory(download_path_file, filename)
    return make_response("No such file!")
    
@app.route('/<filename>', methods=['DELETE'])
def delete_file(filename):
# Can be checked in the terminal with cURL e.g.:
# curl -X DELETE http://localhost:5000/hash-filename
    delete_path_file = os.path.join(uploads_dir, filename[0:2], filename)
    if os.path.exists(delete_path_file):
        os.remove(delete_path_file)
        return make_response("Successfully deleted!")
    return make_response("No such file!")

@app.errorhandler(400)
def not_found_error(error):
    return make_response("Something is wrong with your file! Check the path is correct.\nShould be: --form file=@root-to-file/file.*"), 400

@app.errorhandler(404)
def not_found_error(error):
    return make_response("Only the root domain can be accessed!"), 404

@app.errorhandler(405)
def not_found_error(error):
    return make_response("Only the root domain can be accessed!"), 405

@app.errorhandler(413)
def not_found_error(error):
    return make_response("File is too big!"), 413

if __name__ == '__main__':
    app.run()