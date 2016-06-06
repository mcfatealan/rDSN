def used_tags():
    tags = ['layer1', 'layer2', 'stateful', 'stateless',
        'leveldb', 'xlock', 'kyotocabinet', 'memcached', 'thumbnail', 'redis', "rrdb", "simple_kv",
        'toollets-tracer', 'toollets-fault_injector', 'toollets-profiler', 'toollets-all',
        'webstudio']

    return tags;

def app_leveldb():
    confs = []
    confs.append(['layer1/leveldb', ['leveldb', 'layer1']])
    confs.append(['layer2/leveldb', ['leveldb', 'layer2', 'stateful']])
    return confs

def app_xlock():
    confs = []
    confs.append(['layer1/xlock', ['xlock', 'layer1']])
    confs.append(['layer2/xlock', ['xlock', 'layer2', 'stateful']])
    return confs

def app_kyotocabinet():
    confs = []
    confs.append(['layer1/kyotocabinet', ['kyotocabinet', 'layer1']])
    confs.append(['layer2/kyotocabinet', ['kyotocabinet', 'layer2', 'stateful']])
    return confs

def app_memcached():
    confs = []
    confs.append(['layer1/memcached', ['memcached', 'layer1']])
    confs.append(['layer2/memcached', ['memcached', 'layer2', 'stateless']])
    return confs

def app_thumbnailserve():
    confs = []
    confs.append(['layer1/thumbnailserve', ['thumbnail', 'layer1']])
    confs.append(['layer2/thumbnailserve', ['thumbnail', 'layer2', 'stateless']])
    return confs

def app_rrdb():
    confs = []
    confs.append(['layer1/rrdb', ['rrdb', 'layer1']])
    confs.append(['layer2/rrdb', ['rrdb', 'layer2', 'stateful']])
    return confs

def app_redis():
    confs = []
    confs.append(['layer1/redis', ['redis', 'layer1']])
    confs.append(['layer2/redis', ['redis', 'layer2', 'stateful']])
    return confs

def app_simplekv():
    confs = []
    confs.append(['layer2/simple_kv', ['simple_kv', 'layer2', 'stateful']])
    return confs

def app_configs() :
    confs = []
    confs = confs + app_leveldb()
    confs = confs + app_xlock()
    confs = confs + app_kyotocabinet()
    confs = confs + app_memcached()
    confs = confs + app_thumbnailserve()
    confs = confs + app_rrdb()
    confs = confs + app_redis()
    confs = confs + app_simplekv()
    return confs
