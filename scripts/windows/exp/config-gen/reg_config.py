import copy

global config_sentences
global max_batch_size

config_sentences = []
max_batch_size = "1"

def set_max_batch_size(value):
    global max_batch_size
    max_batch_size = value
    
def add(content, org_include = [], org_exclude = []):
    include = copy.copy(org_include)
    exclude = copy.copy(org_exclude)
   # print [content,include,exclude]
    global config_sentences
    fin_include = []
    for inc in include:
        if inc.startswith('not:') :
            exclude.append(inc[4:])
        else:
            fin_include.append(inc)
    config_sentences.append([content, fin_include, exclude])
    #print [content,fin_include,exclude]

def add_some(contents, org_include = [], org_exclude = []): 
    for c in contents:
        include = copy.copy(org_include)
        exclude = copy.copy(org_exclude)
        if type(c).__name__ == 'list':
            if len(c) > 1:
                for i in range(1, len(c)):
                    _inc = include + c[i]
                    add(c[0], _inc, exclude) 
            else:
                add(c[0], include, exclude)
        else:
            add(c, include, exclude)

def gen_common_config():
    #content, include, exclude
    add_some([
        '[apps..default]',
        'run = true',
        'count = 1',
        ''])
    
    add_some(['[core]',
        'start_nfs = true',
        'tool = fastrun',
        ['toollets = profiler', ['layer1', 'toollets-profiler'], ['webstudio']],
        ['toollets = fault_injector', ['layer1', 'toollets-fault_injector']],
        ['toollets = tracer', ['layer1', 'toollets-tracer']],
        ['toollets = profiler, fault_injector, tracer', ['layer1','toollets-all']],
        'perf_counter_factory_name = dsn::tools::simple_perf_counter_v2_fast',
        'logging_factory_name = dsn::tools::hpc_logger',
        ''])

    add_some([
        '[tools.simulator]',
        'random_seed = 0',
        ''])

    add_some([
        '[network]',
        'io_service_worker_count = 4',
        ''])

    add_some([
        '[threadpool..default]',
        'worker_share_core = true',
        'worker_affinity_mask = 65535',
        'worker_count = 4',
        ''])

    add_some([
        '[threadpool.THREAD_POOL_DEFAULT]',
        'name = default',
        'partitioned = false',
        'max_input_queue_length = 1024',
        'worker_priority = THREAD_xPRIORITY_NORMAL',
        ''])

    add_some([
        '[task..default]',
        'is_trace = true',
        'is_profile = true',
        'allow_inline = false',
        'rpc_call_channel = RPC_CHANNEL_TCP',
        'fast_execution_in_network_thread = false',
        'rpc_call_header_format_name = dsn',
        'rpc_timeout_milliseconds = 5000',
        'perf_test_rounds = 10000',
        'rpc_msg_payload_serialize_default_format = DSF_THRIFT_BINARY',
        '',
        'disk_read_fail_ratio = 0.0',
        'disk_write_fail_ratio= 0.0',
        'rpc_message_delay_ms_min = 0',
        'rpc_message_delay_ms_max = 0',
        'disk_io_delay_ms_min = 0',
        'disk_io_delay_ms_max = 0',
        ''])
    
    add_some([
        'perf_test_seconds = 30',
        'perf_test_key_space_size = 5000000',
        'perf_test_concurrency = 30',
        'perf_test_payload_bytes = 100',
        'perf_test_timeouts_ms = 3000',
        ''],
        ['not:webstudio'])
        
    add_some([
        'perf_test_seconds = 20000000000000',
        'perf_test_key_space_size = 1000',
        'perf_test_concurrency = 10',
        'perf_test_payload_bytes = 10',
        'perf_test_timeouts_ms = 1000',
        ''],
        ['webstudio'])

    add_some([
        '[task.LPC_AIO_IMMEDIATE_CALLBACK]',
        'is_trace = false',
        'is_profile = false',
        'allow_inline = false',
        ''])

    add_some([
        '[task.LPC_RPC_TIMEOUT]',
        'is_trace = false',
        'is_profile = false',
        ''])

