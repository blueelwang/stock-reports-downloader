#!/usr/bin/env python3
"""
A股年报PDF下载脚本
从巨潮资讯网下载上市公司年报PDF
"""

import os
import re
import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Optional


class AnnualReportDownloader:
    """A股年报下载器"""
    
    def __init__(self, download_dir: str = "./annual_reports"):
        """
        初始化下载器
        
        Args:
            download_dir: 下载目录
        """
        self.base_url = "http://www.cninfo.com.cn"
        self.static_url = "http://static.cninfo.com.cn"
        self.download_dir = download_dir
        
        # 创建下载目录
        os.makedirs(download_dir, exist_ok=True)
        
        # 设置请求头，模拟浏览器访问
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'http://www.cninfo.com.cn/',
        }
        
        # 缓存 orgId，避免重复请求
        self._org_id_cache: Dict[str, str] = {}
    
    def get_org_id(self, stock_code: str) -> Optional[str]:
        """
        通过 topSearch API 获取股票的 orgId
        
        Args:
            stock_code: 股票代码（6位数字）
        
        Returns:
            orgId 字符串，失败返回 None
        """
        # 检查缓存
        if stock_code in self._org_id_cache:
            return self._org_id_cache[stock_code]
        
        search_url = f"{self.base_url}/new/information/topSearch/query"
        data = {
            'keyWord': stock_code,
            'maxNum': 10
        }
        
        try:
            response = requests.post(search_url, data=data, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            results = response.json()
            
            if not results or not isinstance(results, list):
                print(f"未找到股票 {stock_code} 的信息")
                return None
            
            # 遍历结果，找到精确匹配的股票代码
            for item in results:
                if item.get('code') == stock_code:
                    org_id = item.get('orgId')
                    if org_id:
                        # 缓存结果
                        self._org_id_cache[stock_code] = org_id
                        print(f"获取到股票 {stock_code} 的 orgId: {org_id}")
                        return org_id
            
            # 如果没有精确匹配，使用第一个结果
            if results:
                org_id = results[0].get('orgId')
                if org_id:
                    self._org_id_cache[stock_code] = org_id
                    print(f"获取到股票 {stock_code} 的 orgId: {org_id}")
                    return org_id
            
            print(f"未找到股票 {stock_code} 的 orgId")
            return None
            
        except requests.RequestException as e:
            print(f"获取 orgId 失败: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"解析 orgId 响应失败: {e}")
            return None
    
    def search_announcements(self, stock_code: str, 
                           start_date: str = "",
                           end_date: str = "") -> List[Dict]:
        """
        搜索公告（使用历史公告查询接口）
        
        Args:
            stock_code: 股票代码（6位数字，不含市场前缀）
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD
        
        Returns:
            公告列表
        """
        # 使用历史公告查询接口
        search_url = f"{self.base_url}/new/hisAnnouncement/query"
        
        # 判断市场
        if stock_code.startswith(('60', '68', '58', '51')):
            plate = 'sh'
            column = 'sse'
        else:
            plate = 'sz'
            column = 'szse'
        
        # 通过 API 获取 orgId
        org_id = self.get_org_id(stock_code)
        if org_id:
            stock_param = f"{stock_code},{org_id}"
        else:
            # 降级使用旧的拼接方式
            print(f"警告: 无法获取 orgId，使用默认拼接方式")
            if plate == 'sh':
                stock_param = f"{stock_code},gssh0{stock_code}"
            else:
                stock_param = f"{stock_code},gssz0{stock_code}"
        
        # 格式化日期范围
        se_date = ""
        if start_date and end_date:
            se_date = f"{start_date}~{end_date}"
        
        # 准备POST请求参数
        base_data = {
            'pageSize': '30',
            'column': column,
            'tabName': 'fulltext',
            'plate': plate,
            'stock': stock_param,
            'searchkey': '',
            'secid': '',
            'category': 'category_ndbg_szsh',  # 年度报告分类
            'trade': '',
            'seDate': se_date,
            'sortName': '',
            'sortType': '',
            'isHLtitle': 'true'
        }
        
        try:
            all_announcements = []
            
            # 查询2页数据
            for page_num in range(1, 3):
                print(f"正在查询公告（第{page_num}页）...")
                data = base_data.copy()
                data['pageNum'] = str(page_num)
                
                response = requests.post(search_url, data=data, headers=self.headers, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                
                if result.get('hasError', False):
                    print(f"查询出错: {result.get('message', '未知错误')}")
                    break
                
                announcements = result.get('announcements')
                
                if announcements is None or not isinstance(announcements, list):
                    if page_num == 1:
                        print(f"未找到公告数据，尝试其他方式...")
                        return self._search_via_fulltext(stock_code, start_date, end_date)
                    break
                
                if len(announcements) == 0:
                    break
                    
                all_announcements.extend(announcements)
                
                # 如果本页不足30条，说明没有更多数据了
                if len(announcements) < 30:
                    break
                
                time.sleep(0.5)  # 避免请求过快
            
            # 过滤，只保留年度报告正文
            annual_reports = []
            for ann in all_announcements:
                title = ann.get('announcementTitle', '')
                # 清理em标签
                clean_title = title.replace('<em>', '').replace('</em>', '')
                
                # 只保留年度报告，排除半年报、季报、决议公告、英文版等
                if '年度报告' in clean_title:
                    # 排除不需要的内容
                    exclude_keywords = ['半年', '摘要', '更正', '取消', '补充', 
                                       '董事会', '监事会', '审计', '意见', '回复',
                                       '英文', 'English', 'english']
                    if not any(kw in clean_title for kw in exclude_keywords):
                        annual_reports.append(ann)
            
            return annual_reports
            
        except requests.RequestException as e:
            print(f"请求失败: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            return []
        except Exception as e:
            print(f"发生未知错误: {e}")
            return []
    
    def _search_via_fulltext(self, stock_code: str, start_date: str, end_date: str) -> List[Dict]:
        """
        备用方案：通过全文搜索接口查询
        """
        search_url = f"{self.base_url}/new/fulltextSearch/full"
        
        params = {
            'searchkey': f"{stock_code} 年度报告",
            'sdate': start_date,
            'edate': end_date,
            'isfulltext': 'false',
            'sortName': 'pubdate',
            'sortType': 'desc',
            'pageNum': '1',
            'pageSize': '30'
        }
        
        try:
            response = requests.get(search_url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            announcements = result.get('announcements') or []
            
            # 过滤，只保留年度报告正文
            annual_reports = []
            for ann in announcements:
                title = ann.get('announcementTitle', '')
                clean_title = title.replace('<em>', '').replace('</em>', '')
                
                if '年度报告' in clean_title:
                    exclude_keywords = ['半年', '摘要', '更正', '取消', '补充', 
                                       '董事会', '监事会', '审计', '意见', '回复',
                                       '英文', 'English', 'english']
                    if not any(kw in clean_title for kw in exclude_keywords):
                        annual_reports.append(ann)
            
            return annual_reports
            
        except Exception as e:
            print(f"备用查询也失败: {e}")
            return []
    
    def download_pdf(self, announcement: Dict, stock_code: str) -> Optional[str]:
        """
        下载PDF文件
        
        Args:
            announcement: 公告信息
            stock_code: 股票代码
        
        Returns:
            保存的文件路径，失败返回None
        """
        adj_url = announcement.get('adjunctUrl', '')
        if not adj_url:
            print("未找到PDF下载链接")
            return None
        
        # 构造完整的下载URL - 使用static.cninfo.com.cn
        if adj_url.startswith('http'):
            download_url = adj_url
        else:
            download_url = f"{self.static_url}/{adj_url}"
        
        # 生成文件名
        announce_title = announcement.get('announcementTitle', 'annual_report')
        
        # 清理em标签
        clean_title = announce_title.replace('<em>', '').replace('</em>', '')
        
        # 提取年份信息，生成简洁文件名（如：2023年年度报告）
        year_match = re.search(r'(\d{4})年', clean_title)
        year_str = year_match.group(1) if year_match else ''
        
        # 简洁文件名格式：股票代码_年份年年度报告.pdf
        file_name = f"{stock_code}_{year_str}年年度报告.pdf"
        
        # 按股票代码分目录
        stock_dir = os.path.join(self.download_dir, stock_code)
        os.makedirs(stock_dir, exist_ok=True)
        
        file_path = os.path.join(stock_dir, file_name)
        
        # 如果文件已存在，跳过下载
        if os.path.exists(file_path):
            print(f"文件已存在: {file_path}")
            return file_path
        
        try:
            print(f"开始下载: {announce_title}")
            print(f"下载链接: {download_url}")
            
            response = requests.get(download_url, headers=self.headers, timeout=60, stream=True)
            response.raise_for_status()
            
            # 下载文件
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # 显示下载进度
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            print(f"\r下载进度: {progress:.1f}%", end='', flush=True)
            
            print(f"\n下载完成: {file_path}")
            return file_path
            
        except requests.RequestException as e:
            print(f"\n下载失败: {e}")
            # 删除不完整的文件
            if os.path.exists(file_path):
                os.remove(file_path)
            return None
    
    def _get_market_code(self, stock_code: str) -> str:
        """
        根据股票代码获取市场代码
        
        Args:
            stock_code: 股票代码
            
        Returns:
            带市场代码的完整代码（如：sz000001, sh600000）
        """
        if stock_code.startswith(('60', '68', '58', '51')):
            return f"sh{stock_code}"
        else:
            return f"sz{stock_code}"
    
    def download_annual_reports(self, stock_code: str, 
                               start_year: Optional[int] = None,
                               end_year: Optional[int] = None) -> List[str]:
        """
        下载指定股票的年报
        
        Args:
            stock_code: 股票代码（6位数字）
            start_year: 开始年份
            end_year: 结束年份
        
        Returns:
            下载成功的文件路径列表
        """
        # 设置默认年份范围
        if end_year is None:
            end_year = datetime.now().year - 1  # 默认到去年，因为今年的年报可能还未发布
        if start_year is None:
            start_year = end_year - 30  # 默认下载最近5年
        
        start_date = f"{start_year}-01-01"
        end_date = f"{end_year}-12-31"
        
        # 获取市场信息（用于显示）
        full_code = self._get_market_code(stock_code)
        
        print(f"\n{'='*60}")
        print(f"查询股票 {stock_code} ({full_code}) 的年报")
        print(f"时间范围: {start_year}年 - {end_year}年")
        print(f"{'='*60}\n")
        
        # 搜索年报公告（使用纯数字代码）
        announcements = self.search_announcements(stock_code, start_date, end_date)
        
        if not announcements:
            print("未找到年报公告")
            return []
        
        print(f"找到 {len(announcements)} 条公告\n")
        
        # 显示公告列表
        for idx, ann in enumerate(announcements, 1):
            print(f"{idx}. {ann.get('announcementTitle', 'N/A')} "
                  f"({ann.get('announcementTime', 'N/A')})")
        
        # 下载PDF
        downloaded_files = []
        print(f"\n开始下载PDF文件...\n")
        
        for ann in announcements:
            file_path = self.download_pdf(ann, stock_code)
            if file_path:
                downloaded_files.append(file_path)
            
            # 避免请求过快，休眠一下
            time.sleep(1)
        
        print(f"\n{'='*60}")
        print(f"下载完成! 共下载 {len(downloaded_files)} 个文件")
        print(f"保存目录: {os.path.abspath(self.download_dir)}")
        print(f"{'='*60}\n")
        
        return downloaded_files


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='下载A股上市公司年报PDF',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 下载平安银行(000001)最近5年的年报
  python download_annual_report.py 000001
  
  # 下载中国平安(601318)2020-2023年的年报
  python download_annual_report.py 601318 --start-year 2020 --end-year 2023
  
  # 指定下载目录
  python download_annual_report.py 600000 --output ./reports
        """
    )
    
    parser.add_argument('stock_code', help='股票代码（6位数字）')
    parser.add_argument('--start-year', type=int, help='开始年份')
    parser.add_argument('--end-year', type=int, help='结束年份')
    parser.add_argument('--output', '-o', default='./annual_reports', 
                       help='下载目录（默认: ./annual_reports）')
    
    args = parser.parse_args()
    
    # 验证股票代码格式
    if not args.stock_code.isdigit() or len(args.stock_code) != 6:
        print("错误: 股票代码必须是6位数字")
        return
    
    # 创建下载器并下载
    downloader = AnnualReportDownloader(download_dir=args.output)
    downloader.download_annual_reports(
        stock_code=args.stock_code,
        start_year=args.start_year,
        end_year=args.end_year
    )


if __name__ == "__main__":
    main()

