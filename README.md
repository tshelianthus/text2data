# Text2Data

Text2Data 是一个基于自然语言处理的应用程序，允许用户通过自然语言查询数据库，并返回 SQL 查询结果。


## 特性

- 支持自然语言输入，自动生成 SQL 查询
- 显示查询结果，并支持下载和复制

## 安装

### 依赖项

确保安装以下依赖项：

- Python 3.9+
- `pip`

### 步骤

1. 克隆仓库：

    ```sh
    git clone 本项目地址
    cd text2data
    ```

2. 创建并激活虚拟环境：

    ```sh
    python3 -m venv .venv
    source .venv/bin/activate 
    ```

3. 安装依赖项：

    ```sh
    pip install -r requirements.txt
    ```

4. 配置项目（见下文的配置部分）

5. 运行应用程序：

    ```sh
    streamlit run app.py
    ```

## 使用

1. 启动应用程序后，打开浏览器并访问 `http://localhost:port`。
2. 输入数据提取需求。
3. 点击“Submit”按钮，查看查询结果。
4. 可以下载查询结果或将其复制到剪贴板。
5. 查看生成的SQL

## 配置

项目需要一些配置文件来指定数据库和 API 密钥。

### 配置文件 `config.yaml`

在项目configs目录下复制 `config.example.yaml`，并重命名为 `config.yaml` 文件。

