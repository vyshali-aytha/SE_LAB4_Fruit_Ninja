import math

class Fruit:
    def __init__(self, x, y, vx, vy, gravity, radius=28, kind="fruit"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.gravity = gravity
        self.radius = radius
        self.kind = kind  # "fruit" or "bomb"
        self.sliced = False

    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy

    def contains_point(self, x, y):
        # NOTE: only checks a single point against the fruit's circle.
        # A fast mouse swipe generates MOUSEMOTION events that can jump
        # from well outside the fruit to well past it between two
        # consecutive frames, so the fruit is never actually "touched"
        # by any single reported point even though the swipe visually
        # passed right through it. See Task 1 in the README.
        return math.hypot(self.x - x, self.y - y) <= self.radius

    def contains_segment(self, x1, y1, x2, y2):
        """Return True if the mouse movement segment intersects the fruit."""
        dx = x2 - x1
        dy = y2 - y1

        # Handle a mouse movement with zero length.
        if dx == 0 and dy == 0:
            return self.contains_point(x1, y1)

        # Project the fruit's center onto the mouse movement segment.
        t = ((self.x - x1) * dx + (self.y - y1) * dy) / (
            dx * dx + dy * dy
        )

        # Keep the closest point within the segment's endpoints.
        t = max(0.0, min(1.0, t))

        closest_x = x1 + t * dx
        closest_y = y1 + t * dy

        # Collision occurs when the segment comes within the fruit's radius.
        distance = math.hypot(self.x - closest_x, self.y - closest_y)
        return distance <= self.radius

    def off_screen(self, height):
        return self.y - self.radius > height
