import numpy as np
import os
import cv2
import mediapipe as mp
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

#remCam = "http://192.168.1.14:4747/video"
cap = cv2.VideoCapture(0)
colors = list()
for i in os.listdir("Colors"):
    tmp = cv2.imread("Colors/" + i)
    colors.append(tmp)


MODEL_PATH = os.path.expanduser("~/Downloads/hand_landmarker.task")

# Standard 21-point hand topology (replaces mp.solutions.hands.HAND_CONNECTIONS)
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # index
    (5, 9), (9, 10), (10, 11), (11, 12),   # middle
    (9, 13), (13, 14), (14, 15), (15, 16), # ring
    (13, 17), (17, 18), (18, 19), (19, 20),# pinky
    (0, 17),                               # palm
]

# LIVE_STREAM mode delivers results asynchronously via this callback
latest_result = None


def _on_result(result, output_image, timestamp_ms):
    global latest_result
    latest_result = result


options = vision.HandLandmarkerOptions(
    base_options=python.BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=vision.RunningMode.LIVE_STREAM,
    num_hands=1,
    min_hand_detection_confidence=0.78,
    result_callback=_on_result,
)
landmarker = vision.HandLandmarker.create_from_options(options)

be = en = 0

dcolor = (0, 0, 0)
positions = []
i = 0
canv = np.zeros((720, 1280, 3), np.uint8)
xp = yp = 0
dcolor = (0, 0, 0)
frame_ts = 0

while True:
    succ, img = cap.read()
    if not succ:
        continue

    # getting image ready

    cv2.flip(img, 1, img)
    img = cv2.resize(img, (1280, 720), img, cv2.INTER_CUBIC)
    imgrgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=imgrgb)
    frame_ts += 1  # LIVE_STREAM requires monotonically increasing timestamps
    landmarker.detect_async(mp_image, frame_ts)
    results = latest_result

    # pasting overlays

    img[0:75, 540:630] = colors[0][0:75, 10:100]
    img[0:75, 650:740] = colors[0][0:75, 1180:1270]

    # actual tracking

    if results and results.hand_landmarks:
        for handldmks in results.hand_landmarks:
            pts = []
            for iid, lnd in enumerate(handldmks):
                h, w, c = img.shape
                cx, cy = int(lnd.x * w), int(lnd.y * h)
                positions.append([iid, cx, cy])
                pts.append((cx, cy))

            # draw landmarks and connections manually (no mp.solutions)
            for a, b in HAND_CONNECTIONS:
                cv2.line(img, pts[a], pts[b], (255, 255, 255), 2)
            for pt in pts:
                cv2.circle(img, pt, 4, (0, 0, 255), cv2.FILLED)

    if positions:
        x1 = positions[8][1]
        y1 = positions[8][2]
        if positions[8][2] < positions[7][2] and positions[12][2] > positions[11][2] and positions[16][2] > \
                positions[15][2] and positions[20][2] > positions[19][2]:

            if xp == yp == 0:
                xp, yp = x1, y1
            if y1 <= 75:
                if 540 <= x1 <= 630:
                    dcolor = (255, 0, 255)
                if 650 <= x1 <= 740:
                    dcolor = (0, 255, 0)
            if dcolor != (0, 0, 0):
                cv2.circle(img, (x1, y1), 15, dcolor, cv2.FILLED)
                cv2.line(canv, (xp, yp), (x1, y1), dcolor, 15)
                cv2.line(img, (xp, yp), (x1, y1), dcolor, 15)
        if positions[8][2] < positions[7][2] and positions[12][2] < positions[11][2] and positions[16][2] < \
                positions[15][2] and positions[20][2] < positions[19][2]:
            dcolor = (0, 0, 0)
            # cv2.rectangle(img, (positions[8][1], positions[8][2] - 50), (positions[20][1], positions[20][2] + 75), dcolor, cv2.FILLED)
            cv2.rectangle(canv, (positions[8][1], positions[8][2] - 50), (positions[20][1], positions[20][2] + 75), dcolor, cv2.FILLED)
        xp, yp = x1, y1
    positions.clear()

    imgGry = cv2.cvtColor(canv, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGry, 50, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, canv)

    en = time.time()
    fps = 1 / (en - be)
    be = en

    cv2.putText(img, str(int(fps)), (10, 650), cv2.FONT_HERSHEY_DUPLEX, 2, (250, 0, 0))
    cv2.imshow("Image", img)
    cv2.waitKey(1)
