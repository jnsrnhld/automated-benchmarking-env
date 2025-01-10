from xml.etree import ElementTree as ET

# Paths to the individual SVG files
svg_files = [
    "executor_count_3-min_target.svg",
    "executor_count_9-min_target.svg",
    "executor_count_5-min_target.svg"
]

# Create a new SVG root
merged_svg = ET.Element('svg', xmlns="http://www.w3.org/2000/svg", version="1.1")
y_offset = 0  # Track the vertical offset for stacking
vertical_margin = 10  # Margin between plots in pixels
padding_x = 20  # Extra padding on the left and right for x-axis
padding_y = 70  # Bottom padding for individual plots
bottom_buffer = 30  # Additional buffer for the bottom of the merged SVG

def parse_dimension(value):
    """Convert SVG dimension string (e.g., '216pt') to an integer."""
    if value.endswith("pt"):
        return int(float(value.replace("pt", "")) * 1.333)  # Convert points to pixels
    elif value.endswith("px"):
        return int(float(value.replace("px", "")))  # Pixels are directly convertible
    else:
        raise ValueError(f"Unknown unit in dimension: {value}")

def get_bounding_box(svg_root):
    """Calculate the bounding box of the content inside an SVG."""
    min_y, max_y = float('inf'), float('-inf')
    for elem in svg_root.iter():
        if 'y' in elem.attrib and 'height' in elem.attrib:
            y = float(elem.attrib['y'])
            height = float(elem.attrib['height'])
            min_y = min(min_y, y)
            max_y = max(max_y, y + height)
    return max_y - min_y if min_y < float('inf') else None

for svg_file in svg_files:
    # Parse the individual SVG
    tree = ET.parse(svg_file)
    root = tree.getroot()

    # Extract width and height
    width = root.attrib.get("width", "1200px")  # Default width
    height = root.attrib.get("height", "300px")  # Default height
    width = parse_dimension(width) + padding_x * 2  # Add x-axis padding
    height = parse_dimension(height)  # Ensure height is an integer

    # Trim the content to remove whitespace and add padding
    bbox_height = get_bounding_box(root)
    if bbox_height:
        height = bbox_height + padding_y  # Add bottom padding to ensure x-axis is fully visible

    # Create a group to hold this SVG and apply vertical translation
    group = ET.Element("g", transform=f"translate(0, {y_offset})")

    # Add all children from the original SVG to the group
    for child in list(root):
        group.append(child)

    # Add this group to the merged SVG
    merged_svg.append(group)

    # Update the offset for the next SVG
    y_offset += height + vertical_margin

# Set the overall size of the merged SVG with extra bottom buffer
merged_svg.set("width", str(width))
merged_svg.set("height", str(y_offset - vertical_margin + bottom_buffer))  # Add bottom buffer for last plot

# Save the merged SVG
merged_tree = ET.ElementTree(merged_svg)
merged_tree.write("merged_executor_plots_final.svg")

print("Merged SVG saved as 'merged_executor_plots_final.svg'")
