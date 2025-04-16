from flask import Flask, render_template, Response, jsonify, request, redirect, url_for, session, make_response, send_from_directory, abort
from flask_socketio import SocketIO
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import subprocess
import webbrowser
import threading

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

@app.route('/heatmap/<image_id>')
def serve_heatmap(image_id):
    """
    Endpoint to serve the SVG from MongoDB if it exists.
    Expects image_id = location_rollerNumber (e.g. nagpur_1)
    """
    MONGO_URI = "mongodb+srv://khduser:khduser@khddemo.s8c1q.mongodb.net/?retryWrites=true&w=majority&appName=KHDDemo"
    client = MongoClient(MONGO_URI)
    db = client["heatmap_db"]
    collection = db["heatmaps"]
    
    try:
        doc = collection.find_one({"_id": image_id})
        #print(image_id)
        if doc:
            print("Document found:")
        else:
            print("Document not found for pune_1")

        #print(image_id)
        if doc and 'svg' in doc:
            svg_data = doc['svg']
            response = Response(svg_data, mimetype='image/svg+xml')
            return response
        else:
            return jsonify({"error": "SVG not found for selected roller and location"}), 404
    except Exception as e:
        return jsonify({"error": f"Error fetching SVG: {str(e)}"}), 500


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('location', None)
    return redirect(url_for('loginpage'))

if __name__ == '__main__':
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Thread(target=open_browser, daemon=True).start()

    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)

