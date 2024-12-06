function output = my_kinematics(mode, input)
    if strcmp(mode, 'ik')
        output = ik_solver(input);
    elseif strcmp(mode, 'fk')
        output = fk_solver(input);
    else
        error('Invalid mode. Use "ik" or "fk".');
    end
end

function jointAngles = ik_solver(poses)
    eulerAngles = [178, -0.0, 0];
    eulerAnglesRad = deg2rad(eulerAngles);

    robot = importrobot("E:/ras/project/project/TEST_files/Final_files/my_pro600.urdf");
    gik = generalizedInverseKinematics('RigidBodyTree', robot, 'ConstraintInputs', {'pose'});
    gik.SolverParameters.MaxIterations = 500;
    initialGuess = homeConfiguration(robot);

    numPoses = size(poses, 1);
    numJoints = numel(homeConfiguration(robot));
    jointAngles = zeros(numPoses, numJoints);

    for i = 1:numPoses
        position = poses(i, :);
        tform = eul2tform(eulerAnglesRad, 'XYZ');
        tform(1:3, 4) = position;

        poseConstraint = constraintPoseTarget('link6');
        poseConstraint.TargetTransform = tform;

        [configSoln, ~] = gik(initialGuess, poseConstraint);
        jointAngles(i, :) = rad2deg([configSoln.JointPosition]);
        initialGuess = configSoln;
    end
end

function endEffectorPose = fk_solver(jointAngles)
    robot = importrobot("E:/ras/project/project/TEST_files/Final_files/my_pro600.urdf");

    config = homeConfiguration(robot);
    for i = 1:numel(jointAngles)
        config(i).JointPosition = deg2rad(jointAngles(i));
    end

    endEffectorPose = getTransform(robot, config, 'link6');
end
