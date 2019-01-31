#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.font_manager import FontProperties

from optparse import OptionParser
from pathlib import Path
from numpy import arange

import os, json

def mttr_handler(name, data):

    if data['build_count'] == 0:
        return

    x_p = []
    y_p = []
    x_ticks = []
    y_ticks = []

    '''
    x_axis_from = data['builds'][0]['number']
    x_axis_to = data['builds'][-1]['number'] + 5

    y_axis_from = data['builds'][0]['mttr']/1000
    y_axis_to = data['builds'][-1]['mttr']/1000 + 1000
    '''

    plt.figure(figsize=(10, 8))

    for build in data['builds']:
        print('create plot:' \
            '\t x:{}' \
            '\t y:{}' \
            '\t text:{}'.format(
                build['number'], build['mttr'], build['mttr_string']))
        x = build['number']
        y = build['mttr']/1000
        x_p.append(x)
        y_p.append(y)
        x_ticks.append('build id: {}'.format(x))
        y_ticks.append('{}'.format(y))

        plt.text(x, y, build['mttr_string'],
                fontproperties=fontProperity)

    plt.plot(x_p, y_p, marker='o')
    plt.xticks(x_p, x_ticks, rotation=17)
    plt.yticks(y_p, y_ticks)
    plt.savefig('{}-MTTR.png'.format(name))
    plt.clf()


DATA_TYPE_HANDLERS = {
    "mttr": mttr_handler
}

def handleJob(name, data):
    print('handle job:' + name)

    try:
        DATA_TYPE_HANDLERS[options.type](name, data)
    except KeyError as e:
        print('type: {} not support'.format(options.type))

def handleDocument(fPath):
    f = open(fPath, 'r')
    try:
        obj = json.load(f)
    except ValueError as e:
        f.close()
        sys.exit(1)

    if 'view_path' in obj:
        print(obj['view_path'])

    if options.job_name:
      try:
        print(obj['jobs'][options.job_name])
      except KeyError as e:
          pass
      return

    if 'jobs' in obj:
        for job_name, data in obj['jobs'].items():
            handleJob(job_name, data)

def searchDocument(folder, suffix):
    for root, dirs, files in os.walk(folder):
        for _file in files:
            fPath = Path(root, _file)
            if fPath.suffix != suffix:
                continue
            print('handle document {}'.format(fPath))

            result = handleDocument(fPath)
            retrievedResult[fPath] = result

if __name__ == '__main__':
    parser = OptionParser()  

    parser.add_option("-x", "--x-label", default="X values",
        action = "store", dest = "x_label",
        help = "x label")

    parser.add_option("-y", "--y-label", default="Y values",
        action = "store", dest = "y_label",
        help = "y label")

    parser.add_option("-p", "--pairs",
        action = "store", dest = "pairs",
        help = "plot values")

    parser.add_option("-F", "--jobs-info-folder",
        action = "store", dest = "folder",
        help = "The folder of JSON data")

    parser.add_option("-T", "--type", default = 'mttr',
        action = "store", dest = "type",
        help = "analyze type, eg: mttr, failed-rate")

    parser.add_option("-j", "--job-name", default = None,
        action = "store", dest = "job_name",
        help = "job_name")


    (options, args) = parser.parse_args()

    '''
    for font in fm.findSystemFonts():
        print(fm.FontProperties(fname=font).get_name())
    '''

    fontProperity = FontProperties(fname=r'/usr/share/fonts/truetype/takao-gothic/TakaoPGothic.ttf', size=14)

    retrievedResult = {}
    documentList = searchDocument(options.folder, ".json")
