import cv2

camera = cv2.VideoCapture(0)  # Use smartphone's camera

while True:
    ret, frame = camera.read()
    if not ret:
        break
    cv2.imshow("Smartphone CCTV", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()