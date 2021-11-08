from flask import Flask
from flask import request
from flask import render_template
import pandas as pd
import numpy as np
import requests
import json
import pickle
from datetime import datetime

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    pkl_ld = open("route_data.pkl", "rb")
    route_data = pickle.load(pkl_ld)
    pkl_ld.close()

    route_dict = dict()

    column_name = list(route_data[0].keys())
    for id in column_name:
        route_dict[id] = [route_data[i][id] for i in range(len(route_data))]

    route_df = pd.DataFrame(route_dict)

    route_name_list = list(route_df['route_long_name'].unique())

    if request.method == 'GET':
        # return render_template('view.html')
        data = {}
        return render_template('view.html', route_name_list=route_name_list, data=data)

    elif request.method == 'POST':
        route_name = request.form['Route']
        data_dict = dict()
        df = route_df[route_df.route_long_name == route_name]
        vehicle_list = list(df['vehicle_id'].unique())
        for veh_id in vehicle_list:
            df1 = df[df.vehicle_id == veh_id]
            l1 = df1.values.tolist()
            data_dict[veh_id] = l1[0][-3:-1]

        return render_template('view.html', data=data_dict)


if __name__ == '__main__':
    app.run(debug=True)
