"""
********************************************************************************
ROUTE GENERATOR Between Primary Locations in Star Citizen
********************************************************************************
Author:   AeroYuki
Version:  1.1.1
SC Patch: Alpha 4.7.2
Updated:  04/25/2026

--------------------------------------------------------------------------------

Disclaimer:
This is a Star Citizen fan project and is not associated with Roberts Space 
Industries (RSI) or Cloud Imperium Games (CIG).

********************************************************************************
"""

# Python Standard Library Module Imports
import math     # access to trigonomerty, pi, and square-root functions


#-------------------------------------------------------------------------------
# File Management Functions
#-------------------------------------------------------------------------------

# Loads Locations Text File (.csv), Creates if Not Found
def get_locations():
    filename = 'saved_locations.csv'
    locations_list = []
    try:
        with open(filename) as file_object:
            for line in file_object:
                locations_list.append(line.strip())
    except FileNotFoundError:
        with open(filename, 'w') as file_object:
            pass
    
    locations_list.sort(key=str.casefold)

    return locations_list


# Writes Text File (.csv) of Saved Locations, Overwrites Existing File
def write_locations_to_file(locations_list):
    filename = 'saved_locations.csv'
    locations_list.sort(key=str.casefold)

    with open(filename, 'w') as file_object:
        for line in locations_list:
            file_object.write(f'{line}\n')

    print('Locations have been saved.')


# Loads Optimized Routes Text File (.csv), Creates if Not Found
def get_opt_routes():
    filename = 'optimized_routes.csv'
    routes_list = []
    try:
        with open(filename) as file_object:
            for line in file_object:
                routes_list.append(line.strip())
    except FileNotFoundError:
        with open(filename, 'w') as file_object:
            pass
    
    routes_list.sort(key=str.casefold)

    return routes_list


# Writes Text File (.csv) of Saved Routes, Overwrites Existing File
def write_routes_to_file(routes_list):
    filename = 'optimized_routes.csv'
    routes_list.sort(key=str.casefold)

    with open(filename, 'w') as file_object:
        for line in routes_list:
            file_object.write(f'{line}\n')

    print('Optimized routes have been saved.')


#-------------------------------------------------------------------------------
# Route Generator Functions
#-------------------------------------------------------------------------------

# Returns List of Available Star Systems
def get_star_systems(locations_list):
    systems = []
    system_check = ''

    for location in locations_list:
        system = location.split(',')[0].strip()
        if system_check != system:
            systems.append(system)
            system_check = system

    return systems


# Generates List of Jump Point Locations
def get_linked_locations(locations_list):
    linked_locs = []
    
    for location in locations_list:
        jump_to_sys = location.split(',')[5].strip()

        if jump_to_sys != 'none':
            linked_locs.append(location)
    
    return linked_locs


# Generates a List of Star Systems Linked by Jump Points
def get_linked_systems(locations_list):
    linked_sys = []

    for location in locations_list:
        loc_params = location.split(',')
        sys_name = loc_params[0].strip()
        jump_to_sys = loc_params[5].strip()

        if jump_to_sys != 'none':
            linked_pair = f'{sys_name},{jump_to_sys}'
            if linked_pair not in linked_sys:
                linked_sys.append(linked_pair)
    
    return linked_sys


# Recursively Builds List of Sequenced Star System Routes
def get_routes_system_seq(start_sys, end_sys, all_sys, linked_sys):
    if start_sys == end_sys:
        return [end_sys]
    
    remaining_sys = all_sys[:]
    remaining_sys.remove(start_sys)
    all_routes_sys_seq = [start_sys]
    first_route = True

    for sys_pair in linked_sys:
        sys_params = sys_pair.split(',')
        sys_name = sys_params[0].strip()
        jump_to_sys = sys_params[1].strip()

        if sys_name == start_sys and jump_to_sys in remaining_sys:
            new_start_sys = jump_to_sys
            new_sys_routes = get_routes_system_seq(new_start_sys, end_sys, 
                                                   remaining_sys, linked_sys)

            for route in new_sys_routes:
                if first_route:
                    first_route = False
                else:
                    all_routes_sys_seq.append(start_sys)

                all_routes_sys_seq[-1] += f',{route.strip()}'

    return all_routes_sys_seq
                    

