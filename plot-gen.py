#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.font_manager import FontProperties

from optparse import OptionParser
from pathlib import Path
from numpy import arange

import os, json

def failed_rate_handler(name, data):
    if data['build_count'] == 0:
        return

    x_p = []
    y_p = []
    z_p = []
    x_ticks = []
    y_ticks = []

    plt.figure(figsize=(10, 8))

    for build in data['builds']:

        x = build['number']
        y = build['failed_rate'] * 100
        z = build['success_rate'] * 100

        print('create plot:' \
            ' x:{:5}' \
            ' y1:{:10}' \
            ' y2:{:10}'.format(
                x, y, z))

        x_p.append(x)
        y_p.append(y)
        z_p.append(z)

        x_ticks.append('build id: {}'.format(x))

    p1 = plt.bar(x_p, z_p, color='green')
    p2 = plt.bar(x_p, y_p, bottom=z_p, color='red')

    outputPath = Path('graph/{}'.format(options.type))
    outputPath.mkdir(parents=True, exist_ok=True)


    mean_failed_rate = round(sum(y_p)/len(y_p), 2)
    mean_success_rate = round(sum(z_p)/len(z_p), 2)
    plt.figtext(0.3, 0.9, '失敗率平均値:{}%'.format(mean_failed_rate),
        fontproperties=fontProperity)
    plt.figtext(0.1, 0.9, '成功率平均値:{}%'.format(mean_success_rate),
        fontproperties=fontProperity)

    plt.xlabel('build id')
    plt.ylabel('%')
    plt.legend((p1[0], p2[0]), ('success rate', 'failed rate'))
    plt.savefig(Path(outputPath, '{}-failed-rate.png'.format(name)))

    plt.clf()

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
        x_ticks.append('{}'.format(x))
        y_ticks.append('{}'.format(y))

        plt.text(x, y, build['mttr_string'],
                fontproperties=fontProperity)

    outputPath = Path('graph/{}'.format(options.type))
    outputPath.mkdir(parents=True, exist_ok=True)

    plt.xlabel('build id')
    plt.ylabel('seconds')
    plt.plot(x_p, y_p, marker='o')
    plt.xticks(x_p, x_ticks, rotation=0)
    plt.yticks(y_p, y_ticks)
    plt.savefig(Path(outputPath, '{}-MTTR.png'.format(name)))
    plt.clf()


DATA_TYPE_HANDLERS = {
    "mttr": mttr_handler,
    "failed-rate": failed_rate_handler
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

    fileDict = {}
    lastTime = {}
    for root, dirs, files in os.walk(folder):
        for _file in files:
            fPath = Path(root, _file)
            if fPath.suffix != suffix:
                continue

            splited = str(fPath.stem).split('-')
            # time splited[-1]
            # view_path splited[-2]

            if splited[-2] not in lastTime:
                lastTime[splited[-2]] = 0

            if int(splited[-1]) > lastTime[splited[-2]]:
                lastTime[splited[-2]] = int(splited[-1])
                fileDict[splited[-2]] = fPath

    for viewPath, path in fileDict.items():
        print(viewPath)
        print('handle document {}'.format(path))
        result = handleDocument(fPath)
        retrievedResult[path] = result

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
