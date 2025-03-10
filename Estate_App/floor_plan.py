import svgwrite,random
from django.http import HttpResponse
import xml.etree.ElementTree as ET
from django.shortcuts import render
from django.http import JsonResponse

def generate_floor_plan():
    """Generate a simple 2D floor plan using SVG."""
    dwg = svgwrite.Drawing(size=("500px", "500px"))
    
    # Define the walls (rectangles)
    dwg.add(dwg.rect(insert=(50, 50), size=(400, 300), stroke="black", fill="none", stroke_width=3))

    # Add a door (simple line)
    dwg.add(dwg.line(start=(50, 200), end=(90, 200), stroke="blue", stroke_width=3))
    
    # Add a window (simple line)
    dwg.add(dwg.line(start=(300, 50), end=(350, 50), stroke="green", stroke_width=3))

    return dwg.tostring()

def generate_dynamic_floor_plan(rooms, room_width, room_height):
    """Generate a 2D floor plan dynamically based on user input."""
    dwg = svgwrite.Drawing(size=("600px", "400px"))
    
    x_offset = 50
    y_offset = 50

    for i in range(rooms):
        # Create room
        dwg.add(dwg.rect(insert=(x_offset, y_offset), 
                         size=(room_width, room_height), 
                         stroke="black", 
                         fill="none", 
                         stroke_width=3))

        # Add a door
        dwg.add(dwg.line(start=(x_offset, y_offset + room_height - 10), 
                         end=(x_offset + 30, y_offset + room_height - 10), 
                         stroke="blue", stroke_width=3))

        # Add a window
        dwg.add(dwg.line(start=(x_offset + room_width - 40, y_offset), 
                         end=(x_offset + room_width - 10, y_offset), 
                         stroke="green", stroke_width=3))

        # Move to the next room
        x_offset += room_width + 20  

    return dwg.tostring()

def generate_realistic_floor_plan():
    """Generate a house-like 2D floor plan dynamically."""
    dwg = svgwrite.Drawing(size=("800px", "600px"))

    # Define house layout (room name, x, y, width, height)
    rooms = [
        ("Living Room", 50, 50, 250, 200),
        ("Kitchen", 320, 50, 200, 200),
        ("Bedroom 1", 50, 270, 200, 200),
        ("Bedroom 2", 270, 270, 200, 200),
        ("Bathroom", 500, 270, 100, 100),
    ]

    # Draw the rooms
    for room in rooms:
        name, x, y, width, height = room

        # Draw walls
        dwg.add(dwg.rect(insert=(x, y), size=(width, height), 
                         stroke="black", fill="none", stroke_width=3))

        # Add room name
        dwg.add(dwg.text(name, insert=(x + 10, y + 20), font_size="16px", fill="black"))

        # Randomly place a door (for simplicity, one per room)
        door_x = x + random.randint(20, width - 40)
        door_y = y + height if random.choice([True, False]) else y  # Bottom or Top
        dwg.add(dwg.line(start=(door_x, door_y), 
                         end=(door_x + 30, door_y), 
                         stroke="blue", stroke_width=3))

        # Randomly place a window
        window_x = x + width if random.choice([True, False]) else x  # Left or Right
        window_y = y + random.randint(20, height - 40)
        dwg.add(dwg.line(start=(window_x, window_y), 
                         end=(window_x, window_y + 30), 
                         stroke="green", stroke_width=3))

    return dwg.tostring()

