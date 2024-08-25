import cv2
from cvzone.HandTrackingModule import HandDetector

# Initialize webcam capture
webcam = cv2.VideoCapture(0)
webcam.set(3, 1280)  # Set width of the webcam frame
webcam.set(4, 720)  # Set height of the webcam frame

# Initialize hand detector with a detection confidence threshold
gesture_detector = HandDetector(detectionCon=0.7)

initial_distance = None  # Initial distance between hands
zoom_amount = 0  # Amount to zoom
image_center_x, image_center_y = 200, 200  # Initial image center coordinates

while True:
    # Capture frame from webcam
    ret, frame = webcam.read()
    if not ret:
        break

    # Detect hands in the current frame
    hands, annotated_frame = gesture_detector.findHands(frame)

    # Load the image to be zoomed
    zoom_image = cv2.imread("photo.jpg")

    if len(hands) == 2:  # If two hands are detected
        hand_one = hands[0]
        hand_two = hands[1]

        # Determine which fingers are up for both hands
        hand_one_fingers = gesture_detector.fingersUp(hand_one)
        hand_two_fingers = gesture_detector.fingersUp(hand_two)

        # Check if index and middle fingers are up on both hands (zoom gesture)
        if hand_one_fingers == [1, 1, 0, 0, 0] and hand_two_fingers == [1, 1, 0, 0, 0]:
            # Calculate distance between the centers of the hands
            if initial_distance is None:
                distance, info, annotated_frame = gesture_detector.findDistance(hand_one["center"], hand_two["center"],
                                                                                annotated_frame)
                initial_distance = distance

            distance, info, annotated_frame = gesture_detector.findDistance(hand_one["center"], hand_two["center"],
                                                                            annotated_frame)
            zoom_amount = int((distance - initial_distance) // 2)
            image_center_x, image_center_y = info[4:]

    else:
        # Reset the initial distance if there aren't two hands detected
        initial_distance = None

    try:
        # Calculate new dimensions for the image based on zoom amount
        img_height, img_width, _ = zoom_image.shape
        new_height = max((img_height + zoom_amount), 1)
        new_width = max((img_width + zoom_amount), 1)
        zoom_image = cv2.resize(zoom_image, (new_width, new_height))

        # Ensure the resized image fits within the frame
        if (image_center_y - new_height // 2 >= 0 and
                image_center_y + new_height // 2 <= frame.shape[0] and
                image_center_x - new_width // 2 >= 0 and
                image_center_x + new_width // 2 <= frame.shape[1]):
            # Overlay the resized image onto the frame
            annotated_frame[image_center_y - new_height // 2: image_center_y + new_height // 2,
            image_center_x - new_width // 2: image_center_x + new_width // 2] = zoom_image

    except Exception as error:
        print(f"Error resizing or overlaying image: {error}")

    # Display the frame with annotations
    cv2.imshow("Hand Gesture Zoom Control", annotated_frame)

    # Exit loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
webcam.release()
cv2.destroyAllWindows()
