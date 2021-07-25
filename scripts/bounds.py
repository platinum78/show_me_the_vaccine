from scripts.point import Point


class SearchBound(object):
    def __init__(self, bounds_string: str):
        bounds = [float(x) for x in bounds_string.split("%3B")]
        self.bound1 = Point(bounds[0], bounds[1])
        self.bound2 = Point(bounds[2], bounds[3])