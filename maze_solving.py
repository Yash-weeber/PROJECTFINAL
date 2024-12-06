#%%
import cv2
import numpy as np
import matplotlib.pyplot as plt
import math
import os

#%%
def detect_entrance_exit(binary_img):
    # [Same as before]
    top_border = np.where(binary_img[0, :] == 255)[0]
    bottom_border = np.where(binary_img[-1, :] == 255)[0]
    left_border = np.where(binary_img[:, 0] == 255)[0]
    right_border = np.where(binary_img[:, -1] == 255)[0]

    if len(top_border) > 0:
        entrance = (0, top_border[0]+4)
    elif len(left_border) > 0:
        entrance = (left_border[0]+4, 0)
    else:
        raise ValueError("Entrance not found.")

    if len(bottom_border) > 0:
        exit_point = (binary_img.shape[0] - 1, bottom_border[0]+4)
    elif len(right_border) > 0:
        exit_point = (right_border[0]+4, binary_img.shape[1] - 1)
    else:
        raise ValueError("Exit not found.")

    return entrance, exit_point

def find_solution_path(maze_map, start, end):
    # [Same as before, with cardinal directions]
    queue = [start]
    visited = set()
    prev = {start: None}

    found_end = False

    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)

        if current == end:
            found_end = True
            break

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if (
                0 <= neighbor[0] < maze_map.shape[0]
                and 0 <= neighbor[1] < maze_map.shape[1]
                and maze_map[neighbor] == 1
                and neighbor not in visited
            ):
                queue.append(neighbor)
                prev[neighbor] = current

    if not found_end:
        raise ValueError("No path found from start to end.")

    # Reconstruct the path
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = prev[current]
    path.reverse()

    # Simplify the path to include only significant points
    simplified_path = [path[0]]  # Start with the entrance point
    last_direction = None

    # Define a threshold distance to ignore minor turns near the entrance
    entrance_threshold = 5  # Adjust as needed based on maze scale

    for i in range(1, len(path)):
        prev_point = path[i - 1]
        current_point = path[i]
        # Compute the direction vector
        direction = (current_point[0] - prev_point[0], current_point[1] - prev_point[1])

        if last_direction is None:
            last_direction = direction
            continue

        # Compute the angle between last direction and current direction
        angle = math.degrees(math.atan2(direction[1], direction[0]) - math.atan2(last_direction[1], last_direction[0]))
        angle = abs((angle + 180) % 360 - 180)  # Normalize angle to [0, 180]

        # Check if the point is beyond the entrance threshold
        distance_from_entrance = abs(current_point[0] - path[0][0]) + abs(current_point[1] - path[0][1])

        # Consider it a turn if angle exceeds threshold and beyond entrance threshold
        if angle > 10 and distance_from_entrance > entrance_threshold:
            simplified_path.append(prev_point)
            last_direction = direction

    # Add the final point
    simplified_path.append(path[-1])

    return simplified_path

def adjust_points_to_center(maze_map, points):
    dist_transform = cv2.distanceTransform(maze_map, cv2.DIST_L2, 5)
    adjusted_points = []
    window_size = 15  # Adjust based on maze size and robot size
    half_window = window_size // 2

    for point in points:
        x, y = point
        x_min = max(x - half_window, 0)
        x_max = min(x + half_window + 1, maze_map.shape[0])
        y_min = max(y - half_window, 0)
        y_max = min(y + half_window + 1, maze_map.shape[1])

        # Extract local neighborhood
        local_dist = dist_transform[x_min:x_max, y_min:y_max]
        # Find the coordinates of the maximum value in the local neighborhood
        max_idx = np.unravel_index(np.argmax(local_dist), local_dist.shape)
        # Adjust point to the position of the maximum
        new_x = x_min + max_idx[0]
        new_y = y_min + max_idx[1]

        adjusted_point = (new_x, new_y)
        adjusted_points.append(adjusted_point)

    return adjusted_points

