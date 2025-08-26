import os
import cv2
from flask import Flask, render_template, Response, request, redirect, url_for, send_file
from ultralytics import YOLO

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"

# Load YOLOv8 model
model = YOLO("yolov8s.pt")

video_path = None


def draw_head_box(frame, x1, y1, x2, y2):
    """Vẽ khung xanh nhỏ quanh vùng đầu"""
    head_h = int((y2 - y1) * 0.5)      # Cao
    head_w = int((x2 - x1) * 0.5)       # Rong
    center_x = (x1 + x2) // 2

    x1_new = max(center_x - head_w // 2, 0)
    x2_new = min(center_x + head_w // 2, frame.shape[1])
    y2_new = min(y1 + head_h, frame.shape[0])

    cv2.rectangle(frame, (x1_new, y1), (x2_new, y2_new), (0, 255, 0), 2)
    cv2.putText(frame, "Head", (x1_new, max(y1 - 5, 0)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


def generate_frames(path):
    cap = cv2.VideoCapture(path)
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        else:
            results = model(frame, conf=0.15, imgsz=1100)
            head_count = 0

            for result in results:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    if model.names[cls_id] == "person":
                        head_count += 1
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        draw_head_box(frame, x1, y1, x2, y2)

            # Hiển thị số người
            cv2.putText(frame, f"People Count: {head_count}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

            # Encode ảnh thành JPEG để stream
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "video" not in request.files:
            return "No file uploaded!"
        file = request.files["video"]
        if file.filename == "":
            return "No selected file!"
        path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(path)
        global video_path
        video_path = path
        return redirect(url_for("play_video"))
    return render_template("index.html")


@app.route("/video")
def play_video():
    global video_path
    if video_path is None:
        return "No video uploaded yet!"
    return Response(generate_frames(video_path),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


# ========== Xử lý ảnh ==========
@app.route("/image", methods=["GET", "POST"])
def upload_image():
    if request.method == "POST":
        if "image" not in request.files:
            return "No image uploaded!"
        file = request.files["image"]
        if file.filename == "":
            return "No selected file!"

        path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(path)

        img = cv2.imread(path)
        results = model(img, conf=0.30, imgsz=1280)
        head_count = 0

        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                if model.names[cls_id] == "person":
                    head_count += 1
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    draw_head_box(img, x1, y1, x2, y2)

        # Hiển thị số người
        cv2.putText(img, f"People Count: {head_count}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        output_path = os.path.join("uploads", "result_" + file.filename)
        cv2.imwrite(output_path, img)

        return send_file(output_path, mimetype="image/jpeg")

    return '''
    <h2>Upload an Image to Count People</h2>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="image">
        <input type="submit" value="Upload & Count">
    </form>
    '''


if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
