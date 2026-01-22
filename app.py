from flask import Flask, render_template
from routes.device_routes import device_bp

app = Flask(__name__)

# Register the Blueprint
app.register_blueprint(device_bp, url_prefix='/devices')

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)