import asyncio
import httpx

from celery import shared_task
from .services.parser import ShopifyParser, CONCURRENCY, TIMEOUT
from .models import Shop


@shared_task(bind=True)
def parse_and_save(self, shops_list):
    async def runner():
        semaphore = asyncio.Semaphore(CONCURRENCY)
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            async def process_shop(url):
                async with semaphore:
                    parser = ShopifyParser(url)
                    cart_url = await parser.build_cart(client)
                    return url, cart_url, parser.error_message

            tasks = [process_shop(u) for u in shops_list if u.strip()]
            return await asyncio.gather(*tasks)

    results = asyncio.run(runner())

    for url, cart_url, error in results:
        status = 'success' if cart_url else 'error'
        shop, _ = Shop.objects.update_or_create(
            url=url,
            defaults={
                'cart_url': cart_url,
                'error_message': error,
                'status': status,
            })


@shared_task
def retry_failed_shops(urls):
    async def runner():
        semaphore = asyncio.Semaphore(CONCURRENCY)
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            async def process_shop(url):
                async with semaphore:
                    parser = ShopifyParser(url)
                    cart_url = await parser.build_cart(client)
                    return url, cart_url, parser.error_message

            tasks = [process_shop(u) for u in urls]
            return await asyncio.gather(*tasks)

    results = asyncio.run(runner())

    for url, cart_url, error in results:
        shop, _ = Shop.objects.update_or_create(
            url=url,
            defaults={
                'cart_url': cart_url,
                'error_message': error,
                'status': 'success' if cart_url else 'failed',
            }
        )
