# Using RaspberryPi Zero 2W, make an autonomous vehicle
details refer to _presentation.pdf_

## 1. Problem

Here is the track and obstacles to address.
![image](https://github.com/user-attachments/assets/0bc64f11-1a61-4549-962b-6df121952a4d)
#### 1. start point
#### 2-3. children zone (speed limit, dynamic obstacles in children zone)
#### 4. static obstacles
#### 5-6. tunnel
#### 7-8. hill
#### 9. end of full record measurement
#### 10. traffic lights



## 2. Solution

### 1) Lane Detection
We took the edge detection and sliding window methods.
Set ROI first, and apply sobel filter.
To command direction information to the motor, we extracted deviation percent using x-coordinate values of the line property.
Through several test driving data, a function was derived using linear interpolation between the deviation value and the angle of the servomotor.

### 2) Object Detection (FAILED)
To handle both static and dynamic obstacles, we planned to use artificial intelligence learning model. We trained YOLOv8n with custom dataset from test driving data and pictures of obstacles we took ourselves.
(Here's link for custom training in colab: https://colab.research.google.com/github/roboflow-ai/yolov5-custom-training-tutorial/blob/main/yolov5-custom-training.ipynb)
However, this model(_best_v8n_x100_final.pt_) was too heavy to run on RaspberryPi Zero 2W and also too slow even if we running on a PC using socket.

### 3) Ultrasonic Sensor
Therefore, we decided to use two ultrasonic sensors on the front and top to avoid obstacles.
The top sensor detects the tunnel and turns on the LED.
The front sensor detects an obstacle directly in front, making the vehicle stop, and then change lanes if an obstacle is detected after a certain period of time (static obstacle).



## 3. Code
You need a PC and a RaspberryPi to run this codes.
#### _jamline_light.py_ is for PC
#### _realnewjamline_final.py_ is for RaspberryPi
