from fastapi import FastAPI, UploadFile, File
import cv2
import numpy as np
from ultralytics import YOLO
from kafka import KafkaProducer
import json

app = FastAPI()
model = YOLO("yolo11n.pt")  # Load pre-trained YOLOv11 model

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

@app.post("/detect")
async def detect_intruder(file: UploadFile = File(...)):
    contents = await file.read()
    np_image = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)
    
    results = model(image)  # Run YOLOv11
    intruder_detected = False
    confidence = 0

    for r in results:
        for box in r.boxes:
            class_id = int(box.cls[0])
            conf = float(box.conf[0])
            if class_id == 0 and conf > 0.6:  # Detecting a "person"
                intruder_detected = True
                confidence = conf

    response = {
        "intruder_detected": intruder_detected,
        "confidence": confidence,
        "image_url": "http://server/image.jpg" if intruder_detected else None
    }

    if intruder_detected:
        producer.send("intruder-detection", response)

    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
