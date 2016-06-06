
cd config1
python ..\gen-config.py name=config.ini
python ..\gen-config.py name=config-all.ini tags=toollets-all apps=layer1
python ..\gen-config.py name=config-tracer.ini tags=toollets-tracer apps=layer1
python ..\gen-config.py name=config-profiler.ini tags=toollets-profiler apps=layer1
python ..\gen-config.py name=config-fault_injector.ini tags=toollets-fault_injector apps=layer1
python ..\gen-config.py name=config-webstudio.ini tags=webstudio apps=layer2
cd ..

cd config8
python ..\gen-config.py name=config.ini batch_size=8
python ..\gen-config.py name=config-all.ini tags=toollets-all apps=layer1 batch_size=8
python ..\gen-config.py name=config-tracer.ini tags=toollets-tracer apps=layer1 batch_size=8
python ..\gen-config.py name=config-profiler.ini tags=toollets-profiler apps=layer1 batch_size=8
python ..\gen-config.py name=config-fault_injector.ini tags=toollets-fault_injector apps=layer1 batch_size=8
python ..\gen-config.py name=config-webstudio.ini tags=webstudio apps=layer2 batch_size=8
cd ..

cd config32
python ..\gen-config.py name=config.ini batch_size=32
python ..\gen-config.py name=config-all.ini tags=toollets-all apps=layer1 batch_size=32
python ..\gen-config.py name=config-tracer.ini tags=toollets-tracer apps=layer1 batch_size=32
python ..\gen-config.py name=config-profiler.ini tags=toollets-profiler apps=layer1 batch_size=32
python ..\gen-config.py name=config-fault_injector.ini tags=toollets-fault_injector apps=layer1 batch_size=32
python ..\gen-config.py name=config-webstudio.ini tags=webstudio apps=layer2 batch_size=32
cd ..

cd config128 
python ..\gen-config.py name=config.ini batch_size=128
python ..\gen-config.py name=config-all.ini tags=toollets-all apps=layer1 batch_size=128
python ..\gen-config.py name=config-tracer.ini tags=toollets-tracer apps=layer1 batch_size=128
python ..\gen-config.py name=config-profiler.ini tags=toollets-profiler apps=layer1 batch_size=128
python ..\gen-config.py name=config-fault_injector.ini tags=toollets-fault_injector apps=layer1 batch_size=128
python ..\gen-config.py name=config-webstudio.ini tags=webstudio apps=layer2 batch_size=128
cd ..