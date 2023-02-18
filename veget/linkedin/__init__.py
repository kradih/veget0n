import logging

from typing import List, Tuple, Optional, Any
from time import sleep

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from .profile_link import ProfileLink
from .experience import Experience
from .profile import Profile


class LinkedIn:
    def __init__(self, username: str, password: str, sleep_time: int = 5, timeout: int = 10):
        self.logger: logging.Logger = logging.getLogger(__name__)

        self.username = username
        self.password = password
        self.sleep_time = sleep_time
        self.timeout = timeout

        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(timeout)

    def __enter__(self):
        self.driver.get("https://www.linkedin.com/login")
        self.driver.find_element(By.ID, "username").send_keys(self.username)
        self.driver.find_element(By.ID, "password").send_keys(self.password)
        self.driver.find_element(By.ID, "password").send_keys(Keys.ENTER)

        return self

    def __exit__(self, *exc_info) -> None:
        self.driver.close()

    def search(self, search_url: str) -> List[ProfileLink]:
        """Search for profiles in a LinkedIn search URL."""
        self.logger.info(f"Searching for profiles in {search_url}...")

        profiles: List[ProfileLink] = []
        self.driver.get(search_url)
        while True:
            sleep(self.sleep_time)

            results: list[WebElement] = self.driver.find_elements(By.CLASS_NAME, "entity-result__item")
            for entity in results:
                links: list[WebElement] = entity.find_elements(By.CLASS_NAME, "app-aware-link")
                profile_link_ = ProfileLink(links[1].text.split('\n')[0], links[1].get_attribute("href"))
                self.logger.info(f"Found profile: {profile_link_}")
                profiles.append(profile_link_)
            try:
                self._next_page()
            except NoSuchElementException:
                logging.debug("No more pages found.")
                break
        return profiles

    def get_profile(self, profile_link_: ProfileLink) -> Optional[Profile]:
        """Get a profile from a profile link."""
        self.logger.info(f"Getting profile: {profile_link_}...")

        # Visit the profile page
        self.driver.get(profile_link_.url)
        sleep(self.sleep_time)

        name: Optional[str] = self._extract_name_from_profile_page()
        name = name if name is not None else profile_link_.name
        location: str = self._extract_location_from_profile_page()

        # Get the experience section
        experience_section = self._get_experience_section()
        experiences = self._get_experiences(experience_section, location)
        return Profile(name, experiences)

    def _get_element_without_waiting_by(self, element: Any, by: By, value: str) -> Optional[WebElement]:
        if element is None:
            return None
        try:
            logging.info("Starting to wait for element...")
            self.driver.implicitly_wait(0)
            return element.find_element(by, value)
        except NoSuchElementException:
            return None
        finally:
            self.driver.implicitly_wait(self.timeout)
            logging.info("Finished waiting for element.")

    def _get_elements_without_waiting_by(self, element: Any, by: By, value: str) -> List[WebElement]:
        if element is None:
            return []
        try:
            logging.info("Starting to wait for elements...")
            self.driver.implicitly_wait(0)
            return element.find_elements(by, value)
        except NoSuchElementException:
            return []
        finally:
            self.driver.implicitly_wait(self.timeout)
            logging.info("Finished waiting for elements.")

    def _extract_name_from_profile_page(self) -> Optional[str]:
        """
        Extract the name from the profile page.
        :return: The name of the profile.
        """
        possible_name: Optional[WebElement] = self._get_element_without_waiting_by(
            self.driver, By.CLASS_NAME, "text-heading-xlarge")
        return possible_name.text if possible_name is not None else "Unknown"

    def _extract_location_from_profile_page(self) -> str:
        """
        Extract the location from the profile page.
        :return: The location of the profile.
        """
        possible_location: Optional[WebElement] = self._get_element_without_waiting_by(
            self.driver, By.CSS_SELECTOR, "main > section > .ph5 > .mt2 > .mt2 > span")
        return possible_location.text.strip() if possible_location is not None else "Unknown"

    def _get_experience_section(self) -> Optional[WebElement]:
        """
        Get the experience section from the profile page.
        :return: The experience section.
        """
        try:
            sections: list[WebElement] = self.driver.find_elements(By.TAG_NAME, "section")
        except NoSuchElementException:
            logging.warning(f"Profile has no sections.")
            return None
        for section in sections:
            if section.text.startswith("Experience\nExperience\n"):
                return section
        return None

    def _get_experiences(self, section: WebElement, location: str) -> List[Experience]:
        """
        Get the experiences from a section.
        :param section: The section to get the experiences from.
        :return: A list of experiences.
        """
        experiences: List[Experience] = []
        for item in self._get_experience_entities(section):
            if self._is_multiple_experience(item):
                experiences.extend(self._get_experience_with_multiple_positions(item, location))
            else:
                experience_ = self._get_experience(item, location)
                if experience_ is not None:
                    experiences.append(experience_)
        return experiences

    def _get_experience_entities(self, section: WebElement) -> List[WebElement]:
        """Get the experience entities from a section."""
        entities = self._get_elements_without_waiting_by(
            section, By.CSS_SELECTOR, "section > .pvs-list__outer-container > .pvs-list > li > .pvs-entity")
        return entities if entities is not None else []

    def _get_experience_with_multiple_positions(self, element: WebElement, location: str) -> List[Experience]:
        """Get the experiences from a section with multiple positions."""
        experiences: List[Experience] = []
        company_element: Optional[WebElement] = self._get_element_without_waiting_by(
            element, By.CSS_SELECTOR, "div:nth-of-type(2) > .display-flex > a > div .visually-hidden")
        company: str = company_element.text.strip() if company_element is not None else "Unknown"

        item: WebElement
        items: List[WebElement] = self._get_elements_without_waiting_by(element, By.CSS_SELECTOR, ".pvs-entity")
        for item in items:
            # Get the position
            position_element: Optional[WebElement] = self._get_element_without_waiting_by(
                item, By.CSS_SELECTOR, "div:nth-of-type(2) > div > a > div > span .visually-hidden")
            position: str = position_element.text.strip() if position_element is not None else "Unknown"

            # Get the duration
            duration_element: Optional[WebElement] = self._get_element_without_waiting_by(
                item, By.CSS_SELECTOR, "div:nth-of-type(2) > div > a > .t-black--light > .visually-hidden")
            if duration_element is None:
                start, end = "Unknown", "Unknown"
            else:
                start, end = self._parse_duration(duration_element.text.strip())
            experiences.append(Experience(company, position, start, end, location))
        return experiences

    def _get_experience(self, element: WebElement, location: str) -> Optional[Experience]:
        """Get the experience from a section with a single position."""
        # Get the company
        company_element: Optional[WebElement] = self._get_element_without_waiting_by(
            element, By.CSS_SELECTOR, "div:nth-of-type(2) > div > div > span .visually-hidden")
        try:
            company: str = company_element.text.split("·")[0].strip() if company_element is not None else "Unknown"
        except IndexError:
            company = "Unknown"

        # Get the position
        position_element: Optional[WebElement] = self._get_element_without_waiting_by(
            element, By.CSS_SELECTOR, "div:nth-of-type(2) > div > div > div > span > .visually-hidden")
        position: str = position_element.text.strip() if position_element is not None else "Unknown"

        # Get the duration
        duration_element: Optional[WebElement] = self._get_element_without_waiting_by(
            element, By.CSS_SELECTOR, "div:nth-of-type(2) > div > div > span:nth-of-type(2) .visually-hidden")
        if duration_element is None:
            start, end = "Unknown", "Unknown"
        else:
            start, end = self._parse_duration(duration_element.text.strip())
        return Experience(company, position, start, end, location)

    def _is_multiple_experience(self, element: WebElement) -> bool:
        """Check if the experience has multiple positions."""
        found = self._get_element_without_waiting_by(
            element, By.CSS_SELECTOR, "div:nth-of-type(2) > div > .optional-action-target-wrapper")
        return found is not None

    @staticmethod
    def _parse_duration(duration: str) -> Tuple[str, str]:
        try:
            result = list(map(str.strip, duration.split('·')[0].split('-')))
            return result[0], result[1]
        except Exception:
            return 'Unknown', 'Unknown'

    def _next_page(self):
        """Click the next page button."""
        self.logger.debug("Clicking next page button...")
        self.driver.execute_script("window.scrollBy(0, 100000)")
        self.driver.find_element(
            By.CSS_SELECTOR, ".artdeco-pagination__button--next:not(.artdeco-button--disabled)").click()
