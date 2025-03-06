#Simple Hand Gesture Controlled Mouse and Window Management

This Python script uses OpenCV and Mediapipe to control the mouse cursor and manage windows using hand gestures.

## Features

-   **Cursor Control:** Move the mouse cursor by tracking the index finger tip.
-   **Hover Click:** Perform a left mouse click by hovering the cursor over a point for a specified duration.
-   **Minimize All Windows:** Minimize all open windows by showing an open palm for a specified duration.
-   **Tab Switching:** Switch between browser tabs using a left-to-right or right-to-left swipe gesture with an open palm.
-   **Smoothing:** Smooths cursor movement for a more natural feel.
-   **Cooldowns:** Implements cooldowns to prevent accidental multiple gesture triggers.
-   **Failsafe:** Uses PyAutoGUI's failsafe to prevent the cursor from getting stuck in a corner.

## Libraries Used:

-   Python 3.x
-   OpenCV (`opencv-python`)
-   Mediapipe (`mediapipe`)
-   PyAutoGUI (`pyautogui`)
-   NumPy (`numpy`)

There are both ".py" file and ".ipynb" file 
choose the file that suits your IDE
IF you wish run in colab ## Running in Google Colab 

To run the `Hand_gesture_control.ipynb` notebook in Google Colab:

1.  Find the notebook on GitHub i.e "Hand_gesture_control.ipynb".
2.  Open the file.
3.  Change the URL "https://github.com/Yuva-Praneeth/Hand_gesture_control/blob/main/Hand_gesture_control.ipynb" to: "https://githubtocolab.com/Yuva-Praneeth/Hand_gesture_control/blob/main/Hand_gesture_control.ipynb".
4.  Run the notebook in Colab.


