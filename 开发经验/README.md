## 开发经验/



开发实践中积累的技术经验总目录——包括调试记录、配置技巧、工具使用、项目实战。



### 子目录结构预览与增长预判



| 子目录 | 当前 | 预估上限 | 结构策略 | 命名策略 |
|--------|------|----------|----------|----------|
| `Spring与Java/` | 13 | ~25 | 扁平，≥20 后按领域分（配置/调试/设计） | `NN-描述性标题.md` |
| `Git与版本控制/` | 5 | ~15 | 扁平，按主题平铺 | `NN-描述性标题.md` |
| `环境与工具/` | 5 | ~15 | 扁平 | `NN-描述性标题.md` |
| `项目实战/` | 3 | ~10 | 扁平，每个项目可独立成子目录 | 当前平铺，≥3 个项目时分子目录 |
| `JS逆向/` | 6 | ~15 | 扁平 + `Tuling/` 课程笔记子目录 | 中文描述性名称 |



### 文件关键词索引



#### Spring与Java/

| 文件 | 关键词 |
|------|--------|
| `02-exec(runnable)方法.md` | 校验链、exec模式、责任链、Runnable插入 |
| `07-Spring全家桶包版本冲突.md` | 版本冲突、SpringAI、依赖回滚、Maven |
| `08-Template解析.md` | 模板解析、Prompt调试、JSON转义、SpringAI |
| `12-单体应用的分段id管理.md` | ID生成、号段模式、数据库分段、biz_type |
| `15-字段既可以是属性也可以是标签.md` | 标签设计、字段演进、实体映射、List标签 |
| `17-缓存使用.md` | JWT缓存、Redis、角色权限、性能优化 |
| `19-record-配置注入.md` | Record类、ConfigurationProperties、类型安全配置 |
| `20-何时不提取为ConfigurationProperties.md` | 配置重构、决策框架、@Value迁移、属性分组 |
| `21-@ConfigurationProperties IDE警告排查记录.md` | IDE误报、ConfigurationPropertiesScan、根因分析 |
| `29-Tomcat访问不到资源.md` | WAR打包、Tomcat部署、pom.xml、maven-war-plugin |
| `30-JavaWeb访问不到资源.md` | WEB-INF、依赖打包、传统JavaWeb、Maven迁移 |
| `2026-04-27.md` | SpringMVC、multipart、@ModelAttribute、请求处理链 |
| `经验.md` | SpringAI、模板转义、IoC注入、流式响应、重试机制 |

#### Git与版本控制/

| 文件 | 关键词 |
|------|--------|
| `03-git-actions.md` | stash、分支切换、暂存工作区 |
| `04-git乱码.md` | 中文编码、core.quotepath、GitBash乱码 |
| `27-github-dev-token.md` | PAT令牌、GitHub认证、凭证持久化 |
| `28-github只下载指定文件夹.md` | sparse-checkout、部分克隆、目录筛选 |
| `01-Git-pr-fix.md` | PR修复、commit amend、force push、PR自动更新 |

#### 环境与工具/

| 文件 | 关键词 |
|------|--------|
| `05-PicGo Core 使用教程.md` | 图床配置、PicGo CLI、Gitee仓库、Typora联动 |
| `14-多端口响应冲突.md` | 端口占用、PyCharm、进程残留、连接拒绝 |
| `22-终端使用技巧.md` | 终端美化、NerdFonts、OhMyPosh、分屏快捷键 |
| `25-linux使用技巧.md` | WSL配置、文件互通、explorer.exe、终端分屏 |
| `26-linux环境中文编码解决.md` | 中文编码、locale设置、ls乱码、git乱码 |

#### 项目实战/

| 文件 | 关键词 |
|------|--------|
| `31-一次课堂临时接手的 Streamlit 问卷平台网络卡顿排查记录.md` | 线上排查、长连接、WebSocket、应急处理、局域网部署 |
| `Tetris.md` | 游戏开发、easyx图形库、碰撞检测、键盘输入、迭代重构 |
| `可变注入.md` | 策略模式、setter注入、运行时切换、Spring单例 |

#### JS逆向/

| 文件 | 关键词 |
|------|--------|
| `main.md` | 逆向基础、API分析、调试器使用、请求拦截 |
| `实战经验.md` | webpack提取、加密识别、XHR重放、hook技术、异步分析 |
| `Tuling/js逆向2518期.md` | 加密定位、调用栈追踪、JS调试 |
| `Tuling/核心编程2523期.md` | 高级函数、闭包、函数式编程 |
| `Tuling/爬虫基础2520期.md` | 爬虫基础、工具链、请求库 |
| `Tuling/新生须知.md` | 课程信息、学号、非技术 |
