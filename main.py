"""
A股实时数据采集服务 - Railway部署版本
使用AKShare获取真实股票数据
"""
import os
import time
import json
from datetime import datetime
from typing import List, Dict, Any
import requests
# 尝试导入akshare，如果失败则给出提示
try:
import akshare as ak
AKSHARE_AVAILABLE = True
except ImportError:
print("警告: AKShare未安装，将使用模拟数据")
AKSHARE_AVAILABLE = False
# Supabase配置
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://hldkorxgqjmlmebxczvy.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
class StockDataCollector:
"""股票数据采集器"""
def __init__(self):
self.supabase_url = SUPABASE_URL
self.supabase_key = SUPABASE_KEY
self.headers = {
'Authorization': f'Bearer {self.supabase_key}',
'apikey': self.supabase_key,
'Content-Type': 'application/json'
}
def get_stock_list(self) -> List[Dict]:
"""从Supabase获取股票列表"""
try:
response = requests.get(
f'{self.supabase_url}/rest/v1/stocks?select=*',
headers=self.headers
)
if response.status_code == 200:
return response.json()
else:
print(f"获取股票列表失败: {response.status_code}")
return []
except Exception as e:
print(f"获取股票列表异常: {e}")
return []
def get_realtime_quotes_akshare(self, symbols: List[str]) -> List[Dict]:
"""使用AKShare获取实时行情"""
quotes = []
now = datetime.now().isoformat()
for symbol in symbols:
try:
# AKShare获取实时行情
# 东方财富实时行情接口
stock_code = symbol
if symbol.startswith('6'):
stock_code = f'sh{symbol}'
elif symbol.startswith('0') or symbol.startswith('3'):
stock_code = f'sz{symbol}'
# 获取实时行情
df = ak.stock_zh_a_spot_em()
stock_data = df[df['代码'] == symbol]
if not stock_data.empty:
row = stock_data.iloc[0]
quote = {
'symbol': symbol,
'ts': now,
'last': float(row['最新价']),
'open': float(row['今开']),
'high': float(row['最高']),
'low': float(row['最低']),
'prev_close': float(row['昨收']),
'vol': float(row['成交量']),
'amount': float(row['成交额']),
'change': float(row['涨跌额']),
'pct_chg': float(row['涨跌幅']),
'source': 'akshare'
}
quotes.append(quote)
print(f"✓ 获取 {symbol} 行情成功")
else:
print(f"✗ 未找到 {symbol} 数据")
except Exception as e:
print(f"✗ 获取 {symbol} 行情失败: {e}")
continue
return quotes
def get_indices_akshare(self) -> List[Dict]:
"""使用AKShare获取指数数据"""
indices = []
now = datetime.now().isoformat()
# 主要指数代码映射
index_map = {
'000001': '上证指数',
'399001': '深证成指',
'399006': '创业板指',
'000300': '沪深300',
'000016': '上证50',
'399005': '中小100'
}
try:
# 获取A股指数实时行情
df = ak.stock_zh_index_spot_em()
for code, name in index_map.items():
try:
# 查找对应指数
index_data = df[df['代码'] == code]
if not index_data.empty:
row = index_data.iloc[0]
index = {
'index_code': code,
'name': name,
'ts': now,
'close': float(row['最新价']),
'open': float(row['今开']),
'high': float(row['最高']),
'low': float(row['最低']),
'pct_chg': float(row['涨跌幅']),
'amount': float(row['成交额']) if '成交额' in row else 0,
'source': 'akshare'
}
indices.append(index)
print(f"✓ 获取 {name}({code}) 数据成功")
else:
print(f"✗ 未找到 {name}({code}) 数据")
except Exception as e:
print(f"✗ 获取 {name}({code}) 数据失败: {e}")
continue
except Exception as e:
print(f"获取指数数据异常: {e}")
return indices
def get_fund_flows_akshare(self, symbols: List[str]) -> List[Dict]:
"""使用AKShare获取资金流向数据"""
flows = []
now = datetime.now().isoformat()
for symbol in symbols:
try:
# 获取个股资金流向
df = ak.stock_individual_fund_flow_rank(indicator="今日")
stock_flow = df[df['代码'] == symbol]
if not stock_flow.empty:
row = stock_flow.iloc[0]
# 主力净流入
main_net = float(row.get('主力净流入-净额', 0))
main_inflow = max(main_net, 0)
main_outflow = abs(min(main_net, 0))
flow = {
'entity_id': symbol,
'entity_type': 'stock',
'ts': now,
'level': '主力',
'time_window': '1d',
'inflow': main_inflow,
'outflow': main_outflow,
'net_amount': main_net,
'net_pct': float(row.get('主力净流入-净占比', 0)),
'source': 'akshare'
}
flows.append(flow)
print(f"✓ 获取 {symbol} 资金流向成功")
else:
print(f"✗ 未找到 {symbol} 资金流向")
except Exception as e:
print(f"✗ 获取 {symbol} 资金流向失败: {e}")
continue
return flows
def save_to_supabase(self, table: str, data: List[Dict]) -> bool:
"""保存数据到Supabase"""
if not data:
print(f"⚠ {table} 没有数据需要保存")
return True
try:
response = requests.post(
f'{self.supabase_url}/rest/v1/{table}',
headers={**self.headers, 'Prefer': 'return=minimal'},
json=data
)
if response.status_code in [200, 201]:
print(f"✓ {table} 保存成功: {len(data)}条记录")
return True
else:
print(f"✗ {table} 保存失败: {response.status_code} - {response.text}")
return False
except Exception as e:
print(f"✗ {table} 保存异常: {e}")
return False
def collect_and_save(self):
"""采集并保存数据"""
print(f"\n{'='*60}")
print(f"开始数据采集: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*60}\n")
# 1. 获取股票列表
print("1. 获取股票列表...")
stocks = self.get_stock_list()
symbols = [s['symbol'] for s in stocks]
print(f"   共 {len(symbols)} 只股票: {', '.join(symbols)}\n")
if not symbols:
print("⚠ 股票列表为空，跳过采集")
return
# 2. 采集行情数据
print("2. 采集实时行情...")
if AKSHARE_AVAILABLE:
quotes = self.get_realtime_quotes_akshare(symbols)
self.save_to_supabase('realtime_quotes', quotes)
else:
print("   ⚠ AKShare不可用，跳过行情采集")
print()
# 3. 采集指数数据
print("3. 采集指数数据...")
if AKSHARE_AVAILABLE:
indices = self.get_indices_akshare()
self.save_to_supabase('indices', indices)
else:
print("   ⚠ AKShare不可用，跳过指数采集")
print()
# 4. 采集资金流向
print("4. 采集资金流向...")
if AKSHARE_AVAILABLE:
flows = self.get_fund_flows_akshare(symbols)
self.save_to_supabase('fund_flows', flows)
else:
print("   ⚠ AKShare不可用，跳过资金流向采集")
print()
print(f"{'='*60}")
print(f"数据采集完成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*60}\n")
def main():
"""主函数"""
collector = StockDataCollector()
# 检查环境变量
if not SUPABASE_KEY:
print("错误: 未设置 SUPABASE_SERVICE_ROLE_KEY 环境变量")
return
print("A股实时数据采集服务启动")
print(f"Supabase URL: {SUPABASE_URL}")
print(f"AKShare可用: {'是' if AKSHARE_AVAILABLE else '否'}")
print()
# 持续运行模式
interval = int(os.getenv('COLLECT_INTERVAL', '60'))  # 默认60秒
print(f"采集间隔: {interval}秒\n")
while True:
try:
collector.collect_and_save()
print(f"等待 {interval} 秒后进行下次采集...\n")
time.sleep(interval)
except KeyboardInterrupt:
print("\n收到退出信号，停止采集")
break
except Exception as e:
print(f"采集过程出错: {e}")
print(f"等待 {interval} 秒后重试...\n")
time.sleep(interval)
if __name__ == '__main__':
main()
