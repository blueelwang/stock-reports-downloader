# A股年报PDF下载工具

这个工具可以帮助你从巨潮资讯网（cninfo.com.cn）下载A股上市公司的年报PDF文件。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

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

## 参数说明

- `stock_code`: 股票代码（6位数字，必填）
  - 例如：`000001`（平安银行）、`601318`（中国平安）、`600000`（浦发银行）
- `--start-year`: 开始年份（可选，默认为当前年份-5）
- `--end-year`: 结束年份（可选，默认为当前年份）
- `--output` 或 `-o`: 下载目录（可选，默认为`./annual_reports`）

## 示例

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

## 常见股票代码

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

## 注意事项

1. 下载的PDF文件会保存在指定的目录中，文件名格式为：`{股票代码}_{公告时间}_{公告标题}.pdf`
2. 如果文件已存在，会自动跳过下载
3. 程序会在每次下载之间暂停1秒，避免请求过于频繁
4. 需要联网使用，数据来源于巨潮资讯网官方网站

## 数据来源

巨潮资讯网（www.cninfo.com.cn）是中国证监会指定的上市公司信息披露网站。

