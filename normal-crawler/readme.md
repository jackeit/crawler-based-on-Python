#  readme

***

该通用小说爬虫可以根据小说的简介链接、标题、简介、内容、下一章链接等的XPath的路径表达式把选取的一个网站的一本小说爬取成.txt格式的文本，在爬取的过程中可以对爬取到的内容进行正则化处理（删除掉内容节点里多余的内容如广告、不相关的的节点内容，或者进行替换），方便进行离线小说阅读，基于selenium爬取。也可以爬取需要登陆的小说网站，不过需要先打开在某个端口（默认设置为9222端口），chrome数据保存路径为F：\selenium\ChromeProfile），即默认的chrome启动路径及参数为
："C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="F:\selenium\ChromeProfile"

只需要改变options文件夹下的配置文件options.json，就可以实现不同小说网站的小说爬取，目前每执行一次只能爬取一本指定的小说，因为爬取的量小，所以没有设置代理选项，而为了使本爬虫程序尽可能通用~~也为了尽可能方便~~，所以不采取selenium无界面爬取（可以通过登录有界面的chrome获取待爬取网站的cookie来进行登录小说网站的爬取，设置好cookie后再关闭有界面的chrome继而开启无界面爬取，但是如果不是接管已开启的有界面chrome进行爬取的话，如果网站有对应的反selenium爬虫手段，比如根据字段window.navigator.webdriver进行反爬，爬虫就会失效，而且直接接管有界面chrome进行爬取的话，可以解决短时间登录频繁导致被禁止登录或者会出现麻烦的验证码验证等问题）或者使用基本查询库如requests、urllib等等+解析库如lxml、BeautifulSoup4等等的组合来编写爬虫程序
***
selenium可实现所<font color=red>见即所爬</font>，也就是说<font color=red>不可见即不可爬</font>（至少不可见的节点内容虽然可以在开发者工具栏中见到且可以通过selenium定位到元素但获取内容为空，虽然可以通过lxml等解析库对浏览器page_source进行内容解析获取，但我没有这么做）,如果通过chrome开发者工具定位xpath，需要注意此时网页HTML中使用的样式及网页显示内容会不会随着开发者工具栏大小的变化而变化，驱动浏览器进行抓取的时候默认是没有打开开发者工具栏的，如果实在无法定位好元素可以采用fiddle抓包分析。
***
## 配置参数
下面是options.json配置文件的各种参数：
```json
"perwaitingtime": [1,3],(list[int],每爬取一次随机等待的时间，如果网络环境不好或者不想爬虫短时间爬太快导致爬虫被反掉，请设置长一点，默认是1~3s)
"writingmode": 1, (int,非0时在标题前加上标题数如"22."方便标题没有排好版时爬取的小说在手机上依旧可以有良好的排版，否则按实际爬取标题写入)
"mode": 0,(int,日后完善)
"timeout": 5,(获取某个element的最长等待时间，如果网络环境不好请设置长一点，int)

"defaultbrowser": "",(str,启动chrome的路径及启动参数,不填请保持为""，默认打开chrome路径为
C:\Program Files\Google\Chrome\Application\chrome.exe，端口为9222，chrome数据保存路径为F:\selenium\ChromeProfile)

"novelabstracturl": "",(str,小说简介页面链接)
"firstchapterurl": "",(str,小说第一章链接)
"booknameXpath":"",(str,小说书名Xpath定位表达式)
"titleXpath":"",(str,小说每一章标题Xpath定位表达式)
"contentXpath" : "",(str,小说每一章内容Xpath定位表达式)
"bookabstractXpath" : "",(str,小说简介Xpath定位表达式)
"nextchapterbuttonXpath" :"",(str,下一章小说点击按钮Xpath定位表达式)

"replacedstr":[],(list[str])
"replaceregexp": [],(list[str]))
设置内容正则化处理，replaceregexp列表中每一个元素下标需与replacedstr列表中每一个元素下标对应，
这样就可以对应一个正则替换,会对内容按顺序进行正则替换，直至完成所有正则替换，这两个list[str]元素个数必须一样。
title_replace_regexp中的replacedstr 和 replaceregexp对应标题的正则化处理
content_replace_regexp中的replacedstr 和 replaceregexp对应内容的正则化处理

"update": 0 ,(int 1 或 0，为0时爬取整本书的全部内容；为1时从上次中断爬取的地方继续爬取，即更新小说，
但是待更新小说必须在爬取目录的book文件夹下并且没有删除小说的最后一行以<<ending开头的内容)
```
可以使用命令行程序或者IDE如Pycharm等运行程序，如果运行出了什么问题，请使用管理员身份运行程序。需要在python中安装好对应的库文件如selenium，另外请下载对应的chromedriver并将其<font color=red>置于环境变量</font>中，<font color=red>chromedriver版本与chrome版本务必一致</font>，否则可能会出一些莫名其妙的错误。
chromedriver下载：[chromedriver下载](https://chromedriver.storage.googleapis.com/index.html)
***
## 测试样例
下面是所有测试网站中的某个小说网站中某本小说(章数只有12，拿来测试刚刚好)的测试爬虫的参数：
chromedriver version:105.0.5195.52
chrome version:105.0.5195.127
```json
{
  "browser": {
    "perwaitingtime": [1,3],
    "writingmode": 1,
    "mode": 0,
    "timeout": 5,
    "defaultbrowser": ""

  },
  "bookinfolocation": {
    "novelabstracturl": "http://www.huanxiangji.com/book/1055/",
    "firstchapterurl": "http://www.huanxiangji.com/book/1055/436942.html",
    "booknameXpath":"//div[@class='top']/h1",
    "titleXpath":"//h1[@class='title']",
    "contentXpath" : "//div[@class='reader-main']/div[@class='content']",
    "bookabstractXpath" : "//div[@class='info']/div[@class='desc xs-hidden']",
    "nextchapterbuttonXpath" :"//div[@class='section-opt']/a[contains(text(),'下一章')]"
  },
  "title_replace_regexp": {
    "replacedstr":["章节",""],
    "replaceregexp": ["分卷阅读","正文"]
  },
  "content_replace_regexp": {
    "replacedstr": [""],
    "replaceregexp": [""]
  },
  "update": 0
}
```
***
测试视频

[1.mp4](testingvideo/1.mp4)


爬取到的小说可以在book文件夹下看到
![](vx_images/412420211220960.png)


