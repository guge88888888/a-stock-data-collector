markdown
# A股实时数据采集服务

基于AKShare的A股市场数据采集服务，自动获取实时股票数据、指数数据和资金流向数据。

## 功能特性

- 📊 **实时股票数据**: 获取A股实时行情数据
- 📈 **指数数据**: 主要股票指数实时数据
- 💰 **资金流向**: 主力资金流向分析
- 🔄 **自动采集**: 按设定间隔自动更新数据
- 🗄️ **数据存储**: 自动保存到Supabase数据库

## 技术栈

- **数据源**: AKShare (东方财富)
- **后端**: Python 3.11
- **数据库**: Supabase (PostgreSQL)
- **部署**: Railway

## 部署说明

本项目已配置为Railway自动部署，只需连接GitHub仓库即可。

### 环境变量

- `SUPABASE_URL`: Supabase项目URL
- `SUPABASE_SERVICE_ROLE_KEY`: Supabase服务密钥
- `COLLECT_INTERVAL`: 数据采集间隔（秒，默认60）

## 数据表结构

- `stocks`: 股票基础信息
- `realtime_quotes`: 实时行情数据
- `indices`: 指数数据
- `fund_flows`: 资金流向数据

## 监控

- 访问Railway项目查看部署状态
- 查看Logs确认数据采集正常运行
- 访问前端应用验证数据更新

## 作者

MiniMax Agent
