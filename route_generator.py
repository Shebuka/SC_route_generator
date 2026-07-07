"""
********************************************************************************
ROUTE GENERATOR Between Primary Locations in Star Citizen
********************************************************************************
Author:   AeroYuki
Version:  1.1.1
SC Patch: Alpha 4.7.2
Updated:  04/25/2026

Description:
    Automatically computes and outputs total travel distances between two 
    selected locations in space, rounded to the nearest 0.01 Gigameter.
    Useful for route planning, even through jump points.

Primary Functions:
    1) record new locations
    2) modify/delete existing locations
    3) calculate routes and total distances between two selected locations
    4) save locations and routes in .csv files

Necessary Data for Recording/Modifying Locations:
    While at a location, open the Star Map (F2) and note the five parameters in 
    the lower-left corner (example: Nyx, Levski, 0.00, -129.99, 14.99). Enter 
    these parameters in sequence when prompted. These parameters can also be 
    obtained by pinning the star map crosshairs to the selected location.

Text File 1: Saved Locations List (.csv):
    Each row represents a location and has the above five parameters separated 
    by commas, along with a final sixth parameter for jump point links to other 
    star systems, if applicable. These parameters are ordered as follows:

        a) star system name
        b) location name
        c) elevation angle (degrees)
        d) planar rotation angle (degrees)
        e) radius (GM)
        f) jump-point-linked system name (or 'none')

    Parameters 'a', 'b', and 'f' are simple text strings. Parameters 'c', 'd', 
    and 'e' are positive or negative floating-point numbers rounded to two 
    decimal places.

Text File 2: Saved Routes List (.csv)
    Each row represents the distance-optimal route between the two given 
    locations, where route parameters are given as simple text strings and are
    separated by commas in the following order:

        a) star system name for start location
        b) name of start location
        c) star system name for end location
        d) name of end location
        e) total route distance, rounded to 0.01 Gm
        f) sequence of star systems in the route, separated by semicolons

    Gateway station pairs across jump tunnels are treated as though they have 
    0.00 Gm of distance between them despite being in different star systems. 
    Thus, "distance-optimal" routes do not account for the extra time or fuel 
    required to traverse jump tunnels between star systems.

Existing .csv files with saved locations/routes must be located in the same
directory as this script. Otherwise new files will be created.

--------------------------------------------------------------------------------

Version Log:
    0.1 - 12/29/2025
        Initial script framework created. Developed functions for Main Menu, 
        file management, coordinate transformations, and same-system distance
        computation.

    0.2 - 01/11/2026
        Created list utility functions: display in terminal, select from list.
        Began work on location management functions: add/modify/delete location.
        Implemented 'add new location' function with user prompts to declare the
        six required location parameters. New locations can now be added, 
        sorted, output to save file, and retrieved from save file. Performed 
        initial testing and bug fixing of functions and program flow.

    0.3 - 01/14/2026
        Implemented 'modify/delete location' function. Locations loaded into
        memory can now be deleted from the database, or their six individual 
        parameters can be modified via user prompts. Performed minor adjustments
        to terminal output formatting, tested edge cases for user input, and 
        fixed bugs.
        
    0.4 - 01/26/2026
        Formatted all code to have a maximum width of 80 characters per line.
        Added route generator functions that determine the locations that must 
        be visited in sequence (including interstellar jump points) to travel 
        from a starting location to an ending location. Added functions to
        compute and view detailed route information between two locations.
        Performed bug fixes for all new functions.

    0.5 - 01/27/2026
        Added functions to view optimized routes loaded from file and 
        generate/update optimized routes for all location pairs. Completed final
        scenario testing and bug fixing.
    
    1.0 - 01/28/2026
        Collected initial data for all major locations across the Star Citizen 
        universe as of alpha patch 4.6.0 and generated the corresponding 
        locations and routes .csv files. Program fully released.

    1.1 - 04/25/2026
        Fixed a text-input bug that previously allowed users to input location
        and system names containing commas and/or semicolons, which are used 
        exclusively as list deliminators throughout this program.

--------------------------------------------------------------------------------

Disclaimer:
This is a Star Citizen fan project and is not associated with Roberts Space 
Industries (RSI) or Cloud Imperium Games (CIG).

********************************************************************************
"""

from route_generator_functions import *


