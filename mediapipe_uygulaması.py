import tkinter as tk
from tkinter import ttk
import cv2
import mediapipe as mp
import numpy as np
import threading
import time

# Counter ve stage değişkenlerini global olarak tanımlayın
counter = 0
stage = None

# Kilit objesi oluşturun
lock = threading.Lock()

running = False  # OpenCV döngüsünü kontrol etmek için bir değişken


def start_exercise():
    def run_opencv():
        global counter, stage, running  # Fonksiyon içinde global değişkenleri kullanacağınızı belirtin

        # Sayaç ve aşama değişkenlerini sıfırla
        with lock:
            counter = 0
            stage = None

        selected_exercise = exercise_var.get()
        print(f"Seçilen Egzersiz: {selected_exercise}")

        mp_drawing = mp.solutions.drawing_utils
        mp_pose = mp.solutions.pose

        def calculate_angle(a, b, c):
            a = np.array(a)  # First
            b = np.array(b)  # Mid
            c = np.array(c)  # End

            radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
            angle = np.abs(radians * 180.0 / np.pi)

            if angle > 180.0:
                angle = 360 - angle

            return angle

        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Kamera açılma süresi boyunca bekleyin
        for i in range(15):
            if cap.isOpened():
                break
            time.sleep(1)

        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while running:
                ret, frame = cap.read()
                if not ret:
                    break

                # Recolor image to RGB
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False

                # Make detection
                results = pose.process(image)

                # Recolor back to BGR
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark

                    if selected_exercise == 'Leg Curls':
                        # Extract landmarks
                        try:
                            # Get coordinates
                            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                                   landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                            knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                                    landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                            ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                                     landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                            # Calculate angle
                            angle_leg_curl = calculate_angle(hip, knee, ankle)

                            # Visualize angle
                            cv2.putText(image, str(int(angle_leg_curl)),
                                        tuple(np.multiply(knee, [640, 480]).astype(int)),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA
                                        )

                            # Curl counter logic
                            if angle_leg_curl > 160:
                                stage = "up"
                            if angle_leg_curl < 100 and stage == 'up':
                                stage = "down"
                                with lock:
                                    counter += 1
                                print(counter)

                        except:
                            pass

                    if selected_exercise == 'Punches':
                        try:
                            # Get coordinates
                            shoulder_left = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                             landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                            elbow_left = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                          landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                            wrist_left = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                          landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                            shoulder_right = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                              landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                            elbow_right = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                                           landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                            wrist_right = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                           landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

                            # Calculate angle
                            angle_left = calculate_angle(shoulder_left, elbow_left, wrist_left)
                            angle_right = calculate_angle(shoulder_right, elbow_right, wrist_right)

                            # Visualize angle
                            cv2.putText(image, str(int(angle_left)),
                                        tuple(np.multiply(elbow_left, [640, 480]).astype(int)),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA
                                        )

                            cv2.putText(image, str(int(angle_right)),
                                        tuple(np.multiply(elbow_right, [640, 480]).astype(int)),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA
                                        )

                            # Punch counter logic
                            if angle_left > 150:
                                stage = "up"
                            if angle_left < 60 and stage == 'up':
                                stage = "down"
                                with lock:
                                    counter += 1
                                print(counter)

                            if angle_right > 150:
                                stage = "up"
                            if angle_right < 60 and stage == 'up':
                                stage = "down"
                                with lock:
                                    counter += 1
                                print(counter)

                            # if (angle_left > 160 and angle_right < 60) or (angle_right > 160 and angle_left < 60):
                            #     stage = "up"
                            # if ((angle_left > 160 and angle_right < 60) or (angle_right > 160 and angle_left < 60)) and stage == 'up':
                            #     stage = "down"
                            #     with lock:
                            #         counter += 1
                            #     print(counter)

                        except:
                            pass

                    if selected_exercise == 'Squat':
                        try:
                            shoulder_right = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                             landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                            hip_right = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                                          landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                            knee_right = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                                          landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]

                            hip_right = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                                   landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                            knee_right = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                                    landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
                            ankle_right = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                                     landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

                            # Calculate angle
                            angle_top = calculate_angle(shoulder_right, hip_right, knee_right)
                            angle_bottom = calculate_angle(hip_right, knee_right, ankle_right)

                            # Visualize angle
                            cv2.putText(image, str(int(angle_top)),
                                        tuple(np.multiply(hip_right, [640, 480]).astype(int)),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA
                                        )

                            cv2.putText(image, str(int(angle_bottom)),
                                        tuple(np.multiply(knee_right, [640, 480]).astype(int)),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA
                                        )

                            # Punch counter logic
                            if angle_top < 90 and angle_bottom < 90:
                                stage = "down"
                            if angle_top > 150 and angle_bottom > 150 and stage == 'down':
                                stage = "up"
                                with lock:
                                    counter += 1
                                print(counter)

                        except:
                            pass

                    if selected_exercise == 'Elbow Plank':
                        try:
                            shoulder_right = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                             landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                            hip_right = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                                          landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                            ankle_right = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                                          landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

                            shoulder_right = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                   landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                            elbow_right = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                                    landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                            wrist_right = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                     landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

                            # Calculate angle
                            angle_top = calculate_angle(shoulder_right, hip_right, ankle_right)
                            angle_bottom = calculate_angle(shoulder_right, elbow_right, wrist_right)

                            # Visualize angle
                            cv2.putText(image, str(int(angle_top)),
                                        tuple(np.multiply(hip_right, [640, 480]).astype(int)),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA
                                        )

                            cv2.putText(image, str(int(angle_bottom)),
                                        tuple(np.multiply(elbow_right, [640, 480]).astype(int)),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA
                                        )

                            # Punch counter logic
                            if (200 > angle_top > 165) and (70 < angle_bottom < 100):
                                stage = "elbow plank"
                                with lock:
                                    counter += 1
                                print(counter)
                        except:
                            pass

                    if selected_exercise == 'Chest Squeezes':
                        try:
                            shoulder_right = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                              landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                            elbow_right = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                                           landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                            wrist_right = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                           landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

                            shoulder_left= [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                   landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                            elbow_left = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                    landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                            wrist_left = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                     landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                            nose = [landmarks[mp_pose.PoseLandmark.NOSE.value].x,
                                              landmarks[mp_pose.PoseLandmark.NOSE.value].y]
                            index_left = [landmarks[mp_pose.PoseLandmark.LEFT_INDEX.value].x,
                                           landmarks[mp_pose.PoseLandmark.LEFT_INDEX.value].y]
                            pinky_left = [landmarks[mp_pose.PoseLandmark.RIGHT_PINKY.value].x,
                                           landmarks[mp_pose.PoseLandmark.RIGHT_PINKY.value].y]

                            # Calculate angle
                            angle_right = calculate_angle(shoulder_right, elbow_right, wrist_right)
                            angle_left = calculate_angle(shoulder_left, elbow_left, wrist_left)
                            angle_top = calculate_angle(nose, index_left, pinky_left)

                            # Visualize angle
                            cv2.putText(image, str(int(angle_right)),
                                        tuple(np.multiply(elbow_right, [640, 480]).astype(int)),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA
                                        )

                            cv2.putText(image, str(int(angle_left)),
                                        tuple(np.multiply(elbow_left, [640, 480]).astype(int)),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA
                                        )

                            cv2.putText(image, str(int(angle_top)),
                                        tuple(np.multiply(index_left, [640, 480]).astype(int)),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA
                                        )

                            # Punch counter logic
                            if angle_right > 165 and angle_left > 165:
                                stage = "down"
                            if angle_right < 60 and angle_left < 60 and angle_top > 160 and stage == 'down':
                                stage = "up"
                                with lock:
                                    counter += 1
                                print(counter)
                        except:
                            pass

                    if selected_exercise == 'High Knees':
                        try:
                            hip_right = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                                         landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                            knee_right = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                                          landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
                            ankle_right = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                                           landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

                            hip_left = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                                         landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                            knee_left = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                                          landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                            ankle_left = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                                           landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                            # Calculate angle
                            angle_right = calculate_angle(hip_right, knee_right, ankle_right)
                            angle_left = calculate_angle(hip_left, knee_left, ankle_left)


                            # Visualize angle
                            cv2.putText(image, str(int(angle_right)),
                                        tuple(np.multiply(knee_right, [640, 480]).astype(int)),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA
                                        )

                            cv2.putText(image, str(int(angle_left)),
                                        tuple(np.multiply(knee_left, [640, 480]).astype(int)),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA
                                        )

                            # Punch counter logic
                            if angle_right < 90:
                                stage = "up"
                            if angle_right > 160 and stage == 'up':
                                stage = "down"
                                with lock:
                                    counter += 1
                                print(counter)
                        except:
                            pass

                    # Setup status box
                    cv2.rectangle(image, (0, 0), (225, 73), (245, 117, 16), -1)

                    # Rep data
                    cv2.putText(image, selected_exercise, (15, 12),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                    cv2.putText(image, str(counter),
                                (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                    # Stage data
                    cv2.putText(image, '- STAGE:', (95, 12),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                    cv2.putText(image, stage,
                                (60, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                    # Render detections
                    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                              mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2,
                                                                     circle_radius=2),
                                              mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                                              )

                cv2.imshow('Mediapipe Feed', image)

                if cv2.waitKey(10) & 0xFF == ord('q'):
                    running = False
                    break

                time.sleep(0.01)  # CPU kullanımını azaltmak için gecikme

        cap.release()
        cv2.destroyAllWindows()
        root.deiconify()  # Tkinter penceresini yeniden göster

    global running
    running = True  # OpenCV döngüsünü başlat
    message_label.config(text="Lütfen bekleyin, ayarları yapıyorum. 15 saniye içinde kamera açılacaktır")

    def wait_and_hide():
        time.sleep(15)  # 15 saniye bekleme
        root.withdraw()  # Tkinter penceresini gizleme

    threading.Thread(target=wait_and_hide).start()
    opencv_thread = threading.Thread(target=run_opencv)
    opencv_thread.daemon = True
    opencv_thread.start()


# Pencereyi oluştur
root = tk.Tk()
root.title("Egzersiz Seçimi")

# Pencere boyutunu ayarlayın
root.geometry("400x200")  # Genişlik x Yükseklik

# Egzersiz seçenekleri
exercise_var = tk.StringVar(root)
exercise_var.set("Leg Curls")  # Varsayılan olarak Leg Curls seçili olsun

exercises = ["High Knees", "Squat", "Punches", "Leg Curls", "Superman", "Chest Squeezes", "Elbow Plank"]
exercise_dropdown = ttk.Combobox(root, textvariable=exercise_var, values=exercises)
exercise_dropdown.pack(pady=20)

# Başlat düğmesini oluştur
start_button = tk.Button(root, text="Başlat", command=start_exercise)
start_button.pack()

# Mesaj etiketi
message_label = tk.Label(root, text="")
message_label.pack()


# Pencereyi kapatırken OpenCV döngüsünü durdurun
def on_closing():
    global running
    running = False
    root.quit()  # Tkinter ana döngüsünü durdur


root.protocol("WM_DELETE_WINDOW", on_closing)

# Pencereyi göster
root.mainloop()
