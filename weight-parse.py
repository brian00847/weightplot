#!/usr/bin/python

import json, csv
from datetime import datetime

#matplot lib is installed for python2.7 on CentOS 7
import matplotlib
import matplotlib.pyplot as plt
import numpy as np



OUT_CSV = './normalized_weights.csv'
garmin_data = 'rawdata/garmin_connect_data.json'
google_fit_data = 'rawdata/google-fit-daily-summaries.csv'

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
    with open(google_fit_file) as csvfile:
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

#def annotate_plot(plt, fig):

def plot_entries(weight_entries):
    t = [ e.date_obj for e in weight_entries[2:] ]
    s = [ e.weight_lb for e in weight_entries[2:] ]

    fig, ax = plt.subplots()
    ax.plot(t, s)

    ax.set(xlabel='date', ylabel='weight (freedom units)',
        title='Weight from 2018 to 2019')
    ax.grid()

    annotations = [( datetime(2018, 5, 15).date(), 'Highest weigh in'),
                   ( datetime(2018, 6, 15).date(), 'Actually Make Changes in Diet'),
                   ( datetime(2018, 7, 1).date(), "Holy Shit it's working!! Lets keep going!!"),
                   ( datetime(2019, 3, 5).date(), "abc123")]
    for annotation in annotations:
        d = annotation[0]
        annotated_text = annotation[1]
        #d = datetime(2018, 5, 15).date()
        #annotated_text = 'Begin Here'

        #for x in weight_entries:
        #    print x.date_obj
        new_list = [ x for x in  weight_entries if x.date_obj == d]
        #print(d)
        #print(len(new_list))
        #print(weight_entries)
        annotated_entry = new_list[0]
        x = annotated_entry.date_obj
        y = annotated_entry.weight_lb

        plt.annotate(annotated_text, xy=(x, y), xytext=(x, y + 5),
                    arrowprops=dict(facecolor='black', shrink=0.05),
                                )


    fig.savefig("test.png")
    plt.show()

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

#Remove old data
combined_list = [ e for e in combined_list if e.date_obj.year >= 2018 and e.date_obj.month >= 3]

plot_entries(combined_list)


