import matlab.engine

# Start the MATLAB engine
eng = matlab.engine.start_matlab()



target_pose = [[-0.46870182575182616, -0.2965701624608671, 0.07],
[-0.46870182575182616, -0.29793956228061853,0.07],
[-0.38354297846504124, -0.29793956228061853,0.07],
[-0.38354297846504124, -0.27876796480409826,0.07],
[-0.34872665415994686, -0.27876796480409826,0.07],
[-0.34872665415994686, -0.2792244314106821,0.07],
[-0.3482561632909591, -0.2792244314106821,0.07],
[-0.3482561632909591, -0.33400042420074,0.07],
[-0.3209676928896689, -0.3308051579546533,0.07]]


# Convert Python list to MATLAB matrix
matlab_pose = matlab.double(target_pose)
# print(matlab_pose)

# Call the MATLAB function
ik_angles = eng.my_kinematics_solver('ik', matlab_pose)
print("Inverse Kinematics Joint Angles:")
for i in ik_angles:
    print(i)

# Stop the MATLAB engine
eng.quit()