#-------------------------------------------------------------------------------
# List Utility Functions (Display, Select Options)
#-------------------------------------------------------------------------------

# Displays Current Locations and Their Parameters on the Terminal
def view_locations(locations_list):
    if len(locations_list) == 0:
        print('No locations found. Add new locations to begin.')
    else:
        print('\n||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||'
              '|||||||||||')
        system_group = ''
        loc_iterator = 0 # location iteration counter

        for location in locations_list:
            loc_params = location.split(',')
            sys_name = loc_params[0].strip()        # star system name
            loc_name = loc_params[1].strip()        # location name
            elev_ang = float(loc_params[2])         # elevation angle (deg)
            rot_ang = float(loc_params[3])          # planar rotation ang (deg)
            radius = float(loc_params[4])           # radius from star (Gm)
            jump_to_sys = loc_params[5].strip()     # jump-point link

            # organize by grouping same-system locations together
            # ('locations_list' is assumed to be sorted)
            if system_group != sys_name:
                system_group = sys_name
                system_loc_title = system_group+' Locations'
                loc_iterator = 1
                print(f'\n #  {system_loc_title:35} '
                      'Spherical Coords (Elev, Rot, Rad)')
                print('--- ----------------------------------- '
                      '----------------------------------')

            # print location to terminal
            print(f'{loc_iterator:2d}. {loc_name:35} ({elev_ang:7.2f}\u00B0, '
                  f'{rot_ang:7.2f}\u00B0, {radius:6.2f} Gm )', end='')

            # print additional jump point info if applicable
            if jump_to_sys != 'none':
                print(f'   JP: {sys_name} --> {jump_to_sys}', end='')

            print('')
            loc_iterator += 1

        print('\n||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||'
              '|||||||||||')


# Displays Avilable Star Systems on the Terminal
def view_star_systems(system_list):
    if len(system_list) == 0:
        print('Note: There are currently no star systems.')
    else:
        sys_iterator = 0

        for system in system_list:
            sys_iterator += 1
            print(f'   {sys_iterator:2d}. {system}')
            

# Selects an Item (System/Location) from an Appropriate List, 
# Includes Input Validation
def choose_from_list(item_list):
    choice = ''
    while choice == '':
        choice_input = input(' >> ')

        if not choice_input.isnumeric():
            print('Invalid entry. Enter the numeric value associated '
                  'with your selection.')
        elif 1 <= int(choice_input) <= len(item_list):
            choice = item_list[int(choice_input)-1]
        elif choice_input.strip() == '0':   # used for a unique choice option
            choice = '0'
        else:
            print('Invalid entry. Enter the numeric value associated '
                  'with your selection.')

    return choice

#-------------------------------------------------------------------------------
# Primary Locations-List Functions (Add, Modify, Delete)
#-------------------------------------------------------------------------------

# Reject Text Inputs with Commas or Semicolons (used as list deliminators)
def validate_input(string_input):
    if ',' in string_input:
        print('Name cannot contain commas. Try again.')
        return '0'
    elif ';' in string_input:
        print('Name cannot contain semicolons. Try again.')
        return '0'
    else:
        return string_input


