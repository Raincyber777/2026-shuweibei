# -*- coding: utf-8 -*-
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import q4_lib4  # noqa: F401  (sets sys.path for 第二题/code)
from q2_lib import travel_time, path_length, wrap180
print("wrap180(-8.81) =", wrap180(-8.81))
print("travel (14,86)->(14.1,86):", travel_time((14.0, 86.0), (14.1, 86.0)))
print("travel (88,68)->(86.9,70.9):", travel_time((88.0, 68.0), (86.9, 70.9)))
print("path (14,86)->(14.1,86):", path_length((14.0, 86.0), (14.1, 86.0)))
print("travel (50,93)->(49.9,92.8):", travel_time((50.0, 93.0), (49.9, 92.8)))
print("travel (15,14)->(14.8,14.3):", travel_time((15.0, 14.0), (14.8, 14.3)))
import q2_lib
print("q2_lib file:", q2_lib.__file__)
import inspect
src = inspect.getsource(q2_lib._seg_hits_rect)
print(src)
