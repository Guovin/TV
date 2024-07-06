from asyncio import Queue, get_running_loop, Semaphore
import re
from bs4 import BeautifulSoup
from tqdm.asyncio import tqdm_asyncio
from concurrent.futures import ThreadPoolExecutor
from driver.setup import setup_driver
from utils.retry import retry_func
from time import sleep
from utils.speed import get_speed


async def get_proxy_list(page_count=1):
    """
    Get proxy list, parameter page_count is the number of pages to get
    """
    url_pattern = [
        "https://www.zdaye.com/free/{}/",
        "https://www.kuaidaili.com/free/inha/{}/",
        "https://www.kuaidaili.com/free/intr/{}/",
    ]
    proxy_list = []
    url_queue = Queue()
    for page_index in range(1, page_count + 1):
        for pattern in url_pattern:
            url = pattern.format(page_index)
            await url_queue.put(url)
    pbar = tqdm_asyncio(total=url_queue.qsize(), desc="Getting proxy list")
    driver = setup_driver()

    def get_proxy(url):
        # driver = None
        try:
            # driver = setup_driver()
            url = pattern.format(page_index)
            retry_func(lambda: driver.get(url), name=url)
            sleep(1)
            source = re.sub(
                r"<!--.*?-->",
                "",
                driver.page_source,
                flags=re.DOTALL,
            )
            soup = BeautifulSoup(source, "html.parser")
            table = soup.find("table")
            trs = table.find_all("tr") if table else []
            for tr in trs[1:]:
                tds = tr.find_all("td")
                ip = tds[0].get_text().strip()
                port = tds[1].get_text().strip()
                proxy = f"http://{ip}:{port}"
                proxy_list.append(proxy)
        finally:
            # if driver:
            #     driver.quit()
            url_queue.task_done()
            pbar.update()

    # with ThreadPoolExecutor(max_workers=5) as executor:
    while not url_queue.empty():
        # loop = get_running_loop()
        url = await url_queue.get()
        get_proxy(url)
        # loop.run_in_executor(executor, get_proxy, url)
    driver.quit()
    pbar.close()
    return proxy_list


async def get_proxy_list_with_test(base_url, proxy_list):
    """
    Get the proxy list with speed test
    """
    if not proxy_list:
        return []
    semaphore = Semaphore(10)

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