def gen_layer1_config():
    add_some([
        '[apps.server]',
        'name = server',
        'type = server',
        'arguments = ',
        'ports = 33001',
        'run = true',
        'pools = THREAD_POOL_DEFAULT',
        ['dmodule = dsn.apps.KyotoCabinet', ['kyotocabinet']],
        ['dmodule = dsn.apps.LevelDb', ['leveldb']],
        ['dmodule = dsn.apps.MemCached', ['memcached']],
        ['dmodule = dsn.apps.ThumbnailServe', ['thumbnail']],
        ['dmodule = dsn.apps.XLock', ['xlock']],
        ['dmodule = rrdb', ['rrdb']],
        ['dmodule = redis', ['redis']],
        ''],
        ['layer1'])

def gen_layer2_config():
    add_some([
        '[apps.meta]',
        'type = meta',
        'dmodule = dsn.meta_server',
        'arguments = ',
        'ports = 34601',
        'run = true',
        'count = 1',
        'pools = THREAD_POOL_DEFAULT,THREAD_POOL_META_SERVER,THREAD_POOL_FD',
        ''],
        ['layer2'])

    add_some([
        '[uri-resolver.dsn://mycluster]',
        'factory = partition_resolver_simple',
        'arguments = %meta_address%:34601',
        ''],
        ['layer2'])

    add_some([
        '[meta_servers]',
        '%meta_address%:34601',
        ''],
        ['layer2'])

    add_some([
        '[apps.webstudio]',
        'name = webstudio',
        'type = webstudio',
        'arguments = 8088',
        'pools = THREAD_POOL_DEFAULT',
        'dmodule = dsn.dev.python_helper',
        'dmodule_bridge_arguments = rDSN.WebStudio/rDSN.WebStudio.py',
        ''],
        ['layer2', 'webstudio'])

    gen_layer2_stateless_config()
    gen_layer2_stateful_config()

def gen_layer2_stateless_config():
    add_some([
        '[apps.daemon]',
        'type = daemon',
        'arguments =',
        'ports = 34901',
        'run = true',
        'count = 1',
        'pools = THREAD_POOL_DEFAULT,THREAD_POOL_FD,THREAD_POOL_REPLICATION',
        '',
        'package_server_host = %meta_address%',
        'package_server_port = 34601',
        'package_dir = ./packages',
        'app_port_min = 59001',
        'app_port_max = 60001',
        'dmodule = dsn.layer2.stateless',
        ''],
        ['layer2', 'stateless'])

    add_some([
        '[meta_server.apps.0]',
        'app_name = server.instance0',
        ['app_type = thumbnail', ['thumbnail']],
        ['app_type = memcached', ['memcached']],
        'partition_count = 1',
        'max_replica_count = 3',
        'stateful = false',
        ''],
        ['layer2', 'stateless'])

