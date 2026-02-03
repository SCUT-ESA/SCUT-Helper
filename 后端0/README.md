# 鲤工助手 - SCUT Helper

华南理工大学嵌入式协会开发的校园智能助手，为师生提供一站式校园服务。

## 🌟 项目简介

**鲤工助手**是一个基于FastAPI + 小程序 +Vue.js的全栈校园智能助手，致力于解决华南理工大学师生的校园生活痛点，通过对话式交互提供便捷服务。



### 核心愿景
- 🤖 **智能对话**：自然语言处理，理解用户需求
- 🎓 **学业支持**：选课指导、成绩查询、学习资源
- 🍱 **生活服务**：云饭堂点餐、校园导航
- 📚 **资源共享**：二手书交易、学习资料共享
- 🔄 **持续扩展**：模块化设计，便于功能迭代

## 🎯 里程碑目标

- [ ] 用户注册登录
- [ ] 基础对话交互
- [ ] 课程查询功能
- [ ] 文件推荐功能
- [ ] 基础前端界面

- [ ] 搭建小程序

- [ ] 用户反馈系统

## 📁 项目结构

```
scut_helper/
├── backend/                    # FastAPI后端
│   ├── app/
│   │   ├── api/              # API路由
│   │   ├── core/             # 核心配置
│   │   ├── models/           # 数据模型
│   │   ├── schemas/          # Pydantic模型
│   │   ├── crud/             # 数据库操作
│   │   ├── services/         # 业务逻辑
│   │   └── main.py           # 应用入口
│   ├── alembic/              # 数据库迁移
│   └── requirements.txt      # Python依赖
├── frontend/                  # Vue.js前端
│   ├── src/
│   │   ├── views/           # 页面组件
│   │   ├── components/      # 可复用组件
│   │   ├── api/             # API调用
│   │   └── store/           # 状态管理
│   └── package.json
└── README.md
```

## 🚀 快速开始

### 后端启动
```bash
# 1. 克隆项目
git clone https://github.com/scut-embedded/scut_helper.git
cd scut_helper

# 2. 创建并激活Conda环境
#用别的虚拟环境也可以
conda create -n scut_helper python=3.11 -y
conda activate scut_helper

# 3. 安装后端依赖
cd backend
pip install -r requirements.txt

cd app
# 4. 配置环境变量
#Linux/macOS 使用 cp 命令
copy .env.example .env
# 编辑.env文件设置数据库和密钥

# 5. 启动服务
uvicorn main:app --reload 
```

### 前端启动（后续开发）
```bash
cd frontend
npm install
npm run dev
```

## 🔧 技术栈

### 后端
- **框架**：FastAPI + Uvicorn
- **数据库**：SQLite（开发）→ PostgreSQL（生产）
- **ORM**：SQLAlchemy + Alembic迁移
- **认证**：JWT + OAuth2.0
- **缓存**：Redis
- **异步任务**：Celery + RabbitMQ
- **API文档**：自动生成Swagger/ReDoc

### 前端（规划）
- **框架**：Vue 3 + TypeScript
- **UI库**：Element Plus
- **状态管理**：Pinia
- **HTTP客户端**：Axios
- **构建工具**：Vite

### 智能模块
- **NLP**：Transformers（BERT）
- **对话**：LangChain + 大语言模型API
- **推荐**：协同过滤 + 内容推荐

## 👥 团队协作规范

### 分支策略
```
main            - 生产环境代码
develop         - 开发主分支
feature/*      - 新功能开发
bugfix/*       - 问题修复
release/*      - 发布准备
```

### 提交规范
```
feat:    新功能
fix:     修复bug
docs:    文档更新
style:   代码格式
refactor:重构
test:    测试相关
chore:   构建/工具
```

### 开发流程
1. 从develop创建特性分支
2. 开发完成后提交Pull Request
3. 代码评审 + CI测试通过
4. 合并到develop分支
5. 定期从develop合并到main发布

## 📞 联系我们

- **项目仓库**：[[tianma-afk/SCUT-Helper: 一个华工学生的日常智能助手。](https://github.com/tianma-afk/SCUT-Helper)](https://github.com/scut-embedded/scut_helper)
- **协会官网**：[https://embedded.scut.edu.cn](https://embedded.scut.edu.cn)
- **交流群**：QQ群 1026210091(软件方向)嵌入式协会交流群

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

**鲤工助手，让校园生活更智能！**

*华南理工大学嵌入式协会 荣誉出品*