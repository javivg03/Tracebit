from services.proxy_pool import ProxyPool

pool = ProxyPool()
pool.validate_all()

proxy = pool.get_random_proxy()
print("Proxy elegido:", proxy)
