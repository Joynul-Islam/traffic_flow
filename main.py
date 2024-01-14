import pygame
import numpy as np
from assets import Vehicle, Link, FlowRateSlider, SimSpeedSlider

# Initialize pygame
pygame.init()

# Set up display
width, height = 1200, 500
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Traffic Flow Model")

# Pygame clock for controlling the frame rate
clock = pygame.time.Clock()
FRAME_RATE = 60
font = pygame.font.Font(None, 18)


# Create links
links = []
for i in range(width//100):  # 12 links
    links.append(Link(x_start=i*100, length=100))  # each 100 units long
for i, link in enumerate(links[1:]):
    link.previous_link = links[i]
for i, link in enumerate(links[:-1]):
    link.next_link = links[i+1]

# global vehicles store
vehicles = []

# === FLOW INFLUX SLIDER ===
flow_rate_slider = FlowRateSlider(200, 10, (width - 200) // 2, height // 3)

# speed slider
sim_speed_slider = SimSpeedSlider(200, 10, (width + 400) // 2, height // 3)

# display toggle
show_cars = False

# Sim loop
while True:
    clock.tick(FRAME_RATE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # mouse click events
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Check if mouse click is within the slider area to update flow rates and sim speed
            if not flow_rate_slider.check_slider_update(mouse_x, mouse_y):
                if not sim_speed_slider.check_slider_update(mouse_x, mouse_y):

                    # Right mouse button adds/removes incident
                    if event.button == 3:
                        for link in links:
                            if (mouse_x >= link.x_start) and (mouse_x < link.x_start + link.length):
                                if link.incident_exists:
                                    link.incident_exists = False
                                else:
                                    link.incident_exists = True
                                break

            # show / hide vehicles toggle
            if 100 < mouse_x < 180:
                if 50 < mouse_y < 100:
                    if show_cars:
                        show_cars = False
                    else:
                        show_cars = True

    # clear screen
    screen.fill((255, 255, 255))

    # influx flow rate (poisson distribution) per seconds
    if np.random.rand() < flow_rate_slider.inflow_rate / 60 / (FRAME_RATE/sim_speed_slider.sim_speed):
        vehicles.append(Vehicle(0))

    # remove vehicles from links
    for link in links:
        link.vehicles = []

    # assign vehicles to links
    for i, vehicle in enumerate(vehicles):
        vehicle.current_link = None
        for link in links:
            if link.density >=1:
                if link.previous_link is not None:
                    link.previous_link.velocity=0
                else:
                    flow_rate_slider.inflow_rate=0
            if link.contains(vehicle):
                vehicle.current_link = link
                break

        if vehicle.current_link is None:
            vehicles.pop(i)  # remove if off the screen/ off the highway

        else:
            vehicle.move(frame_rate=FRAME_RATE/sim_speed_slider.sim_speed)  # vehicles moves according to link velocity

    for link in links:
        link.update_density()
        link.update_velocity()

        # draw density of links (with color intensity)
        color = min(255, int(abs(255 * link.density)))
        pygame.draw.rect(screen, (color, 0, 0), (link.x_start, 0, link.length, height))

        # display text for density, velocity and vehicle count per link
        vehicle_count = font.render(f"#:{len(link.vehicles)}", True, (255, 255, 255))
        link_density = font.render(f"p:{link.density}", True, (255, 255, 255))
        link_velocity = font.render(f"v:{link.velocity}", True, (255, 255, 255))
        screen.blit(vehicle_count, (link.x_start+(link.length/2), 10))
        screen.blit(link_density, (link.x_start + (link.length / 2), height-50))
        screen.blit(link_velocity, (link.x_start + (link.length / 2), height-30))

    # display total vehicle count
    total_vehicles = font.render(f"total vehicles:{len(vehicles)}", True, (255, 255, 255))
    screen.blit(total_vehicles, (200, 200))

    # display circle for each vehicle
    if show_cars:
        for vehicle in vehicles:
            pygame.draw.circle(screen, (20, 80, 175), (vehicle.x, height//2), 6)

    # draw yellow circle for incidents
    for link in links:
        if link.incident_exists:
            pygame.draw.circle(screen, (255, 255, 0), (link.x_start+(link.length//2), 50), 15)

    # Draw the flow rate slider
    pygame.draw.rect(screen, FlowRateSlider.gray, (flow_rate_slider.x, flow_rate_slider.y - (flow_rate_slider.height // 2), flow_rate_slider.width,flow_rate_slider.height))
    pygame.draw.circle(screen, flow_rate_slider.knob_color, (int(flow_rate_slider.knob_x), flow_rate_slider.knob_y),flow_rate_slider.knob_radius)
    flow_rate_text = font.render(f"Veh/min:{flow_rate_slider.inflow_rate:.1f}", True, (255, 255, 255))
    screen.blit(flow_rate_text, (flow_rate_slider.x, flow_rate_slider.y - 35))

    # Draw the sim speed slider
    pygame.draw.rect(screen, SimSpeedSlider.gray, (sim_speed_slider.x, sim_speed_slider.y - (sim_speed_slider.height // 2), sim_speed_slider.width, sim_speed_slider.height))
    pygame.draw.circle(screen, sim_speed_slider.knob_color, (int(sim_speed_slider.knob_x), sim_speed_slider.knob_y), sim_speed_slider.knob_radius)
    flow_rate_text = font.render(f"Sim Speed: 1sec (real) = {sim_speed_slider.sim_speed:.1f}sec (sim)", True, (255, 255, 255))
    screen.blit(flow_rate_text, (sim_speed_slider.x, sim_speed_slider.y - 35))

    # display delays
    free_flow_text = font.render(f"Free flow time:{Vehicle.free_flow_travel_time:.1f}", True, (255, 255, 255))
    congested_text = font.render(f"Congested flow time:{Vehicle.congested_travel_time:.1f}", True, (255, 255, 255))
    screen.blit(free_flow_text, (200, 100))
    screen.blit(congested_text, (200, 130))

    # show cars box
    pygame.draw.rect(screen, (100,100,100),(100, 50, 80, 50))

    if show_cars:
        show_cars_text = font.render(f"Hide cars", True, (255, 255, 255))
        screen.blit(show_cars_text, (110, 70))
    else:
        hide_cars_text = font.render(f"Show cars", True, (255, 255, 255))
        screen.blit(hide_cars_text, (110, 70))

    # draw everything
    pygame.display.flip()
