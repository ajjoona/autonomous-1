![header](https://capsule-render.vercel.app/api?type=venom&color=gradient&customColorList=12&width=1000&height=200&text=AUTONOMOUS%20ver.1&fontSize=54&fontAlignY=42&desc=Using%20RaspberryPi%20Zero%202W&descSize=22&descAlignY=62&stroke=0072ff)

### All the details refer to _presentation.pdf_
<br>
<p align="center">
<a href="https://youtu.be/U8neLkONT78?t=11637"><img src="https://github.com/user-attachments/assets/d4757f2f-fb76-4cde-954e-19eea2649775" width="70%"></a>
</p>


## 1. Problem

Here is the track and obstacles to address.
<p align="center">
  <img src="https://github.com/user-attachments/assets/0bc64f11-1a61-4549-962b-6df121952a4d" width=900>
</p>
<p>1. start point</p>
<p>2-3. children zone (speed limit, dynamic obstacles in children zone)</p>
<p>4. static obstacles</p>
<p>5-6. tunnel</p>
<p>7-8. hill</p>
<p>9. end of full record measurement</p>
<p>10. traffic lights</p>
<br>


## 2. Solution
<p align="center">
  <img src="https://github.com/user-attachments/assets/e6ef68de-431b-4f6c-abd4-b1e822a95ed8" width=800>
</p>

### 1) Lane Detection
<p>
We took the edge detection and sliding window methods.
Set ROI first, and apply sobel filter.
</p><p>To command direction information to the motor, we extracted deviation percent using x-coordinate values of the line property.
Through several test driving data, a function was derived using linear interpolation between the deviation value and the angle of the servomotor.
</p>
<br>

### 2) Object Detection (FAILED)
<p>To handle both static and dynamic obstacles, we planned to use artificial intelligence learning model. We trained YOLOv8n with custom dataset from test driving data and pictures of obstacles we took ourselves.
<br>(Here's link for custom training in colab: https://colab.research.google.com/github/roboflow-ai/yolov5-custom-training-tutorial/blob/main/yolov5-custom-training.ipynb)
</p><p>
However, this model(_best_v8n_x100_final.pt_) was too heavy to run on RaspberryPi Zero 2W and also too slow even if we running on a PC using socket.
</p><br>

### 3) Ultrasonic Sensor
<p>
Therefore, we decided to use two ultrasonic sensors on the front and top to avoid obstacles.
The top sensor detects the tunnel and turns on the LED.
The front sensor detects an obstacle directly in front, making the vehicle stop, and then change lanes if an obstacle is detected after a certain period of time (static obstacle).
</p>
<br><br>

## 3. Code
You need a PC and a RaspberryPi to run this codes.
#### _jamline_light.py_ is for PC
#### _realnewjamline_final.py_ is for RaspberryPi