# Add New Location to Temporary Locations List in RAM
def add_new_location(locations_list):
    systems = get_star_systems(locations_list)

    print('\nTo add a new location, first select a star system.')
    view_star_systems(systems)
    print('    0. (add a new star system)')    # unique choice option
    sys_name = choose_from_list(systems)

    while sys_name == '0':
        sys_name = input('\nEnter new star system name: ').strip().title()
        sys_name = validate_input(sys_name)

    print(f'\nChosen star system: {sys_name}')

    # new location name
    loc_name = '0'
    while loc_name == '0':
        loc_name = input('\nEnter new location name (case sensitive): ').strip()
        loc_name = validate_input(loc_name)

    # new location spherical coordinates
    elev_ang, rot_ang, radius = 0,0,0
    while True:
        print(f'\nEnter the three spherical coordinates for "{loc_name}" from '
              f'the mobiGlas star map.')
        try:
            elev_ang = float(input('Elevation Angle (degrees): '))
            rot_ang = float(input('Planar Rotation Angle (degrees): '))
            radius = float(input('Radius (Gm): '))
        except ValueError:
            print('Values must be positive or negative floating-point numbers. '
                  'Check the values and try again.')
        else:
            break

    # assemble location parameters
    loc_params = [sys_name, loc_name, 
                  f'{elev_ang:.2f}', f'{rot_ang:.2f}', f'{radius:.2f}']

    # jump point check
    print(f'\nDoes "{loc_name}" have a jump point to an existing star system?')
    print('If no, enter 0. If yes, select the linked star system.')
    view_star_systems(systems)
    print('    0. (no jump point)')    # unique choice option
    jump_to_sys = choose_from_list(systems)
    if jump_to_sys == '0' or jump_to_sys == sys_name:
        jump_to_sys = 'none'
    loc_params.append(jump_to_sys)

    # review new location
    print('\n+++ New Location to be Added to the Locations List +++')
    print(f'    - {loc_name}, {sys_name} System')
    print(f'    - Elevation Angle: {loc_params[2]}\u00B0')
    print(f'    - Planar Rotation Angle: {loc_params[3]}\u00B0')
    print(f'    - Radius: {loc_params[4]} Gm')
    if jump_to_sys != 'none':
        print(f'    - Contains a jump point from {sys_name} to {jump_to_sys}.')
    else:
        print('    - Does not contain a jump point.')
    
    print('\nDo you want to add this location to the locations list?')
    print('You will still need to save from the Main Menu to make these '
          'changes permanent.')
    
    # user input and validation
    while True:
        print('    1. Yes, add location.')
        print('    0. No, disregard location and return to Main Menu.')
        user_input = input(' >> ')

        if user_input == '0':
            return locations_list
        elif user_input == '1':
            new_location = ','.join(loc_params)
            locations_list.append(new_location)
            locations_list.sort(key=str.casefold)
            print(f'\n"{loc_name}" has been added to the {sys_name} '
                  f'star system.')
            return locations_list
        else:
            print('Invalid choice. Please try again.')


# Deletes Location from Temporary Locations List in RAM
def delete_location(location, locations_list):
    loc_params = location.split(',')
    sys_name = loc_params[0].strip().title()    # star system name
    loc_name = loc_params[1].strip()            # location name

    print(f'\nAre you sure you want to delete "{loc_name}, {sys_name}"?')
    confirmation = input('Enter "0" to delete, or enter any other value '
                         'to return to Main Menu: ')
    if confirmation == '0':
        locations_list.remove(location)
        print(f'\n"{loc_name}" in {sys_name} has been deleted.')
    
    return locations_list


