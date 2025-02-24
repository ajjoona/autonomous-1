import numpy as np
import cv2
import warnings
import socket
warnings.filterwarnings('ignore')

HOST = '192.168.137.139'  # 라즈베리 파이의 IP 주소로 변경 필요
PORT = 12346

cap = cv2.VideoCapture('http://192.168.137.139:8081/')

def sobel_filter(img, orient='x', thresh=(20, 100)):
    sobel = cv2.Sobel(img, cv2.CV_64F, 1, 0) if orient == 'x' else cv2.Sobel(img, cv2.CV_64F, 0, 1)
    abs_sobel = np.absolute(sobel)
    scaled_sobel = np.uint8(255 * abs_sobel / np.max(abs_sobel))
    binary_output = np.zeros_like(scaled_sobel)
    binary_output[(scaled_sobel >= thresh[0]) & (scaled_sobel <= thresh[1])] = 255
    return binary_output

def update_line(line, line_fit, prev_line, plotx, ploty):
    if len(prev_line.prevx) > 10:
        avg_line = np.mean(prev_line.prevx, axis=0)
        avg_fit = np.polyfit(ploty, avg_line, 2)
        fit_plotx = avg_fit[0] * ploty ** 2 + avg_fit[1] * ploty + avg_fit[2]
        line.current_fit = avg_fit
        line.allx, line.ally = fit_plotx, ploty
    else:
        line.current_fit = line_fit
        line.allx, line.ally = plotx, ploty
    line.startx, line.endx = line.allx[-1], line.allx[0]
    line.detected = True


