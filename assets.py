import copy

class Vehicle:
    avg_vehicle_length = 5
    free_flow_travel_time = 0.0
    congested_travel_time = 0.0

    def __init__(self, x):
        self.x = x
        self.current_link: Link = None

    def move(self, frame_rate):
        meters_per_frame = (self.current_link.velocity * 1.60934 * 1000) / 60 / 60 / frame_rate

        if self.current_link.congestion_ahead:
            # dont move vehicle if its at the edge of the current link and about to go into a congested link or other cars are waiting in front
            temp = copy.copy(self)
            temp.x += meters_per_frame + len(temp.current_link.vehicles) * Vehicle.avg_vehicle_length
            if not self.current_link.contains(temp):
                Vehicle.congested_travel_time += (1 / frame_rate) / 60  # minutes

            else:
                # if the next link is congested but there is still room to move forward, move
                self.x += meters_per_frame
                if self.current_link.velocity < self.current_link.speed_limit:
                    # congestion time relative to how much slower than speed limit vehicles are going
                    Vehicle.congested_travel_time += (abs((self.current_link.velocity/self.current_link.speed_limit) - 1) / frame_rate) / 60  # minutes
                else:
                    Vehicle.free_flow_travel_time += (1/frame_rate)/60 #minutes

        else:
            self.x += meters_per_frame
            if self.current_link.velocity < self.current_link.speed_limit:
                # congestion time relative to how much slower than speed limit vehicles are going
                Vehicle.congested_travel_time += (abs((
                                                                  self.current_link.velocity / self.current_link.speed_limit) - 1) / frame_rate) / 60  # minutes
            else:
                Vehicle.free_flow_travel_time += (1 / frame_rate) / 60  # minutes


class Link:
    critical_density = 0.2
    def __init__(self, x_start, length):
        self.x_start = x_start
        self.length = length
        self.density = 0
        self.velocity = 0
        self.speed_limit = 60  # miles per hour
        self.vehicles = []
        self.incident_exists = False
        self.previous_link = None
        self.next_link = None
        self.congestion_ahead = False

    def update_density(self):
        """
        density = (#vehicles * vehicle_length) / Link_length -> 0-1
        cannot be greater than 1
        """
        self.density = (len(self.vehicles)*Vehicle.avg_vehicle_length) / self.length

        # increase density if there is an incident (effectively reducing road space)
        if self.incident_exists:
            self.density *= 2

    def update_velocity(self):

        # free flow if density is below critical density
        if self.density < Link.critical_density:
            self.velocity = self.speed_limit

        # else velocity if a quadratic decreasing function of density
        else:
            self.velocity = self.speed_limit * (1 - self.density ** 2)

        # cap min speed to 15 mph
        if self.velocity < 15:
            self.velocity = 15

    def contains(self, veh: Vehicle):
        """
        checks if a vehicle resides within the link
        """
        return (veh.x >= self.x_start) and (veh.x < self.x_start + self.length)


class Slider:
    # Colors
    white = (255, 255, 255)
    blue = (100, 0, 200)
    gray = (200, 200, 200)

    def __init__(self, width, height, x, y):
        # Slider parameters
        self.width = width
        self.height = height
        self.x = x
        self.y = y

        # Slider properties
        self.slider_color = Slider.blue
        self.knob_color = Slider.blue
        self.knob_radius = 10
        self.knob_x = self.x
        self.knob_y = self.y


class FlowRateSlider(Slider):

    def __init__(self, width, height, x, y):
        # Slider parameters
        super().__init__(width, height, x, y)

        self.max_flow_rate = 100  # max 100 cars pers unit min

        # Set initial slider value
        self.inflow_rate = 1

    def check_slider_update(self, mouse_x, mouse_y):
        # Check if mouse click is within the slider area to update flow rate
        if self.x <= mouse_x <= self.x + self.width and \
                self.y - (self.height // 2) <= mouse_y <= self.y + (self.height // 2):
            self.knob_x = max(min(mouse_x, self.x + self.width), self.x)
            self.inflow_rate = ((self.knob_x - self.x) / self.width) * self.max_flow_rate
            return True
        return False


class SimSpeedSlider(Slider):
    def __init__(self, width, height, x, y):
        # Slider parameters
        super().__init__(width, height, x, y)

        self.sim_speed = 1  # 1 sec (real) = 1 sec (sim)
        self.max_speed = 20  # 1 sec (real) = 20 sec (sim)

    def check_slider_update(self, mouse_x, mouse_y):
        # Check if mouse click is within the slider area to update flow rate
        if self.x <= mouse_x <= self.x + self.width and \
                self.y - (self.height // 2) <= mouse_y <= self.y + (self.height // 2):
            self.knob_x = max(min(mouse_x, self.x + self.width), self.x)
            self.sim_speed = ((self.knob_x - self.x) / self.width) * self.max_speed
            return True

        return False