# A City Geocoder and Webmap Display

### Description
A simple python script that asks the user for the name of a city and retrieves the latitude and longitude of that city, or recieves coordinate data from the user and retrieves address information through reverse geocoding. The script updates json and csv data files with the new data. 

### Requirements:
- Python  
Download from https://www.python.org/downloads/
- GeoPy  
Using pip, install GeoPy with the command below

        pip install geopy
  
	Documentation available at https://geopy.readthedocs.io/en/stable/
- Nominatim User Name  
Update python script with appropriate user name, line 64 in Geocode.py  
The script is distributed with a default palceholder, using this placeholder violates Nominatims terms of use.

### Usage Instructions 
	
Copy the content in the dist folder into your webpage directory
	
Sample data has been included in the src directory for preview purposes, the layer and data files in the dist directory has been left empty for individual use. 
	
Update the data displayed in the map by using the python script:
Answer the prompts to enter the city, state, and country information of the city you want to add to the map, or if the city name is uncertain, enter the longitude and latitude coordinates. The state or country prompts can be left blank if that information is not known or not applicable. 
	
You can also manually update the csv data file and then run the python script, chosing the option to update the map without adding data. This will update the geojson file and the webmap display based on the data in the csv without prompting for additional information. 
		
### License
Licensed under the MIT License
	
### Credits
Basemap supplied by OpenStreetMap (c) OpenStreetMap and OpenStreetMap contributors  
Geocoder by Nominatim (c) Nominatim and Nominatim contributors  
Geocoding Python library by GeoPy (c) GeoPy contributors  
Webmap built using OpenLayers API and Vite.  
