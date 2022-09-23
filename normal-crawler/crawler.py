import os
import random
import re
import time
import json
import datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException, JavascriptException
from selenium.webdriver.chrome.options import Options


class Crawler:
    """
    normal crawler
    """

    def __init__(self):
        """

        """
        # int,为0时爬取整本书的全部内容，为1时从上次中断爬取的地方继续爬取
        self.update = 0
        self.browser = None
        # 默认启动chrome的路径及启动参数
        self.defaultbrowser = '"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 ' \
                              '--user-data-dir="F:\selenium\ChromeProfile" '
        # 为0时采取有界面浏览器爬取，为1时采取无界面爬取，待完善
        self.mode = 0
        # int,非0时在标题前加上标题数，否则按实际爬取标题写入
        self.writingmode = 0
        # 随机等待时间，为interesting类型的list，默认1至8s
        self.perwaitingtime = [1, 8]
        # 获取某个element的最长等待时间，int
        self.timeout = 20
        self.nextbutton = ""
        self.chap_number = 1
        self.amount = 0
        self.totalcrawingtime = 0

        self.novelabstracturl = ""
        self.firstchapterurl = ""
        self.endingurl = ""
        # 书籍内容详情
        self.bookname = ""
        self.bookabstract = ""
        self.title = ""
        self.content = ""

        # 通过Xpath定位书籍的各种内容
        self.bookname_xpath = ""
        self.title_xpath = ""
        self.content_xpath = ""
        self.book_abstract_xpath = ""
        self.nextchapter_button_xpath = ""
        # 内容正则化处理相关
        self.title_reg_zip_replacedstr = []
        self.content_reg_zip_replacedstr = []

    def set_cookie(self):
        """待完善，用于无界面爬取时设置cookie"""
        pass

    def set_default_browser(self, options: dict = None):
        if options is None:
            options = {}
        self.mode = options.get("mode")
        self.writingmode = options.get("writingmode")
        self.perwaitingtime = options.get("perwaitingtime") if options.get("perwaitingtime") else self.perwaitingtime
        self.timeout = options.get("timeout")
        if options.get("defaultbrowser") != "":
            self.defaultbrowser = options.get("defaultbrowser")

    def openbrowser(self):
        chrome_option = Options()
        # 接管本地端口为9222的chrome
        chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        # 打开chrome，端口为9222，chrome数据保存路径为F:\selenium\ChromeProfile
        os.popen(self.defaultbrowser)
        self.browser = webdriver.Chrome(options=chrome_option)
        self.browser.implicitly_wait(self.timeout)
        try:
            self.browser.maximize_window()
        except WebDriverException:
            print("窗口已最大")

    def shutdown_browser(self):
        """关闭浏览器"""
        self.browser.quit()
        # 请勿用(\d+?)

        repattern = re.compile(r"--remote-debugging-port[\S\s]*?(\d+)")
        port = repattern.search(self.defaultbrowser).group(1)

        f = os.popen("netstat -ano|findstr \"%s\"" % port)
        j = f.readlines()
        for i in j:
            # print(i.split())
            if i.split()[4] == "0":
                continue
            os.system(r"taskkill /f /pid %s" % i.split()[4])

    def set_chapter_url(self, firsturl: str, abstracturl):
        self.firstchapterurl = firsturl
        self.novelabstracturl = abstracturl

    def set_content_replace_regexp(self, replaceregexp: list = None, replacedstr: list = None):
        """
        设置内容正则化处理，replaceregexp列表中每一个元素下标需与replacedstr列表中每一个元素下标对应，这样就可以对应一个正则替换

        Args:
            replaceregexp: 待匹配的正则表达式列表
            replacedstr: 用于替换符合正则表达式的字符串列表
        Returns:
            None

        """
        if (replaceregexp is not None) and (replacedstr is not None):
            # zip()是迭代器iterator，只能读一次，读完就没了
            self.content_reg_zip_replacedstr = list(zip(replaceregexp, replacedstr))

    def set_title_replace_regexp(self, replaceregexp: list = None, replacedstr: list = None):
        """
        设置标题正则化处理，replaceregexp列表中每一个元素下标需与replacedstr列表中每一个元素下标对应，这样就可以对应一个正则替换
        Args:
            replaceregexp: 待匹配的正则表达式列表
            replacedstr: 用于替换符合正则表达式的字符串列表
        Returns:
            None

        """
        if (replaceregexp is not None) and (replacedstr is not None):
            # zip()是迭代器iterator，只能读一次，读完就没了
            self.title_reg_zip_replacedstr = list(zip(replaceregexp, replacedstr))

    def set_title_xpath(self, titlexpath: str):
        self.title_xpath = titlexpath

    def set_book_name_xpath(self, booknamexpath: str):
        self.bookname_xpath = booknamexpath

    def set_content_xpath(self, contentxpath: str):
        self.content_xpath = contentxpath

    def set_book_abstract_xpath(self, bookabstractxapth: str):
        self.book_abstract_xpath = bookabstractxapth

    def set_next_chapter_button_xpath(self, nextchapterbuttonxpath: str):
        self.nextchapter_button_xpath = nextchapterbuttonxpath

    def claw_book_abstract(self):
        """前往小说简介页面并爬取小说标题和简介"""
        self.browser.get(self.novelabstracturl)
        time.sleep(random.randint(self.perwaitingtime[0], self.perwaitingtime[1]))

        try:
            self.bookname = self.browser.find_element_by_xpath(self.bookname_xpath).text

        except NoSuchElementException:
            print("no such bookname element")
            self.bookname = str(datetime.datetime.now().date())

        try:
            self.bookabstract = self.browser.find_element_by_xpath(self.book_abstract_xpath).text
        except NoSuchElementException:
            print("no such bookabstract element")

    def claw_title(self):
        """
        爬取小说标题并进行正则化处理
        """
        try:
            self.title = self.browser.find_element_by_xpath(self.title_xpath).text
        except NoSuchElementException:
            print("no such title element")
            self.title = ""

        if self.title_reg_zip_replacedstr:
            for reg, replacedstr in self.title_reg_zip_replacedstr:
                self.title = re.sub(re.compile(reg), replacedstr, self.title)

    def claw_content(self):
        """
        爬取小说内容并进行正则化处理
        """
        try:
            self.content = self.browser.find_element_by_xpath(self.content_xpath).text
        except NoSuchElementException:
            print("no such content element")
            self.content = ""

        if self.content_reg_zip_replacedstr:
            for reg, replacedstr in self.content_reg_zip_replacedstr:
                self.content = re.sub(re.compile(reg), replacedstr, self.content)

    def claw_content_from_pre(self):
        """从上次停止爬取的地方继续爬取"""

        self.claw_book_abstract()

        with open("./book/" + self.bookname + ".txt", encoding="utf-8") as f:
            bookcontent = f.read()
            repattern1 = re.compile(
                r"([\S\s]*?)<<endingtitlenum:(\d+?)><endingurl-->(http[\s\S]*?)>>")
            self.content = repattern1.search(bookcontent).group(1)
            self.chap_number = int(repattern1.search(bookcontent).group(2))
            self.firstchapterurl = repattern1.search(bookcontent).group(3)

        self.bookname = self.bookname + str(datetime.datetime.now().date())
        with open("./book/" + self.bookname + ".txt", mode="w", encoding="utf-8") as f:
            f.write(self.content)
        self.go_first_charter()
        try:
            self.nextbutton = self.browser.find_element_by_xpath(self.nextchapter_button_xpath)
        except NoSuchElementException:
            print("next button no found")
            self.nextbutton = None

        while self.nextbutton is not None:
            self.find_next_button()
            self.claw_title()
            self.claw_content()
            self.write_chapter()
            self.go_next_chapter()

    def claw_total_content_restart(self):
        """重新爬取全书的内容"""

        self.claw_book_abstract()
        self.write_book_abstract()
        self.go_first_charter()

        while self.nextbutton is not None:
            self.find_next_button()
            self.claw_title()
            self.claw_content()
            self.write_chapter()
            self.go_next_chapter()

    def write_book_abstract(self):
        with open("./book/" + self.bookname + ".txt", encoding="UTF-8", mode="w") as f:
            if self.bookabstract == "":
                f.write("简介：无 \n")
            else:
                f.write("简介：\n" + self.bookabstract + "\n")
                f.write("---------------------------\n")

    def write_chapter(self):
        if self.browser.current_url != self.novelabstracturl:
            with open("./book/" + self.bookname + ".txt", encoding="UTF-8", mode="a") as f:
                self.title = self.title if self.writingmode == 0 else (str(self.chap_number) + "." + self.title)

                f.write(self.title + "\n")
                print("now writing chapter %s : %s \n" % (self.chap_number, self.title))
                f.write("本章字数：%s \n" % len(self.content))
                f.write(self.content + "\n")
                print(
                    "this chapter numbers about %s now writing content %s..." % (len(self.content), self.content[:20]))

                self.amount += len(self.content)
                self.chap_number += 1
                print("having claw amount : %s \n" % self.amount)

    def go_next_chapter(self):
        """点击下一章，然后随机等待一段时间"""
        waitingtime = random.randint(self.perwaitingtime[0], self.perwaitingtime[1])
        self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        # 不知为何，调用self.nextbutton.click()有可能会触发element click intercepted，
        # 可能是元素被遮罩导致无法点击，改为通过执行js代码前往下一页
        # self.nextbutton.click()
        try:
            self.browser.execute_script("arguments[0].click()", self.nextbutton)
        except JavascriptException:
            print("this button may be null or noclickable")
        print("waiting for %s s" % waitingtime)
        time.sleep(waitingtime)
        if self.browser.current_url == self.bookabstract:
            self.nextbutton = None

    def go_first_charter(self):
        self.browser.get(self.firstchapterurl)
        self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        waitingtime = random.randint(self.perwaitingtime[0], self.perwaitingtime[1])
        time.sleep(waitingtime)
        print("waiting for %s s" % waitingtime)

    def find_next_button(self):
        """定位下一章按钮,并记录结束页url"""
        if self.browser.current_url != self.novelabstracturl:
            self.endingurl = self.browser.current_url
        try:
            self.nextbutton = self.browser.find_element_by_xpath(self.nextchapter_button_xpath)
        except NoSuchElementException:
            print("next button no found")
            self.nextbutton = None

    def ending_process(self):
        if self.browser.current_url != self.novelabstracturl:
            self.endingurl = self.browser.current_url
        with open("./book/" + self.bookname + ".txt", mode="a", encoding="UTF-8") as f:
            f.write("<<endingtitlenum:%s><endingurl-->%s>>" % (self.chap_number, self.endingurl))
        print("ending")
        self.shutdown_browser()

    def set_all_configuration(self):
        """
        设置好各种爬取规则
        """
        options = json.load(open("./options/options.json", encoding="utf-8"))
        self.update = options.get("update")

        self.set_default_browser(options.get("browser"))
        self.openbrowser()

        self.set_chapter_url(options.get("bookinfolocation").get("firstchapterurl"),
                             options.get("bookinfolocation").get("novelabstracturl"))
        self.set_book_name_xpath(options.get("bookinfolocation").get("booknameXpath"))
        self.set_book_abstract_xpath(options.get("bookinfolocation").get("bookabstractXpath"))
        self.set_title_xpath(options.get("bookinfolocation").get("titleXpath"))
        self.set_content_xpath(options.get("bookinfolocation").get("contentXpath"))
        self.set_next_chapter_button_xpath(options.get("bookinfolocation").get("nextchapterbuttonXpath"))

        self.set_title_replace_regexp(options.get("title_replace_regexp").get("replaceregexp"),
                                      options.get("title_replace_regexp").get("replacedstr"))
        self.set_content_replace_regexp(options.get("content_replace_regexp").get("replaceregexp"),
                                        options.get("content_replace_regexp").get("replacedstr"))

    def run(self):

        self.set_all_configuration()
        try:
            if self.update == 0:
                self.claw_total_content_restart()
            elif self.update == 1:
                self.claw_content_from_pre()
            else:
                print("please set the update 0 or 1")
                raise ValueError
            self.ending_process()
        except ValueError:
            print(" interrupt ending")


if __name__ == '__main__':
    crawler = Crawler()
    crawler.run()
