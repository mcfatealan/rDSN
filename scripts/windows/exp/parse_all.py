import re
import os
import json
import jinja2

apps = ['LevelDb','rrdb','redis','XLock','KyotoCabinet','MemCached','ThumbnailServe']
print_apps = ['LevelDb','rrdb','redis','XLock','MemCached']
layers = ['layer1','layer2']
data = {}
for app in apps:
    data[app] = {}
    for layer in layers:
        data[app][layer] = []

print 'PARSING STARTING...'

for layer in layers:
    for root, dirs, files in os.walk('D:\\log\\'+layer):
        appname = root.split('\\')[-1]
        for filename in files:
            if 'ini' in filename:
                continue
            else:
                logfile = open(root+'\\'+filename)
                logstr = logfile.read()

                pat = re.compile('qps: (.*)#/s')
                qps = re.findall(pat,logstr)[1]
                print appname, layer, qps
                data[appname][layer].append(float(qps))
                logfile.close()

print(json.dumps(data, indent = 4))
print 'PARSE DONE.'


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

nickname = {
        'LevelDb':'LevelDb',
        'rrdb':'Rocksdb',
        'redis':'Redis',
        'XLock':'XLock',
        'KyotoCabinet':'Kyoto\\nCabinet',
        'MemCached':'Mem\\nCached',
        'ThumbnailServe':'Thumbnail\\nServe'
}
datafile = open('D:\\rDSN\\scripts\\windows\\exp\\perf-all.dat','w')
for app in print_apps:
    stat = {}
    for layer in layers:
        stat[layer] = [0.0,0.0,0.0]
        stat[layer][0] = sum(data[app][layer])/float(len(data[app][layer]))/1000.0*32
        stat[layer][1] = min(data[app][layer])/1000.0*32
        stat[layer][2] = max(data[app][layer])/1000.0*32
    Tstr = jinja2.Template('''{{app}}\t{% for layer in layers %}{% for i in range(3)%}{{stat[layer][i]}}\t{% endfor%}{% endfor %}''')
    
    datafile.write(Tstr.render({
        'app': nickname[app],
        'layers': layers,
        'stat':stat
        })+'\n')
datafile.close()


print 'GENERATE PLOT DATA DONE.'
