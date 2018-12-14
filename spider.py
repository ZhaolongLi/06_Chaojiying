# coding:utf-8

import time
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from chaojiying import Chaojiying

EMAIL = ''
PASSWORD = ''
# 超级鹰的用户名、密码、软件ID、验证码类型
CHAOJIYING_USERNAME = ''
CHAOJIYING_PASSWORD = ''
CHAOJIYING_SOFT_ID =
CHAOJIYING_KIND =


class CrakTouClick():
    def __init__(self):
        self.url = 'http://admin.touclick.com/login.html'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser,20)
        self.email = EMAIL
        self.password = PASSWORD
        self.chaojiying = Chaojiying(CHAOJIYING_USERNAME,CHAOJIYING_PASSWORD,CHAOJIYING_SOFT_ID)

    def open(self):
        """
        打开网页输入用户民密码
        :return:
        """
        self.browser.get(self.url)
        email = self.wait.until(EC.presence_of_element_located((By.ID,'email')))
        password = self.wait.until(EC.presence_of_element_located((By.ID,'password')))
        email.send_keys(self.email)
        password.send_keys(self.password)

    def get_touclick_button(self):
        """
        获取初始验证按钮
        :return:
        """
        button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'touclick-hod-wrap')))
        return button

    def get_touclick_element(self):
        """
        获取验证图片对象
        :return: 图片对象
        """
        element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME,'touclick-pub-content')))
        return element

    def get_position(self):
        """
        获取验证码位置
        :return: 验证码位置元祖
        """
        element = self.get_touclick_element()
        time.sleep(2)
        location = element.location
        size = element.size
        top,bottom,left,right = location['y'],location['y'] + size['height'],location['x'],location['x'] + size['width']
        return (top,bottom,left,right)

    def get_screenshot(self):
        """
        获取网页截图
        :return:
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_touclick_image(self,name='captcha.png'):
        """
        获取验证码图片
        :param name:
        :return: 图片对象
        """
        top,bottom,left,right = self.get_position()
        print('验证码位置',top,bottom,left,right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left,top,right,bottom))

    def get_points(self,captcha_result):
        """
        解析识别结果
        :param captcha_result:识别结果
        :return: 转化后的结果
        """
        groups = captcha_result.get('pic_str').split('|')
        locations = [[int(number) for number in group.split(',')] for group in groups]
        return locations

    def touch_click_words(self,locations):
        """
        点击验证图片
        :param locations:点击位置
        :return:
        """
        for location in locations:
            print(location)
            ActionChains(self.browser).move_to_element_with_offset(self.get_touclick_element(),location[0],
                                                                   location[1]).click().perform()
            time.sleep(1)

    def touch_click_verify(self):
        """
        点击验证码按钮
        :return:
        """
        button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'touclick-pub-submit')))
        button.click()

    def login(self):
        """
        登录
        :return:
        """
        submit = self.wait.until(EC.element_to_be_clickable((By.ID,'_submit')))
        submit.click()
        time.sleep(10)
        print('登录成功')


    def crack(self):
        """
        破解入口
        :return:
        """
        self.open()
        button = self.get_touclick_button()
        button.click()

        image = self.get_touclick_image()
        bytes_array = BytesIO()
        image.save(bytes_array,format='PNG')

        result = self.chaojiying.PostPic(bytes_array.getvalue(),CHAOJIYING_KIND)
        print(result)
        locations = self.get_points(result)
        self.touch_click_words(locations)
        self.touch_click_verify()

        success = self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME,'touclick-hod-note'),'验证成功'))
        print(success)

        if not success:
            self.crack()
        else:
            self.login()


if __name__ == '__main__':
        crack = CrackTouclick()
        crack.crack()