# Modify Location from Temporary Locations List in RAM
def modify_location(location, locations_list, all_systems):
    locations_list.remove(location)
    temp_systems = all_systems[:]   # all available star systems
    
    loc_params = location.split(',')
    sys_name = loc_params[0].strip()        # star system name
    loc_name = loc_params[1].strip()        # location name
    elev_ang = float(loc_params[2])         # elevation angle (deg)
    rot_ang = float(loc_params[3])          # planar rotation angle (deg)
    radius = float(loc_params[4])           # radius from star (Gm)
    jump_to_sys = loc_params[5].strip()     # jump point link

    while True:
        print(f'\nWhich parameter for "{loc_name}" would you like to modify?')
        print('    1. Star System')
        print('    2. Location Name')
        print('    3. Spherical Coordinates')
        print('    4. Jump Point Link')
        print('    0. (modifications finished)')
        
        user_input = input(' >> ')
        match user_input:

            # modify star system
            case '1':
                print(f'\nCurrent Star System: {sys_name}')
                print(f'Move "{loc_name}" into which star system?')
                view_star_systems(temp_systems)
                print('    0. (create new star system)')  # unique choice option

                new_sys_name = choose_from_list(temp_systems)
                if new_sys_name == '0':
                    while new_sys_name == '0':
                        new_sys_name = (input('\nEnter new star system name: ')
                                             .strip().title())
                        new_sys_name = validate_input(new_sys_name)
                    temp_systems.append(new_sys_name)
                    temp_systems.sort(key=str.casefold)

                if new_sys_name == sys_name:
                    print(f'\nNo changes made to star system for "{loc_name}".')
                else:
                    print(f'\nStar system for "{loc_name}" changed '
                          f'from {sys_name} to {new_sys_name}.')
                                
                loc_params[0] = new_sys_name
                sys_name = loc_params[0]

            # modify location name
            case '2':
                new_loc_name = '0'
                while new_loc_name == '0':
                    new_loc_name = (input('\nEnter new name for this location '
                                          '(case sensitive): ').strip())
                    new_loc_name = validate_input(new_loc_name)
                print(f'Location name changed from "{loc_name}" '
                      f'to "{new_loc_name}".')
                loc_params[1] = new_loc_name
                loc_name = loc_params[1]

            # modify spherical coordinates
            case '3':
                new_elev_ang, new_rot_ang, new_radius = 0,0,0
                while True:
                    print('\nEnter new spherical coordinates for '
                          'this location.')
                    try:
                        new_elev_ang = float(input(f'Elevation Angle '
                                                  f'(degrees): {elev_ang} >> '))
                        new_rot_ang = float(input(f'Planar Rotation Angle '
                                                  f'(degrees): {rot_ang} >> '))
                        new_radius = float(input(f'Radius (Gm): {radius} >> '))
                    except ValueError:
                        print('Values must be positive or negative floating-'
                              'point numbers. Check the values and try again.')
                    else:
                        break

                print(f'\nSpherical coordinates (elev, rot, rad) '
                      f'for "{loc_name}" changed')
                print(f'   from ( {elev_ang:7.2f}\u00B0, '
                                f'{rot_ang:7.2f}\u00B0, '
                                f'{radius:7.2f} Gm )')
                print(f'     to ( {new_elev_ang:7.2f}\u00B0, '
                                f'{new_rot_ang:7.2f}\u00B0, '
                                f'{new_radius:7.2f} Gm ).')

                loc_params[2] = f'{new_elev_ang:.2f}'
                elev_ang = float(loc_params[2])

                loc_params[3] = f'{new_rot_ang:.2f}'
                rot_ang = float(loc_params[3])

                loc_params[4] = f'{new_radius:.2f}'
                radius = float(loc_params[4])

            # modify jump point link
            case '4':
                if jump_to_sys == 'none':
                    print('\nThis location currently does not link to '
                          'another star system.')
                else:
                    print(f'\nThis location currently has a jump point link '
                          f'to {jump_to_sys}.')
                                
                print('Select the linked star system.')
                view_star_systems(temp_systems)
                print('    0. (no jump point)') # unique choice option

                new_jump_to_sys = choose_from_list(temp_systems)
                if new_jump_to_sys == '0':
                    new_jump_to_sys = 'none'

                if (new_jump_to_sys == jump_to_sys or 
                    new_jump_to_sys == sys_name):
                    print(f'\nNo jump point changes made to "{loc_name}".')
                elif jump_to_sys == 'none':
                    print(f'\nAdded jump point link to {new_jump_to_sys} '
                          f'for "{loc_name}".')
                elif new_jump_to_sys == 'none':
                    print(f'\nRemoved jump point link from "{loc_name}".')
                else:
                    print(f'\nJump point link for "{loc_name}" changed '
                          f'from {jump_to_sys} to {new_jump_to_sys}.')
                                    
                loc_params[5] = new_jump_to_sys
                jump_to_sys = loc_params[5]

            # modifications complete
            case '0':
                break

            # invalid selection
            case _:
                print('Invalid entry. Enter the numeric value associated '
                      'with your selection.')
            
    # finalize location modifications
    modified_location = ','.join(loc_params)
    locations_list.append(modified_location)

    return locations_list


