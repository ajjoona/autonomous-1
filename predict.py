from ultralytics import YOLO
import cv2


model = YOLO('best_v8n_x100_final.pt')
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    results = model.predict(img, conf=0.7, show=True)[0]
    names = model.names
    detected = []

    for r in results:
        for c in r.boxes.cls:
            detected.append(names[int(c)])

    #if 'car' in detected:
        #차선변경
    #    print("차량을 감지했습니다. 차선을 변경합니다.")
    #if 'school-zone' in detected:
       # isSchool
        #속도제한

    #cv2.imshow('웹캠', results.plot())
    #if cv2.waitKey(1) == ord('q'):
    #    break

cap.release()
cv2.destroyAllWindows()

