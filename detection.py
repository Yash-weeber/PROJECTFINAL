import cv2
import os
import time

# Global variables for drawing the rectangle
drawing = False
ix, iy, x2, y2 = -1, -1, -1, -1


def get_physical_coordinates(marker_id):
    """
    Prompt the user to input the physical coordinates for each detected marker.
    :param marker_id: ID of the detected ArUco marker
    :return: A tuple (x, y) representing the physical coordinates of the marker
    """
    print(f"\nEnter the physical coordinates for Marker {marker_id}:")
 
    while True:
        try:
            x = float(input(f"Enter X-coordinate (in mm): "))
            y = float(input(f"Enter Y-coordinate (in mm): "))
            # If the input is valid, return the coordinates as a list
          
            return [x,y]
        except ValueError:
            print("Invalid input. Please enter numeric values.")


            
def mean_calc(a, b):
    return ((a+b)/2.0)



def calculate_line_equation(x1, y1, x2, y2):
    if x2 - x1 == 0:
        raise ValueError("The line is vertical, slope is undefined.")
    m = (y2 - y1) / (x2 - x1)
    c = y1 - m * x1
    return m, c


def getRobotCoordinates(cameraX, cameraY, mx, cx, my, cy):
    return (cameraX * mx + cx, cameraY * my + cy)