while cap.isOpened():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # 라즈베리 파이와 연결
        s.connect((HOST, PORT))
    
        while True:
            ret, frame = cap.read()
            # 주행시 frame resize 생략가능
            frame = cv2.resize(frame, None, fx=1, fy=1, interpolation=cv2.INTER_AREA)
            height, width = frame.shape[:2]
            top, bot, left, right = [ 80, height-40, 10, width-20 ]
            temp = frame[top:bot, left:right, 2]

            th_sobelx = (60, 300)
            sobel_x = sobel_filter(temp, 'x', th_sobelx)
            result = sobel_x

            height, width = result.shape[:2]
            s_LTop2, s_RTop2 = [64, 0], [122, 0]
            s_LBot2, s_RBot2 = [30, 42], [155, 42]
            src = np.float32([s_LBot2, s_RBot2, s_RTop2, s_LTop2])
            dst = np.float32([[90, 0], [270, 0], [270, 360], [90, 360]])

            M = cv2.getPerspectiveTransform(src, dst)
            warp_img = cv2.warpPerspective(result, M, (360, 90), flags=cv2.INTER_LINEAR)

            
            class Line:
                def __init__(self):
                    self.prevx = []  
                    self.current_fit = [np.array([False])]  
                    self.startx = None  
                    self.endx = None 

            left_line = Line()
            right_line = Line()

            histogram = np.sum(warp_img[int(warp_img.shape[0] / 2):, :], axis=0)
            midpoint = np.intc(histogram.shape[0] / 2)

            start_leftX = np.argmax(histogram[:midpoint])
            start_rightX = np.argmax(histogram[midpoint:]) + midpoint

            num_windows = 8
            window_height = np.intc(warp_img.shape[0] / num_windows)

            nonzero = warp_img.nonzero()
            nonzeroy = np.array(nonzero[0])
            nonzerox = np.array(nonzero[1])

            current_leftX = start_leftX
            current_rightX = start_rightX

            min_num_pixel = 100
            window_margin = 48
            win_left_lane = []
            win_right_lane = []

            for window in range(num_windows):
                win_y_low = warp_img.shape[0] - (window + 1) * window_height
                win_y_high = warp_img.shape[0] - window * window_height
                margin = window_margin

                win_leftx_min, win_leftx_max = current_leftX - margin, current_leftX + margin
                win_rightx_min, win_rightx_max = current_rightX - margin, current_rightX + margin

                left_window_inds = ((nonzeroy >= win_y_low) & (nonzeroy <= win_y_high) & (nonzerox >= win_leftx_min) & (
                            nonzerox <= win_leftx_max)).nonzero()[0]
                right_window_inds = ((nonzeroy >= win_y_low) & (nonzeroy <= win_y_high) & (nonzerox >= win_rightx_min) & (
                            nonzerox <= win_rightx_max)).nonzero()[0]

                win_left_lane.append(left_window_inds)
                win_right_lane.append(right_window_inds)

                if len(left_window_inds) > min_num_pixel:
                    current_leftX = np.intc(np.mean(nonzerox[left_window_inds]))
                if len(right_window_inds) > min_num_pixel:
                    current_rightX = np.intc(np.mean(nonzerox[right_window_inds]))

            win_left_lane = np.concatenate(win_left_lane)
            win_right_lane = np.concatenate(win_right_lane)

            leftx, lefty = nonzerox[win_left_lane], nonzeroy[win_left_lane]
            rightx, righty = nonzerox[win_right_lane], nonzeroy[win_right_lane]

            if len(lefty) > 0 and len(leftx) > 0:
                left_fit = np.polyfit(lefty, leftx, 2)
            else:
                if len(righty) > 0 and len(rightx) > 0:
                    right_fit = np.polyfit(righty, rightx, 2)
                    left_fit = right_fit - np.array([0, 0, 135])
            if len(righty) > 0 and len(rightx) > 0:
                right_fit = np.polyfit(righty, rightx, 2)
            else:
                if len(lefty) > 0 and len(leftx) > 0:
                    left_fit = np.polyfit(lefty, leftx, 2)
                    right_fit = left_fit + np.array([0, 0, 135])

            left_line.current_fit = left_fit
            right_line.current_fit = right_fit
            ploty = np.linspace(0, warp_img.shape[0] - 1, warp_img.shape[0])

            left_plotx = left_fit[0] * ploty ** 2 + left_fit[1] * ploty + left_fit[2]
            right_plotx = right_fit[0] * ploty ** 2 + right_fit[1] * ploty + right_fit[2]

            left_line.prevx.append(left_plotx)
            right_line.prevx.append(right_plotx)

            update_line(left_line, left_fit, left_line, left_plotx, ploty)
            update_line(right_line, right_fit, right_line, right_plotx, ploty)

            center_lane = (right_line.startx + left_line.startx) / 2
            lane_width = right_line.startx - left_line.startx
            center_car = warp_img.shape[1] /2
            deviation_percent = abs(center_lane - center_car) / (lane_width / 2) * 100
    
            if center_lane < center_car:
                jamangle = deviation_percent
            elif center_lane > center_car:
                jamangle = -deviation_percent
            else:
                jamangle = 0
            #print(jamangle)

            ka = 130
            ja = -100 

            kb = 120
            jb = -85

            kc = 110
            jc = -60

            kd = 100
            jd = -30 

            ke = 90
            je = 0

            kf = 80
            jf = 20

            kg = 70
            jg = 37

            kh = 60
            jh = 50

            ki = 50
            ji = 70
            
            try:
                if jamangle <= jb :
                    jangle = int((kb-ka) / (jb-ja) * jamangle + kb - (kb-ka) / (jb-ja) * jb)
                elif jb < jamangle and jamangle <= jc :
                    jangle = int((kc-kb) / (jc-jb) * jamangle + kc - (kc-kb) / (jc-jb) * jc)
                elif jc < jamangle and jamangle <= jd :
                    jangle = int((kd-kc) / (jd-jc) * jamangle + kd - (kd-kc) / (jd-jc) * jd)
                elif jd < jamangle and jamangle <= je :
                    jangle = int((ke-kd) / (je-jd) * jamangle + ke - (ke-kd) / (je-jd) * je)
                elif je < jamangle and jamangle <= jf :
                    jangle = int((kf-ke) / (jf-je) * jamangle + kf - (kf-ke) / (jf-je) * jf)
                elif jf < jamangle and jamangle <= jg :
                    jangle = int((kg-kf) / (jg-jf) * jamangle + kg - (kg-kf) / (jg-jf) * jg)
                elif jg < jamangle and jamangle <= jh :
                    jangle = int((kh-kg) / (jh-jg) * jamangle + kh - (kh-kg) / (jh-jg) * jh)
                elif jh < jamangle :
                    jangle = int((ki-kh) / (ji-jh) * jamangle + ki - (ki-kh) / (ji-jh) * ji)
                else :
                    pass
                if 20 <= jangle and jangle <= 160 :
                    angle = jangle
                    data = str(angle).encode('utf-8')
                    s.sendall(data)
                #print(int(angle))
            except:
                #print('outline')
                pass
                
cv2.destroyAllWindows()
