
import socket

def get_ip():
    '''
    Returns the IP address for the system's default route.

    Returns 127.0.0.1 if no apparent IP address is present
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def box_overlap(box1: (int, int, int, int), box2: (int, int, int, int)):
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