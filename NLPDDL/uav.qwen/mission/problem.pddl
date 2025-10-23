Do not write any additional information or comments.

Response: domain uav = {
    initial = uav is on ground,
    action = takeoff,
    action = move forward,
    action = land,
    object = uav,
    effect = uav is in the air,
    precondition = uav is on ground,
    effect = uav is 200m away,
    precondition = uav is in the air,
    goal = uav is on ground
};