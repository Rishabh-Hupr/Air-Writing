import numpy as np
import os
import cv2
import mediapipe as mp
import time

#remCam = "http://192.168.1.14:4747/video"
cap = cv2.VideoCapture(0)
colors = list()
for i in os.listdir("Colors"):
    tmp = cv2.imread("Colors/" + i)
    colors.append(tmp)


mphands = mp.solutions.hands

hands = mphands.Hands(max_num_hands=1, min_detection_confidence=0.78)
mpDraw = mp.solutions.drawing_utils

be = en = 0

dcolor = (0, 0, 0)
positions = []
i = 0
canv = np.zeros((720, 1280, 3), np.uint8)
xp = yp = 0
dcolor = (0, 0, 0)

while True:
    succ, img = cap.read()

    # getting image ready

    cv2.flip(img, 1, img)
    img = cv2.resize(img, (1280, 720), img, cv2.INTER_CUBIC)
    imgrgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgrgb)

    # pasting overlays

    img[0:75, 540:630] = colors[0][0:75, 10:100]
    img[0:75, 650:740] = colors[0][0:75, 1180:1270]

    # actual tracking

    if results.multi_hand_landmarks:
        for handldmks in results.multi_hand_landmarks:
            for iid, lnd in enumerate(handldmks.landmark):
                h, w, c = img.shape
                cx, cy = int(lnd.x * w), int(lnd.y * h)
                positions.append([iid, cx, cy])

            # mpDraw.draw_landmarks(img, handldmks, mphands.HAND_CONNECTIONS)

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
