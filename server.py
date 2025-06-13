from flask import Flask, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
CORS(app)

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/output_glb/<path:path>')
def serve_glb(path):
    return send_from_directory('output_glb', path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)