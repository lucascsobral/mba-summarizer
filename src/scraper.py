"""
Web scraping script using Playwright for automated browser interactions.

This script logs into a website, navigates to a specific page, and captures
requests to a specific URL pattern. The captured requests are stored in a list
and returned at the end of the script.

Environment Variables:
- URL_SITE: The base URL of the site to log into.
- URL_LINK_DOWNLOAD: The URL pattern to capture requests for.
- URL_CLASS: The URL of the page to navigate to after login.
- LOGIN: The login username.
- PASSWORD: The login password.
"""

import os
from dotenv import load_dotenv
import asyncio
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
import time

# Load environment variables from a .env file
load_dotenv()

# Environment variables
URL_SITE: Optional[str] = os.getenv("URL_SITE")
URL_LINK_DOWNLOAD: Optional[str] = os.getenv("URL_LINK_DOWNLOAD")
URL_CLASS: Optional[str] = os.getenv("URL_CLASS")
LOGIN: Optional[str] = os.getenv("LOGIN")
PASSWORD: Optional[str] = os.getenv("PASSWORD")

class WebAutomator:
    """
    A class to automate web interactions using Playwright.
    """

    def __init__(self) -> None:
        """
        Initializes the WebAutomator with browser, page, and context set to None.
        """
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.context: Optional[BrowserContext] = None

    async def open_browser(self) -> None:
        """
        Opens a browser instance and creates a new context and page.
        """
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
        )
        self.page = await self.context.new_page()

    async def login(self, url: str, username: Optional[str] = None, password: Optional[str] = None) -> None:
        """
        Logs into the website using the provided URL, username, and password.

        Args:
            url (str): The URL of the login page.
            username (str): The login username.
            password (str): The login password.
        """
        await self.page.goto(url)
        await self.page.fill("#signInName", username)
        await self.page.fill("#password", password)
        await self.page.click("#next")
        time.sleep(5)

    async def goto_page_content(self, url: str) -> None:
        """
        Navigates to the specified URL and waits for the page to load.

        Args:
            url (str): The URL of the page to navigate to.
        """
        await self.page.goto(url, wait_until="load")

    async def wait_element(self, selector: str) -> None:
        """
        Waits for an element specified by the selector to appear on the page.

        Args:
            selector (str): The CSS selector of the element to wait for.
        """
        await self.page.wait_for_selector(selector)

    async def get_p_class_query(self, class_name: str) -> List:
        """
        Queries all <p> elements within a specified class.

        Args:
            class_name (str): The class name to query for <p> elements.

        Returns:
            list: A list of elements matching the query.
        """
        return await self.page.query_selector_all(f".{class_name} p")

    async def close_browser(self) -> None:
        """
        Closes the browser instance.
        """
        await self.browser.close()

async def scraper_main() -> tuple[str, str | None] | None:
    """
    Main function to execute the web automation tasks.
    """
    wa = WebAutomator()
    try:
        await wa.open_browser()
        await wa.login(
            URL_SITE,
            LOGIN,
            PASSWORD,
        )

        await wa.goto_page_content(URL_CLASS)

        await wa.wait_element("#tabContent > #tab-content-cards > div.container")

        div = await wa.page.query_selector("#tabContent")
        div = await div.query_selector_all(".card.card-default")

        actual_date = datetime.now() # - timedelta(days=2) # For testing a class from x days ago
        previous_date = actual_date - timedelta(days=1)
        str_previous_date = previous_date.strftime("%d/%m/%Y")

        link: Optional[str] = None
        class_name: Optional[str] = None

        for d in div:
            p_date = await d.query_selector("p.card-small-text-11")
            p_date = await p_date.inner_text()
            p_date = p_date.split(" - ")[0]
            if p_date == str_previous_date:
                class_name = await d.query_selector("h4")
                class_name = await class_name.inner_text()
                a_tag = await d.query_selector("a")
                link = await a_tag.get_attribute("href")
                break

        print(class_name)

        if link is None:
            print("No class found")
            return None

        requests_list: List[str] = []
        request_captured = False  # Flag to track if the desired request has been captured

        async def handle_request(route, request) -> None:
            """
            Handles network requests and captures those matching the URL pattern.

            Args:
                route: The route object.
                request: The request object.
            """
            nonlocal request_captured
            try:
                if URL_LINK_DOWNLOAD in request.url and not request_captured:
                    requests_list.append(request.url)
                    request_captured = True  # Set the flag to stop further handling
                    print(f"Captured request: {request.url}")
                    # Continue the request
                    await route.continue_()
                else:
                    await route.continue_()
            except Exception as e:
                print(f"Error handling request: {e}")
                await route.continue_()

        await wa.context.route("**/*", handle_request)

        if link is not None:
            try:
                # Start navigation to the class page
                navigation_task = asyncio.create_task(wa.page.goto(URL_SITE + link, wait_until="networkidle"))

                # Wait while the request is captured or timeout is reached
                for _ in range(30):  # Attempts for 30 seconds (adjust if necessary)
                    if request_captured:
                        # Request captured, cancel navigation and exit the loop
                        navigation_task.cancel()  # Cancel navigation
                        break
                    await asyncio.sleep(1)  # Check every 1 second

                # Ensure the browser is closed after capturing the request
                await wa.close_browser()

                if requests_list:
                    request_link = requests_list[0]
                    return request_link, class_name
                else:
                    print("No class found")
                    return None
            except Exception as e:
                print(f"Error: {e}")
                await wa.close_browser()
                raise e
        else:
            print("No class found")
            await wa.close_browser()
            return None

    except Exception as e:
        print(f"Error: {e}")
        await wa.close_browser()
        raise e

# if __name__ == "__main__":
#     asyncio.run(main())