def gen_layer2_stateful_config():
    base_tags = ['layer2', 'stateful']
    add_some([
        '[apps.replica]',
        'type = replica',
        'dmodule = dsn.layer2.stateful.type1',
        'arguments =',
        'ports = 34801',
        'run = true',
        'count = 3',
        'pools = THREAD_POOL_DEFAULT,THREAD_POOL_REPLICATION_LONG,THREAD_POOL_REPLICATION,THREAD_POOL_FD,THREAD_POOL_LOCAL_APP',
        ['hosted_app_type_name = server', ['not:simple_kv']],
        ['hosted_app_type_name = simple_kv', ['simple_kv']],
        'hosted_app_arguments =',
        ''],
        base_tags)

    add_some([
        '[threadpool.THREAD_POOL_REPLICATION]',
        'name = replication',
        'partitioned = true',
        'max_input_queue_length = 2560',
        'worker_priority = THREAD_xPRIORITY_ABOVE_NORMAL',
        'worker_share_core = false',
        'worker_count = 32',
        ''],
        base_tags)

    add_some([
        ['[task.RPC_LEVELDB_LEVELDB_PUT]', ['leveldb']],
        ['[task.RPC_XLOCK_XLOCK_WRITE]', ['xlock']],
        ['[task.RPC_REDIS_REDIS_WRITE]', ['redis']],
        ['[task.RPC_KYOTOCABINET_KYOTOCABINET_PUT]', ['kyotocabinet']],
        ['[task.RPC_RRDB_RRDB_PUT]', ['rrdb']],
        ['[task.RPC_SIMPLE_KV_SIMPLE_KV_WRITE]', ['simple_kv']],
        'rpc_request_is_write_operation = true',
        ['[task.RPC_RRDB_RRDB_REMOVE]', ['rrdb']],
        ['rpc_request_is_write_operation = true', ['rrdb']],
        ''],
        base_tags)

    add_some([
        ['[task.RPC_LEVELDB_LEVELDB_BATCH_PUT]', ['leveldb']],
        ['[task.RPC_XLOCK_XLOCK_BATCH_WRITE]', ['xlock']],
        ['[task.RPC_REDIS_REDIS_BATCH_WRITE]', ['redis']],
        ['[task.RPC_KYOTOCABINET_KYOTOCABINET_BATCH_PUT]', ['kyotocabinet']],
        ['[task.RPC_RRDB_RRDB_BATCH_PUT]', ['rrdb']],
        ['rpc_request_is_write_operation = true', ['leveldb'], ['xlock'], ['kyotocabinet'], ['rrdb'], ['redis']],
        ['[task.RPC_RRDB_RRDB_BATCH_REMOVE]', ['rrdb']],
        ['rpc_request_is_write_operation = true', ['rrdb']],
        ''],
        base_tags)
        
    add_some([
        '[replication.app]',
        'app_name = server.instance0',
        'partition_count = 32',
        'max_replica_count = 3',
        'stateful = true',
        ['app_type = server', ['not:simple_kv']],
        ['app_type = simple_kv', ['simple_kv']],
        ''],
        base_tags)

    add_some([
        '[replication]',
        'prepare_timeout_ms_for_secondaries = 10000',
        'prepare_timeout_ms_for_potential_secondaries = 20000',
        'learn_timeout_ms = 30000',
        'staleness_for_commit = 20',
        'staleness_for_start_prepare_for_potential_secondary = 110',
        'mutation_max_size_mb = 15',
        'mutation_max_pending_time_ms = 20',
        'mutation_2pc_min_replica_count = 2',
        'checkpoint_min_decree_gap = 100',
        'checkpoint_interval_seconds = 50000',
        'prepare_list_max_size_mb = 250',
        'request_batch_disabled = false',
        'group_check_internal_ms = 100000',
        'group_check_disabled = false',
        'fd_disabled = false',
        'fd_check_interval_seconds = 5',
        'fd_beacon_interval_seconds = 3',
        'fd_lease_seconds = 14',
        'fd_grace_seconds = 15',
        'working_dir = .',
        'log_buffer_size_mb = 1',
        'log_pending_max_ms = 100',
        'log_file_size_mb = 32',
        'log_batch_write = true',
        'log_enable_shared_prepare = true',
        'log_enable_private_commit = false',
        'config_sync_interval_ms = 60000',
        ''],
        base_tags)

