********************************************************************************
ROUTE GENERATOR Between Primary Locations in Star Citizen
********************************************************************************
Author:   AeroYuki
Version:  1.1
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
