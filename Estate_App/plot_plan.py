import random
import numpy as np
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import ezdxf
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Room types with standard sizes (Width x Height in meters)
ROOM_TYPES = {
    "Living Room": (6, 5),
    "Kitchen": (4, 4),
    "Bedroom": (5, 5),
    "Bathroom": (3, 3),
    "Dining Room": (4, 4),
    "Entry": (2, 2)
}

DOOR_WIDTH = 1
WINDOW_WIDTH = 1.5

def generate_floor_plan(room_counts):
    rooms = []
    placed_rooms = []
    
    # Generate layout order dynamically
    layout_order = []

    # Add essential rooms first
    layout_order += ["Entry"] * room_counts["Entry"]
    layout_order += ["Living Room"] * room_counts["Living Room"]
    layout_order += ["Dining Room"] * room_counts["Dining Room"]
    layout_order += ["Kitchen"] * room_counts["Kitchen"]

    # Generate bedrooms & bathrooms dynamically
    bedrooms = ["Bedroom"] * room_counts["Bedroom"]
    bathrooms = ["Bathroom"] * room_counts["Bathroom"]

    # Shuffle the bedrooms & bathrooms to randomize placement
    random.shuffle(bedrooms)
    random.shuffle(bathrooms)

    # Add bedrooms and bathrooms to the layout order
    layout_order += bedrooms + bathrooms

    # Start with Entry at (0,0)
    x_offset, y_offset = 0, 0
    rooms.append(("Entry", x_offset, y_offset, *ROOM_TYPES["Entry"]))
    placed_rooms.append(("Entry", x_offset, y_offset, *ROOM_TYPES["Entry"]))

    max_x, max_y = ROOM_TYPES["Entry"]  # Ensure initialized properly

    for room_type in layout_order[1:]:  # Skip Entry since it's placed
        width, height = ROOM_TYPES[room_type]
        placed = False

        for _ in range(500):  # Try more times to ensure placement
            # Pick a random existing room to attach to
            anchor = random.choice(placed_rooms)
            ax, ay, aw, ah = anchor[1], anchor[2], anchor[3], anchor[4]

            # Possible placements (ensure no gaps)
            possible_positions = [
                (ax + aw, ay),  # Right
                (ax, ay + ah),  # Bottom
                (ax - width, ay),  # Left
                (ax, ay - height)  # Top
            ]
            random.shuffle(possible_positions)

            for x_offset, y_offset in possible_positions:
                new_room = Polygon([(x_offset+1, y_offset+1), 
                                    (x_offset + width+1, y_offset+1),
                                    (x_offset + width+1, y_offset + height+1), 
                                    (x_offset+1, y_offset + height+1)])

                # Ensure no overlap
                if all(not new_room.intersects(Polygon([(r[1], r[2]), 
                                                        (r[1] + r[3], r[2]),
                                                        (r[1] + r[3], r[2] + r[4]), 
                                                        (r[1], r[2] + r[4])])) 
                       for r in placed_rooms):
                    placed = True
                    break  # Stop searching once valid position is found

            if placed:
                break  # Stop retrying if placed successfully

        if placed:
            rooms.append((room_type, x_offset, y_offset, width, height))
            placed_rooms.append((room_type, x_offset, y_offset, width, height))

            # Update max_x and max_y correctly
            max_x = max(max_x, x_offset + width)
            max_y = max(max_y, y_offset + height)
        else:
            print(f"⚠️ Could not place {room_type}, skipping!")

    return rooms, max_x, max_y

