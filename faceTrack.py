import cv2
import pyautogui
import time

#load Haar face cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

#use default camera
cap = cv2.VideoCapture(0)

#key control variables
last_key_time = time.time()
current_key = None
key_display_time = 0
key_hold_start = 0
key_hold_threshold = 2.0  # seconds to hold before continuous press
key_cooldown = 0.1  # seconds between repeated presses
key_being_held = False

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    #get frame dimensions 
    height, width = frame.shape[:2]
    
    #box size 
    box_width = width//11
    box_height = height//7
    
    #center position of frame
    center_x = width // 2
    center_y = height // 2
    
    #threshold box coordinates
    x1 = center_x - (box_width // 2)
    y1 = center_y - (box_height // 2)
    x2 = center_x + (box_width // 2)
    y2 = center_y + (box_height // 2)
    
    # Draw white threshold box with instructions
    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 255), 3)
    cv2.putText(frame, "Control Zone", (x1+10, y1-10), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    #convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    #detect faces
    faces = face_cascade.detectMultiScale(
        gray, 
        scaleFactor=1.1, 
        minNeighbors=5, 
        minSize=(30, 30)
    )
    
    #track largest face (main ting face)
    new_key = None
    if len(faces) > 0:
        largest_face = max(faces, key=lambda item: item[2] * item[3])
        x, y, w, h = largest_face
        
        #calc face center
        face_center_x = x + w//2
        face_center_y = y + h//2
        
        #draw green dot at face center
        cv2.circle(frame, (face_center_x, face_center_y), 8, (0, 255, 0), -1)
        
        #draw line from face center to box center
        cv2.line(frame, (face_center_x, face_center_y), (center_x, center_y), (0, 255, 255), 2)
        
        #determine which arrow key should be pressed based on position
        current_time = time.time()
        if face_center_x < x1:  #right eft of threshold
            new_key = "RIGHT"
        elif face_center_x > x2:  #left of threshold
            new_key = "LEFT"
        elif face_center_y < y1:  #above threshold
            new_key = "UP"
        elif face_center_y > y2:  #below threshold
            new_key = "DOWN"
    
    current_time = time.time()
    
    #if key changed, release any held key and reset timer
    if new_key != current_key:
        if key_being_held:
            pyautogui.keyUp(current_key.lower())
            key_being_held = False
        current_key = new_key
        key_hold_start = current_time if current_key else 0
        last_key_time = current_time
    
    #handle key pressing
    if current_key:
        #if holding position for more than threshold, hold down the key
        if current_time - key_hold_start > key_hold_threshold and not key_being_held:
            pyautogui.keyDown(current_key.lower())
            key_being_held = True
            key_display_time = current_time
        #if not holding yet, press at regular intervals
        elif current_time - last_key_time > key_cooldown and not key_being_held:
            pyautogui.press(current_key.lower())
            last_key_time = current_time
            key_display_time = current_time
    
    #release key if no direction
    elif key_being_held:
        pyautogui.keyUp(current_key.lower())
        key_being_held = False
    
    #display the pressed key for 1 second
    if current_key and (time.time() - key_display_time < 1.0):
        #background rectangle for the text
        text_size = cv2.getTextSize(current_key, cv2.FONT_HERSHEY_SIMPLEX, 3, 5)[0]
        text_x = (width - text_size[0]) // 2
        text_y = (height + text_size[1]) // 2
        cv2.rectangle(frame, 
                     (text_x - 20, text_y - text_size[1] - 20), 
                     (text_x + text_size[0] + 20, text_y + 20), 
                     (50, 50, 50), -1)
        
        #add "HOLD" text if key is being held down
        display_text = current_key + (" (HOLD)" if key_being_held else "")
        cv2.putText(frame, display_text, (text_x, text_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 255), 5)
    else:
        if not current_key and key_being_held:
            pyautogui.keyUp(current_key.lower())
            key_being_held = False
    
    #display status info
    status = "Ready" if current_key is None else f"Pressed: {current_key}{' (HOLDING)' if key_being_held else ''}"
    cv2.putText(frame, status, (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    #display output
    cv2.imshow('Face Control - Arrow Keys', frame)
    
    #exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        if key_being_held:
            pyautogui.keyUp(current_key.lower())
        break

cap.release()
cv2.destroyAllWindows()
