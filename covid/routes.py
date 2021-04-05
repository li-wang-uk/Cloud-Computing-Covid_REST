from flask import render_template, request, jsonify, redirect, url_for
from covid import app, db, bcrypt
import json
import requests
from covid.forms import RegistrationForm, LoginForm
from covid.models import Favorite, User
from flask_login import login_user, logout_user, current_user, login_required


def create_country_summary(x, summary_json):
	'''
	method that creates a country(x)'s covid stats summary from a json data (summary_json)
	achieved from external API (https://api.covid19api.com/summary).
	x is an instance of Favorite.
    '''
	countries_summary = summary_json["Countries"]
	for country in countries_summary:
		# if the slug (country code) matches x's slug, create the country's covid stats summary 
		if country["Slug"] == x.slug: 
			country_summary = {"Country":country["Country"],
								"Date":country["Date"],
								"NewConfirmed":country["NewConfirmed"],
								"NewDeaths":country["NewDeaths"],
								"NewRecovered":country["NewRecovered"],
								"Slug":country["Slug"],
								"TotalConfirmed":country["TotalConfirmed"],
								"TotalDeaths":country["TotalDeaths"],
								"TotalRecovered":country["TotalRecovered"],
								"WatchLevel":x.watchlevel} 
								# WatchLevel: the priority of the country for the user. Possible values are "high", "middle" or "low".
			break
	return country_summary


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET"])
def register():
	# if the user is already logged in, redirect the user to "home"
	if current_user.is_authenticated:
		return redirect(url_for("home"))

	form = RegistrationForm()
	return render_template("register.html", form=form)


@app.route("/register", methods=["POST"])
def create_user():
	form = RegistrationForm()
	hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8") # create a hashed password from the userinput
	
	# create a new user and store it to DB
	user = User(username=form.username.data, password=hashed_password)
	db.session.add(user)
	db.session.commit()
	
	return redirect(url_for("login"))


@app.route("/login", methods=["GET"])
def login():
	# if the user is already logged in, redirect the user to "home"
	if current_user.is_authenticated:
		return redirect(url_for("home"))

	form = LoginForm()
	return render_template("login.html", form=form)


@app.route("/login", methods=["POST"])
def login_post():
	form = LoginForm()

	# check if the username and password are valid. If so, redirect the user to "home", otherwise show this page again
	user = User.query.filter_by(username=form.username.data).first()
	if user and bcrypt.check_password_hash(user.password, form.password.data):
		login_user(user)
		return redirect(url_for("home"))
	else:
		return render_template("login.html", form=form)


