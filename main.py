from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

app = FastAPI()

sensor_db = []

class SensorData(BaseModel):
    device_id: str = Field(..., example="sensor_1")
    temperature: float = Field(..., ge=-50, le=100)
    humidity: float = Field(..., ge=0, le=100)
    timestamp: datetime = None

@app.post("/sensor_data")
async def post_sensor_data(data: SensorData):
    if not data.timestamp:
        data.timestamp = datetime.utcnow()
    sensor_db.append(data)
    return {"message": "Sensor data recorded", "data": data}

@app.get("/sensor_data")
async def get_sensor_data(device_id: str):
    results = [d for d in sensor_db if d.device_id == device_id]
    if not results:
        raise HTTPException(status_code=404, detail="No data found for device")
    return results
# PUT - Update sensor data (latest entry only)
@app.put("/sensor_data/{device_id}")
def update_sensor_data(device_id: str, updated_data: SensorData):
    for i in range(len(sensor_db)-1, -1, -1):  # search from end (latest first)
        if sensor_db[i].device_id == device_id:
            updated_data.timestamp = datetime.utcnow()
            sensor_db[i] = updated_data
            return {"message": "Sensor data updated", "data": updated_data}
    raise HTTPException(status_code=404, detail="Device not found")

# DELETE - Delete sensor data by device_id
@app.delete("/sensor_data/{device_id}")
def delete_sensor_data(device_id: str):
    global sensor_db
    new_db = [entry for entry in sensor_db if entry.device_id != device_id]
    if len(new_db) == len(sensor_db):
        raise HTTPException(status_code=404, detail="Device not found")
    sensor_db = new_db
    return {"message": f"Data for {device_id} deleted"}