def interpolate_points(start, end, threshold=3):
    """
    Generate intermediate points between start and end, handling diagonal movements
    and filling all gaps. Uses a threshold to infer cardinal directions.
    """
    points = []
    dx = abs(end[0] - start[0])  # Vertical difference
    dy = abs(end[1] - start[1])  # Horizontal difference

    # If already aligned, return cardinal points
    if dx == 0 or dy == 0:
        return interpolate_cardinal_points(start, end)

    # Check if within the threshold to infer alignment
    if dx <= threshold and dy > threshold:  # Approximate horizontal
        mid_point = (start[0], end[1])  # Force alignment
        return interpolate_cardinal_points(start, mid_point) + interpolate_cardinal_points(mid_point, end)
    elif dy <= threshold and dx > threshold:  # Approximate vertical
        mid_point = (end[0], start[1])  # Force alignment
        return interpolate_cardinal_points(start, mid_point) + interpolate_cardinal_points(mid_point, end)

    # For larger gaps, break into two steps
    if dx > threshold and dy > threshold:
        mid_point = (start[0], end[1])  # Break diagonally into cardinal moves
        return interpolate_cardinal_points(start, mid_point) + interpolate_cardinal_points(mid_point, end)

    # Log and raise an error if unresolvable
    print(f"Cannot resolve movement between: Start={start}, End={end}")
    raise ValueError(f"Invalid movement between {start} and {end}: Cannot interpolate.")    

def interpolate_cardinal_points(start, end):
    """
    Generate points for strictly horizontal or vertical movements.
    """
    points = []
    if start[0] == end[0]:  # Horizontal movement
        step = 1 if start[1] < end[1] else -1
        for y in range(start[1], end[1] + step, step):
            points.append((start[0], y))
    elif start[1] == end[1]:  # Vertical movement
        step = 1 if start[0] < end[0] else -1
        for x in range(start[0], end[0] + step, step):
            points.append((x, start[1]))
    return points

def refine_path(path, threshold=3):
    """
    Refine the path to ensure all points are aligned along cardinal directions,
    filling any gaps with intermediate points using a threshold.
    """
    refined_path = [path[0]]  # Start with the first point
    for i in range(1, len(path)):
        prev = refined_path[-1]
        curr = path[i]
        if prev[0] == curr[0] or prev[1] == curr[1]:  # Aligned
            refined_path.append(curr)
        else:  # Gap detected, interpolate points
            interpolated = interpolate_points(prev, curr, threshold)
            refined_path.extend(interpolated[1:])  # Skip the first point to avoid duplication
    return refined_path

