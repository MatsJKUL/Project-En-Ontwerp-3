import cv2
import time


def check_color_present(frame):
    total_pixel = 0
    red_pixel = 0
    for row in frame:
        for pixel in row:
            if (pixel[2] > 200 and pixel[1] < 50 and pixel[0] < 50):
                red_pixel += 1
            total_pixel += 1

    print(red_pixel/total_pixel)


# Load frame, grayscale, blur, Otsu's threshold
i = 0
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    # Capture frame-by-frame
    frame = cv2.imread("./red.png")
    # if frame is read correctly ret is True
    check_color_present(frame)

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
