from flask import Flask, render_template, Response, jsonify, request, redirect, url_for, session, make_response, send_from_directory, abort
from flask_socketio import SocketIO
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import subprocess
import webbrowser
import threading
import gridfs
import base64

app = Flask(__name__)
app.secret_key = 'my_secure_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

def open_browser():
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    subprocess.Popen([chrome_path, "http://localhost:5000"])

@app.route('/')
def loginpage():
    return render_template('loginpage.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Example user credentials
    valid_users = {
        "admin": {"password": "adm123", "location": "Nagpur"}
    }

    if username in valid_users and valid_users[username]["password"] == password:
        session['username'] = username
        session['location'] = valid_users[username]["location"]  # Store location

        return jsonify({"status": "success", "redirect": url_for('homepage')})
    else:
        return jsonify({"status": "error", "message": "INVALID CREDENTIALS!! PLEASE TRY AGAIN WITH VALID CREDENTIALS."})

@app.route('/homepage')
def homepage():
    if 'username' not in session:
        return redirect(url_for('loginpage'))
    
    response = make_response(render_template(
        'homepage.html',
        username=session['username'],
        location=session['location']
    ))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/pressanalysis')
def pressanalysis():
    if 'username' not in session:
        return redirect(url_for('loginpage'))
        
    response = make_response(render_template('pressanalysis.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

from flask import Response, jsonify
from pymongo import MongoClient

import base64
from flask import jsonify, Response

from flask import Flask, jsonify
from pymongo import MongoClient
import gridfs
import io, zipfile, base64
from flask import jsonify
from pymongo import MongoClient
import gridfs
import zipfile
import io
import os
import base64

from flask import jsonify
from pymongo import MongoClient
import gridfs
import io, zipfile, base64, os

# @app.route('/heatmap/<image_id>')
# def serve_heatmap(image_id):
#     print(f"🔍 Fetching heatmap for: {image_id}")
#     MONGO_URI = "mongodb+srv://khduser:khduser@khddemo.s8c1q.mongodb.net/?retryWrites=true&w=majority&appName=KHDDemo"

#     try:
#         # Step 1: Connect to MongoDB and GridFS
#         client = MongoClient(MONGO_URI)
#         db = client["your_db"]
#         fs = gridfs.GridFS(db)
#         meta_collection = db["svg_metadata"]

#         # Step 2: Fetch metadata
#         doc = meta_collection.find_one({"_id": image_id})
#         if not doc or "zip_file_id" not in doc:
#             return jsonify({"error": f"No ZIP reference found for ID: {image_id}"}), 404

#         # Step 3: Read ZIP from GridFS
#         zip_file_id = doc["zip_file_id"]
#         zip_stream = fs.get(zip_file_id)
#         zip_bytes = zip_stream.read()

#         # Step 4: Unzip and classify contents
#         zip_buffer = io.BytesIO(zip_bytes)
#         file_map = {}

#         with zipfile.ZipFile(zip_buffer, 'r') as zipf:
#             print("📦 ZIP Contents:", zipf.namelist())

#             for file_name in zipf.namelist():
#                 with zipf.open(file_name) as f:
#                     content = f.read()
#                     print(f"➤ Processing file: {file_name} | Size: {len(content)} bytes")

#                     name = os.path.basename(file_name).strip()
#                     name_key = os.path.splitext(name)[0].lower()

#                     # Detect type by content if no extension
#                     if content.strip().startswith(b'<svg'):
#                         try:
#                             file_map[name_key] = content.decode('utf-8')
#                             print(f"✅ Treated as SVG: {name_key}")
#                         except Exception as e:
#                             file_map[name_key] = f"Error decoding SVG: {str(e)}"
#                     elif content[:4] == b'\x89PNG':  # PNG signature
#                         b64_img = base64.b64encode(content).decode('utf-8')
#                         file_map[name_key] = f"data:image/png;base64,{b64_img}"
#                         print(f"🖼️ Treated as PNG: {name_key}")
#                     else:
#                         file_map[name_key] = "Unsupported file type"
#                         print(f"❌ Unknown file type: {name_key}")

#         return jsonify(file_map)

#     except Exception as e:
#         return jsonify({"error": f"Error fetching or extracting ZIP: {str(e)}"}), 500


from bson.objectid import ObjectId
import traceback

@app.route('/heatmap/<image_id>')
def serve_heatmap(image_id):
    print(f"🔍 Fetching heatmap for: {image_id}")

    # MONGO_URI = "mongodb+srv://khduser:khduser@khddemo.s8c1q.mongodb.net/?retryWrites=true&w=majority&appName=KHDDemo"
    MONGO_URI = "mongodb+srv://khduser:khduser@cluster0.wtu9c.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

    try:
        client = MongoClient(MONGO_URI)

        # ✅ FIX DB NAME
        # db = client["cluster0"]
        db = client["your_db"]
        

        fs = gridfs.GridFS(db)
        meta_collection = db["svg_metadata"]

        # ✅ FIX QUERY
        doc = meta_collection.find_one({"_id": image_id})

        if not doc:
            return jsonify({"error": f"No document found for ID: {image_id}"}), 404

        if "zip_file_id" not in doc:
            return jsonify({"error": "zip_file_id missing in document"}), 500

        zip_file_id = doc["zip_file_id"]

        # ✅ FIX ObjectId
        zip_stream = fs.get(ObjectId(zip_file_id))
        zip_bytes = zip_stream.read()

        zip_buffer = io.BytesIO(zip_bytes)
        file_map = {}

        with zipfile.ZipFile(zip_buffer, 'r') as zipf:
            print("📦 ZIP Contents:", zipf.namelist())

            for file_name in zipf.namelist():
                with zipf.open(file_name) as f:
                    content = f.read()

                    name = os.path.basename(file_name).strip()
                    name_key = os.path.splitext(name)[0].lower()

                    if content.strip().startswith(b'<svg'):
                        file_map[name_key] = content.decode('utf-8')

                    elif content[:4] == b'\x89PNG':
                        b64_img = base64.b64encode(content).decode('utf-8')
                        file_map[name_key] = f"data:image/png;base64,{b64_img}"

                    else:
                        file_map[name_key] = "Unsupported file type"

        return jsonify(file_map)

    except Exception as e:
        print("❌ ERROR:", str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('location', None)
    return redirect(url_for('loginpage'))

if __name__ == '__main__':
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Thread(target=open_browser, daemon=True).start()

    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)

