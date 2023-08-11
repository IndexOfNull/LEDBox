def box_overlap(box1: tuple(int, int, int, int), box2: tuple(int, int, int, int)):
    '''
    Checks if the two bounding boxes overlap. Coords are given as (x1, y1, x2, y2) tuples.
    
    x1 and y1 must be less than x2 and y1 respectively.
    '''
    
    #If either box is to the left or right of each other
    if box1[2] < box2[0] or box1[0] > box2[2]:
        return False
    
    #If either box is above or below each other
    if box1[3] < box2[1] or box1[1] > box2[3]:
        return False
    
    return True