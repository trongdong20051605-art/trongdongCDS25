1. Giới thiệu

Ứng dụng web sử dụng Flask + YOLOv8 để đếm số lượng người trong ảnh hoặc video. Khi người dùng upload, hệ thống sẽ nhận diện người, vẽ khung quanh vùng đầu và hiển thị tổng số lượng.

2. Môi trường

Python 3.8+

Thư mục uploads/ sẽ tự tạo khi chạy để lưu ảnh/video và kết quả.

File model yolov8s.pt cần được tải từ Ultralytics
.

Chạy ứng dụng:

python app.py


Truy cập tại: http://localhost:5000

3. Chức năng

Upload video → phát video có nhận diện + đếm số người.

Upload ảnh → trả về ảnh kết quả với khung và số người.

Vẽ khung nhỏ quanh đầu người thay vì toàn thân.

4. Thư viện

Các thư viện chính được sử dụng trong project:

Flask → xây dựng web app.

Ultralytics (YOLOv8) → mô hình phát hiện người.

OpenCV (cv2) → xử lý ảnh, vẽ khung.

os → xử lý file/thư mục.

5. Giao diện

<img width="1139" height="876" alt="image" src="https://github.com/user-attachments/assets/3b0568a0-0cca-4c1d-a374-72cb71e17858" />
