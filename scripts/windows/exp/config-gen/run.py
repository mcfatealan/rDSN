from subprocess import call
import os

batch_size_options = ['1', '8', '32', '128']

base = [['python', 'gen-config.py', 'name=config.ini'],
    ['python', 'gen-config.py', 'name=config-all.ini', 'tags=toollets-all', 'apps=layer1'],
    ['python', 'gen-config.py', 'name=config-tracer.ini', 'tags=toollets-tracer', 'apps=layer1'],
    ['python', 'gen-config.py', 'name=config-profiler.ini', 'tags=toollets-profiler', 'apps=layer1'],
    ['python', 'gen-config.py', 'name=config-fault_injector.ini', 'tags=toollets-fault_injector', 'apps=layer1'],
    ['python', 'gen-config.py', 'name=config-webstudio.ini', 'tags=webstudio', 'apps=layer2']]

for batch_size in batch_size_options:
    directory = "config" + batch_size
    if not os.path.exists(directory):
            os.makedirs(directory)
    for ins in base:
        call(ins + ['root=' + directory] + ['batch_size=' + batch_size])