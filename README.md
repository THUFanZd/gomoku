# 运行方式

## 安装依赖库

``` bash
pip install -r requirements.txt
```

如不成功，请尝试分别安装 pygame 和 numpy
``` bash
pip install pygame numpy
```

## 运行条件

游戏双方需跟运行服务器代码`server.py`的机器在同一局域网内，同时知道服务器的IP地址。可以由游戏的某一方负责运行服务器。
连接校园网、部分手机热点等客户端隔离的网络时，无法运行游戏。建议在私人网络环境下运行，如宿舍独立wifi等。

## 运行步骤

1. 获取服务器IP地址
    1. 打开命令提示符（Windows）或终端（macOS/Linux）。
    2. 输入`ipconfig`（Windows）或`ifconfig`（macOS/Linux）。
    3. 查找`IPv4 地址`或`inet`地址，这就是服务器的IP地址。

2. 服务器端、客户端均将IP地址作为字符串赋值给`macro.py`的HOST变量

3. 服务器端运行`server.py`

``` bash
python server.py
```

4. 游戏双方运行`main.py`

``` bash
python main.py
```

# 文件树

└─Project
    aiagent.py
    button.py
    frontend.py
    macro.py
    main.py
    README.md
    requirements.txt
    server.py