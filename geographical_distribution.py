import pandas as pd
import requests
import time

# matching ISO-2 and ISO-3 codes of countries
iso_codes = pd.read_csv('Country.csv', delimiter=';')
iso_2_to_3 = {}
for i, iso2 in enumerate(iso_codes['Alpha2Code'].values):
    iso_2_to_3[iso2.upper()] = iso_codes['Alpha3Code'].values[i].upper()


# loading data of sql-query results
locations = pd.read_csv('QueryResults.csv')
locations = locations['Location'].astype(str).values.tolist()

# Google Maps Geocoding API is used to match user addresses to the corresponding countries
with open('api_key.txt', 'r') as f:
    api_key = f.read()
output_format = 'json'
url_base = 'https://maps.googleapis.com/maps/api/geocode/' + output_format + '?address='

geo_distr = {}
relevant_users_count = 0
for address in locations:
    # generating the http-request
    address_for_request = ('+').join(address.split(' '))
    url = url_base + address_for_request + '&key=' + api_key
    response = requests.get(url)
    json_result = response.json()

    # processing possible errors which can occur in the response
    if not json_result['results']:
        continue
    tries = 0
    while json_result['status'] == 'OVER_QUERY_LIMIT' and tries < 10:
        tries += 1
        time.sleep(0.5)
        response = requests.get(url)
        json_result = response.json()
    results = json_result['results'][0]

    # parsing the json result of the request
    found = 0
    for comp in results['address_components']:
        if comp['types'][0] == 'country':
            country = comp
            found = 1
            break
    if not found:
        continue

    # getting the name of the country and ISO-2 code
    long_name = country['long_name']
    iso2 = country['short_name']

    # determining the ISO-3 code of the country and evaluating the corresponding number of users
    iso3 = iso_2_to_3[iso2]
    if long_name in geo_distr.keys():
        geo_distr[long_name][1] += 1
    else:
        geo_distr[long_name] = [iso3, 1]

    relevant_users_count += 1
    if relevant_users_count >= 1000:
        break

# writing the resulting geographical distribution to .csv-file
with open('geographical_distribution.csv', 'w') as f:
    f.write('Country,ISO-3,NumOfUsers\n')
    for country_name in geo_distr.keys():
        f.write('{},{},{}\n'.format(country_name, geo_distr[country_name][0], geo_distr[country_name][1]))
