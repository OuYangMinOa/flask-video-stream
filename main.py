from cv2      import VideoCapture, imencode, COLOR_BGR2RGB, cvtColor
from flask    import Flask, render_template_string, Response
from io       import BytesIO
from dotter   import dotter
from PIL      import Image
from time     import sleep
from datetime import datetime

import threading
import cv2
import os


class Frame:
    def __init__(self):
        self.save_folder = "GoClass"
        self.frame_bytes = None
        self.frame_cap = None
        self.state = False
        self.open_camera()
        self.grabbing = True
    
    def start_test(self):  
        threading.Thread(target=self.close_countdown,daemon=True).start()

    def start_record(self,filename, total_time = 1.5 * 3600):
        threading.Thread(target=self.record_frame, args = (filename, total_time), daemon=True).start()

    def record_frame(self, filename, total_time = 1.5 * 3600):
        if (not self.state):
            self.open_camera()
        start_time = datetime.now()
        fps = 20.0
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        out = cv2.VideoWriter(filename, fourcc, fps, (
             int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
             int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            ))

        print("start recording ... ")
        while (datetime.now() - start_time).seconds < total_time:
            self.grabbing = True
            if (self.frame_cap is not None):
                out.write(self.frame_cap)
                sleep(1/fps)
        print((datetime.now() - start_time).seconds , total_time,(datetime.now() - start_time).seconds > total_time)

        print("record stop")
        out.release()
    
    def book_record_each_week(self, date, hour, minute, total_time=1.5*3600):
        def while_start():
            print(f"[*] Book at {date=} {hour=} {minute=}")
            os.makedirs(self.save_folder, exist_ok=True)
            filename = f"{self.save_folder}/{date}-{hour}-{minute}" + ".avi"
            if (os.path.exists(filename)):
                os.remove(filename)
            while True:
                now = datetime.now()
                this_now = (now.weekday()+1, now.hour, now.minute)
                if (this_now == (date, hour, minute)):
                    self.start_record(filename,total_time)
                sleep(60)

        threading.Thread(target=while_start, daemon=True).start()

    def close_countdown(self):
        while True:
            self.grabbing = False
            sleep(20)
            if (self.grabbing == False):
                self.state = False                
            sleep(60)

    def open_camera(self):
        self.state = True
        threading.Thread(target=self.gen_frames,daemon=True).start()

    def resize_img_2_bytes(self,image, resize_factor, quality):
        bytes_io = BytesIO()
        img = Image.fromarray(image)
        w, h = img.size
        img.thumbnail((int(w * resize_factor), int(h * resize_factor)))
        img.save(bytes_io, 'jpeg', quality=quality)
        return bytes_io.getvalue()

    def gen_frames(self):
        print("[*] Open camera ")
        self.cap = VideoCapture(-1)
        while self.state:
            success, frame = self.cap.read()  # read the camera frame
            self.frame_cap = frame
            if not success:
                self.cap = VideoCapture(-1)
                sleep(1)
            else:   
                img = cvtColor(frame, COLOR_BGR2RGB)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                img = cv2.putText(img, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                1, (255, 255, 255), 2, cv2.LINE_AA)
                self.frame_bytes = self.resize_img_2_bytes(img, resize_factor=2, quality=300)

        print("[*] Camera close")
        
    def get_frame(self):
        if (not self.state):
            self.open_camera()

        while True:
            self.grabbing = True
            sleep(1/120)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + self.frame_bytes + b'\r\n')

app = Flask(__name__)
frame = Frame()

with dotter("[*] Waiting for frame"):
    while frame.frame_bytes is None:
        sleep(1)
frame.book_record_each_week(1,13,30)
frame.book_record_each_week(2,17, 0)
frame.book_record_each_week(6,14, 0)

frame.start_test()

@app.route("/", methods=['GET'])
def get_stream_html():
    return render_template_string('''<!DOCTYPE html>
<html lang="en">
	<head>
		<script src="https://cdn.tailwindcss.com"></script>
	</head>
	<body>
        <center>
		<div class="container">
			<div class="row">
				<div class="grid-cols-8">
					<h3 class="text-4xl text-center m-11">Live Streaming</h3>
					<img src="{{ url_for('video_stream') }}" width="100%">
				</div>
			</div>
		</div>
        </center>
	</body>
</html>''')




@app.route('/api/stream')
def video_stream():
    return Response(frame.get_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    
    app.run(debug=False, host='0.0.0.0', port=8789, threaded=True, use_reloader=False)
