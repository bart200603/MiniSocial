# 将MiniSocial部署到Vercel的步骤

## 前提条件

1. 一个GitHub账号
2. 一个Vercel账号 (可以使用GitHub账号直接登录)

## 部署步骤

### 1. 将代码推送到GitHub仓库

1. 在GitHub上创建一个新仓库
2. 将本地代码推送到该仓库:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/你的用户名/仓库名.git
   git push -u origin main
   ```

### 2. 在Vercel上部署

1. 访问 [Vercel](https://vercel.com) 并使用GitHub账号登录
2. 点击 "Add New..." 然后选择 "Project"
3. 从列表中找到并选择你的GitHub仓库
4. 配置项目:
   - 框架预设: 选择 "Other"
   - 构建命令: 留空
   - 输出目录: 留空
   - 环境变量: 可以添加 `SECRET_KEY` 环境变量以增强安全性
5. 点击 "Deploy" 按钮

### 3. 验证部署

1. 部署完成后，Vercel会提供一个域名 (形如 `https://your-project.vercel.app`)
2. 点击该链接访问你的应用
3. 测试各项功能是否正常

## 注意事项

- 在Vercel的无服务器环境中，文件系统是临时的，每次函数执行结束后上传的文件会丢失
- 数据文件(data.json)的更改也会在函数执行结束后丢失
- 这是Vercel无服务器环境的限制，实际生产环境应使用:
  - 数据库 (如MongoDB Atlas, Supabase, Firebase等) 存储用户和帖子数据
  - 云存储服务 (如AWS S3, Cloudinary等) 存储上传的图片

## 自定义域名 (可选)

1. 在Vercel项目设置中，点击 "Domains" 选项卡
2. 添加你拥有的域名
3. 按照Vercel提供的说明配置DNS记录
4. 配置完成后，你可以通过自定义域名访问你的应用 