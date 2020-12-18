import sqlite3 # to connect to database
import json # response returned by API
from flask_api import FlaskAPI # API library similar to Django
from flask import request # for GET request parameters

db_name = 'example'
app = FlaskAPI(__name__)

app.config["DEBUG"] = True

@app.route('/country', methods=['GET'])
def country():
    """ Return covid statistic per country
    """
    conn = sqlite3.connect(f"{db_name}.db")
    c = conn.cursor()
    # c.execute(
    #     """
    #     SELECT country_region, SUM(Confirmed), DATE(last_update) AS last_update 
    #     FROM example GROUP BY country_region, last_update 
    #     ORDER BY last_update;
    
    # """)
    c.execute(
        """select Country_Region, sum(Confirmed), sum(deaths), sum(recovered) 
        from example 
        group by Country_Region 
        order by country_region;""")
    content = c.fetchall()
    c.close()
    data = [{'country': country, 'confirmed': confirmed, 'deaths': deaths, 'recovered': recovered} \
        for country, confirmed, deaths, recovered in content]
    return {
        'request_data': data
    }

@app.route('/summary', methods=['GET'])
def summary(): # using query parameters
    """ Return global summary of covid statistics
    """
    conn = sqlite3.connect(f"{db_name}.db")
    c = conn.cursor()
    # optional parameters in format YYYY-MM-DD, ex 2020-09-13
    start = request.args.get('start')
    end = request.args.get('end')
    print(start,end)
    
    if start and end:
        c.execute(
            f"""select sum(Confirmed), sum(deaths), sum(recovered) 
            from example where DATE(last_update) <= '{end}' and DATE(last_update) >= {start};""")
    else:
        c.execute(
            f"""select sum(Confirmed), sum(deaths), sum(recovered) 
            from example;""")
    content = c.fetchall()
    c.close()
    data = [{'confirmed': confirmed, 'deaths': deaths, 'recovered': recovered} \
        for confirmed, deaths, recovered in content]
    return {
        'request_data': data
    }


# @app.route('/data')
# def data():
#     # here we want to get the value of user (i.e. ?user=some-value)
#     user = request.args.get('user')

# labels = ['Province_State', 'Country_Region', 'Last_Update', 'Confirmed', 'Deaths', 'Recovered']

app.run()
