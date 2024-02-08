import math

def get_distance(pos1:tuple[int|float, int|float], pos2:tuple[int|float, int|float]):
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    