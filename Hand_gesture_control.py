#!/usr/bin/env python
# coding: utf-8

# In[1]:


import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time


# In[2]:


# Initialize Mediapipe hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)


# In[3]:


cap = cv2.VideoCapture(0)# Initialize video capture


# In[4]:


screen_width, screen_height = pyautogui.size()# Get screen dimensions


# In[5]:


# Variables for cursor control
cursor_smoothing = 0.5  # Smoothing factor (0-1)
prev_cursor_x, prev_cursor_y = None, None


# In[6]:


# Variable for hover selection
hover_start_time = 0
hover_position = None
hover_threshold = 5  # 5 seconds for selection
hover_radius = 15  # pixels of movement allowed during hove


# In[7]:


# Variable for open palm detection
palm_open_start_time = 0
palm_open_detected = False
palm_open_threshold = 5  # 5 seconds for minimize all windows


# In[8]:


# Variables for swipe gesture
swipe_start_position = None
swipe_threshold = 100  # pixels for minimum swipe distance
swipe_cooldown = 0  # cooldown timer to prevent multiple swipes
swipe_cooldown_threshold = 2  # seconds between swipes


# In[9]:


# Pyautogui settings for safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1


# In[10]:


while True:
    # Read frame from video capture
    ret, frame = cap.read()
    if not ret:
        break
        
    # Flip the frame horizontally for a more intuitive experience
    frame = cv2.flip(frame, 1)
    
    frame_height, frame_width, _ = frame.shape
    
    # Convert the BGR frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the frame with Mediapipe hands
    results = hands.process(frame_rgb)
    
    # Current cursor position
    cursor_x, cursor_y = None, None
    
    # Current time for timing functions
    current_time = time.time()
    
    # Decrease swipe cooldown if active
    if swipe_cooldown > 0:
        swipe_cooldown = max(0, swipe_cooldown - 0.03)  # decrease by ~30ms per frame
    
    # Check if hands are detected
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw landmarks on the hand
            mp_drawing.draw_landmarks(
                frame, 
                hand_landmarks, 
                mp_hands.HAND_CONNECTIONS
            )
            
            # Get the palm landmark
            palm_landmark = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            palm_x = int(palm_landmark.x * frame_width)
            palm_y = int(palm_landmark.y * frame_height)
            
            # Draw a circle to represent the palm
            cv2.circle(frame, (palm_x, palm_y), 10, (0, 255, 0), -1)
            
            # Add green dots at fingertips
            fingertip_indices = [
                mp_hands.HandLandmark.THUMB_TIP,
                mp_hands.HandLandmark.INDEX_FINGER_TIP, 
                mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                mp_hands.HandLandmark.RING_FINGER_TIP,
                mp_hands.HandLandmark.PINKY_TIP
            ]
            
            for tip_idx in fingertip_indices:
                fingertip = hand_landmarks.landmark[tip_idx]
                fingertip_x = int(fingertip.x * frame_width)
                fingertip_y = int(fingertip.y * frame_height)
                cv2.circle(frame, (fingertip_x, fingertip_y), 8, (0, 255, 0), -1)
            
            # Get index finger tip for cursor control
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            index_x = int(index_tip.x * frame_width)
            index_y = int(index_tip.y * frame_height)
            
            # Calculate cursor position (map from camera coordinates to screen coordinates)
            cursor_x = int(index_tip.x * screen_width)
            cursor_y = int(index_tip.y * screen_height)
            
            # Apply smoothing if previous position exists
            if prev_cursor_x is not None and prev_cursor_y is not None:
                cursor_x = int(cursor_smoothing * cursor_x + (1 - cursor_smoothing) * prev_cursor_x)
                cursor_y = int(cursor_smoothing * cursor_y + (1 - cursor_smoothing) * prev_cursor_y)
            
            # Update previous cursor position
            prev_cursor_x, prev_cursor_y = cursor_x, cursor_y
            
            # Move the cursor
            try:
                pyautogui.moveTo(cursor_x, cursor_y)
            except pyautogui.FailSafeException:
                pass  # Ignore if cursor moves to corner (failsafe triggered)
            
            # Hover selection logic
            if hover_position is not None:
                hover_x, hover_y = hover_position
                # Calculate distance from current position to hover start position
                hover_distance = np.sqrt((cursor_x - hover_x)**2 + (cursor_y - hover_y)**2)
                
                # If moved too far, reset hover
                if hover_distance > hover_radius:
                    hover_position = None
                    hover_start_time = 0
                # If hovered long enough, perform click
                elif current_time - hover_start_time >= hover_threshold:
                    # Perform click
                    try:
                        pyautogui.click()
                        # Visual feedback for click
                        cv2.circle(frame, (index_x, index_y), 30, (0, 0, 255), 5)
                    except pyautogui.FailSafeException:
                        pass  # Ignore failsafe
                    
                    # Reset hover timer
                    hover_position = None
                    hover_start_time = 0
                else:
                    # Still hovering, show progress
                    hover_progress = (current_time - hover_start_time) / hover_threshold
                    radius = int(30 * hover_progress)
                    cv2.circle(frame, (index_x, index_y), radius, (255, 0, 0), 2)
            
            # If no hover position yet, start new hover
            elif hover_position is None:
                hover_position = (cursor_x, cursor_y)
                hover_start_time = current_time
            
            # Check for open palm gesture
            # Get finger MCP points (knuckles)
            finger_mcp_indices = [
                mp_hands.HandLandmark.THUMB_CMC,
                mp_hands.HandLandmark.INDEX_FINGER_MCP,
                mp_hands.HandLandmark.MIDDLE_FINGER_MCP,
                mp_hands.HandLandmark.RING_FINGER_MCP,
                mp_hands.HandLandmark.PINKY_MCP
            ]
            
            # Get finger tip positions
            finger_tips = [hand_landmarks.landmark[i] for i in fingertip_indices]
            finger_mcps = [hand_landmarks.landmark[i] for i in finger_mcp_indices]
            
            # Check if palm is open (all fingers extended)
            is_palm_open = True
            for tip, mcp in zip(finger_tips, finger_mcps):
                # Skip thumb as it behaves differently
                if tip == finger_tips[0]:
                    continue
                
                # Check if finger is extended by ensuring tip is above mcp (y is smaller since origin is top-left)
                if tip.y > mcp.y:
                    is_palm_open = False
                    break
            
            # Check pinky and index finger horizontal distance for wide-open palm
            pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            fingers_spread = abs(pinky_tip.x - index_tip.x) > 0.2  # threshold for spread fingers
            
            is_palm_open = is_palm_open and fingers_spread
            
            # Palm open status and time tracking
            if is_palm_open:
                if not palm_open_detected:
                    palm_open_start_time = current_time
                    palm_open_detected = True
                
                # Check if palm has been open for threshold time
                if current_time - palm_open_start_time >= palm_open_threshold:
                    # Minimize all windows
                    pyautogui.hotkey('win', 'd')
                    
                    # Visual feedback
                    cv2.putText(frame, "Minimizing all windows!", (50, frame_height - 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
                    # Reset timer to prevent multiple actions
                    palm_open_start_time = current_time + 5  # Add 5 seconds cooldown
                
                # Show progress for palm open gesture
                palm_progress = min(1.0, (current_time - palm_open_start_time) / palm_open_threshold)
                progress_bar_width = int(frame_width * palm_progress)
                cv2.rectangle(frame, (0, frame_height - 20), (progress_bar_width, frame_height), (0, 255, 0), -1)
                cv2.putText(frame, "Palm Open", (10, frame_height - 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                palm_open_detected = False
            
            # Swipe detection - left to right to change tabs
            if is_palm_open and swipe_cooldown <= 0:
                if swipe_start_position is None:
                    swipe_start_position = (palm_x, palm_y)
                else:
                    # Calculate horizontal movement
                    swipe_distance_x = palm_x - swipe_start_position[0]
                    
                    # Check if hand moved significantly horizontally
                    if abs(swipe_distance_x) > swipe_threshold:
                        # Left to right swipe
                        if swipe_distance_x > 0:
                            # Switch to next tab with Ctrl+Tab
                            pyautogui.hotkey('ctrl', 'tab')
                            cv2.putText(frame, "Next Tab", (50, 120), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        # Right to left swipe
                        else:
                            # Switch to previous tab with Ctrl+Shift+Tab
                            pyautogui.hotkey('ctrl', 'shift', 'tab')
                            cv2.putText(frame, "Previous Tab", (50, 120), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        
                        # Reset swipe detection and set cooldown
                        swipe_start_position = None
                        swipe_cooldown = swipe_cooldown_threshold
            else:
                swipe_start_position = None
            
            # Display cursor position
            cv2.putText(frame, f"Cursor: ({cursor_x}, {cursor_y})", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    else:
        # Reset palm open detection if no hand is detected
        palm_open_detected = False
        swipe_start_position = None
    
    # Display the frame
    cv2.imshow('Hand Gesture Controls', frame)
    
    # Exit the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and destroy all windows


# In[11]:


cap.release()
cv2.destroyAllWindows()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




