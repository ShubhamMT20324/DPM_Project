from flask import Flask
from flask import request
from flask import render_template
import pandas as pd
import numpy as np
import requests
import json
import pickle
from datetime import datetime
import sqlite3 as sql

app = Flask(__name__)

'''
def extractdata(route_name):
    datalist=list()
    df=route_df[route_df.route_long_name == route_name]
    vehicle_list=list(df['vehicle_id'].unique())
    for veh_id in vehicle_list:
        df1=df[df.vehicle_id == veh_id]
        l1=df1[['vehicle_id','route_id','upcoming_stop_id','eta']].values.tolist()
        datalist.append(l1[0])
    
    return datalist 
'''


def getstopname(stopid):
    conn = sql.connect('project.db')
    cur = conn.cursor()
    cur.execute('''
    SELECT STOP_NAME
    FROM STOPS
    WHERE STOP_ID = ?''', (stopid,))
    stopname = cur.fetchone()[0]
    conn.close()
    return stopname


def getarrivaltime(stopid, routeid):
    conn = sql.connect('project.db')
    cur = conn.cursor()
    cur.execute('''
    SELECT ARRIVAL_TIME
    FROM STOP_TIME
    WHERE STOP_ID = ? AND ROUTE_ID= ? ''', [stopid, routeid])
    arrivaltimelist = cur.fetchall()
    conn.close()
    return arrivaltimelist


def getstatus(arrivaltimelist, eta):
    tnow = datetime.now()
    currenttime = tnow.strftime('%H:%M:%S')
    format = '%H:%M:%S'
    arrivaldelay = 120
    scheduledArrival = ""
    status = "On Time"

    for at in arrivaltimelist:
        atime = at[0]
        tempdif = datetime.strptime(
            atime, format) - datetime.strptime(currenttime, format)
        timedif = abs(int(tempdif.total_seconds()/60) - eta)
        if (timedif < arrivaldelay):
            arrivaldelay = timedif
            scheduledArrival = atime

    if arrivaldelay >= 2:
        status = "Running Late"

    return scheduledArrival, status


@app.route('/', methods=['GET', 'POST'])
def index():

    response = requests.get(
        'http://192.168.26.172:14002/all_rt_buses_data').text
    route_data = json.loads(response)

    '''
    pkl_ld = open("route_data.pkl", "rb")
    route_data = pickle.load(pkl_ld)
    pkl_ld.close()
    '''

    route_dict = dict()
    column_name = list(route_data[0].keys())
    for id in column_name:
        route_dict[id] = [route_data[i][id] for i in range(len(route_data))]

    route_df = pd.DataFrame(route_dict)

    route_name_list = list(route_df['route_long_name'].unique())
    route_name_list.sort()

    if request.method == 'GET':
        data = {"": ["", "", "", "", ""]}
        return render_template('view.html', route_name_list=route_name_list, data=data)

    elif request.method == 'POST':

        route_name = request.form['Route']

        datalist = list()
        df = route_df[route_df.route_long_name == route_name]
        vehicle_list = list(df['vehicle_id'].unique())
        for veh_id in vehicle_list:
            df1 = df[df.vehicle_id == veh_id]
            l1 = df1[['vehicle_id', 'route_id',
                      'upcoming_stop_id', 'eta']].values.tolist()
            datalist.append(l1[0])

        data_dict = dict()
        for data in datalist:
            vehid = data[0]
            routeid = data[1]
            stopid = data[2]
            eta = data[3]
            arrivaltimelist = getarrivaltime(stopid, routeid)
            status = getstatus(arrivaltimelist, eta)
            stopname = getstopname(stopid)

            data_dict[vehid] = [stopname, status[0], status[1], eta]

        return render_template('view.html', route_name_list=route_name_list, data=data_dict, route=route_name)


if __name__ == '__main__':
    app.run(debug=True)
