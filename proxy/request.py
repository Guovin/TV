from asyncio import Semaphore
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio
from utils.speed import get_speed
from concurrent.futures import ThreadPoolExecutor
from utils.config import get_config
from driver.utils import get_soup_driver
from requests_custom.utils import get_soup_requests, close_session

config = get_config()


def get_proxy_list(page_count=1):
    """
    Get proxy list, parameter page_count is the number of pages to get
    """
    url_pattern = [
        "https://www.zdaye.com/free/{}/",
        "https://www.kuaidaili.com/free/inha/{}/",
        "https://www.kuaidaili.com/free/intr/{}/",
    ]
    proxy_list = []
    urls = []
    for page_index in range(1, page_count + 1):
        for pattern in url_pattern:
            url = pattern.format(page_index)
            urls.append(url)
    pbar = tqdm(total=len(urls), desc="Getting proxy list")

    def get_proxy(url):
        proxys = []
        try:
            soup = (
                get_soup_driver(url) if config.open_driver else get_soup_requests(url)
            )
            table = soup.find("table")
            trs = table.find_all("tr") if table else []
            for tr in trs[1:]:
                tds = tr.find_all("td")
                ip = tds[0].get_text().strip()
                port = tds[1].get_text().strip()
                proxy = f"http://{ip}:{port}"
                proxys.append(proxy)
        finally:
            pbar.update()
            return proxys

    max_workers = 3 if config.open_driver else 10
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(get_proxy, url) for url in urls]
        for future in futures:
            proxy_list.extend(future.result())
    if not config.open_driver:
        close_session()
    pbar.close()
    return proxy_list


async def get_proxy_list_with_test(base_url, proxy_list):
    """
    Get the proxy list with speed test
    """
    if not proxy_list:
        return []
    semaphore = Semaphore(100)

    async def get_speed_task(url, timeout, proxy):
        async with semaphore:
            return await get_speed(url, timeout=timeout, proxy=proxy)

    response_times = await tqdm_asyncio.gather(
        *(get_speed_task(base_url, timeout=30, proxy=url) for url in proxy_list),
        desc="Testing proxy speed",
    )
    proxy_list_with_test = [
        (proxy, response_time)
        for proxy, response_time in zip(proxy_list, response_times)
        if response_time != float("inf")
    ]
    if not proxy_list_with_test:
        print("No valid proxy found")
        return []
    proxy_list_with_test.sort(key=lambda x: x[1])
    proxy_urls = [url for url, _ in proxy_list_with_test]
    print(f"Valid proxy found: {len(proxy_urls)}")
    return proxy_urls
