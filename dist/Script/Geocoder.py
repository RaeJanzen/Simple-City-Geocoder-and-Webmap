#----------------------------------------------------------------------------------------------------------------------------------------------------
# Program   : Geocoder.py
# Purpose   : Geocode from a city name or reverse geocode from coordinates,
#             Increase count data if location is a duplicate
#                           AND
#             Update CSV and map layer files with obtained data
#
# Written By: RJanzen
#
# Copyright : Coordinate data derived from OpenStreetMap through Nominatim 
#             Geocoding library by GeoPy
#----------------------------------------------------------------------------------------------------------------------------------------------------

#======================================================
# Define Functions
#======================================================

# Pull in Data from CSV
#______________________________________________________

def getData():
    #create empty list to store data
    templines=[]

    #check if file exists, pull in data if it does, otherwise create file
    if os.path.exists('..\layers\city_locations.csv') == True:
        #open csv to read data
        with open(r'..\layers\city_locations.csv','r', encoding="utf-8") as file:
            #skip the header line
            file.readline()
            #iterate through csv rows and store data
            for item in file:
                item  = item.rstrip('\n').title()                       #remove newline character and adjust case for comparison
                ctyD, stD, ctryD, longD, latD, countD = item.split(',') #separate data into separate items
                lineD = [ctyD, stD, ctryD, longD, latD, countD]         #assign items to list
                templines.append(lineD)                                 #add data to a master list
    #if the file does not exist, create it and leave the templines list empty
    else:
        file = open(r'..\layers\city_locations.csv','x', encoding="utf-8")
        file.close()

    return templines



# Check if input is a duplicate
#______________________________________________________

def duplicateData(city, state, country, data):
    #assign variable to hold duplicate status, assume data is not duplicate
    dupe= 'n'
    
    #compare user input to data
    for line in data:
        if city.title() == line[0].title() and state.title() == line[1].title() and country.title() == line[2].title():
            dupe    ='y'                        #if the input matches the data change duplicate status to yes
            line[5] = str(int(line[5])+1)       #increase count by 1
    if dupe == 'y':
        print('\n---City data adjusted, updating files')

    return dupe, data


# Run geocoder
#______________________________________________________

def findLatLong(city, state, country, nom):
    #run user input through Nominatim's geocoder
    #try getting location data with user input
    location = nom.geocode(city+', '+state+', '+country,          #user input
                                  language = 'en',                #specify language to prevent Unicode errors
                                  exactly_one = False,            #return a list of all matches
                                  addressdetails = True,          #return includes address details
                                  featuretype = 'city',           #return only city type features
                                  timeout = 15)
    #if first try returns a null or none value try again with only city and country input
    if location is None:
        location = nom.geocode(city+', '+country,           #user input
                                      language = 'en',      #specify language to prevent Unicode errors
                                      exactly_one=False,    #return a list of all matches
                                      addressdetails=True,  #return includes address details
                                      featuretype='city',   #return only city type features
                                      timeout = 15)
    
    #verify location is a city
    plType = ['city','town','village','hamlet','city_district','municipality','state'] #list of settlement tags
    plc = []
    for place in location:
        keys = list(place.raw['address'].keys())
        if keys[0] in plType:
            plc.append(place)

    #if multiple matches return from the geocoder ask user to make a selection
    if len(plc) > 1:
        print('\nThere was some trouble identifying the city\n'
              'Please chose an option from the list below:')
        tab = '\t'
        for i in range(len(plc)):
            print(f"{tab}{i+1}).{tab}{plc[i]}")    #present all options in a list
        #include user input validation
        while isinstance(plc, list) == True:
            choice = input('\nPlease indicate your selection: ')
            try:
                choice = int(choice)-1
                plc    = plc[choice]
            except:
                print('\nSelection is unclear. Please choose an integer value from the above list')
        print(f"Chosen location is: {plc}")

    #if geolocator returns a none null value that is not multiple list items, it should be one item in a list
    #select the only item in the list
    #if no list item exists, let the try stament that the function is called within handle the error
    else:
        plc = plc[0]
            
    #output relevant data
    plc_keys = list(plc.raw['address'].keys())     #assign dictionary keys to a list for tidy access

    mun = plc.raw['address'][plc_keys[0]]   #variable for municipality name
    #handle cases where state information is not applicable by inserting an empty string as a placeholder
    if 'state' not in plc_keys:             #variable for state name
        sta = ''
    else:
        sta = plc.raw['address']['state']
    #handle cases where country information is not applicable by inserting an empty string as a placeholder
    if 'country' not in plc_keys:           #variable for country name
        ct = ''
    else:
        ct = plc.raw['address']['country']
        
    return [mun, sta, ct, str(plc.longitude), str(plc.latitude), '1']


