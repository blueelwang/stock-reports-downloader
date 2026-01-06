# 股票年报PDF下载工具

这个工具可以帮助你下载上市公司的年报PDF文件，支持：
- **A股**：从巨潮资讯网（cninfo.com.cn）下载
- **港股**：从港交所披露易网站（hkexnews.hk）下载

## 安装依赖

```bash
pip install -r requirements.txt
```

---

## A股年报下载

### 基本用法

下载指定股票最近5年的年报：

```bash
python download_annual_report.py 000001
```

### 指定年份范围

下载指定年份范围的年报：

```bash
python download_annual_report.py 601318 --start-year 2020 --end-year 2023
```

### 指定下载目录

```bash
python download_annual_report.py 600000 --output ./my_reports
```

### A股参数说明

- `stock_code`: 股票代码（6位数字，必填）
  - 例如：`000001`（平安银行）、`601318`（中国平安）、`600000`（浦发银行）
- `--start-year`: 开始年份（可选，默认为当前年份-5）
- `--end-year`: 结束年份（可选，默认为当前年份）
- `--output` 或 `-o`: 下载目录（可选，默认为`./annual_reports`）

### A股示例

```bash
# 下载平安银行(000001)最近5年的年报
python download_annual_report.py 000001

# 下载中国平安(601318) 2020-2023年的年报
python download_annual_report.py 601318 --start-year 2020 --end-year 2023

# 下载浦发银行(600000)的年报，保存到指定目录
python download_annual_report.py 600000 -o ./reports

# 下载贵州茅台(600519) 2022年的年报
python download_annual_report.py 600519 --start-year 2022 --end-year 2022
```

### 常见A股代码

- **银行股**：
  - 平安银行: 000001
  - 招商银行: 600036
  - 浦发银行: 600000
  - 中国银行: 601988

- **保险股**：
  - 中国平安: 601318
  - 中国人寿: 601628

- **白酒股**：
  - 贵州茅台: 600519
  - 五粮液: 000858

---

## 港股年报下载

### 基本用法

下载指定港股最近5年的年报：

```bash
python download_hk_annual_report.py 00700
```

### 指定年份范围

下载指定年份范围的年报：

```bash
python download_hk_annual_report.py 00005 --start-year 2020 --end-year 2023
```

### 指定下载目录

```bash
python download_hk_annual_report.py 00700 --output ./my_reports
```

### 港股参数说明

- `stock_code`: 股票代码（港股代码，必填）
  - 例如：`00700`（腾讯）、`09988`（阿里巴巴）、`00005`（汇丰控股）
  - 支持输入 `700`、`00700`、`HK00700` 等格式，会自动转换
- `--start-year`: 开始年份（可选，默认为当前年份-5）
- `--end-year`: 结束年份（可选，默认为当前年份）
- `--output` 或 `-o`: 下载目录（可选，默认为`./hk_annual_reports`）

### 港股示例

```bash
# 下载腾讯(00700)最近5年的年报
python download_hk_annual_report.py 00700

# 下载汇丰控股(00005) 2020-2023年的年报
python download_hk_annual_report.py 00005 --start-year 2020 --end-year 2023

# 下载阿里巴巴(09988)的年报，保存到指定目录
python download_hk_annual_report.py 09988 -o ./reports

# 下载比亚迪(01211) 2022年的年报
python download_hk_annual_report.py 01211 --start-year 2022 --end-year 2022
```

### 常见港股代码

- **科技股**：
  - 腾讯控股: 00700
  - 阿里巴巴: 09988
  - 美团: 03690
  - 小米集团: 01810
  - 京东集团: 09618
  - 网易: 09999

- **金融股**：
  - 汇丰控股: 00005
  - 招商银行: 03968
  - 中国平安: 02318
  - 友邦保险: 01299

- **电信/能源**：
  - 中国移动: 00941
  - 中国石油: 00857
  - 中国海油: 00883

- **汽车/制造**：
  - 比亚迪: 01211
  - 吉利汽车: 00175
  - 理想汽车: 02015

---

## 注意事项

1. 下载的PDF文件会保存在指定的目录中，按股票代码分子目录存放
2. 文件名格式为：`{股票代码}_{年份}年年度报告.pdf`
3. 如果文件已存在，会自动跳过下载
4. 程序会在每次下载之间暂停1秒，避免请求过于频繁
5. 需要联网使用

## 数据来源

- **A股**: 巨潮资讯网（www.cninfo.com.cn）是中国证监会指定的上市公司信息披露网站
- **港股**: 港交所披露易（www.hkexnews.hk）是香港联合交易所官方信息披露平台
