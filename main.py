from cv2    import VideoCapture, imencode, COLOR_BGR2RGB, cvtColor
from flask  import Flask, render_template_string, Response
from io     import BytesIO
from dotter import dotter
from PIL    import Image
from time   import sleep
import threading


class Frame:
    def __init__(self):
        self.frame_bytes = None
        threading.Thread(target=self.gen_frames,daemon=True).start()

    def resize_img_2_bytes(self,image, resize_factor, quality):
        bytes_io = BytesIO()
        img = Image.fromarray(image)
        w, h = img.size
        img.thumbnail((int(w * resize_factor), int(h * resize_factor)))
        img.save(bytes_io, 'jpeg', quality=quality)
        return bytes_io.getvalue()

    def gen_frames(self):
        cap = VideoCapture(0)
        while True:
            success, frame = cap.read()  # read the camera frame
            if not success:
                cap = VideoCapture(0)
                sleep(1)
            else:
                img = cvtColor(frame, COLOR_BGR2RGB)
                self.frame_bytes = self.resize_img_2_bytes(img, resize_factor=2, quality=300)

    def get_frame(self):
        while True:
            sleep(1/120)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + self.frame_bytes + b'\r\n')

app = Flask(__name__)
frame = Frame()


with dotter("[*] Waiting for frame"):
    while frame.frame_bytes is None:
        sleep(1)


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