# Modify/Delete Location - Menu Selection and List Processing
def process_location(locations_list):
    if len(locations_list) == 0:
        print('Note: There are no locations to modify.')
        return locations_list
    
    systems = get_star_systems(locations_list)
    print('\nTo modify or delete a location, first select a star system.')
    view_star_systems(systems)

    # select system
    sys_name = '0'  # invalidate unique choice option
    while sys_name == '0':
        sys_name = choose_from_list(systems)
        if sys_name == '0':
            print('Invalid entry. Enter the numeric value associated with '
                  'your selection.')

    # create a sub-list of locations from the chosen star system
    ss_locations, other_locations = [], []
    for location in locations_list:
        sys_check = location.split(',')[0].strip()
        if sys_name == sys_check:
            ss_locations.append(location)
        else:
            other_locations.append(location)
        
    view_locations(ss_locations)
    print('\nSelect one of the above locations.')

    # select location
    selected_loc = '0'  # invalidate unique choice option
    while selected_loc == '0':
        selected_loc = choose_from_list(ss_locations)
        if selected_loc == '0':
            print('Invalid entry. Enter the numeric value associated with '
                  'your selection.')

    loc_params = selected_loc.split(',')
    sys_name = loc_params[0].strip()        # star system name
    loc_name = loc_params[1].strip()        # location name
    elev_ang = float(loc_params[2])         # elevation angle (deg)
    rot_ang = float(loc_params[3])          # planar rotation angle (deg)
    radius = float(loc_params[4])           # radius from star (Gm)
    jump_to_sys = loc_params[5].strip()     # jump point link
        
    # review selected location
    print('\n+++ Selected Location Details +++')
    print(f'    - {loc_name}, {sys_name} System')
    print(f'    - Elevation Angle: {elev_ang}\u00B0')
    print(f'    - Planar Rotation Angle: {rot_ang}\u00B0')
    print(f'    - Radius: {radius} Gm')
    if jump_to_sys != 'none':
        print(f'    - Contains a jump point from {sys_name} to {jump_to_sys}.')
    else:
        print('    - Does not contain a jump point.')
        
    print('\nWould you like to Modify or Delete this location?')
    print('    1. Modify location parameters.')
    print('    2. Return to Main Menu with no changes.')
    print('    0. Delete this location.')

    # user input and validation
    while True:
        user_input = input(' >> ')
        match user_input:
            case '2':   # return to menu
                return locations_list
            case '0':   # delete location
                ss_locations = delete_location(selected_loc, ss_locations)
                break
            case '1':   # modify location parameters
                ss_locations = modify_location(selected_loc, ss_locations,
                                               systems)
                break
            case _:
                print('Invalid entry. Enter the numeric value associated '
                      'with your selection.')

    # assemble locations list with modifications (if any)
    modified_locations_list = []
    for location in ss_locations:
        modified_locations_list.append(location)
    for location in other_locations:
        modified_locations_list.append(location)
    modified_locations_list.sort(key=str.casefold)

    print('\nThe locations list has been updated.')
    print('You will still need to save from the Main Menu to make these '
          'changes permanent.')

    return modified_locations_list





#-------------------------------------------------------------------------------
# Route Operations Functions (Display, Optimize)
#-------------------------------------------------------------------------------


# Displays Multiple Routes with Distances for a Given Location Pair
def view_routes_for_loc_pair(loc_1, loc_2, locations_list):
    # location 1
    loc_1_params = loc_1.split(',')
    sys_1_name = loc_1_params[0].strip()    # star system name
    loc_1_name = loc_1_params[1].strip()    # location name

    # location 2
    loc_2_params = loc_2.split(',')
    sys_2_name = loc_2_params[0].strip()    # star system name
    loc_2_name = loc_2_params[1].strip()    # location name

    print(f'\nViewing Routes from "{loc_1_name}, {sys_1_name}" to '
          f'"{loc_2_name}, {sys_2_name}"')
    print('-------------------------------------------------------------------'
          '-----------------')

    # compute and sort routes
    routes = get_routes_location_seq(loc_1, loc_2, locations_list)
    sorted_routes = get_sorted_routes_list(routes)

    # route sequence display parameters
    route_alpha = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O',
                   'P','Q','R','S','T','U','V','W','X','Y','Z']
    route_num = 0
    cycle = 0

    for route in sorted_routes:
        if route_num % 26 == 0:
            route_num = 0
            cycle +=1

        # get route distances
        segment_dists = get_route_segment_distances(route)
        total_dist = get_route_total_distance(route)

        # number of jump point tunnels to navigate
        total_jumps = len(segment_dists) - 1

        # route summary with total distance
        print(f'\n  [Route {route_alpha[route_num]*cycle}]  Total Distance: '
              f'{total_dist:.2f} Gm  (Jump Tunnels: {total_jumps}',end='')
        if total_jumps >= 1:
            print(' - extra time & fuel needed)')
        else:
            print(')')
        
        # location sequence details and distances
        QT_index = 0
        while bool(route):
            loc_A = route.pop(0)
            loc_A_params = loc_A.split(',')
            sys_A_name = loc_A_params[0].strip()
            loc_A_name = loc_A_params[1].strip()

            loc_B = route.pop(0)
            loc_B_name = loc_B.split(',')[1].strip()

            print(f'    {(QT_index+1):2d}. {sys_A_name+' QT: ':12} '
                  f'{float(segment_dists[QT_index]):6.2f} Gm    '
                  f'{loc_A_name}  -->  {loc_B_name}')
            
            QT_index += 1
        
        route_num += 1

    print()
    print('-------------------------------------------------------------------'
          '-----------------')


