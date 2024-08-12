from .request import get_proxy_list, get_proxy_list_with_test

proxy_list = []
proxy_list_test = []
proxy_index = 0
async def get_proxy(url=None, best=False, with_test=False):
  """
  Get the proxy
  """
  global proxy_list, proxy_list_test, proxy_index
  if not proxy_list:
    proxy_list = get_proxy_list(3)
  if not proxy_list_test or with_test:
    proxy_list_test = await get_proxy_list_with_test(url or "https://www.baidu.com", proxy_list)
  if not proxy_list_test:
    return None
  if best:
    return proxy_list_test[0]
  else:
    proxy = proxy_list_test[proxy_index]
    proxy_index = (proxy_index + 1) % len(proxy_list_test)
    return proxy
  
def get_proxy_next():
  """
  Get the next proxy
  """
  global proxy_list_test, proxy_index
  if not proxy_list_test:
    return None
  else:
    proxy = proxy_list_test[proxy_index]
    proxy_index = (proxy_index + 1) % len(proxy_list_test)
    return proxy