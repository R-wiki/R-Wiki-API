# R-Wiki-API
银临Wiki的API部分 | API for Rachel Wiki

## 简介 | Intro
- 使用FastAPI开发（Python >= 3.10）
- 数据库使用MongoDB
- 前端部分请见：[R-Wiki](https://github.com/yc005/R-Wiki)

## 使用须知 | Reminder
- 首次启动（数据库不存在admin权限用户）时，会自动创建新的admin用户，初始密码请留意命令行输出
- 浏览文档请在启动项目后访问 http://\<r-wiki-api host\>/docs

## 使用Docker部署 | Deploy with Docker
```bash
git clone https://github.com/R-wiki/R-Wiki-API.git
cd R-Wiki-API
docker build -t r-wiki-api .
docker run -v <config_file_path>:/app/config.ini -p <port>:8000 r-wiki-api
```