import cv2
import time

# Load frame, grayscale, blur, Otsu's threshold
i = 0
cap = cv2.VideoCapture(2)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    # if frame is read correctly ret is True

    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    result = frame.copy()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

# adaptive threshold
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 51, 9)

# Fill rectangular contours
    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(thresh, [c], -1, (255, 255, 255), -1)

# Morph open
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=4)

# Draw rectangles, the 'area_treshold' value was determined empirically
    cnts = cv2.findContours(opening, cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
area_treshold = 4000
for c in cnts:
    x, y, w, h = cv2.boundingRect(c)
    cv2.rectangle(frame, (x, y), (x + w - 3, y + h - 2),
                  (36, 255, 12), 3)
    if cv2.contourArea(c) > area_treshold and cv2.contourArea(c) < 3000000000:

print(cv2.contourArea(c))
x, y, w, h = cv2.boundingRect(c)
cv2.rectangle(frame, (x, y), (x + w - 3, y + h - 2),
              (36, 255, 12), 3)

card = frame[y:y+h, x:x+w]
card = card[0:120, 0:175]

cv2.imwrite(f'kaart_{i}.jpg', card)
i += 1
print(i)
time.sleep(0.1)

<< << << < HEAD
cv2.imshow('thresh', thresh)
== == == =
>>>>>> > Mats
cv2.imshow('frame', frame)
if cv2.waitKey(1) == ord('q'):
    break


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