def detect_markers_once(cap):
    """
    Detect two sets of ArUco markers. Detect the second set only after pressing the 'e' key.
    Capture and save the frame as PNG after pressing 'k'.
    """
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    aruco_params = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

    marker_1_pixel = []
    marker_2_pixel = []
    marker_3_pixel = []
    marker_4_pixel = []

    marker_set_1_detected = False
    ready_for_second_set = False
    second_set_detected = False  # New flag to track if second set is detected

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame. Exiting.")
            break

        # Crop the frame to focus on the white plate
        frame = zoom_to_plate(frame)

        # Convert frame to grayscale for ArUco detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect markers
        corners, ids, _ = detector.detectMarkers(gray)

        if ids is not None:
            for i, corner in enumerate(corners):
                marker_id = ids[i][0]

                # Calculate center coordinates of the marker
                center_x = int((corner[0][0][0] + corner[0][2][0]) / 2)
                center_y = int((corner[0][0][1] + corner[0][2][1]) / 2)

                # Draw marker and center
                cv2.polylines(frame, [corner.astype(int)], True, (0, 255, 0), 2)
                cv2.circle(frame, (center_x, center_y), 5, (0, 255, 0), -1)
                cv2.putText(frame, f"ID: {marker_id}", (center_x - 20, center_y - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                # Detect the first set of markers
                if not marker_set_1_detected and marker_id in [1, 2]:
                    if marker_id == 1 and not marker_1_pixel:
                        marker_1_pixel = [center_x, center_y]
                        print(f"Marker 1 detected at: {marker_1_pixel}")
                    elif marker_id == 2 and not marker_2_pixel:
                        marker_2_pixel = [center_x, center_y]
                        print(f"Marker 2 detected at: {marker_2_pixel}")

                    if marker_1_pixel and marker_2_pixel:
                        print("First set of markers detected.")
                        marker_set_1_detected = True
                        print("Press 'e' to detect the second set of markers.")

                # Detect the second set of markers after pressing 'e'
                elif ready_for_second_set and marker_id in [1, 2]:
                    if marker_id == 1 and not marker_3_pixel:
                        marker_3_pixel = [center_x, center_y]
                        print(f"Marker 3 detected at: {marker_3_pixel}")
                    elif marker_id == 2 and not marker_4_pixel:
                        marker_4_pixel = [center_x, center_y]
                        print(f"Marker 4 detected at: {marker_4_pixel}")

                    if marker_3_pixel and marker_4_pixel and not second_set_detected:
                        print("Second set of markers detected.")
                        print("Press 'k' to capture and save the current frame.")
                        second_set_detected = True  # Set the flag to True

        # Display the frame
        cv2.imshow("Camera Feed", frame)

        # Check for key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('e') and marker_set_1_detected:
            print("Ready to detect the second set of markers.")
            ready_for_second_set = True
        elif key == ord('k') and second_set_detected:
            # Capture and save the current frame as a PNG image
            timestamp = int(time.time())
            filename = f"captured_frame_{timestamp}.png"
            cv2.imwrite(filename, frame)
            print(f"Frame captured and saved as {filename}")
            break  # Exit after capturing
        elif key == ord('q'):
            print("Exiting.")
            break

    return marker_1_pixel, marker_2_pixel, marker_3_pixel, marker_4_pixel


def draw_rectangle(event, x, y, flags, param):
    global ix, iy, x2, y2, drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            x2, y2 = x, y

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        x2, y2 = x, y

def zoom_to_plate(frame):
    global ix, iy, x2, y2
    x_start, x_end = sorted([ix, x2])
    y_start, y_end = sorted([iy, y2])
    return frame[y_start:y_end, x_start:x_end]

def main():
    
    marker_1_pixel = []
    marker_2_pixel = []
    marker_3_pixel = []
    marker_4_pixel = []
    
    
    cap = cv2.VideoCapture(2)
    if not cap.isOpened():
        print("Failed to open camera.")
        return

    print("Instructions:")
    print("1. Draw a rectangle on the live feed by clicking and dragging with the left mouse button.")
    print("2. Press 'z' to zoom in and detect ArUco markers within the selected area.")
    print("3. After detecting the second set of markers, press 'k' to capture and save the image.")
    print("4. Press 'q' to quit at any time.")

    cv2.namedWindow("Draw Area for Zoom")
    cv2.setMouseCallback("Draw Area for Zoom", draw_rectangle)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break

        # Draw rectangle if user is drawing
        temp_frame = frame.copy()
        if ix != -1 and iy != -1 and x2 != -1 and y2 != -1:
            cv2.rectangle(temp_frame, (ix, iy), (x2, y2), (0, 255, 0), 2)

        cv2.imshow("Draw Area for Zoom", temp_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('z') and (ix, iy, x2, y2) != (-1, -1, -1, -1):
            zoomed_frame = zoom_to_plate(frame)
            if zoomed_frame.size == 0:
                print("Invalid area selected. Try again.")
                continue
            print("Zooming in on selected area...")
            #cv2.imshow("Zoomed Area", zoomed_frame)
            marker_1_pixel, marker_2_pixel, marker_3_pixel, marker_4_pixel = detect_markers_once(cap) 
            
            
        elif key == ord('q'):
            print("Exiting.")
            break

    cap.release()
    cv2.destroyAllWindows()
    
    print("FINAL_RESULT")
    print("\n")
    print(f"marker-1: {marker_1_pixel}, marker-2: {marker_2_pixel}, marker-3: {marker_3_pixel}, marker-4: {marker_4_pixel}" )

    physical_marker_1 = get_physical_coordinates(1)
    physical_marker_2 = get_physical_coordinates(2)
    physical_marker_3 = get_physical_coordinates(3)
    physical_marker_4 = get_physical_coordinates(4)



    # Print final results
    print("\nFinal Results:")
    print(f"Marker 1 Pixel Coordinates: {marker_1_pixel}, Physical Coordinates: {physical_marker_1}")
    print(f"Marker 2 Pixel Coordinates: {marker_2_pixel}, Physical Coordinates: {physical_marker_2}")
    print(f"Marker 3 Pixel Coordinates: {marker_3_pixel}, Physical Coordinates: {physical_marker_3}")
    print(f"Marker 4 Pixel Coordinates: {marker_4_pixel}, Physical Coordinates: {physical_marker_4}")

    mx1, cx1 = calculate_line_equation(marker_1_pixel[0], physical_marker_1[0], marker_2_pixel[0], physical_marker_2[0])
    mx2, cx2 = calculate_line_equation(marker_3_pixel[0], physical_marker_3[0], marker_4_pixel[0], physical_marker_4[0])

    my1, cy1 = calculate_line_equation(marker_1_pixel[1], physical_marker_1[1], marker_2_pixel[1], physical_marker_2[1])
    my2, cy2 = calculate_line_equation(marker_3_pixel[1], physical_marker_3[1], marker_4_pixel[1], physical_marker_4[1])

    print("\n" )
    print(f"mx1, cx1 = {mx1, cx1}, mx2, cx2 = {mx2, cx2}, my1, cy1 = {my1, cy1}, my2, cy2 = {my2, cy2}")

    mx = mean_calc(mx1, mx2)
    my = mean_calc(my1, my2)
    cx = mean_calc(cx1, cx2)
    cy = mean_calc(cy1, cy2)

    print("\n")
    print(f"mx = {mx}, my = {my}")
    print(f"cx = {cx}, cy = {cy}")

if __name__ == "__main__":
    main()