import matlab.engine
import pandas as pd

# Start the MATLAB engine
eng = matlab.engine.start_matlab()

# Load target poses from CSV file
input_csv = "E:/ras/project/project/TEST_files/Final_files/mazecoord.csv"  # Replace with the path to your CSV file
poses_df = pd.read_csv(input_csv)

# Convert the DataFrame to a Python list
target_pose = poses_df[['x', 'y', 'z']].values.tolist()

# Convert Python list to MATLAB matrix
matlab_pose = matlab.double(target_pose)

# Call the MATLAB function to compute joint angles
ik_angles = eng.my_kinematics('ik', matlab_pose)

# Convert MATLAB output to Python format
ik_angles = [list(row) for row in ik_angles]

# Save the output angles to a CSV file
output_csv = "E:/ras/project/project/TEST_files/Final_files/mazeangles.csv"  # Replace with the desired output path
angles_df = pd.DataFrame(ik_angles, columns=[f'Joint{i+1}' for i in range(len(ik_angles[0]))])
angles_df.to_csv(output_csv, index=False)

print(f"Inverse Kinematics Joint Angles saved to {output_csv}")

# Stop the MATLAB engine
eng.quit()
