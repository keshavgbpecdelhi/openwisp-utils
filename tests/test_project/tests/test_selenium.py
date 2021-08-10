from django.conf import settings
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..models import Shelf
from .utils import SeleniumTestCase


class TestFilter(SeleniumTestCase):
    admin_username = 'admin'
    admin_password = 'password'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = webdriver.ChromeOptions()
        if getattr(settings, 'SELENIUM_HEADLESS', True):
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1366,768')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--remote-debugging-port=9222')
        capabilities = DesiredCapabilities.CHROME
        capabilities['goog:loggingPrefs'] = {'browser': 'ALL'}
        cls.web_driver = webdriver.Chrome(
            options=chrome_options, desired_capabilities=capabilities
        )

    @classmethod
    def tearDownClass(cls):
        cls.web_driver.quit()
        super().tearDownClass()

    def tearDown(self):
        # Clear local storage
        self.web_driver.execute_script('window.localStorage.clear()')

    def setUp(self):
        self.admin = self._create_admin(
            username=self.admin_username, password=self.admin_password
        )
        self._create_test_data()

    def _create_test_data(self):
        # create two users
        tester1 = self._create_admin(username='tester1', password=self.admin_password)
        self._create_admin(username='tester2', password=self.admin_password)
        '''
        creating 2 Horror and 2 Fantasy shelfs.
        tester1 is the owner of all books
        '''
        for i in range(2):
            Shelf.objects.create(
                name='horror' + str(i), book_type='HORROR', owner=tester1
            )
        for i in range(2):
            Shelf.objects.create(
                name='fantasy' + str(i), book_type='FANTASY', owner=tester1
            )

    def test_shelf_filter(self):
        # It has total number of filters greater than 4
        self.login()
        url = reverse('admin:test_project_shelf_changelist')
        self.open(url)
        dropdown = self._get_filter_dropdown('book-type')
        title = self._get_filter_title('book-type')
        main_content = self._get_main_content()
        selected_option = self._get_filter_selected_option('book-type')
        with self.subTest('Test visibility of filter'):
            self.assertEqual(self.check_exists_by_id('ow-changelist-filter'), True)

        with self.subTest('Test visibility of filter button'):
            self.assertEqual(self.check_exists_by_id('ow-apply-filter'), True)

        with self.subTest('Test filter dropdown is not visible'):
            self.assertEqual(dropdown.is_displayed(), False)

        with self.subTest('Test input tag in filter options'):
            self.assertEqual(
                self.check_exists_by_css_selector('.username .filter-options input'),
                True,
            )
        with self.subTest('Test filter dropdown is visble on click'):
            title.click()
            self.assertEqual(dropdown.is_displayed(), True)
            title.click()
            self.assertEqual(dropdown.is_displayed(), False)
            title.click()
            self.assertEqual(dropdown.is_displayed(), True)
            main_content.click()
            self.assertEqual(dropdown.is_displayed(), False)

        with self.subTest('Test changing of filter option'):
            title.click()  # open dropdown
            old_value = selected_option.get_attribute('innerText')
            fantasy_option = self._get_filter_option('Book typeFANTASY')
            fantasy_option.click()
            self.assertEqual(dropdown.is_displayed(), False)
            self.assertNotEqual(selected_option.get_attribute('innerText'), old_value)
            self.assertEqual(selected_option.get_attribute('innerText'), 'FANTASY')

        filter_button = self._get_filter_button()
        with self.subTest('Test apply filter'):
            filter_button.click()
            WebDriverWait(self.web_driver, 2).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="site-name"]'))
            )
            self.assertEqual(self.check_exists_by_id('changelist-filter-clear'), True)
            paginator = self.web_driver.find_element_by_css_selector('.paginator')
            self.assertEqual(paginator.get_attribute('innerText'), '2 shelfs')

        with self.subTest('Test clear filter button'):
            clear_button = self._get_clear_button()
            clear_button.click()
            WebDriverWait(self.web_driver, 2).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="site-name"]'))
            )
            paginator = self.web_driver.find_element_by_css_selector('.paginator')
            self.assertEqual(paginator.get_attribute('innerText'), '4 shelfs')

        with self.subTest('Test multiple filters'):
            # Select Fantasy book type
            book_type_title = self._get_filter_title('book-type')
            username_title = self._get_filter_title('username')
            book_type_title.click()
            fantasy_option = self._get_filter_option('Book typeFANTASY')
            fantasy_option.click()
            username_title.click()
            username_option = self._get_filter_option('usernametester2')
            username_option.click()
            filter_button = self._get_filter_button()
            filter_button.click()
            WebDriverWait(self.web_driver, 2).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="site-name"]'))
            )
            paginator = self.web_driver.find_element_by_css_selector('.paginator')
            self.assertEqual(paginator.get_attribute('innerText'), '0 shelfs')

    def test_users_filter(self):
        # It has total number of filters less than 4
        self.login()
        url = reverse('admin:auth_user_changelist')
        self.open(url)
        with self.subTest('Test visibility of filter'):
            self.assertEqual(self.check_exists_by_id('ow-changelist-filter'), True)

        with self.subTest('Test filter button is not visible'):
            self.assertEqual(self.check_exists_by_id('ow-apply-filter'), False)

        with self.subTest('Test anchor tag in filter options'):
            self.assertEqual(
                self.check_exists_by_css_selector('.username .filter-options a'), True
            )

        with self.subTest('Test dropdown and apply filter'):
            dropdown = self._get_filter_dropdown('username')
            title = self._get_filter_title('username')
            option = self._get_filter_anchor('username=tester2')
            selected_option = self._get_filter_selected_option('username')
            old_value = selected_option.get_attribute('innerText')
            self.assertEqual(dropdown.is_displayed(), False)
            title.click()
            self.assertEqual(dropdown.is_displayed(), True)
            option.click()
            WebDriverWait(self.web_driver, 2).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="site-name"]'))
            )
            selected_option = self._get_filter_selected_option('username')
            self.assertNotEqual(old_value, selected_option.get_attribute('innerText'))
            self.assertEqual(selected_option.get_attribute('innerText'), 'tester2')
            paginator = self.web_driver.find_element_by_css_selector('.paginator')
            self.assertEqual(paginator.get_attribute('innerText'), '1 user')