# Run reverse geocoder
#______________________________________________________

def findFromCoord(nom):
    #user input verification
    num = 'N'
    while num == 'N':
        print('asking for data')
        #ask user for lat and long data
        lat = input('\tPlease enter latitude coordinate: ')
        lon = input('\tPlease enter longitude coordinate: ')
        #check input is at least numeric
        try:
            lat = float(lat)
            lon = float(lon)
            num = 'Y'
        except:
            print('These values do not seem to be numeric')
            
    #run user input through Nominatim's reverse geocoder
    location = nom.reverse([lat, lon],
                           language = 'en',         #specify language to prevent Unicode errors
                           addressdetails = True,   #return includes address details
                           timeout = 15)

    #ask user to verify location name
    mun   = ''                                                                  #start with placeholder variable for municipality
    nameL = []                                                                  #list to store found values
    l_keys = list(location.raw['address'].keys())                               #list of dictionary keys
    plType = ['city','town','village','hamlet','municipality','city_district']  #list of settlement tags
    #look for a name within the returned address by comparing settlment tags with the list of dictionary keys
    for i in l_keys:
        if i in plType:
            nameL.append(i)
    #if only one value is found present to user as an option to use for city name data
        #(if more than one value, do not present options, city name is likely uncertain if coordinates are being used, do not confuse the user with too many options)
    if len(nameL) == 1:
        print('A potential name for this location has been identified')
        given = input(f'Would you like to use {location.raw["address"][nameL[0]]} for the name of this location? [Y/N]').upper()
        if given == 'Y':
            mun = location.raw['address'][nameL[0]]
    #if an appropriate name is not found within the address details, ask the user if they would like to supply one
    if mun == '':
        manual = input('would you like to enter the name of this location manually? [Y/N]').upper()
        if manual == 'Y':
            mun = input('Please type the name you would like to use for this location: ')
        #use a default value
        else:
            mun = 'Village'
            print('\n---Using default value "Village"')

    #handle cases where state information is not applicable by inserting an empty string as a placeholder
    if 'state' not in l_keys:       #variable for state name
        sta = ''
    else:
        sta = location.raw['address']['state']
    #handle cases where country information is not applicable by inserting an empty string as a placeholder
    if 'country' not in l_keys:     #variable for country name
        ct = ''
    else:
        ct  = location.raw['address']['country']

    return [mun, sta, ct, str(lon), str(lat), '1']

# Update CSV file
#______________________________________________________

def updateCSV(newData):
    #create a temp file and write in the new data
    with open(r'..\layers\temp.csv', 'w', encoding="utf-8") as temp:
        #write in the header line
        temp.write('City,State or Province,Country,Longitude,Latitude,Count\n')
        for line in newData:
            temp.write(",".join(line)+'\n')
            
    #some file management
    dt = datetime.now().strftime('%Y-%m-%d-T%H-%M-%S')          #store current datetime in a variable
    os.rename('..\\layers\\city_locations.csv','..\\layers\\PreviousVersions\\city_locations_'
              +dt+'.csv')                                       #rename old csv file so there remains a backup
    os.rename('..\\layers\\temp.csv',
              '..\\layers\\city_locations.csv')           #rename temp file
    oldF = os.listdir('..\\layers\\PreviousVersions')           #get list of old csv files
    oldF.sort(reverse=True)                                     #sort alphanumerically descending
    for i in range(len(oldF)):
        if i > 99:                                   
            os.remove('..\\layers\\PreviousVersions\\'+oldF[i]) #remove the oldest files beyond the first 100
            