def save_path_instructions(path, file_append, robot_width=192):
    """
    Generate movement instructions from the refined path, scaled to the robot's block size.
    """
    path = refine_path(path)  # Ensure path is refined
    instructions = []
    pixels_in_direction = 0  # Counter for pixels moved in the current direction
    current_direction = None

    for i in range(1, len(path)):
        prev = path[i - 1]
        curr = path[i]

        # Determine the direction of movement
        if curr[0] == prev[0]:  # Horizontal movement
            new_direction = "Right" if curr[1] > prev[1] else "Left"
        elif curr[1] == prev[1]:  # Vertical movement
            new_direction = "Down" if curr[0] > prev[0] else "Up"
        else:
            raise ValueError(f"Invalid movement detected between {prev} and {curr}: Diagonal movement is not allowed.")

        if current_direction is None:  # First step, initialize direction
            current_direction = new_direction
        elif new_direction == current_direction:  # Continue in the same direction
            pixels_in_direction += abs(curr[0] - prev[0] + curr[1] - prev[1])
        else:  # Direction change (turn detected)
            # Add the "Go Straight" instruction scaled to the robot's width
            blocks = max(1, pixels_in_direction // robot_width)  # Ensure at least 1 block
            instructions.append(f"Go Straight {blocks} Block{'s' if blocks > 1 else ''}")

            # Add the turn instruction
            turn_direction = determine_turn(current_direction, new_direction)
            instructions.append(f"Turn {turn_direction}")

            # Reset for the new direction
            current_direction = new_direction
            pixels_in_direction = abs(curr[0] - prev[0] + curr[1] - prev[1])

    # Add the final "Go Straight" instruction
    if pixels_in_direction > 0:
        blocks = max(1, pixels_in_direction // robot_width)
        instructions.append(f"Go Straight {blocks} Block{'s' if blocks > 1 else ''}")

    # Save instructions to a file
    file_save = f"./path_instructions_{file_append}.txt"
    with open(file_save, "w") as f:
        f.write("\n".join(instructions))

    return instructions

def determine_turn(prev_direction, new_direction):
    """
    Determine whether the turn is Left or Right based on the direction change.
    """
    turn_map = {
        ("Up", "Right"): "Right",
        ("Right", "Down"): "Right",
        ("Down", "Left"): "Right",
        ("Left", "Up"): "Right",
        ("Up", "Left"): "Left",
        ("Left", "Down"): "Left",
        ("Down", "Right"): "Left",
        ("Right", "Up"): "Left",
    }

    # Return the turn direction or log an error for unknown cases
    if (prev_direction, new_direction) in turn_map:
        return turn_map[(prev_direction, new_direction)]
    else:
        print(f"Unknown turn detected: from {prev_direction} to {new_direction}")
        return "Unknown"

#%%
def main():
    # Load the maze image
    img_name = "captured_frame_1733340407.png"  # Replace with your maze image
    img = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE)
    
    
    
    modified_img = cv2.convertScaleAbs(img, alpha=1.5, beta=-150)    
    cv2.imshow('modified Image', modified_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # Threshold the image to binary
    _, binary_img = cv2.threshold(modified_img, 127, 255, cv2.THRESH_BINARY)
    cv2.imshow('Binary Image', binary_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Dilate the walls to consider the robot's size
    robot_size =  35# Size of the robot in pixels
    kernel_size = int(np.ceil(robot_size / 2))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    dilated_walls = cv2.dilate(255 - binary_img, kernel, iterations=1)
    adjusted_maze = 255 - dilated_walls
    
    cv2.imshow('Adjusted maze', adjusted_maze)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Detect entrance and exit on the adjusted maze
    entrance, exit_point = detect_entrance_exit(adjusted_maze)
    print(f"Entrance: {entrance}, Exit: {exit_point}")

    # Create the maze map
    maze_map = (adjusted_maze // 255).astype(np.uint8)

    # Ensure the entrance and exit are open
    maze_map[entrance] = 1
    maze_map[exit_point] = 1

    # Find the solution path
    try:
        simplified_path = find_solution_path(maze_map, entrance, exit_point)
    except ValueError as e:
        print(e)
        return

    # Adjust only the significant points (simplified path)
    adjusted_points = adjust_points_to_center(maze_map, simplified_path)

    # Ensure adjusted points are aligned along cardinal directions
    aligned_points = [adjusted_points[0]]
    for i in range(1, len(adjusted_points) - 1):
        prev_point = aligned_points[-1]
        curr_point = adjusted_points[i]
        next_point = adjusted_points[i + 1]

        # Align curr_point to be either same row or same column as prev_point
        if prev_point[0] == next_point[0]:  # Horizontal line
            aligned_point = (prev_point[0], curr_point[1])
        elif prev_point[1] == next_point[1]:  # Vertical line
            aligned_point = (curr_point[0], prev_point[1])
        else:
            # Decide based on the majority direction
            if abs(prev_point[0] - curr_point[0]) > abs(prev_point[1] - curr_point[1]):
                aligned_point = (curr_point[0], prev_point[1])
            else:
                aligned_point = (prev_point[0], curr_point[1])
        aligned_points.append(aligned_point)
    aligned_points.append(adjusted_points[-1])  # Add the last point

    # Visualize the solution path
    solution_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # Draw the path as straight lines between aligned points
    for i in range(len(aligned_points) - 1):
        pt1 = (aligned_points[i][1], aligned_points[i][0])  # (x, y) format
        pt2 = (aligned_points[i + 1][1], aligned_points[i + 1][0])
        cv2.line(solution_img, pt1, pt2, (0, 0, 255), thickness=1)

    # Draw the turn points
    for point in aligned_points[1:-1]:  # Exclude start and end
        x, y = point
        cv2.circle(solution_img, (y, x), 1, (0, 255, 0), -1)  # Green circles at turns
        print(f"x coordinate: {x}, y coordniate: {y}")

    # Draw entrance and exit points
    cv2.circle(solution_img, (entrance[1], entrance[0]), 1, (255, 0, 0), -1)  # Blue circle for entrance
    cv2.circle(solution_img, (exit_point[1], exit_point[0]), 1, (255, 0, 0), -1)  # Blue circle for exit


    aligned_points = list(dict.fromkeys(aligned_points))

    save_path_instructions(aligned_points[0:], file_append=img_name)

    # Show and save the solution image
    plt.imshow(solution_img)
    plt.axis('off')
    plt.title('Solution Path with Perfectly Straight Lines')
    plt.show()

if __name__ == "__main__":
    main()
# %%
