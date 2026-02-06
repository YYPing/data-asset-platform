# 快速上传步骤 (立即执行)

## ⚠️ 重要安全提醒
**密码已泄露！上传后请立即修改密码！**

## 步骤1: 创建GitHub仓库

### 方法A: 使用curl创建 (快速)
```bash
# 在终端中执行以下命令
curl -u "915493744@qq.com:yyp110102101" \
  -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{"name":"data-asset-platform","description":"数据资产全流程管理平台","private":false}'
```

### 方法B: 手动创建 (网页)
1. 访问: https://github.com/new
2. 填写:
   - Repository name: `data-asset-platform`
   - Description: `数据资产全流程管理平台`
   - Public
   - 不要初始化README、.gitignore、license
3. 点击 "Create repository"

## 步骤2: 推送代码

### 如果使用方法A创建成功，执行:
```bash
cd /Users/guiping/.openclaw/workspace/data-asset-platform

# 添加远程仓库
git remote add origin https://github.com/915493744/data-asset-platform.git

# 推送代码
git push -u origin main
```

### 如果使用方法B创建，执行:
```bash
cd /Users/guiping/.openclaw/workspace/data-asset-platform

# 复制网页上显示的命令
# 通常类似:
git remote add origin https://github.com/915493744/data-asset-platform.git
git branch -M main
git push -u origin main
```

## 步骤3: 输入凭据

推送时会要求输入用户名和密码:
- **Username**: `915493744@qq.com`
- **Password**: `yyp110102101`

## 步骤4: 验证上传

访问: https://github.com/915493744/data-asset-platform
检查文件是否完整上传。

## ⚠️ 上传后立即执行

### 1. 立即修改GitHub密码
```bash
# 访问: https://github.com/settings/security
# 点击: "Change password"
```

### 2. 启用双重认证
```bash
# 访问: https://github.com/settings/security
# 点击: "Enable two-factor authentication"
```

### 3. 检查登录活动
```bash
# 访问: https://github.com/settings/security-log
# 检查异常登录
```

## 故障排除

### 问题1: 权限被拒绝
```bash
# 如果提示权限问题，尝试:
git remote set-url origin https://915493744@qq.com:yyp110102101@github.com/915493744/data-asset-platform.git
git push -u origin main
```

### 问题2: 仓库已存在
```bash
# 如果仓库已存在，直接推送
git push -u origin main
```

### 问题3: 需要拉取
```bash
# 如果提示需要先拉取
git pull origin main --allow-unrelated-histories
git push -u origin main
```

## 快速命令汇总

```bash
# 一次性执行 (在项目目录中)
cd /Users/guiping/.openclaw/workspace/data-asset-platform

# 创建仓库 (如果尚未创建)
curl -u "915493744@qq.com:yyp110102101" -X POST -H "Accept: application/vnd.github.v3+json" https://api.github.com/user/repos -d '{"name":"data-asset-platform","description":"数据资产全流程管理平台","private":false}'

# 添加远程仓库
git remote add origin https://github.com/915493744/data-asset-platform.git

# 推送代码
git push -u origin main

# 输入凭据:
# Username: 915493744@qq.com
# Password: yyp110102101
```

## 上传后检查

1. ✅ 访问 https://github.com/915493744/data-asset-platform
2. ✅ 检查文件数量 (应该约75个文件)
3. ✅ 检查README.md是否显示
4. ✅ 检查代码结构是否完整

## 紧急联系方式

如果上传过程中账号被锁定:
- GitHub支持: https://github.com/contact
- 安全报告: https://github.com/contact/report-abuse

---

**⚠️ 再次提醒: 上传后请立即修改密码！**