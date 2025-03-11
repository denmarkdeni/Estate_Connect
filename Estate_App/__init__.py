# import random
# import numpy as np
# import matplotlib.pyplot as plt
# from shapely.geometry import Polygon
# import ezdxf

# # Room Types and Sizes (in meters)
# ROOM_TYPES = {
#     "Living Room": (5, 4),
#     "Bedroom": (4, 4),
#     "Kitchen": (3, 3),
#     "Dining Room": (4, 3),
#     "Bathroom": (2.5, 2),
#     "Entry": (2, 2)
# }

# # Function to generate a random floor plan
# def generate_floor_plan(room_count):
#     rooms = []
#     base_x, base_y = 0, 0  # Start at (0,0)

#     for _ in range(room_count):
#         room_type = random.choice(list(ROOM_TYPES.keys()))
#         width, height = ROOM_TYPES[room_type]

#         # Random placement ensuring non-overlapping
#         x = base_x + random.randint(0, 2) * width
#         y = base_y + random.randint(0, 2) * height

#         new_room = Polygon([(x, y), (x + width, y), (x + width, y + height), (x, y + height)])

#         # Ensure no overlap
#         if all(not new_room.intersects(room) for room in rooms):
#             rooms.append(new_room)
#             plt.fill(*zip(*new_room.exterior.coords), color="lightblue", edgecolor="black")
#             plt.text(x + width / 2, y + height / 2, room_type, fontsize=8, ha="center", va="center", weight="bold")

#     return rooms

# # Function to generate DXF file
# def generate_dxf(rooms, filename="floorplan.dxf"):
#     doc = ezdxf.new()
#     msp = doc.modelspace()

#     for room in rooms:
#         points = list(room.exterior.coords)
#         for i in range(len(points) - 1):
#             msp.add_line(points[i], points[i + 1])

#     doc.saveas(filename)

# # Generate the plan
# plt.figure(figsize=(10, 6))
# plt.title("AI-Generated Floor Plan")
# rooms = generate_floor_plan(6)
# plt.axis("equal")
# plt.show()

# # Save as DXF
# generate_dxf(rooms)
# print("Floor plan generated and saved as 'floorplan.dxf'!")
import matplotlib.pyplot as plt
import random
import ezdxf

# Room types with default sizes (Width x Height)
ROOM_TYPES = {
    "Living Room": (6, 5),
    "Kitchen": (4, 4),
    "Bedroom": (5, 5),
    "Bathroom": (3, 3),
    "Dining Room": (4, 4),
    "Entry": (2, 2)
}

# Function to generate a structured 2D floor plan
def generate_floor_plan(bhk):
    rooms = []
    x_offset, y_offset = 0, 0

    # Define order for logical placement
    layout_order = ["Entry", "Living Room", "Dining Room", "Kitchen"]
    layout_order += ["Bedroom"] * bhk + ["Bathroom"]

    for room_type in layout_order:
        width, height = ROOM_TYPES[room_type]

        # Ensure bedrooms and bathrooms are placed correctly
        if "Bedroom" in room_type:
            if len(rooms) > 1 and "Bedroom" in rooms[-1][0]:
                x_offset += width  # Stack horizontally
            else:
                y_offset += height  # Stack vertically

        elif room_type == "Bathroom":
            x_offset += width  # Keep it next to a bedroom

        else:
            x_offset += width  # Place normally in a sequence

        rooms.append((room_type, x_offset, y_offset, width, height))

    return rooms

# Function to visualize the 2D floor plan
def plot_floor_plan(rooms):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for room in rooms:
        room_type, x, y, w, h = room
        ax.add_patch(plt.Rectangle((x, y), w, h, fill=True, alpha=0.4, edgecolor="black"))
        ax.text(x + w / 2, y + h / 2, room_type, ha="center", va="center", fontsize=10, fontweight="bold")

    ax.set_xlim(-2, 20)
    ax.set_ylim(-2, 15)
    ax.set_title("AI-Generated Floor Plan")
    plt.grid(True)
    plt.show()

# Function to generate DXF file for CAD editing
def export_dxf(rooms, filename="floor_plan.dxf"):
    doc = ezdxf.new()
    msp = doc.modelspace()

    for room in rooms:
        room_type, x, y, w, h = room
        msp.add_lwpolyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)], close=True)
        msp.add_text(room_type, dxfattribs={"height": 0.3}).set_pos((x + w / 2, y + h / 2))

    doc.saveas(filename)
    print(f"DXF file saved as {filename}")

# Generate & Display a Floor Plan
bhk = 3  # Example: 3BHK
floor_plan = generate_floor_plan(bhk)
plot_floor_plan(floor_plan)
export_dxf(floor_plan)
