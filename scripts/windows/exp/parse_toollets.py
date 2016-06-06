import re
import os
import json
import jinja2

apps = ['LevelDb','rrdb','redis','XLock','KyotoCabinet','MemCached','ThumbnailServe']
toollets = ['bare','tracer','profiler','fault_injector']
toollets_without_bare = ['tracer','profiler','fault_injector']
data = {}
for app in apps:
    data[app] = {}
    for tool in toollets:
        data[app][tool] = []

print 'PARSING STARTING...'

for root, dirs, files in os.walk('D:\\rDSN\\scripts\\windows\\exp\\log_graph'):
    appname = root.split('\\')[-1]
    for filename in files:
        if 'ini' in filename:
            continue
        else:
            chosen_tool = ''
            for tool in toollets:
                if tool in filename:
                    chosen_tool = tool

            logfile = open(root+'\\'+filename)
            logstr = logfile.read()

            #timeout alert
            #tmo_pat = re.compile('suc(#): (.*),')
            #print re.findall(tmo_pat,logstr)
            #tmo_err_suc = re.findall(tmo_pat,logstr)[1]
            #tmo = int(tmo_err_suc.split('/')[0])
            #err = int(tmo_err_suc.split('/')[1])
            #suc = int(tmo_err_suc.split('/')[2])
            #print (suc<0.8*(tmo+err+suc))
            #if(suc<0.8*(tmo+err+suc)):
            #    print 'WARNING! ' + logfile + 'contains big timeout error!'

            pat = re.compile('qps: (.*)#/s')
            qps = re.findall(pat,logstr)[1]
            print appname, chosen_tool, qps
            data[appname][chosen_tool].append(float(qps))
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
        'MemCached':'MemCached',
        'ThumbnailServe':'Thumbnail\\nServe'
}
datafile = open('D:\\rDSN\\scripts\\windows\\exp\\overhead.dat','w')
for app in apps:
    stat = {}
    for tool in toollets:
        bare_qps = sum(data[app]['bare'])/float(len(data[app]['bare']))
        stat[tool] = [0,0,0]
        stat[tool][0] = sum(data[app][tool])/float(len(data[app][tool]))/bare_qps
        stat[tool][1] = min(data[app][tool])/bare_qps
        stat[tool][2] = max(data[app][tool])/bare_qps
    Tstr = jinja2.Template('''{{app}}\t{% for tool in toollets_without_bare%}{% for i in range(3)%}{{stat[tool][i]}}\t{% endfor%}{% endfor%}''')
    
    datafile.write(Tstr.render({
        'app': nickname[app],
        'bare_qps': "%.1f" % (bare_qps/1000),
        'toollets_without_bare': toollets_without_bare,
        'stat':stat
        })+'\n')
datafile.close()


print 'GENERATE PLOT DATA DONE.'