# Function to visualize the 2D floor plan
def plot_floor_plan(rooms, max_x, max_y):
    fig, ax = plt.subplots(figsize=(12, 8))

    doors = add_doors(rooms) # Get doors
    windows = add_windows(rooms, max_x, max_y)  # Get windows

    for room in rooms:
        room_type, x, y, w, h = room

        # Draw Room
        ax.add_patch(plt.Rectangle((x, y), w, h, fill=True, alpha=0.5, edgecolor="black"))
        ax.text(x + w / 2, y + h / 2, room_type, ha="center", va="center", fontsize=10, fontweight="bold")

    for door_x, door_y, orientation in doors:
        if orientation == "horizontal":
            ax.plot([door_x - 0.3, door_x + 0.3], [door_y, door_y], color="brown", linewidth=3)  # Horizontal door
        else:
            ax.plot([door_x, door_x], [door_y - 0.3, door_y + 0.3], color="brown", linewidth=3)  # Vertical door

     # Draw windows (dashed blue lines)
    for window_x, window_y, orientation in windows:
        if orientation == "horizontal":
            ax.plot([window_x - 0.3, window_x + 0.3], [window_y, window_y], color="blue", linestyle="dashed", linewidth=2)
        else:
            ax.plot([window_x, window_x], [window_y - 0.3, window_y + 0.3], color="blue", linestyle="dashed", linewidth=2)

    # Draw outer boundary
    ax.plot([-0.5, max_x+0.5, max_x+0.5, -0.5, -0.5], [-0.5, -0.5, max_y+0.5, max_y+0.5, -0.5], color="red", linewidth=2)

    ax.set_xlim(-1, max_x + 2)
    ax.set_ylim(-1, max_y + 2)
    ax.set_title("AI-Generated Floor Plan")
    ax.set_aspect("equal")
    # plt.grid(True)
    # plt.show()
    plt.savefig(r"C:\Users\Admin\Desktop\Maria Deniston\EstateConnect\Estate_App\static\plot\2D\plot.png")  
    plt.close(fig)
    print("2D Floor Plan saved as plot.png")

def add_doors(rooms):
    doors = []  # Store door positions

    # Convert room data into a list of dictionaries for easy access
    room_data = []
    for room in rooms:
        room_type, x, y, w, h = room
        room_data.append({"type": room_type, "x": x, "y": y, "w": w, "h": h})

    # Sort rooms by position (left to right, top to bottom)
    room_data.sort(key=lambda r: (r["y"], r["x"]))

    for i, room in enumerate(room_data):
        x, y, w, h = room["x"], room["y"], room["w"], room["h"]

        # Check for horizontal neighbor (right-side room)
        for neighbor in room_data:
            if neighbor["x"] == x + w and neighbor["y"] == y:  # Same Y, right-side
                door_x = x + w  # Door on right wall
                door_y = y + h / 2  # Middle of shared vertical wall
                doors.append((door_x, door_y, "vertical"))

        # Check for vertical neighbor (above room)
        for neighbor in room_data:
            if neighbor["y"] == y + h and neighbor["x"] == x:  # Same X, room above
                door_x = x + w / 2  # Middle of shared horizontal wall
                door_y = y + h  # Door at top
                doors.append((door_x, door_y, "horizontal"))

    # Add main entrance (bottom of first room)
    first_room = room_data[0]
    entry_x = first_room["x"] + first_room["w"] / 2
    entry_y = first_room["y"]  # Entry at bottom
    doors.append((entry_x, entry_y, "horizontal"))

    return doors

def add_windows(rooms, max_x, max_y, entry_room_type="Entry"):
    windows = []  # Store window positions

    for i, room in enumerate(rooms):
        room_type, x, y, w, h = room
        possible_sides = []  # Store walls where windows can be placed

        # Skip entry room (no windows in entry)
        if room_type == entry_room_type:
            continue

        # Check for neighbors (other rooms touching this one)
        has_left_neighbor = any(other_x + other_w == x and other_y < y + h and other_y + other_h > y for _, other_x, other_y, other_w, other_h in rooms)
        has_right_neighbor = any(other_x == x + w and other_y < y + h and other_y + other_h > y for _, other_x, other_y, other_w, other_h in rooms)
        has_bottom_neighbor = any(other_y + other_h == y and other_x < x + w and other_x + other_w > x for _, other_x, other_y, other_w, other_h in rooms)
        has_top_neighbor = any(other_y == y + h and other_x < x + w and other_x + other_w > x for _, other_x, other_y, other_w, other_h in rooms)

        # Only add windows on sides without neighbors
        if not has_left_neighbor:
            possible_sides.append("left")
        if not has_right_neighbor:
            possible_sides.append("right")
        if not has_bottom_neighbor:
            possible_sides.append("bottom")
        if not has_top_neighbor:
            possible_sides.append("top")

        # Randomly choose 1 or 2 sides for windows
        chosen_sides = random.sample(possible_sides, min(len(possible_sides), 2))

        for side in chosen_sides:
            if side == "left":
                window_x = x  # Left edge
                window_y = y + h / 2  # Middle of the left wall
                windows.append((window_x, window_y, "vertical"))

            elif side == "right":
                window_x = x + w  # Right edge
                window_y = y + h / 2
                windows.append((window_x, window_y, "vertical"))

            elif side == "bottom":
                window_x = x + w / 2  # Middle of bottom wall
                window_y = y
                windows.append((window_x, window_y, "horizontal"))

            elif side == "top":
                window_x = x + w / 2
                window_y = y + h
                windows.append((window_x, window_y, "horizontal"))

    return windows