# Displays All Optimized Routes and Their Parameters on the Terminal
def view_optimized_routes(routes_list):
    if len(routes_list) == 0:
        print('\nRoutes have not yet been optimized.')
    else:
        print('\n||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||'
              '||||||||||||||||||||||||||')
        
        route_iterator = 0 # route iteration counter
        current_location = ''

        for route in routes_list:
            route_params = route.split(',')
            sys_1_name = route_params[0].strip()    # starting star system name
            loc_1_name = route_params[1].strip()    # starting location name
            sys_2_name = route_params[2].strip()    # ending star system name
            loc_2_name = route_params[3].strip()    # ending location name
            total_dist = route_params[4].strip()    # total distance for route
            sys_sequence = route_params[5].strip()  # sequence of star systems..
                                                    # .. to traverse for route

            # convert system sequence (deliminated by ;) into a list
            sys_seq_list = sys_sequence.split(';')

            # print extra space between different starting locations
            if current_location != loc_1_name:
                current_location = loc_1_name
                print()

            # print route to terminal
            route_iterator += 1
            print(f'{route_iterator:5d}. '
                  f'({sys_1_name+') '+loc_1_name:43}  to  '
                  f'({sys_2_name+') '+loc_2_name+':':44}  '
                  f'{total_dist:>7} Gm    [',end='')
            
            # print system sequence
            sys_count = 0
            total_sys_count = len(sys_seq_list)
            for system in sys_seq_list:
                sys_count += 1
                print(f'{system}',end='')

                # termination print logic
                if total_sys_count == 1:
                    print(' only]')
                elif sys_count == total_sys_count:
                    print(']')
                else:
                    print(' -> ',end='')

        print('\n||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||'
              '||||||||||||||||||||||||||')


# Optimizes All Location-Pair Routes for Minimum Distance
def optimize_routes(locations_list):
    optimized_routes = []

    for loc_1 in locations_list:
        for loc_2 in locations_list:
            if loc_1 == loc_2:
                continue
                
            # compute and sort routes
            routes = get_routes_location_seq(loc_1, loc_2, locations_list)
            sorted_routes = get_sorted_routes_list(routes)

            # select optimal route
            optimal_route = sorted_routes[0]

            # route starting location
            start_loc = optimal_route[0]
            start_loc_params = start_loc.split(',')
            start_sys_name = start_loc_params[0].strip()
            start_loc_name = start_loc_params[1].strip()

            # route ending location
            end_loc = optimal_route[-1]
            end_loc_params = end_loc.split(',')
            end_sys_name = end_loc_params[0].strip()
            end_loc_name = end_loc_params[1].strip()

            # route total distance
            total_dist = get_route_total_distance(optimal_route)

            # route system sequence
            sys_seq_list = []
            loc_iterator = 0
            route_total_locs = len(optimal_route)
            while loc_iterator < route_total_locs:
                system = optimal_route[loc_iterator].split(',')[0].strip()
                sys_seq_list.append(system)
                loc_iterator += 2

            sys_seq_str = ';'.join(sys_seq_list)
            
            # construct route string
            route_str = (f'{start_sys_name},{start_loc_name},'
                         f'{end_sys_name},{end_loc_name},'
                         f'{total_dist:.2f},{sys_seq_str}')
            
            # save optimized route to list
            optimized_routes.append(route_str)

    print('\nRoutes have been generated and optimized for all location pairs.')
    print('You will still need to save from the Main Menu to make these '
          'changes permanent.')
    
    return optimized_routes


