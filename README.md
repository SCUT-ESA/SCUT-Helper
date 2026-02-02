# 鲤工助手

一个专为华南理工大学学生打造的导航软件，集成了常用的校园服务和功能入口，让校园生活更便捷。

## 📱 项目简介

鲤工助手是一款基于 uni-app 开发的跨平台应用，支持微信小程序、App 等多个平台。通过统一的入口，快速访问课程中心、教务系统、VPN、一卡通等常用校园服务。

## ✨ 功能特性

### 🎡 每日抽签
- 每日抽签功能，为校园生活增添趣味

### 📚 常用功能
- **课程中心** - 快速访问在线课程平台
- **资料** - 获取学习资料和资源
- **猹话会** - 校园社区交流
- **VPN** - 校园 VPN 访问
- **一卡通** - 一卡通服务查询
- **教务系统** - 教务管理功能
- **选课通** - 选课辅助工具
- **自主选课** - 自主选课入口
- **长江雨课** - 雨课堂学习平台
- **教务处** - 教务处信息查询

### 🔍 更多功能
- **公众号** - 校园公众号入口
- **校园地图** - 校园地图导航
- **查分** - 成绩查询
- **GPA** - GPA 计算和查询
- **教材订购** - 教材订购服务
- **知网资源** - 知网学术资源
- **万方资源** - 万方数据库资源

### 💬 反馈功能
- 一键反馈通道
- 联系方式
- 博客链接

## 🛠️ 技术栈

- **框架**: uni-app 3.x
- **前端框架**: Vue 3
- **构建工具**: Vite 5.2.8
- **样式预处理**: Sass
- **国际化**: vue-i18n 9.1.9

## 📁 项目结构

```
my-vue3-project/
├── src/                    # 源代码目录
│   ├── pages/              # 页面目录
│   │   ├── index/         # 首页
│   │   ├── feedback/      # 反馈页面
│   │   └── webview/       # WebView 页面
│   ├── components/         # 组件目录
│   │   └── TabBar.vue     # 底部导航栏组件
│   ├── custom-tab-bar/     # 自定义 TabBar
│   ├── static/            # 静态资源
│   ├── App.vue            # 应用入口
│   ├── main.js            # 主入口文件
│   ├── pages.json         # 页面配置
│   └── manifest.json      # 应用配置
├── dist/                  # 构建输出目录
├── unpackage/             # 打包资源目录
├── vite.config.js         # Vite 配置
└── package.json           # 项目依赖配置
```

## 🚀 快速开始

### 环境要求

- Node.js >= 14.x
- npm 或 yarn

### 安装依赖

```bash
npm install
```

### 开发运行

#### 微信小程序开发

```bash
npm run dev:mp-weixin
```

#### H5 开发

```bash
npm run dev:h5
```

#### App 开发

```bash
npm run dev:custom
```

### 构建打包

#### 微信小程序打包

```bash
npm run build:mp-weixin
```

#### H5 打包

```bash
npm run build:h5
```

#### App 打包

```bash
npm run build:custom
```

## 📦 支持的平台

- ✅ 微信小程序 (mp-weixin)
- ✅ H5
- ✅ App (Android/iOS)
- ✅ 支付宝小程序 (mp-alipay)
- ✅ 百度小程序 (mp-baidu)
- ✅ 字节跳动小程序 (mp-toutiao)
- ✅ QQ 小程序 (mp-qq)
- ✅ 快手小程序 (mp-kuaishou)
- ✅ 京东小程序 (mp-jd)
- ✅ 飞书小程序 (mp-lark)
- ✅ 小红书小程序 (mp-xhs)
- ✅ 快应用 (quickapp-webview)

## 🎨 功能说明

### 链接复制功能

应用中的大部分功能入口采用链接复制的方式，点击功能项后会将对应的链接复制到剪贴板，用户可以在浏览器或其他应用中打开。

### 小程序跳转

部分功能支持直接跳转到微信小程序，使用小程序协议链接实现。

### WebView 支持

应用内置 WebView 页面，可以加载外部网页内容。

## 📝 开发说明

### 添加新功能

1. 在 `src/pages/index/index.vue` 中的 `commonFunctions` 或 `moreFunctions` 数组中添加新项：

```javascript
{
  name: '功能名称',
  icon: '🎯',
  url: 'https://example.com',
  type: 'web' // 'web' | 'miniprogram' | 'none'
}
```

2. 根据需要修改样式和布局

### 自定义 TabBar

TabBar 组件位于 `src/components/TabBar.vue`，可以根据需要自定义样式和功能。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。

## 📮 联系方式

- 博客: [moon-explorer.top](https://moon-explorer.top)
- 反馈: 通过应用内反馈功能提交

## 🙏 致谢

感谢所有使用和支持鲤工助手的同学们！

---

**注意**: 本项目仅供学习和交流使用，请遵守相关平台的使用规范。