# Function to generate DXF file for CAD editing
def export_dxf(rooms, max_x, max_y, filename="floor_plan.dxf"):
    doc = ezdxf.new()
    msp = doc.modelspace()

    for room in rooms:
        room_type, x, y, w, h = room
        # Draw room walls
        msp.add_lwpolyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)], close=True)

        # Add room label
        msp.add_text(room_type, dxfattribs={"height": 0.5}).set_placement((x + w / 2, y + h / 2))

        # Add door (simple line)
        door_x = x + w - 0.5
        door_y = y + h / 2
        msp.add_line((door_x, door_y), (door_x + DOOR_WIDTH, door_y))

        # Add window (dashed line)
        window_x = x + w / 2
        window_y = y + h
        msp.add_line((window_x, window_y), (window_x + WINDOW_WIDTH, window_y))

    # Add outer boundary
    msp.add_lwpolyline([(0, 0), (max_x, 0), (max_x, max_y), (0, max_y), (0, 0)], close=True, dxfattribs={"color": 1})

    doc.saveas(filename)
    print(f"DXF file saved as {filename}")

def get_room_counts():
    room_counts = {}

    # Get user inputs dynamically
    room_counts["Entry"] = 1  # Always 1 entry room
    room_counts["Living Room"] = int(input("Enter number of Living Rooms: "))
    room_counts["Dining Room"] = int(input("Enter number of Dining Rooms: "))
    room_counts["Kitchen"] = int(input("Enter number of Kitchens: "))
    room_counts["Bedroom"] = int(input("Enter number of Bedrooms: "))
    room_counts["Bathroom"] = int(input("Enter number of Bathrooms: "))

    return room_counts

def plot_3d_floor_plan(rooms, max_x, max_y, wall_height=2):
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')

    for room in rooms:
        room_type, x, y, w, h = room

        # 2D base points (floor level)
        base_points = np.array([
            [x, y, 0],      # Bottom-left
            [x + w, y, 0],  # Bottom-right
            [x + w, y + h, 0],  # Top-right
            [x, y + h, 0]   # Top-left
        ])

        # Extrude to 3D (wall height)
        top_points = base_points.copy()
        top_points[:, 2] = wall_height  # Raise Z-axis to wall height

        # Define faces for each wall
        faces = [
            [base_points[0], base_points[1], top_points[1], top_points[0]],  # Front wall
            [base_points[1], base_points[2], top_points[2], top_points[1]],  # Right wall
            [base_points[2], base_points[3], top_points[3], top_points[2]],  # Back wall
            [base_points[3], base_points[0], top_points[0], top_points[3]],  # Left wall
            [top_points[0], top_points[1], top_points[2], top_points[3]],    # Ceiling
        ]
        print(faces)

        # Add walls to 3D plot
        ax.add_collection3d(Poly3DCollection(faces, color='skyblue', alpha=0.6, edgecolor='black'))

        # Label room in 3D
        ax.text(x + w / 2, y + h / 2, wall_height + 0.2, room_type, ha='center', fontsize=10, color='black')

    # Draw ground (floor) at Z=0
    ax.add_collection3d(Poly3DCollection(
        [[
            [0, 0, 0], [max_x, 0, 0], [max_x, max_y, 0], [0, max_y, 0]
        ]], color='gray', alpha=0.3))

    ax.set_xlabel("X Axis")
    ax.set_ylabel("Y Axis")
    ax.set_zlabel("Height (m)")
    ax.set_title("3D Floor Plan")

    # Set limits
    ax.set_xlim(0, max_x)
    ax.set_ylim(0, max_y)
    ax.set_zlim(0, wall_height + 1)

    # plt.show()
    plt.savefig(r"C:\Users\Admin\Desktop\Maria Deniston\EstateConnect\Estate_App\static\plot\3D\plot.png")  
    plt.close()
    print("3D Floor Plan saved as plot.png")


# rooms_count = get_room_counts()
# floor_plan, max_x, max_y = generate_floor_plan(rooms_count)
# plot_floor_plan(floor_plan, max_x, max_y)
# export_dxf(floor_plan, max_x, max_y)
# plot_3d_floor_plan(floor_plan, max_x, max_y)