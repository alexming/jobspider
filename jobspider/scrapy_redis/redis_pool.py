#coding=utf-8


import redis

RedisCfg = {
#职位分享链接缓存
    'remote_252_0': {'host': '192.168.1.250', 'port': 6379, 'db': 0},
#redis缓存数据
    'remote_252_1': {'host': '192.168.1.250', 'port': 6379, 'db': 1},
    'remote_238_0': {'host': '192.168.1.250', 'port': 6379, 'db': 0},
    'remote_238_1': {'host': '192.168.1.250', 'port': 6379, 'db': 1},
    'remote_238_2': {'host': '192.168.1.250', 'port': 6379, 'db': 2},

    'redis_cache_1': {'host': '192.168.1.250', 'port': 6379, 'db': 1},
    'redis_cache_2': {'host': '192.168.1.250', 'port': 6379, 'db': 2},
    'login_cache_0': {'host': '192.168.1.250', 'port': 6379, 'db': 3},
    'local_cache_1': {'host': '127.0.0.1', 'port': 6379, 'db': 1},
}

class TQRedis:
    #私有类变量
    __RedisPool = {}
    #redis 选择db0
    #私有方法
    @classmethod
    def __GetPool(Self, redisName):
        global RedisCfg
        if Self.__RedisPool.has_key(redisName):
            return Self.__RedisPool[redisName]
        else:
            pool = redis.ConnectionPool(
                host=RedisCfg[redisName]['host'],port=RedisCfg[redisName]['port'],db=RedisCfg[redisName]['db']
            )
            Self.__RedisPool[redisName] = pool
            return pool

    @classmethod
    def GetRedis(Self, redisName):
        pool = Self.__GetPool(redisName)
        return redis.Redis(connection_pool=pool)
