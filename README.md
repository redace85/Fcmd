# Fcmd
Fcmd 是一个用于操作fcoin账户的交互式命令行工具

:cn: :cn: :cn: :cn: :cn: :cn: :cn: :cn: :cn: 

使用的是fcoin官方提供的接口，文档地址：https://developer.fcoin.com/zh.html

---

## 安装

本程序使用 Python3.7+
基于 cmd 包实现的交互式命令行，使用 aiohttp 包实现的异步api调用，虽然现在命令的实现还是用的同步的方式。  

根目录下有requirement文件  

```
pip3 install -r requirements.txt
```

成功安装完依赖后，切换到根目录，重命名config.py.example -> config.py  

```
mv config.py.example config.py
```

编辑配置文件，填入在fcoin网站上开通的 key,secret 字串。  
如果本机不能直接访问接口地址的话，可以设置一个代理服务器地址，目前只支持http的代理

```
# http proxy for scientific internet access
proxy = 'http://127.0.0.1:9012/'
```

## 使用

执行 fcmd.py 进入交互式命令行

```
fcmd.py
```

在命令行中输入`?`查看全部的命令  
输入`?命令名`查看命令的功能与示例  

命令都采用了极短的命名缩写方式，方便记忆  

| 首字母含义 | 命令描述 |
|:----------:|-------------|
| **`m`** market 市场行情 | mtk(ticker):最新ticker; mdp(depth):深度; mtr(trade):成交单 |
| **`o`** order 交易单 | ol(list):交易单列表; oc(create):创建买卖单; osc(submit-cancel):撤销交易单 |
| **`c`** otc 相关 | cb(balance):otc余额; ci(trans-in):转入; co(trans-out):转出|
| **`t`** trading 交易账户 | tb(balance):交易余额; t2w(trading to wallet):交易账户转钱包账户|
| **`w`** wallet 钱包账户 | wb(balance):钱包余额; w2t(wallet to trading):钱包账户转交易账户|

其他命令
- **`alat`**(alarm at): 盯盘功能，在指定的价格停止数据拉取并播放声音。（在当前目录下放置 alarm/alarm.mp3 文件，只支持MACOS）

PS:目前otc的部分整体的流程还没完全搞明白，杠杆部分不太懂所以没有接入

:bangbang: 注意事项
目前操作方式为阻塞同步，所以在输入命令后请等命名执行完成再进行输入。  
多次按回车键会使同一个命令执行多次  

## 贡献

任何人都可以随意使用此容器内的代码。  
或参考`aiofcoin.py`文件构建自己的程序。  

:heavy_dollar_sign: 或者捐赠一点金钱，让作者在买煎饼果子时可以多加个蛋，在买盒饭时可以多加个鸡腿。  

![hb](/img/hb.jpeg)
![zfb](/img/zfb.jpeg)
![wx](/img/wx.jpeg)

## License
`Fcmd` is licensed under the 3-Clause BSD license - see the LICENSE file for details.
