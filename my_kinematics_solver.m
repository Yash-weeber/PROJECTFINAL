function output = my_kinematics_solver(mode, input)
    if strcmp(mode, 'ik')
        output = ik_solver(input);
    elseif strcmp(mode, 'fk')
        output = fk_solver(input);
    else
        error('Invalid mode. Use "ik" or "fk".');
    end
end

function jointAngles = ik_solver(poses)
    eulerAngles = [178  , -0.0, 0];
    eulerAnglesRad = deg2rad(eulerAngles);
    % tform = eul2tform(eulerAnglesRad, 'XYZ');
    % tform(1:3, 4) = poses;
    robot = importrobot('E:\RASLAB\project\structure\my_pro600.urdf');

    gik = generalizedInverseKinematics('RigidBodyTree', robot, 'ConstraintInputs', {'pose'});
    gik.SolverParameters.MaxIterations = 500;
    % poseConstraint = constraintPoseTarget('link6');
    % poseConstraint.TargetTransform = tform;
    initialGuess = homeConfiguration(robot);

    % disp(initialGuess.JointPosition);

    numPoses = size(poses, 1);
    numJoints = numel(homeConfiguration(robot));
    jointAngles = zeros(numPoses, numJoints);
    % disp(poses);
    % Iterate over each pose
    for i = 1:numPoses
        % disp(i);
        % Extract position and orientation from the current pose row
        position = poses(i, :);
        tform = eul2tform(eulerAnglesRad, 'XYZ');
        tform(1:3, 4) = position;
        % disp(position);

        % Define the pose constraint for the current row
        poseConstraint = constraintPoseTarget('link6');
        poseConstraint.TargetTransform = tform;

        % Solve for joint configurations
        [configSoln, ~] = gik(initialGuess, poseConstraint);

        % Store the joint angles in the result matrix
        jointAngles(i, :) = rad2deg([configSoln.JointPosition]);
        initialGuess = configSoln;
    end
end


function endEffectorPose = fk_solver(jointAngles)
    % Load a predefined robot model
    robot = importrobot("E:\RASLAB\project\structure\my_pro600.urdf"); % Replace with your robot model if different

    % Assign joint angles to the robot's configuration
    config = homeConfiguration(robot);
    for i = 1:numel(jointAngles)
        config(i).JointPosition = deg2rad(jointAngles(i));
    end

    % Compute the forward kinematics (end-effector pose)
    endEffectorPose = getTransform(robot, config, 'link6');
end