import numpy as np

def normalize(vec):
    v = np.array(vec)
    return (v / np.linalg.norm(v)).tolist()