def gen_perf_config():
    global max_batch_size
    
    add_some([
        ['[apps.client.perf.kyotocabinet]', ['kyotocabinet']],
        ['name = client.perf.kyotocabinet', ['kyotocabinet']],
        ['type = client.perf.kyotocabinet', ['kyotocabinet']],
        ['[apps.client.perf.xlock]', ['xlock']],
        ['name = client.perf.xlock', ['xlock']],
        ['type = client.perf.xlock', ['xlock']],
        ['[apps.client.perf.leveldb]', ['leveldb']],
        ['name = client.perf.leveldb', ['leveldb']],
        ['type = client.perf.leveldb', ['leveldb']],
        ['[apps.client.perf.memcached]', ['memcached']],
        ['name = client.perf.memcached', ['memcached']],
        ['type = client.perf.memcached', ['memcached']],
        ['[apps.client.perf.thumbnail]', ['thumbnail']],
        ['name = client.perf.thumbnail', ['thumbnail']],
        ['type = client.perf.thumbnail', ['thumbnail']],
        ['[apps.client.perf.redis]', ['redis']],
        ['name = client.perf.redis', ['redis']],
        ['type = client.perf.redis', ['redis']],
        ['[apps.client.perf.rrdb]', ['rrdb']],
        ['name = client.perf.rrdb', ['rrdb']],
        ['type = client.perf.rrdb', ['rrdb']],
        ['[apps.client.perf.simple_kv]', ['simple_kv']],
        ['name = client.perf.test', ['simple_kv']],
        ['type = client.perf.test', ['simple_kv']],
        'count = 1',
        'run = true',
        'pools = THREAD_POOL_DEFAULT',
        ['delay_seconds = 1', ['not:stateless']],
        ['delay_seconds = 15', ['stateless']],
        'max_batch_size = ' + max_batch_size,
        ['dmodule = dsn.apps.KyotoCabinet', ['kyotocabinet']],
        ['dmodule = dsn.apps.LevelDb', ['leveldb']],
        ['dmodule = dsn.apps.Memcached', ['memcached']],
        ['dmodule = dsn.apps.ThumbnailServe', ['thumbnail']],
        ['dmodule = dsn.apps.XLock', ['xlock']],
        ['dmodule = rrdb', ['rrdb']],
        ['dmodule = redis', ['redis']],
        ['dmodule = dsn.replication.simple_kv.module', ['simple_kv']],
        ['arguments = dsn://mycluster/server.instance0', ['layer2']],
        ['arguments = %server_address%:33001', ['layer1']],
        ''])

    add_some([
        '[apps.client.perf.test]',
        ['type = client.perf.kyotocabinet ', ['kyotocabinet']],
        ['type = client.perf.xlock', ['xlock']],
        ['type = client.perf.leveldb', ['leveldb']],
        ['type = client.perf.memcached', ['memcached']],
        ['type = client.perf.thumbnail', ['thumbnail']],
        ['type = client.perf.redis', ['redis']],
        ['type = client.perf.rrdb', ['rrdb']],
        ['type = client.perf.simple_kv', ['simple_kv']],
        'exit_after_test = true',
        ''],
        [])

    add_some([
        ['[kyotocabinet.perf-test.case.0]', ['kyotocabinet']],
        ['[xlock.perf-test.case.0]', ['xlock']],
        ['[leveldb.perf-test.case.0]', ['leveldb']],
        ['[memcached.perf-test.case.0]', ['memcached']],
        ['[thumbnail.perf-test.case.0]', ['thumbnail']],
        ['[rrdb.perf-test.case.0]', ['rrdb']],
        ['[redis.perf-test.case.0]', ['redis']],
        ['[simple_kv.perf-test.case.0]', ['simple_kv']],
        ['perf_test_seconds = 10', ['not:leveldb']],
        ['perf_test_seconds = 1', ['leveldb']],
        ['perf_test_hybrid_request_ratio = 1,0', ['kyotocabinet'], ['leveldb'], ['memcached'], ['simple_kv'], ['xlock']],
        ['perf_test_hybrid_request_ratio = 1', ['thumbnail']],
        ['perf_test_hybrid_request_ratio = 1,0,0', ['rrdb']],
        ['perf_test_hybrid_request_ratio = 0,1,0,0,0,0,0,0,0,0,0,0,0,0,0', ['redis']],
        ''],
        [])

    add_some([
        ['[kyotocabinet.perf-test.case.1]', ['kyotocabinet']],
        ['[xlock.perf-test.case.1]', ['xlock']],
        ['[leveldb.perf-test.case.1]', ['leveldb']],
        ['[memcached.perf-test.case.1]', ['memcached']],
        ['[thumbnail.perf-test.case.1]', ['thumbnail']],
        ['[rrdb.perf-test.case.1]', ['rrdb']],
        ['[redis.perf-test.case.1]', ['redis']],
        ['[simple_kv.perf-test.case.1]', ['simple_kv']],
        ['perf_test_hybrid_request_ratio = 1,4 ',
            ['kyotocabinet', 'not:webstudio'],
            ['leveldb', 'not:webstudio'],
            ['memcached', 'not:webstudio'], 
            ['simple_kv', 'not:webstudio']],
        ['perf_test_hybrid_request_ratio = 4,1 ', ['xlock', 'not:webstudio']],
        ['perf_test_hybrid_request_ratio = 1,0 ',
            ['kyotocabinet', 'webstudio'],
            ['leveldb', 'webstudio'],
            ['memcached', 'webstudio'],
            ['simple_kv', 'webstudio'],
            ['xlock', 'webstudio']],
        ['perf_test_hybrid_request_ratio = 1 ', ['thumbnail']],
        ['perf_test_hybrid_request_ratio = 4,1,0', ['rrdb']],
        ['perf_test_hybrid_request_ratio = 0,1,4,0,0,0,0,0,0,0,0,0,0,0,0', ['redis']],
        ''],
        [])

"""
    for i in range(1, 16):
        add('[redis.perf-test.case.' + str(i) + ']', ['redis'])
        add('perf_test_seconds = 10', ['redis'])
        t = 'perf_test_hybrid_request_ratio = '
        for j in range(1, 16):
            if j != 1:
               t = t + ',' 
            if j == i:
                t = t + str(1)
            else:
                t = t + str(0)
        add(t, ['redis'])
"""

def get_config_sentence():
    global config_sentences
    gen_common_config()
    gen_layer1_config()
    gen_layer2_config()
    gen_perf_config()
    return config_sentences
