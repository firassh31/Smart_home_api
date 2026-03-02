from flask import Flask, render_template
from routes.device_routes import device_bp
from helper import DeviceManager
from patterns import Observer

# Define External Services (Observers) 
class MobileAppService(Observer):
    """
    Simulates a separate mobile microservice. 
    It listens for updates and sends 'push notifications'.
    """
    def update(self, device_id: str, new_status: str):
        print(f"[Mobile Push]: Device {device_id} was turned {new_status.upper()}!")


# Initialize the Web Server 
app = Flask(__name__)

# Register the API Blueprint for all /devices routes
app.register_blueprint(device_bp, url_prefix='/devices')

# Frontend Route
@app.route('/')
def home():
    return render_template('index.html')


#  Application Bootstrap
if __name__ == '__main__':
    print("\n🚀 Booting up Smart Home API Server...")
    
    # Initialize the Singleton Manager
    manager = DeviceManager()
    
    # Create observers and attach them to the manager
    mobile_service = MobileAppService()
    manager.add_observer(mobile_service)
    print("✅ Observers attached and listening.")
    
    # Start the server
    print("🌐 Server running on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)