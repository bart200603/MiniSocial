# MiniSocial (迷你社交平台)

MiniSocial是一个简单的社交平台，具有用户注册/登录、发布帖子、点赞评论、关注用户等功能。

## 功能特点

1. 用户注册和登录
2. 发布文字和图片帖子
3. 点赞和评论功能
4. 个人资料页面
5. 搜索并关注其他用户
6. 查看关注动态
7. 实时消息墙

## 技术栈

- 前端: HTML, CSS, JavaScript
- 后端: Python + Flask
- 数据存储: JSON文件 (实际项目中应使用数据库)
- UI设计: 黏土(Clay)风格

## 本地运行

1. 克隆仓库
2. 安装依赖: `pip install -r requirements.txt`
3. 运行应用: `python app.py`
4. 访问: `http://localhost:5000`

## 演示账号

- 用户名: demo
- 密码: 123456

## 部署到Vercel

本项目已配置为可直接部署到Vercel平台。

1. Fork本仓库到GitHub
2. 注册并登录[Vercel](https://vercel.com)
3. 在Vercel中点击"New Project"并选择导入你的GitHub仓库
4. 部署完成后即可通过Vercel提供的域名访问

## 注意事项

- 本项目仅用于学习和演示目的
- 在Vercel环境中，上传的文件和数据更改在函数执行结束后会丢失
- 实际生产环境应使用数据库和云存储服务

## 实时消息墙 (Message Wall)

这是一个简单的实时消息墙功能，允许用户发送消息并实时显示在页面上。

# MiniSocial - 简易社交平台

MiniSocial是一个简单的社交平台，具有用户注册/登录、发布帖子、点赞评论、关注用户等功能。

## 功能特点

- 用户注册和登录系统
- 个人资料管理
- 帖子发布（支持图片）
- 点赞和评论功能
- 用户关注系统
- 实时消息墙
- 搜索功能

## 技术栈

- 后端: Flask (Python)
- 前端: 原生HTML/CSS/JavaScript
- 数据存储: JSON文件
- UI设计: 黏土(Clay)风格

## 本地运行

1. 克隆仓库
2. 安装依赖: `pip install -r requirements.txt`
3. 运行应用: `python app.py`
4. 访问: `http://localhost:5000`

## 演示账号

- 用户名: demo
- 密码: 123456

## 部署到Vercel

本项目已配置为可直接部署到Vercel平台。

1. Fork本仓库
2. 在Vercel中导入项目
3. 部署完成后即可访问

## 注意事项

- 本项目仅用于学习和演示目的
- 在Vercel环境中，上传的文件和数据更改在函数执行结束后会丢失
- 实际生产环境应使用数据库和云存储服务

# MiniSocial (迷你社交平台)

这是一个简单的前后端项目，展示前后端交互的基本原理。用户可以注册账号，发布帖子，关注其他用户，并与他人互动。

## 项目特点

- 黏土风格UI设计
- 用户注册和登录系统
- 个人资料管理
- 帖子发布（支持文本和图片）
- 点赞和评论功能
- 用户关注系统
- 关注动态流
- 用户搜索功能
- 实时消息墙（原始功能保留）

## 项目结构
- `templates/` - HTML模板文件
  - `index.html` - 主页
  - `login.html` - 登录页面
  - `register.html` - 注册页面
  - `profile.html` - 个人资料页面
  - `edit_profile.html` - 编辑资料页面
  - `create_post.html` - 发布帖子页面
  - `feed.html` - 关注动态页面
  - `search_results.html` - 搜索结果页面
  - `message_wall.html` - 原始消息墙页面
- `static/` - 静态资源
  - `style.css` - CSS样式文件
  - `script.js` - 原始消息墙JavaScript逻辑
  - `uploads/` - 用户上传的图片存储目录
- `app.py` - 后端Flask应用
- `data.json` - 数据存储文件（模拟数据库）
- `requirements.txt` - Python依赖

## 数据模型

- 用户 (Users)
- 帖子 (Posts)
- 评论 (Comments)
- 点赞 (Likes)
- 关注关系 (Follows)

## 如何运行

### 1. 安装后端依赖
```
pip install -r requirements.txt
```

### 2. 启动后端服务
```
python app.py
```

### 3. 访问应用
打开浏览器访问 http://localhost:5000

## 初次使用

1. 注册新账号
2. 登录系统
3. 编辑个人资料
4. 发布帖子
5. 搜索并关注其他用户
6. 查看关注动态

# 实时消息墙 (Message Wall)

这是一个简单的前后端项目，展示前后端交互的基本原理。用户可以在页面上提交消息，消息会实时显示在公共消息墙上。

## 项目结构
- `index.html` - 前端页面
- `static/style.css` - 样式文件
- `static/script.js` - 前端JavaScript逻辑
- `app.py` - 后端Flask应用
- `requirements.txt` - Python依赖

## 如何运行

### 1. 安装后端依赖
```
pip install -r requirements.txt
```

### 2. 启动后端服务
```
python app.py
```

### 3. 访问应用
打开浏览器访问 http://localhost:5000 