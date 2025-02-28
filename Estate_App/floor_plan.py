import svgwrite,random

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