# Generates List of Sequenced Locations for All Routes
def get_routes_location_seq(start_loc, end_loc, locations_list):
    start_sys = start_loc.split(',')[0].strip()
    end_sys = end_loc.split(',')[0].strip()
    all_sys = get_star_systems(locations_list)
    linked_sys = get_linked_systems(locations_list)

    all_routes_sys_seq = get_routes_system_seq(start_sys, end_sys,
                                           all_sys, linked_sys)
    
    all_routes_loc_seq = []
    linked_locs = get_linked_locations(locations_list)

    # convert each system sequence into a location sequence
    for route in all_routes_sys_seq:
        route_locs = [start_loc]

        route_sys = route.split(',')
        current_sys = route_sys.pop(0)

        while bool(route_sys):
            next_sys = route_sys.pop(0)

            # search jump-point linked locations for matching systems
            loc_1, loc_2 = '', ''
            for location in linked_locs:
                loc_params = location.split(',')
                sys_name = loc_params[0].strip()
                jump_to_sys = loc_params[5].strip()

                # jump point entrance in current system
                if sys_name == current_sys and jump_to_sys == next_sys:
                    loc_1 = location
                # jump point exit in next system
                elif sys_name == next_sys and jump_to_sys == current_sys:
                    loc_2 = location
                
            # add jump-point locations to route
            route_locs.append(loc_1)
            route_locs.append(loc_2)

            # update current system for next loop iteration
            current_sys = next_sys

        # jump-point locations complete; add final location to route
        route_locs.append(end_loc)

        # add route location sequence to list of all routes
        all_routes_loc_seq.append(route_locs)

    # Returns a list of routes, each route is itself a list of locations,
    # and each location is a string of six parameters separated by commas.
    return all_routes_loc_seq


#-------------------------------------------------------------------------------
# Distance Computation Functions
#-------------------------------------------------------------------------------

# Location Coordinate Transformation: Spherical to Rectangular
def get_rect_coords(location):
    loc_params = location.split(',')

    if len(loc_params) < 5:
        return 0,0,0

    # spherical coordinates
    elev_ang = float(loc_params[2])/180*math.pi  # elevation angle (rad)
    rot_ang = float(loc_params[3])/180*math.pi   # planar rotation angle (rad)
    radius = float(loc_params[4])                  # radius from star (Gm)

    # rectangular coordinates
    x = radius*math.cos(elev_ang)*math.cos(rot_ang)
    y = radius*math.cos(elev_ang)*math.sin(rot_ang)
    z = radius*math.sin(elev_ang)

    return x,y,z
            

# Same-System Distance
def get_ss_distance(loc_1, loc_2):
    x1, y1, z1 = get_rect_coords(loc_1)
    x2, y2, z2 = get_rect_coords(loc_2)

    distance = math.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)
    
    return f'{distance:.5f}'


# Single-Route Segment Distances (start/end may be in different star systems)
def get_route_segment_distances(route):
    segment_distances = []
    route_locs = route[:]

    while bool(route_locs):
        loc_1 = route_locs.pop(0)
        loc_2 = route_locs.pop(0)
        distance = get_ss_distance(loc_1, loc_2)
        segment_distances.append(distance)
    
    return segment_distances


# Total Route Distance
def get_route_total_distance(route):
    total_dist = 0
    segment_dists = get_route_segment_distances(route)
    for dist in segment_dists:
        total_dist += float(dist)
    
    return total_dist
    

#-------------------------------------------------------------------------------
# Route Operations Functions (Sort)
#-------------------------------------------------------------------------------

# Sorts Routes List for a Location Pair by Minimum Distance
def get_sorted_routes_list(loc_pair_routes_list):
    sorted_routes = []
    total_distances = []
    
    for route in loc_pair_routes_list:
        route_total_dist = 0
        segment_dists = get_route_segment_distances(route)

        for dist in segment_dists:
            route_total_dist += float(dist)

        # insert-sort algorithm
        route_index = 0
        while route_index <= len(total_distances):
            if route_index == len(total_distances):
                total_distances.append(route_total_dist)
                sorted_routes.append(route)
                break
            elif route_total_dist <= float(total_distances[route_index]):
                total_distances.insert(route_index, route_total_dist)
                sorted_routes.insert(route_index, route)
                break
            else:
                route_index += 1
        
    return sorted_routes