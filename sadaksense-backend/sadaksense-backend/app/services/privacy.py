"""Blur faces and licence plates before any frame is stored."""
import cv2

_face = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


def blur_regions(img_bgr, boxes):
    for x1, y1, x2, y2 in boxes:
        roi = img_bgr[int(y1):int(y2), int(x1):int(x2)]
        if roi.size:
            img_bgr[int(y1):int(y2), int(x1):int(x2)] = cv2.GaussianBlur(roi, (51, 51), 0)
    return img_bgr


def anonymise(img_bgr, plate_boxes=()):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    faces = [(x, y, x + w, y + h) for x, y, w, h in _face.detectMultiScale(gray, 1.1, 5)]
    return blur_regions(img_bgr, list(faces) + list(plate_boxes))
