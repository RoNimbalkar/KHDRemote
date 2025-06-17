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

@app.route('/heatmap/<image_id>')
def serve_heatmap(image_id):
    print(image_id)
    MONGO_URI = "mongodb+srv://khduser:khduser@khddemo.s8c1q.mongodb.net/?retryWrites=true&w=majority&appName=KHDDemo"
    try:
        client = MongoClient(MONGO_URI)
        db = client["your_db"]
        fs = gridfs.GridFS(db)
        meta_collection = db["svg_metadata"]  # Make sure to match your insert logic

        # Fetch metadata
        doc = meta_collection.find_one({"_id": image_id})
        if not doc or "svg_ids" not in doc:
            return jsonify({"error": f"No metadata or SVG references found for ID: {image_id}"}), 404

        svg_ids = doc["svg_ids"]
        ordered_fields = [
            "svg", "svgheatmap", "linechart", "comninedgraph",
            "profile15", "profile35", "profile60", "profile80",
            "profile105", "profile125", "profile150", "profile170",
            "profile195", "profile215", "profile240", "profile260",
            "profile285", "profile305", "profile330", "profile350"
        ]

        svg_data = {}

        for index, file_id in enumerate(svg_ids):
            try:
                name = ordered_fields[index] if index < len(ordered_fields) else f"svg_{index}"

                grid_out = fs.get(file_id)
                file_data = grid_out.read()

                if file_data.strip().startswith(b'<?xml') or b'<svg' in file_data[:100]:
                    svg_data[name] = file_data.decode('utf-8')
                else:
                    b64_data = base64.b64encode(file_data).decode('utf-8')
                    svg_data[name] = f"data:image/png;base64,{b64_data}"
            except Exception as e:
                svg_data[name] = f"Error reading file: {str(e)}"

        return jsonify(svg_data)

    except Exception as e:
        return jsonify({"error": f"Error fetching SVGs: {str(e)}"}), 500

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('location', None)
    return redirect(url_for('loginpage'))

if __name__ == '__main__':
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Thread(target=open_browser, daemon=True).start()

    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)

