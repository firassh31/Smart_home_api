# 🏠 Smart Home API (Microservices Architecture)

A scalable, microservices-based Smart Home API built to manage and monitor IoT devices. The system utilizes a Python/Flask backend, a JavaScript frontend, and is designed to integrate with additional Java/Node.js microservices. 

It heavily leverages Object-Oriented Programming (OOP) principles and structural design patterns (Singleton, Observer) to maintain a clean, decoupled, and efficient codebase.

## 🏗️ Architecture & Tech Stack
* **Backend:** Python 3, Flask
* **Database:** MongoDB Atlas (Cloud NoSQL)
* **Frontend:** Vanilla JavaScript, HTML, CSS
* **Design Patterns:** Singleton (Database Connection), Observer (Device State Management)
* **Security:** `python-dotenv` for environment variable management, CORS policies configured for microservice communication.

## 🚀 Recent Updates & Optimizations
* **Cloud Migration:** Transitioned from a local SQLite database to a fully managed MongoDB Atlas cluster.
* **Query Optimization:** Replaced $O(N)$ collection scans with $O(1)$ `ObjectId` lookups for CRUD operations.
* **Database Indexing:** Implemented a B-tree index on the `room` field to drastically speed up sorting and data grouping at the database level.
* **Resilience:** Added comprehensive `try...except` error handling to gracefully manage database timeouts or network drops without crashing the server.

---

## ⚙️ How to Run the Project

### 1. Prerequisites
* Python 3.x installed
* A MongoDB Atlas Cluster (Free Tier is sufficient)

### 2. Installation & Setup
Clone the repository and navigate into the project folder:
```bash
git clone <your-repository-url>
cd Smart_home_api
```
### 3. Environment Variables (Important!)
``` bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

install the required dependencies:

pip install -r requirements.txt

For security, database credentials are not tracked in version control. You must create a .env file in the root directory of the project and add your MongoDB connection string:

MONGO_URI="mongodb+srv://<username>:<password>@<your-cluster-address>/?retryWrites=true&w=majority"
```
### 4. Start the Server

Run the Flask application:

``` Bash
python app.py
The server will start running on http://127.0.0.1:5000. You can now open your frontend index.html file in a browser to interact with the API!
```

## 📡 API Endpoints

| HTTP Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/devices/` | Fetches a list of all devices, sorted automatically by room and name. |
| **POST** | `/devices/` | Creates a new smart device in the database. |
| **PUT** | `/devices/<id>/status` | Toggles the operational status (on/off) of a specific device. |
| **DELETE** | `/devices/<id>` | Permanently removes a device using its MongoDB ObjectId. |
