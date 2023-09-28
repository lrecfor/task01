import asyncio
import sys
from arsenic import get_session, keys, browsers, services


class NoSuchElementException(Exception):
    pass


class RegistrationError(Exception):
    pass


class SigninError(Exception):
    pass


class InputError(Exception):
    pass


# async def ret_error(error_text):
#     if error_text == "Пользователь с таким логином уже существует":
#         raise InputError(f"Driver.open_browser_for_cr: Error: Account already exists. Please, use another login or "
#                          f"sign in.")
#     elif error_text == "Пользователь с такой почтой уже существует":
#         raise InputError(f"Driver.open_browser_for_cr: Error: Account with e-mail already exists. Please, use another "
#                          f"e-mail or sign in.")
#     elif error_text == "Введите правильный адрес электронной почты":
#         raise InputError(f"Driver.open_browser_for_cr: Error: Incorrect e-mail")
#     elif error_text == "Пароль должен быть больше 5 символов":
#         raise InputError(f"Driver.open_browser_for_cr: Error: Password should be more than 5 characters")


class Driver:
    def __init__(self):
        if sys.platform.startswith('win'):
            self.geckodriver = './geckodriver.exe'
        else:
            self.geckodriver = './geckodriver'

        self.session = None

    async def click_element(self, selector):
        try:
            element = await self.session.get_element(selector)
            await element.click()
        except Exception:
            raise NoSuchElementException(f"Driver.click_element: Error: Unable to locate element '{selector}'")

    async def find_element(self, selector):
        try:
            await self.session.get_element(selector)
        except Exception:
            raise NoSuchElementException(f"Driver.fill_element: Error: Unable to locate element '{selector}'")

    async def fill_element(self, selector, data_):
        field = await self.session.get_element(selector)
        await field.send_keys(data_)

    async def fill_elements(self, class_name, data_):
        input_fields = await self.session.get_elements(class_name)
        if len(input_fields) == 0:
            raise NoSuchElementException(f"Driver.fill_elements: Error: Unable to locate element '{class_name}'")
        for input_field in input_fields:
            field_value = data_.get(await input_field.get_attribute('name'))
            await input_field.send_keys(field_value)

    async def open_browser_for_sign_in(self):
        async with (get_session(services.Geckodriver(binary=self.geckodriver), browsers.Firefox()) as self.session):
            await self.session.get('http://cappa.csu.ru/')
            await self.click_element('.profile__bar-login')

    async def open_browser_for_cr(self, data_):
        async with (get_session(services.Geckodriver(binary=self.geckodriver), browsers.Firefox()) as self.session):
            await self.session.get('http://cappa.csu.ru/')
            await self.click_element('.profile__bar-login')
            await self.click_element('.profile__bar-login')
            await self.click_element('.signup__link')

            try:
                await self.fill_elements('.form-control', data_)
                await self.click_element('.btn')
            except NoSuchElementException as e:
                raise RegistrationError(e)

            try:
                await self.find_element('.btn')
            except NoSuchElementException as e:
                print(e)
                raise RegistrationError(e)
        print("Done")

# async def open_webpage():
#     if sys.platform.startswith('win'):
#         GECKODRIVER = './geckodriver.exe'
#     else:
#         GECKODRIVER = './geckodriver'
#
#     service = services.Geckodriver(binary=GECKODRIVER)
#     browser = browsers.Firefox()
#
#     async with (get_session(service, browser) as session):
#         await session.get('http://cappa.csu.ru/')
#
#         sign_in_button = await session.get_element('.profile__bar-login')
#         await sign_in_button.click()

data = {
    'username': 'test_user5',
    'email': 'XXXXXXXX5@gmail.com',
    'password1': 'test_password',
    'password2': 'test_password',
    'first_name': 'test_first_name',
    'last_name': 'test_last_name',
}
driver = Driver()
try:
    asyncio.run(driver.open_browser_for_cr(data))
except RegistrationError as e:
    print(e)
