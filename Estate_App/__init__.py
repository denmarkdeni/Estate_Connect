import cv2
import numpy as np

def extract_room_contours(image_path):
    # Load the image in grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # Apply binary threshold (invert to ensure walls are black)
    _, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)

    # Find contours (outlines of rooms)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    room_coordinates = []
    for contour in contours:
        # Approximate the contour (simplifies corners)
        approx = cv2.approxPolyDP(contour, epsilon=5, closed=True)
        
        # Convert points to a list of tuples
        room = [(int(point[0][0]), int(point[0][1])) for point in approx]
        room_coordinates.append(room)

    return room_coordinates

# Example Usage
image_path = r"C:\Users\Admin\Desktop\Maria Deniston\EstateConnect\Estate_App\static\plot\2D\plot.png"  # Your floor plan image
room_data = extract_room_contours(image_path)

print(room_data) 