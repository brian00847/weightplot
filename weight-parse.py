#!/usr/bin/python3

import json, csv
from datetime import datetime


OUT_CSV = './normalized_weights.csv'
garmin_data = 'garmin_connect_data.json'
google_fit_data = 'google-fit-daily-summaries.csv'

class WeightEntry(object):
    def __init__(self, date_obj_, weight_lb_):
        self.date_obj = date_obj_
        self.weight_lb = weight_lb_

LB_TO_GRAMS = 453.592
#Pulling Garmin Data: Use this URL: https://connect.garmin.com/modern/proxy/userprofile-service/userprofile/personal-information/weightWithOutbound/filterByDay?from=1483228800&until=1527807599999
#from and until arguments should be in epoch MILISECONDS!! So add 3 extra 0's

def parse_garmin(garmin_file):
    data_map = {}
    with open(garmin_file) as fin:
        jdata = json.load(fin)
        for day in jdata: 
            weight_grams = float(day['weight'])
            timestamp_ms = int(day['samplePk'])
            timestamp = timestamp_ms / 1000
            date_obj = datetime.fromtimestamp(timestamp).date()
            weight_lb = weight_grams / LB_TO_GRAMS
            data_map[date_obj] = (weight_lb)

    x1 = list()
    for k in sorted(data_map.keys()):
        we = WeightEntry(k, data_map[k])
        #x1.append( (k, data_map[k] ) )
        x1.append(we)

    return x1

def fill_google_weights(weight_entries):
    prev_weight = None
    normalized_data = list()
    for we in weight_entries:

        #if len(we.weight_lb) == 0:
        if we.weight_lb == None:
            if prev_weight == None:
                continue
            else:
                we.weight_lb = prev_weight
                #we = (we[0], prev_weight)

        normalized_data.append(we)
        prev_weight = we.weight_lb
    
    return normalized_data
    
    

def parse_google_fit(google_fit_file):
    weight_entries = list()
    with open(google_fit_file, newline='') as csvfile:
        my_csv_reader = csv.reader(csvfile)
        irow = 0
        for row in my_csv_reader:
            irow += 1
            if irow == 1:
                continue
            gdate = row[0]
            weight1_kg =  row[11] #Average weight
            if not weight1_kg:
                weight_lb = None
            else:
                weight_lb = ( float(weight1_kg) * 1000.0 ) / LB_TO_GRAMS
            #print(weight1_kg)
            #if 
            #weight2 =  row[12] #Max Weight
            #weight3 =  row[13] #Min Weight
            date_obj = datetime.strptime(gdate , '%Y-%m-%d').date()
            we = WeightEntry(date_obj, weight_lb)

            #weight_entries.append((date_obj, weight1))
            weight_entries.append(we)

            #print('date: %s. w1: %s w2: %s w3: %s' % ( str(date_obj), weight1, weight2, weight3))
    normalized_data = fill_google_weights(weight_entries)
    return normalized_data 

def dump_entries(entries, out_csv):
    fout = open(out_csv, 'w')
    for we in entries: 

        #fout.write('{}, {}\n'.format(x[0], x[1]))
        fout.write('{}, {}\n'.format(we.date_obj, we.weight_lb))
    

def combine_entries(entries1, entries2):
    d1 = dict()

    for e in entries1:
        d1[e.date_obj] = e

    for e in entries2:
        #if the date already exists
        if e.date_obj in d1.keys():
            e1 = d1[e.date_obj]
            print('overlapped data: date: {} e2 {} e1 {}'.format(e.date_obj, e.weight_lb, e1.weight_lb))
        else:
            d1[e.date_obj] = e
        #d2[e.date_obj] = e
    print("Found total of {} weight entries".format(len(d1)))
    sorted_list = list()
    for k in sorted(d1.keys()):
        sorted_list.append(d1[k])
    return sorted_list

weight_entries_garmin = list()
weight_entries_google = list()

if 1:
    weight_entries_garmin = parse_garmin(garmin_data)

if 1:
    weight_entries_google = parse_google_fit(google_fit_data)

print("Parsed {} entries from Garmin Connect Data".format(len(weight_entries_garmin)))
print("Parsed {} entries from Google Fit Data".format(len(weight_entries_google)))

combined_list = combine_entries(weight_entries_garmin, weight_entries_google)
print("{} entries total".format(len(combined_list)))
#for we in combined_list:
    #print("{} {}".format(we.date_obj, we.weight_lb))

dump_entries(combined_list, OUT_CSV)


