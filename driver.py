import asyncio
import sys
from arsenic import get_session, keys, browsers, services


class NoSuchElementException(Exception):
    # class for exceptions when element is not found
    pass


class RegistrationError(Exception):
    # class for exceptions when registration is not successful
    pass


class SigninError(Exception):
    # class for exceptions when signin is not successful
    pass


class InputError(Exception):
    # class for exceptions when input is not valid
    pass


class Driver:
    def __init__(self):
        # path to geckodriver
        if sys.platform.startswith('win'):
            self.geckodriver = './geckodriver.exe'
        else:
            self.geckodriver = './geckodriver'

        self.session = None

    async def click_element(self, selector):
        # function for clicking element by [selector]
        # raise an exception [NoSuchElementException] if element is not found
        try:
            element = await self.session.get_element(selector)
            await element.click()
        except Exception:
            raise NoSuchElementException(f"Driver.click_element: Error: Unable to locate element '{selector}'")

    async def find_element(self, selector):
        # function for finding element by [selector]
        # raise an exception [NoSuchElementException] if element is not found
        # return element if it is found
        # return None if it is not found
        try:
            element = await self.session.get_element(selector)
        except Exception:
            raise NoSuchElementException(f"Driver.find_element: Error: Unable to locate element '{selector}'")

    async def fill_element(self, selector, data_):
        # function for filling element by [selector] with [data_]
        # raise an exception [NoSuchElementException] if element is not found
        try:
            field = await self.session.get_element(selector)
            await field.send_keys(data_)
        except Exception:
            raise NoSuchElementException(f"Driver.fill_element: Error: Unable to locate element '{selector}'")

    async def fill_elements(self, class_name, data_):
        # function for filling elements by [class_name] with [data_]
        # raise an exception [NoSuchElementException] if element is not found
        input_fields = await self.session.get_elements(class_name)
        if len(input_fields) == 0:
            raise NoSuchElementException(f"Driver.fill_elements: Error: Unable to locate element '{class_name}'")
        for input_field in input_fields:
            field_value = data_.get(await input_field.get_attribute('name'))
            await input_field.send_keys(field_value)

    async def open_browser_for_sign_in(self, username, password):
        # function for opening browser for sign in with [username] and [password]
        # raise an exception [SigninError] if sign in is not successful
        try:
            async with (get_session(services.Geckodriver(binary=self.geckodriver), browsers.Firefox()) as self.session):
                await self.session.get('http://cappa.csu.ru/')
                await self.click_element('.profile__bar-login')
                await self.fill_element('#id_login', username)
                await self.fill_element('#id_password', password)
                await self.click_element('.btn')
        except Exception as e_:
            raise SigninError(e_)

    async def open_browser_for_cr(self, data_):
        # function for opening browser for creating new account with [data_]
        # raise an exception [RegistrationError] if registration is not successful
        try:
            async with (get_session(services.Geckodriver(binary=self.geckodriver), browsers.Firefox()) as self.session):
                await self.session.get('http://cappa.csu.ru/')
                await self.click_element('.profile__bar-login')
                await self.click_element('.signup__link')
                await self.fill_elements('.form-control', data_)
                await self.click_element('.btn')
                try:
                    await self.find_element('.btn')
                    raise InputError(f"Driver.open_browser_for_cr: Error: input data is wrong")
                except NoSuchElementException:
                    pass
        except Exception as e_:
            raise RegistrationError(e_)
