from TSetting import Setting

import keyboard
import time 
import threading

import torch
import cv2
import os 
import numpy

class Controller(Setting):
    
    def __init__(self):
        Setting.__init__(self)
        self.controller_state = False
        self.controller_thread = None

        if not hasattr(self.drone,'_connected'):
            self.drone._connected = False
    
        self.stream_state = False

        self.follow_me_state = False
        self.follow_me_thread = None

        self.model_path = os.path.join(os.path.dirname(__file__), 'data', 'weight', 'last.pt')
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=self.model_path)

#------------------------------------------------------------------

    def ConnectDisconnect(self): 
            print("sium")
            self.drone.connect()

    def takeoff(self):
        self.drone.takeoff()
    
    def land(self):
        self.drone.land()


    def up(self):
        self.drone.move_up(self.y_cm)
    
    def down(self):
        self.drone.move_down(self.y_cm)

    def forward(self):
        self.drone.move_forward(self.x_cm)

    def back(self):
        self.drone.move_back(self.x_cm)

    def left(self):
        self.drone.move_left(self.z_cm)
    
    def right(self):
        self.drone.move_right(self.z_cm)

    def rotate_clockwise(self):
        self.drone.rotate_clockwise(self.degree)
    
    def rotate_counterclockwise(self):
        self.drone.rotate_counter_clockwise(self.degree)

#------------------------------------------------------------------

    def stream_switch(self):
        if not self.stream_state:
            self.drone.streamon()
            self.stream_state = True
        else:
            self.drone.streamoff()
            self.stream_state = False

#------------------------------------------------------------------

    def face_detect(self):
        """
        Esegue la face detection sul frame corrente del drone.
        Ritorna il frame annotato e la lista delle box rilevate.
        """
        frame = self.drone.get_frame_read().frame
        if frame is None:
            return None, None

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.model(frame_rgb)
        boxes = results.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2, conf, class]

        # Disegna solo le box con confidenza > 0.7
        for box in boxes:
            x1, y1, x2, y2, conf, cls = box
            if conf > 0.7:
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0,255,0), 2)
                cv2.putText(frame, f"Face {conf:.2f}", (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

        self.follow_me_frame = frame
        return frame, boxes

    def xPIDController(self, target, cVal, limit=[-100, 100], pTime=0, pError=0, I=0):
        """
        PID controller per l'asse X.
        """
        t = time.time() - pTime if pTime else 1e-3
        error = target - cVal
        P = self.xPID[0] * error  
        I = I + (self.xPID[1] * error * t)
        D = self.xPID[2] * (error - pError) / t if t > 0 else 0
        val = P + I + D
        val = float(numpy.clip(val, limit[0], limit[1]))
        return int(val), time.time(), error, I

    def yPIDController(self, target, cVal, limit=[-100, 100], pTime=0, pError=0, I=0):
        """
        PID controller per l'asse Y.
        """
        t = time.time() - pTime if pTime else 1e-3
        error = target - cVal
        P = self.yPID[0] * error  
        I = I + (self.yPID[1] * error * t)
        D = self.yPID[2] * (error - pError) / t if t > 0 else 0
        val = P + I + D
        val = float(numpy.clip(val, limit[0], limit[1]))
        return int(val), time.time(), error, I

    def zPIDController(self, target, cVal, limit=[-100, 100], pTime=0, pError=0, I=0):
        """
        PID controller per l'asse Z (area).
        """
        t = time.time() - pTime if pTime else 1e-3
        error = target - cVal
        P = self.zPID[0] * error  
        I = I + (self.zPID[1] * error * t)
        D = self.zPID[2] * (error - pError) / t if t > 0 else 0
        val = P + I + D
        val = float(numpy.clip(val, limit[0], limit[1]))
        return int(val), time.time(), error, I

    def follow_me(self, boxes, frame):
        """
        Segue il volto con la confidenza più alta.
        """
        if boxes is not None and len(boxes) > 0:
            best_box = max(boxes, key=lambda b: b[4])
            x1, y1, x2, y2, conf, cls = best_box
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            area = (x2 - x1) * (y2 - y1)

            # PID per ogni asse (puoi salvare pTime, pError, I come attributi se vuoi continuità)
            xVal, _, _, _ = self.xPIDController(self.xTarget, cx)
            yVal, _, _, _ = self.yPIDController(self.yTarget, cy)
            zVal, _, _, _ = self.zPIDController(self.zTarget, area, limit=[-20, 15])

            # Invia i comandi al drone
            self.drone.send_rc_control(xVal, yVal, zVal, 0)
        else:
            # Nessun volto rilevato: ferma il drone
            self.drone.send_rc_control(0, 0, 0, 0)

    def following(self):
        while self.follow_me_state:
            frame,boxes = self.face_detect()
            self.follow_me(boxes,frame)

#------------------------------------------------------------------

    def Controller(self):
        while self.controller_state:
            time.sleep(0.1)
            
            if keyboard.is_pressed(self.setting_section_controller[0][1]):
                self.ConnectDisconnect()

            elif keyboard.is_pressed(self.setting_section_controller[1][1]):
                self.stream_switch()
            
            elif keyboard.is_pressed(self.setting_section_controller[2][1]):
                self.takeoff()
            
            elif keyboard.is_pressed(self.setting_section_controller[3][1]):
                self.land()
            
            elif keyboard.is_pressed(self.setting_section_controller[4][1]):  
                self.forward()

            elif keyboard.is_pressed(self.setting_section_controller[5][1]):
                self.back()
            
            elif keyboard.is_pressed(self.setting_section_controller[6][1]):
                self.left()
            
            elif keyboard.is_pressed(self.setting_section_controller[7][1]):
                self.right()
            
            elif keyboard.is_pressed(self.setting_section_controller[8][1]):
                self.up()
            
            elif keyboard.is_pressed(self.setting_section_controller[9][1]):    
                self.down()
            
            elif keyboard.is_pressed(self.setting_section_controller[10][1]):
                self.rotate_clockwise()
            
            elif keyboard.is_pressed(self.setting_section_controller[11][1]):
                self.rotate_counterclockwise()
            
    def controller_switch(self):
        if self.controller_state:
            self.controller_state = False
            if self.controller_thread is not None and self.controller_thread.is_alive():
                self.controller_thread.join()
                self.controller_thread = None
        else:
            self.controller_state = True
            if self.controller_thread is None or not self.controller_thread.is_alive():
                self.controller_thread = threading.Thread(target=self.Controller)
                self.controller_thread.start()

        