require('dotenv').config(); // טעינת המשתנים מהקובץ .env
const { MongoClient } = require('mongodb');

async function testConnection() {
    const uri = process.env.MONGODB_URI;
    const client = new MongoClient(uri);

    try {
        // 1. התחברות
        await client.connect();
        console.log("✅ Connected to MongoDB via Node.js!");

        // 2. בחירת מסד הנתונים והאוסף (אותם שמות כמו בפייתון)
        const database = client.db("smart_home_db");
        const collection = database.collection("devices");

        // 3. שליפת המכשיר הראשון שמצליחים למצוא
        const device = await collection.findOne({});

        if (device) {
            console.log("👀 Node.js found a device created by Python:");
            console.log(device);
        } else {
            console.log("🤷‍♂️ Connected, but no devices found.");
        }

    } catch (e) {
        console.error("❌ Error:", e);
    } finally {
        await client.close();
    }
}

testConnection();