# Menu Selection for Viewing Routes
def view_routes(locations_list, routes_list):
    print('\nSelect an option:')
    print('    1. Display detailed routes between a pair of locations.')
    print('    2. Display optimized routes for all location pairs.')
    print('    3. Return to Main Menu.')
    
    # user input and validation
    while True:
        user_input = input(' >> ')
        match user_input:
            case '3':   # return to main menu
                break
            case '2':   # display optimized routes
                view_optimized_routes(routes_list)
                break
            case '1':   # route between a location pair
                if len(locations_list) < 2:
                    print('\nAdd more locations to view routes.')
                    break

                loc_1 = ''
                loc_2 = ''
                loc_iterator = 1

                while loc_iterator <= 2:
                    systems = get_star_systems(locations_list)
                    print(f'\nSelect the star system for location '
                          f'#{loc_iterator}.')
                    view_star_systems(systems)

                    # select system
                    sys_name = '0'  # invalidate unique choice option
                    while sys_name == '0':
                        sys_name = choose_from_list(systems)
                        if sys_name == '0':
                            print('Invalid entry. Enter the numeric value '
                              'associated with your selection.')

                    # create a sub-list of locations from the chosen star system
                    ss_locations = []
                    for location in locations_list:
                        sys_check = location.split(',')[0].strip()
                        if sys_name == sys_check:
                            ss_locations.append(location)

                    view_locations(ss_locations)
                    print('\nSelect one of the above locations.')

                    # select location
                    selected_loc = '0'  # invalidate unique choice option
                    while selected_loc == '0':
                        selected_loc = choose_from_list(ss_locations)
                        if selected_loc == '0':
                            print('Invalid entry. Enter the numeric value '
                                  'associated with your selection.')
                    
                    # assign location
                    if loc_iterator == 1:
                        loc_1 = selected_loc
                        loc_1_params = loc_1.split(',')
                        sys_1_name = loc_1_params[0].strip()
                        loc_1_name = loc_1_params[1].strip()
                        print(f'Location 1: {loc_1_name}, {sys_1_name} System')
                    elif loc_iterator == 2:
                        loc_2 = selected_loc

                    loc_iterator += 1

                view_routes_for_loc_pair(loc_1, loc_2, locations_list)
                break

            case _:
                print('Invalid entry. Enter the numeric value associated with '
                      'your selection.')


#-------------------------------------------------------------------------------
# Main Menu
#-------------------------------------------------------------------------------

def get_menu_selection():
    while True:
        # menu text
        print('\n---------------------------------------')
        print('|              Main Menu              |')
        print('---------------------------------------')
        print('    1. View Locations')
        print('    2. Add New Location')
        print('    3. Modify/Delete Existing Location')
        print('    4. View Route Information')
        print('    5. Optimize Routes')
        print('    6. Save Changes to File')
        print('    0. Quit')

        # user input and validation
        user_input = input('\nSelect an option: ')
        match user_input:
            case '1' | '2' | '3' | '4' | '5' | '6' | '0':
                return user_input
            case _:
                print('\nInvalid choice. Please try again.')


#-------------------------------------------------------------------------------
# MAINLINE LOGIC
#-------------------------------------------------------------------------------

def main():
    # initialize program
    print('\n\n=====================================================')
    print('||  Welcome to the Star Citizen Route Calculator.  ||')
    print('||        written by AeroYuki, January 2026        ||')
    print('=====================================================')
    
    locations_list = get_locations()
    locations_list.sort(key=str.casefold)
    routes_list = get_opt_routes()
    routes_list.sort(key=str.casefold)
    
    # begin menu loop until "quit"
    loop_menu = True
    while loop_menu:
        menu_selection = get_menu_selection()
        match menu_selection:
            
            case '1': # view current locations list
                view_locations(locations_list)

            case '2': # add new location
                locations_list = add_new_location(locations_list)

            case '3': # modify/delete existing location
                locations_list = process_location(locations_list)

            case '4': # view route info
                view_routes(locations_list, routes_list)

            case '5': # optimize routes
                routes_list = optimize_routes(locations_list)

            case '6': # save locations and routes to file
                print()
                write_locations_to_file(locations_list)
                write_routes_to_file(routes_list)

            case '0': # quit
                print('\nAre you sure you want to quit? '
                      'Unsaved changes will be lost.')
                user_input = input('Enter "0" to quit, or enter any other '
                                   'value to return to Main Menu: ')
                
                if user_input == '0':
                    loop_menu = False
                else:
                    pass
    
    # exit program
    print('\nThank you for using the Route Generator, written by AeroYuki.')
    print('o7\n')
    
    
if __name__ == "__main__":
    main()