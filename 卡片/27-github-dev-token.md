---
create-time: 2026-05-16
update-time: 2026-05-16
---



## Github 加入团队项目开发时身份验证



问题描述：

我加入了一个 Github 团队，需要拉取项目，但是 Github 要求我登陆身份验证，我输入了用户名，以及 Github 的登陆密码之后，还是提示失败。



你遇到的核心问题是：**GitHub 早已禁用了账号密码直接认证 Git 操作**，HTTPS 方式克隆/推送代码时，**密码栏必须填写「个人访问令牌（PAT）」**，而不是你的 GitHub 登录密码。

我一步步教你解决，超简单：

---

### 第一步：生成 GitHub 个人访问令牌（PAT）
1. 浏览器登录你的 GitHub 账号
2. 点击右上角头像 → **Settings（设置）**
3. 左侧菜单栏拉到最底 → **Developer settings（开发者设置）**
4. 左侧选择 **Personal access tokens（个人访问令牌）** → **Tokens (classic)**
5. 点击 **Generate new token** → **Generate new token (classic)**
6. 按提示填写：
   - **Note**：给令牌起个名字（比如 `git-clone`）
   - **Expiration**：过期时间（建议选 `No expiration` 永久有效）
   - **Select scopes**：**只勾选 `repo`**（仓库权限，必须）
7. 拉到最底点击 **Generate token**
8. **关键**：生成的令牌以 `ghp_` 开头，**只显示这一次，立刻复制保存**！

---

### 第二步：重新克隆仓库
回到你的终端，重新执行克隆命令：
```bash
git clone https://github.com/adachissss/ourdb.git
```
1. 提示 `Username`：输入你的 GitHub 用户名 `Kualk4410`
2. 提示 `Password`：**粘贴你刚才复制的 PAT 令牌**（粘贴时终端不会显示字符，直接回车即可）

✅ 就能成功克隆了！

---

### 第三步（可选）：永久保存凭证，不用每次输入
WSL/Linux 下执行这条命令，让 Git 记住你的令牌，后续操作不用重复输：
```bash
git config --global credential.helper store
```

---

### 总结
1. 错误原因：GitHub 不支持密码登录，必须用 **PAT 令牌**；
2. 操作核心：密码栏粘贴生成的 `ghp_` 开头令牌；
3. 优化：配置凭证存储，一劳永逸。