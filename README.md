# Covid-19 REST API
- Provides global/all countries covid summary/ranking for non-login users 
- Provides favorite countries covid summary/ranking for login users 
- Login users can add/delete countries to their favorite countries 
- Login users can edit “WatchLevel” of their favorite countries 


# Data Source
- This API uses the following external API as a data source: 
https://covid19api.com/


# Pages for housekeeping
##Home (/)
- Links for register, login and logout 

##Login (/login)
- CURL example (need to use “-c cookie” to keep the state in the following sessions) 
    - curl -X POST -d username=Sarah -d password=sarahsmith -c cookie <URL>
- You can use the following user as test users
    - username=Sarah, password=sarahsmith 
    - username=John, password=johnsmith 

##Register (/register)
- The user can register a new user

##Account (/account)
- Login required
- Shows username and password of the current user

##Logout (/logout)
- Logout from the current session


# API endpoints 
## /global
- Provides global summary 
- Login not required 
- GET only 
- CURL example 
    - curl <URL>                                                                                                

## /all
- Provides all countries' summary 
- Login not required 
- GET only 
- CURL example 
    - curl <URL>

## /all/ranking/<stat>
- Allows the user to view all the countries in ranked order based on a statistic entered in the URL. 
- GET method, not user authentication required 
- Returns 400 if the request was unsuccessful as the statistic entered by the user was invalid. 
- CURL example 
    - curl <URL>                                              

## /favorite
- Provide the summary and “WatchLevel” (how much seriously the user follows the country)  of favorite countries of the login user 
- Login required 
- GET, POST 
- CURL example (need to login (create a cookie) beforehand) 
    - curl -b cookie -v <URL> 
    - curl -i -H "Content-Type:application/json" -X POST -b cookie -d "{\"Slug\":\"japan\", \"WatchLevel\":\"middle\"}" <URL> 

## /favorite/<country>
- Provide the summary and “WatchLevel” (how seriously the user follows the country)  of a country in favorite countries of the login user 
- <country> is designated by “slug” in the country (e.g., united-kingdom, france, japan) 
- Login required 
- GET, PUT, DELETE 
- CURL example (need to login (create a cookie) beforehand) 
    - curl -b cookie -v <URL> 
    - curl -i -H "Content-Type:application/json" -X PUT -b cookie -d "{\"WatchLevel\":\"high\"}" <URL>
    - curl -X DELETE -b cookie <URL> 

## /favorite/ranking/<stat> 
- Allows the user to view all of their favorite countries in ranked order based on a statistic entered in the URL. 
- GET method, requires user authentication 
- Returns 400 if the request was unsuccessful as the statistic entered by the user was invalid. 
- CURL example 
    - curl <URL>

## /query/<commonCountryName>
- Allows the user to enter a query (e.g., "united") and returns a list of mathcing country names and ISO2 codes.
- Return format: {"countryNameResult1":["United Kingdom","GB"],"countryNameResult2":["United Arab Emirates","AE"], "countryNameResult3":["Tanzania, United Republic of","TZ"],"countryNameResult4":["United States of America","US"]}
- No match returns 400.
- GET only 
- CURL example 
    - curl <URL>

## /query/percentage/<commonCountryName>
- Returns an indivdual country's stats divided by the global stats.
- No match returns 400, mulitple matches returns 300.
- GET only 
- CURL example 
    - curl <URL>


# Coursework Requirements 

- The application provides a dynamically generated REST API. The API must have a sufficient set of services for the selected application domain. The REST API responses must conform to REST standards (e.g. response codes).  3 Points 
    - => OK. This API provides REST services about covid-19, including GET, POST, PUT and DELETE methods.
- The application makes use of an external REST service to complement its functionality. 3 Points
    - => OK. This API uses the following external API as a data source: 
https://covid19api.com/
- The application uses a cloud database for accessing persistent information. 3 Points
    - => OK. This API uses a cloud database (Azure SQL database) and store persistent information about users and their favorite countries.
- The application code is well documented (in each of the code files, as well as in the README.MD file of the git repository). 1 Point 
    - => OK. The codes are documented, and there is a README file.

Option 2: Up to 5 for any 3 implementations as mentioned below  : 
- Serving the application over https. 
    - => OK. This API is served over https.
- Implementing hash-based authentication. 
    - => OK. User password is stored in the hash form in the database. 
- Implementing user accounts and access management. 
    - => Ok. This API offers login features. Users can edit their favorite countries.