@app.route("/account", methods=["GET"])
@login_required # non-logged in user cannnot access
def account():
	return render_template("account.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))    


@app.route('/global', methods=['GET'])
def get_global():
	'''
	returns global covid stats summary achieved from external API (https://api.covid19api.com/summary)
    '''
	resp = requests.get("https://api.covid19api.com/summary")
	if resp.ok:
		summary_json = resp.json()
		global_summary = summary_json["Global"]
		return global_summary
	else:
		return resp.reason


@app.route('/all', methods=['GET'])
def get_all():
	'''
	returns all countries' covid stats summary achieved from external API (https://api.covid19api.com/summary)
    '''
	resp = requests.get("https://api.covid19api.com/summary")
	if resp.ok:
		summary_json = resp.json()
		countries_summary = summary_json["Countries"]
		
		# drop unnecessary attributes
		for country_summary in countries_summary:
			del country_summary["CountryCode"], country_summary["ID"], country_summary["Premium"] 
		return jsonify(countries_summary)
	else:
		return resp.reason


@app.route('/all/ranking/<stat>', methods=['GET'])
def ranked_by_stat(stat):
	'''
	returns all countries ranked in descending order by their value of the statistic entered by the user
	'''
	resp = requests.get("https://api.covid19api.com/summary")
	if resp.ok:
		summary_json = resp.json()
		summary_dict = dict(summary_json)

		# only if statistic entered in URL is a key in the summary dictionary
		if stat in summary_json["Countries"][0]:
			
			# sort list in reverse order
			desc_order = sorted(summary_dict["Countries"], key=lambda i: i[f"{stat}"], reverse=True)
			ranks = {}
			for n in range(len(desc_order)):

				# display only country and the statistic
				ranks[n+1] = {
					"Country": desc_order[n]["Country"],
					f"{stat}": desc_order[n][f"{stat}"]
				}
			return jsonify(ranks), 200
		else:
			return jsonify({'error':'Statistic not available'}), 400
	else:
		return resp.reason


@app.route('/favorite', methods=['GET'])
@login_required # non-logged in user cannnot access
def get_favorite():
	'''
	returns covid stats summary of favorite countries of the current user.
	a list of favarite countries is stored in the DB.
    '''
	favorite_countries = Favorite.query.filter_by(favorite_user=current_user).all() # get favorite countries of the user

	# if no country is registerd as a favorite country, return an error message
	if len(favorite_countries) == 0:
		return jsonify({"message": "no favorite country registered"})

	resp = requests.get("https://api.covid19api.com/summary")
	if resp.ok:
		summary_json = resp.json()
		favorite_summary = [] # empty list to store the summary of the favorite countries
		for favorite_country in favorite_countries:
			favorite_country_summary = create_country_summary(favorite_country, summary_json) # call create_country_summary() to create a summary
			favorite_summary.append(favorite_country_summary)
		return jsonify(favorite_summary)
	else:
		return resp.reason


@app.route('/favorite', methods=['POST'])
@login_required # non-logged in user cannnot access
def create_favorite():
	'''
	the user can add a new country to the list of favorite countries.
	must specify the slug of the new country and "WatchLevel".
	"WatchLevel" must be "high", "middle" or "low".
    '''

	# if a request is not json or no "slug" in the request, return an error
	if not request.json or not 'Slug' in request.json:
		return jsonify({'error':'the slug of the country is needed'}), 400

	resp = requests.get("https://api.covid19api.com/summary")
	if resp.ok:
		summary_json = resp.json()
		countries_summary = summary_json["Countries"]
		slug_list = [country["Slug"] for country in countries_summary] # a list of slugs of the all countries

		# slug must be in the slug list
		if request.json["Slug"] not in slug_list: 
			return jsonify({'error':'invalid slug'}), 400

		# slug must not be already registered to the favorite coutnries of the user
		elif request.json["Slug"] in [favorite.slug for favorite in Favorite.query.filter_by(favorite_user=current_user).all()]:
			return jsonify({'error':'this country is already registered'}), 400	

		# "WatchLevel" must be "high", "middle" or "low"
		elif request.json["WatchLevel"] not in ["high", "middle", "low"]:
			return jsonify({'error':'WatchList must be "high", "middle" or "low"'}), 400

		# create a new Favorite and store it to DB		
		else: 
			new_favorite = Favorite(slug=request.json["Slug"], watchlevel=request.json["WatchLevel"], favorite_user=current_user)
			db.session.add(new_favorite)
			db.session.commit()
			return jsonify({'message': '{} is added to your favorite countries'.format(request.json["Slug"])}), 201

	else:
		return resp.reason


@app.route('/favorite/<country>', methods=['GET'])
@login_required # non-logged in user cannnot access
def get_favorite_country(country):
	'''
	returns covid stats summary of a favorite country in the favorite list of the current user
    '''

	# the country must be in the favorite list of the user
	if country not in [favorite.slug for favorite in Favorite.query.filter_by(favorite_user=current_user).all()]:
		return jsonify({'error':'no such country in your favorite countries'}), 400

	resp = requests.get("https://api.covid19api.com/summary")
	if resp.ok:
		summary_json = resp.json()
		favorite_country = Favorite.query.filter_by(favorite_user=current_user).filter_by(slug=country).first()
		favorite_country_summary = create_country_summary(favorite_country, summary_json)
		return jsonify(favorite_country_summary)
	else:
		return resp.reason


@app.route('/favorite/<country>', methods=['PUT'])
@login_required # non-logged in user cannnot access
def change_watchlevel(country):
	'''
	the user can change "WatchLevel" of his favorite country
    '''

	# the country must be in the favorite list of the user
	if country not in [favorite.slug for favorite in Favorite.query.filter_by(favorite_user=current_user).all()]:
		return jsonify({'error':'no such country in your favorite countries'}), 400

	# request must specify new "WatchLevel"
	if not request.json or not 'WatchLevel' in request.json:
		return jsonify({'error':'new WatchLevel is needed'}), 400
	
	# "WatchLevel" must be "high", "middle" or "low"
	if request.json["WatchLevel"] not in ["high", "middle", "low"]:
		return jsonify({'error':'WatchList must be "high", "middle" or "low"'}), 400

	# change the "WatchLevel" and store it to DB		
	favorite_country = Favorite.query.filter_by(favorite_user=current_user).filter_by(slug=country).first()
	favorite_country.watchlevel = request.json["WatchLevel"]
	db.session.commit()
	return jsonify({'message': 'the WatchLevel of {} is updated to {}'.format(country, request.json["WatchLevel"])}), 200


@app.route('/favorite/<country>', methods=['DELETE'])
@login_required # non-logged in user cannnot access
def delete_favorite_country(country):
	'''
	the user can delete his favorite country
    '''

	# the country must be in the favorite list of the user
	if country not in [favorite.slug for favorite in Favorite.query.filter_by(favorite_user=current_user).all()]:
		return jsonify({'error':'no such country in your favorite countries'}), 400

	# delete the country and store it to DB		
	Favorite.query.filter_by(favorite_user=current_user).filter_by(slug=country).delete()
	db.session.commit()
	return jsonify({'success': True})


@app.route('/favorite/ranking/<stat>', methods=['GET'])
@login_required # requires user log-in
def favorites_ranked_by_stat(stat):
	'''
	returns only favourite countries ranked in descending order by their value of the statistic entered by the user
	'''
	favorite_countries = Favorite.query.filter_by(favorite_user=current_user).all()
	
	# if no country is registerd as a favorite country, return an error message
	if len(favorite_countries) == 0:
		return jsonify({"message": "no favorite country registered"})

	resp = requests.get("https://api.covid19api.com/summary")
	if resp.ok:
		summary_json = resp.json()
		favorite_summary = [] # empty list to store the summary of the favorite countries
		for favorite_country in favorite_countries:
			favorite_country_summary = create_country_summary(favorite_country, summary_json) # call create_country_summary() to create a summary
			favorite_summary.append(favorite_country_summary)

		# only if statistic entered in URL is a key in favorite_summary
		if stat in favorite_summary[0]:
			
			# sort list in reverse order
			desc_order = sorted(favorite_summary, key=lambda i: i[f"{stat}"], reverse=True)
			ranks = {}
			for n in range(len(desc_order)):

				# display only country and the statistic
				ranks[n+1] = {
					"Country": desc_order[n]["Country"],
					f"{stat}": desc_order[n][f"{stat}"]
				}
			return jsonify(ranks), 200
		else:
			return jsonify({'error':'Statistic not available'}), 400
	else:
		return resp.reason


def queryFunction(commonCountryName):
    '''
    method that allows user to enter "/query/united"in as a query
    and returns a list of mathcing country names and ISO2 codes in the following format
    {"countryNameResult1":["United Kingdom","GB"],"countryNameResult2":["United Arab Emirates","AE"],
    "countryNameResult3":["Tanzania, United Republic of","TZ"],"countryNameResult4":["United States of America","US"]}
    '''
    resp = requests.get("https://api.covid19api.com/countries") #call exteral API and get list of all countries
    if resp.ok:
        countryCodeQueryResult = {}
        counter = 1
        for i in resp.json():
            temp = {}

            if len(commonCountryName) ==2 and commonCountryName.isupper():##check if the input is an ISO2 code
                if commonCountryName == i['ISO2']: # If the userinput is a substring of the current item add it to the return output['ISO2']:
                    temp["countryName{}".format(counter)] = i['Country']
                    temp["countrySlug{}".format(counter)] = i['Slug']
                    temp["countryCode{}".format(counter)] = i['ISO2']
                    countryCodeQueryResult["countryNameResult{}".format(counter)] = [temp["countryName{}".format(counter)], temp["countrySlug{}".format(counter)],temp["countryCode{}".format(counter)]]

            elif commonCountryName.lower().replace(" ", "").replace("-", "") in i['Country'].lower().replace(" ", ""): # If the userinput is a substring of the current item add it to the return output
                temp["countryName{}".format(counter)] = i['Country']
                temp["countrySlug{}".format(counter)] = i['Slug']
                temp["countryCode{}".format(counter)] = i['ISO2']
                countryCodeQueryResult["countryNameResult{}".format(counter)] = [temp["countryName{}".format(counter)],temp["countrySlug{}".format(counter)],temp["countryCode{}".format(counter)]]
                counter += 1

        if len(countryCodeQueryResult) == 1: # if there was only one substring match
            countryName = str(countryCodeQueryResult["countryNameResult1"][0])
            resp2 = requests.get("https://api.covid19api.com/total/country/{}".format(countryName)) #call exteral API for data with the matching countryName
            if resp2.ok:
                summary_json = resp2.json()
                country_summary = summary_json  # ["Countries"]
                return country_summary[len(country_summary) - 1], 200  # return most current stats for the country and 200 code
            else:
                return resp2.reason
        if countryCodeQueryResult == {}:
            return jsonify(
                {'countryCodeResult': 'No result found'}), 400  # return error because no substring match was found 400 code
        if len(countryCodeQueryResult) > 1:
            return jsonify(countryCodeQueryResult), 300  # return list of all partial matches. 300 because of MULTIPLE CHOICES
    else:
        print(resp.reason)


@app.route('/query/<commonCountryName>', methods=['GET'])
def usingQueryFunction(commonCountryName):
    '''uses the fucntion queryFunction to find a matching country and returns output'''
    return queryFunction(commonCountryName) # call the function above and return the output


@app.route('/query/percentage/<commonCountryName>', methods=['GET'])
def PercentageOfGlobalStats(commonCountryName):
    '''PercentageOfGlobalStats passes user input to queryFunction to reuse the same functionality.
     no match returns 400, mulitple matches returns 300 same as queryFunction.
     If only 1 country returned from queryFunction then PercentageOfGlobalStats returns the indivdual countrys  stats
     divided by the global stats.
     '''
    globalStatsJson = get_global()
    queryJson , httpCode = queryFunction(commonCountryName)

    if httpCode == 400:
        return jsonify({'countryCodeResult': 'No result found'}), 400  # return error because no match found 400 code
    elif httpCode == 300:
        return jsonify({'error': 'too many matches. this function only works with one target country please try to narrow your search'}), 300  # return list of all partial matches. 300 because of MULTIPLE CHOICES
    else:
        TotalDeaths = float(globalStatsJson['TotalDeaths'])
        TotalConfirmed = float(globalStatsJson['TotalConfirmed'])
        TotalRecovered = float(globalStatsJson['TotalRecovered'])

        Deaths = float(queryJson['Deaths'])
        Confirmed = float(queryJson['Confirmed'])
        Recovered = float(queryJson['Recovered'])
        country = queryJson['Country']
        return jsonify({
            'A_Description':'{} statistics presented as a percentage % of global statistics'.format(country),
            'Deaths as % of Global Deaths'          :'{:.2f}'.format(Deaths/TotalDeaths*100),
            'Cases as % of Global Cases'            : '{:.2f}'.format(Confirmed/TotalConfirmed*100),
            'Recovered as % of Global Recovered'    : '{:.2f}'.format(Recovered/TotalRecovered*100),

            'DeathRate(Global)'                       : '{:.2f}'.format((TotalDeaths/TotalConfirmed)* 100),
            'DeathRate({})'.format(country): '{:.2f}'.format((Deaths/Confirmed) * 100)
        })


