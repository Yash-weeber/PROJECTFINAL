def savePointsInCSV(points):
    with open("E:/ras/project/project/TEST_files/demotest/Final Project/Final Project/Robot/InterpolationPoints.csv", 'w') as f:
        for point in points:
            f.write(f'{point[0]},{point[1]}/n')