# Update js data file
#______________________________________________________

def updateMap (newData):
    #open the js file to write into
    with open(r'..\layers\city_locations.geojson', 'w', encoding="utf-8") as jsOut:
        
        #write begining of js file
        jsOut.write('{"type":"FeatureCollection","name":"city_locations","crs":{"type":"name","properties":{"name":"urn:ogc:def:crs:OGC:1.3:CRS84"}},"features":[')

        #iterate through each line of data read from CSV
        for line in newData:
            dataPoint = (
            '{"type":"Feature","properties":{'
            f'"city":"{line[0]}","country":"{line[2]}","longitude":{line[3]},"latitude":{line[4]},"count":{line[5]}'
            '},"geometry":{"type":"Point","coordinates":['
            f'{line[3]},{line[4]}'
            ']}}'
            )                               #store the data point with proper formatting in a variable
            jsOut.write(dataPoint)          #write the data point to the js file

            #if the data point is not the last one, insert a comma for formatting purposes      
            if line != newData[-1]:
                jsOut.write(',')
            else:
                jsOut.write(']}')               #write end of js file                
                

#======================================================
# Import Modules
#======================================================

import os
from geopy.geocoders import Nominatim
from datetime import datetime

#setup variable
geolocator = Nominatim(user_agent="my-application")
    #warning on nominatin usage from GeoPy documentation:    
        #Using Nominatim with the default "geopy/1.17.0" user_agent is strongly discouraged, 
        #as it violates Nominatim's ToS operations.osmfoundation.org/policies/nominatim 
        #and may possibly cause 403 and 429 HTTP errors. 
        #Please specify a custom user_agent with Nominatim(user_agent="my-application") 
        #or by overriding the default user_agent: geopy.geocoders.options.default_user_agent = "my-application"    


#======================================================
# Get user input and call functions, loop if asked 
#======================================================
update = (input('Did you need to update the map from the CSV without adding data?[Y/N]')).upper()
if update[0] == 'Y':        #only run the functions to update the map based on the data currently in the CSV file
    Data = getData()        #pull in data from CSV
    updateMap(Data)         #update the map file
    print('\n---Map has been updated')
    print('\n\n---Closing The Script_____________________________________________________')
else:
    print('\n')
    #functionality to run the script multiple times
    again = 'Y'
    while again[0] == 'Y':
        try:
            #pull in the data from the csv
            Data = getData()

            #determine if the user wants to geocode or reverse geocode
            geo = (input('Do you have the name of the location? [Y/N]')).upper()
            if geo[0] == 'Y':
                #user input for geocoding
                cty     = input('\tPlease enter the name of the city: ').title()
                st      = input('\tPlease enter the name of the province or state: ').title()
                ctry    = input('\tPlease enter the name of the country: ').title()

                #check if the input is a duplicate city
                Dupe, Data = duplicateData(cty, st, ctry, Data)
                if Dupe == 'n':

                    #run geolocator
                    NewCity = findLatLong(cty, st, ctry, geolocator)
                    
                    #check again for duplicate
                    Dupe, Data = duplicateData(NewCity[0], NewCity[1], NewCity[2], Data)

                    #if still not a duplicate
                    if Dupe == 'n':
                    
                        #add data from geolocator to our list containing our data
                        Data.append(NewCity)
                        print('\n---Adding new city data to files')               
            else:
                #run function for reverse geocoding
                NewCity = findFromCoord(geolocator)
                Data.append(NewCity)
                print('\n---Adding new city data to files')
                        
            #update files
            updateCSV(Data)
            updateMap(Data)
            print('\n---Files have been updated')                

            #ask user if they want to run the script again
            again = (input('\n\tWould you like to run the script again for another location?[Y/N]')).upper()
            if again[0] == 'Y':
                print('\n\n---Restarting_____________________________________________________________\n\n')
            else:
                print('\n\n---Closing The Script_____________________________________________________')
        except:
            print('\nSomething went wrong \n'
                  'Please check your data and re-enter')
            again = 'Y'
