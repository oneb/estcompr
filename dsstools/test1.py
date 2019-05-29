import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import comb

k = comb.amp_count(3/4, 0.999)
print(k)
