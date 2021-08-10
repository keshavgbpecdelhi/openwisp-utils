from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.common.exceptions import NoSuchElementException

User = get_user_model()


class SeleniumTestCase(StaticLiveServerTestCase):
    def open(self, url, driver=None):
        """
        Opens a URL
        Argument:
            url: URL to open
            driver: selenium driver (default: cls.base_driver)
        """
        if not driver:
            driver = self.web_driver
        driver.get(f'{self.live_server_url}{url}')

    def _create_user(self, **kwargs):
        opts = dict(
            username='tester',
            password='tester',
            first_name='Tester',
            last_name='Tester',
            email='test@tester.com',
        )
        opts.update(kwargs)
        user = User(**opts)
        user.full_clean()
        return User.objects.create_user(**opts)

    def _create_admin(self, **kwargs):
        opts = dict(
            username='admin', email='admin@admin.com', is_superuser=True, is_staff=True
        )
        opts.update(kwargs)
        return self._create_user(**opts)

    def login(self, username=None, password=None, driver=None):
        """
        Log in to the admin dashboard
        Argument:
            driver: selenium driver (default: cls.web_driver)
            username: username to be used for login (default: cls.admin.username)
            password: password to be used for login (default: cls.admin.password)
        """
        if not driver:
            driver = self.web_driver
        if not username:
            username = self.admin_username
        if not password:
            password = self.admin_password
        driver.get(f'{self.live_server_url}/admin/login/')
        if 'admin/login' in driver.current_url:
            driver.find_element_by_name('username').send_keys(username)
            driver.find_element_by_name('password').send_keys(password)
            driver.find_element_by_xpath('//input[@type="submit"]').click()

    def logout(self):
        account_button = self._get_account_button()
        account_button.click()
        logout_link = self._get_logout_link()
        logout_link.click()

    def _get_account_button(self):
        return self.web_driver.find_element_by_css_selector('.account-button')

    def _get_account_dropdown(self):
        return self.web_driver.find_element_by_css_selector('.account-menu')

    def _get_logout_link(self):
        return self.web_driver.find_element_by_xpath(
            '//a[@class="menu-link" and @href="/admin/logout/"]'
        )

    def _get_filter(self):
        return self.web_driver.find_element_by_id('ow-changelist-filter')

    def _get_filter_button(self):
        return self.web_driver.find_element_by_id('ow-apply-filter')

    def _get_clear_button(self):
        return self.web_driver.find_element_by_id('changelist-filter-clear')

    def check_exists_by_id(self, id):
        try:
            self.web_driver.find_element_by_id(id)
        except NoSuchElementException:
            return False
        return True

    def check_exists_by_xpath(self, xpath):
        try:
            self.web_driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True

    def check_exists_by_css_selector(self, selector):
        try:
            self.web_driver.find_element_by_css_selector(selector)
        except NoSuchElementException:
            return False
        return True

    def _get_filter_selected_option(self, filter_class):
        return self.web_driver.find_element_by_css_selector(
            f'.{filter_class} .selected-option'
        )

    def _get_filter_dropdown(self, filter_class):
        return self.web_driver.find_element_by_css_selector(
            f'.{filter_class} .filter-options'
        )

    def _get_filter_title(self, filter_class):
        return self.web_driver.find_element_by_css_selector(
            f'.{filter_class} .filter-title'
        )

    def _get_main_content(self):
        return self.web_driver.find_element_by_id('main-content')

    def _get_filter_option(self, option_name):
        return self.web_driver.find_element_by_xpath(f'//label[@for="{option_name}"]')

    def _get_filter_anchor(self, query):
        return self.web_driver.find_element_by_xpath(f'//a[@href="?{query}"]')