def generate_blueprin(request):
    floor_plan = [
        {
            "name": "Living Room",
            "x": 50, "y": 50, "width": 300, "height": 200,
            "walls": [{"x1": 50, "y1": 50, "x2": 350, "y2": 50}],
            "doors": [{"x": 170, "y": 50, "width": 60, "height": 10, "type": "swing"}],
            "windows": [{"x": 300, "y": 100, "width": 40, "height": 10}]
        },
        {
            "name": "Kitchen",
            "x": 50, "y": 260, "width": 200, "height": 150,
            "walls": [{"x1": 50, "y1": 260, "x2": 250, "y2": 260}],
            "doors": [{"x": 150, "y": 260, "width": 40, "height": 10, "type": "swing"}],
            "windows": [{"x": 180, "y": 260, "width": 40, "height": 10}]
        },
        {
            "name": "Hall Room",
            "x": 350, "y": 50, "width": 300, "height": 200,
            "walls": [{"x1": 350, "y1": 50, "x2": 450, "y2": 50}],
            "doors": [{"x": 170, "y": 50, "width": 60, "height": 10, "type": "swing"}],
            "windows": [{"x": 300, "y": 100, "width": 40, "height": 10}]
        },
        {
            "name": "Living Room 2",
            "x": 250, "y": 260, "width": 200, "height": 150,
            "walls": [{"x1": 250, "y1": 260, "x2": 450, "y2": 260}],
            "doors": [{"x": 150, "y": 260, "width": 40, "height": 10, "type": "swing"}],
            "windows": [{"x": 180, "y": 260, "width": 40, "height": 10}]
        }
    ]
    
    # Create SVG
    svg = ET.Element("svg", width="800", height="600", xmlns="http://www.w3.org/2000/svg")

    # Draw grid
    for i in range(0, 800, 50):
        ET.SubElement(svg, "line", x1=str(i), y1="0", x2=str(i), y2="600", stroke="#ddd", stroke_width="1")
    for j in range(0, 600, 50):
        ET.SubElement(svg, "line", x1="0", y1=str(j), x2="800", y2=str(j), stroke="#ddd", stroke_width="1")

    # Draw rooms
    for room in floor_plan:
        ET.SubElement(svg, "rect", x=str(room["x"]), y=str(room["y"]), 
                      width=str(room["width"]), height=str(room["height"]),
                      stroke="black", fill="none", stroke_width="3")

        # Room name
        ET.SubElement(svg, "text", x=str(room["x"] + 10), y=str(room["y"] + 20),
                      font_size="14", fill="black").text = room["name"]

        # Draw walls
        for wall in room["walls"]:
            ET.SubElement(svg, "line", x1=str(wall["x1"]), y1=str(wall["y1"]), 
                          x2=str(wall["x2"]), y2=str(wall["y2"]), 
                          stroke="black", stroke_width="5")

        # Draw doors
        for door in room["doors"]:
            ET.SubElement(svg, "rect", x=str(door["x"]), y=str(door["y"]),
                          width=str(door["width"]), height=str(door["height"]),
                          stroke="brown", fill="none", stroke_width="3")

        # Draw windows
        for window in room["windows"]:
            ET.SubElement(svg, "rect", x=str(window["x"]), y=str(window["y"]),
                          width=str(window["width"]), height=str(window["height"]),
                          stroke="blue", fill="none", stroke_width="3")

    # Convert to string & return response
    svg_data = ET.tostring(svg).decode()
    return HttpResponse(svg_data, content_type="image/svg+xml")


def generate_blueprint(request):
    # Get room details from GET request
    room_names = request.GET.getlist("name")
    widths = request.GET.getlist("width")
    heights = request.GET.getlist("height")
    x_positions = request.GET.getlist("x")
    y_positions = request.GET.getlist("y")

    num_rooms = min(len(room_names), len(widths), len(heights), len(x_positions), len(y_positions))

    # Create SVG
    svg = ET.Element("svg", width="800", height="600", xmlns="http://www.w3.org/2000/svg")

    # Draw grid
    for i in range(0, 800, 50):
        ET.SubElement(svg, "line", x1=str(i), y1="0", x2=str(i), y2="600", stroke="#ddd", stroke_width="1")
    for j in range(0, 600, 50):
        ET.SubElement(svg, "line", x1="0", y1=str(j), x2="800", y2=str(j), stroke="#ddd", stroke_width="1")

    # **Fix: Properly Iterate Through All Rooms**
    for i in range(num_rooms):
        try:
            name = room_names[i]
            width = int(widths[i])
            height = int(heights[i])
            x = int(x_positions[i])
            y = int(y_positions[i])

            # Draw Room (Rectangle)
            ET.SubElement(svg, "rect", x=str(x), y=str(y), 
                        width=str(width), height=str(height),
                        stroke="black", fill="lightblue", stroke_width="3")

            # Room Name (Text)
            ET.SubElement(svg, "text", x=str(x + 10), y=str(y + 20),
                        font_size="14", fill="black").text = name
        except Exception as e:
            print(f"Error processing room {i}: {e}")

    # Convert SVG to string
    svg_data = '<?xml version="1.0" encoding="UTF-8"?>' + ET.tostring(svg, encoding="unicode")

    return render(request, "blueprint_form.html", {"svg_data": svg_data})

def generate_3d(request):
    room_names = request.GET.getlist("name")
    widths = request.GET.getlist("width")
    heights = request.GET.getlist("height")
    x_positions = request.GET.getlist("x")
    y_positions = request.GET.getlist("y")

    num_rooms = min(len(room_names), len(widths), len(heights), len(x_positions), len(y_positions))

    rooms = []
    for i in range(num_rooms):
        try: 
            rooms.append({
                "name": room_names[i],
                "width": int(widths[i]),
                "height": int(heights[i]),
                "x": int(x_positions[i]),
                "y": int(y_positions[i])
            })
        except Exception as e:
            print(f"Error processing room {i}: {e}")
    print("Generated Blueprint Data:", rooms)
    return JsonResponse({"rooms": rooms})
