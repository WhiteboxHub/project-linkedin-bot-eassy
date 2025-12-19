# GitHub Repository Setup Guide

## 📋 Prerequisites
- GitHub account created
- Git installed on your computer (already done ✓)
- Your project is ready (already done ✓)

---

## 🚀 Step-by-Step Guide to Push Your Project to GitHub

### Step 1: Create a New Repository on GitHub

1. Go to [GitHub.com](https://github.com) and log in
2. Click the **"+"** icon in the top-right corner
3. Select **"New repository"**
4. Fill in the details:
   - **Repository name**: `linkedin-job-bot` (or your preferred name)
   - **Description**: "AI-powered LinkedIn job application automation bot with YAML configuration"
   - **Visibility**: Choose **Public** or **Private**
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click **"Create repository"**
6. **Copy the repository URL** (e.g., `https://github.com/YOUR-USERNAME/linkedin-job-bot.git`)

---

### Step 2: Prepare Your Local Repository

Open PowerShell/Terminal in your project directory and run these commands:

```powershell
# Navigate to your project (if not already there)
cd "c:\Users\KUMAR-MINI-PC-7\Downloads\linkeein bot\linkeein bot test1\linkeein bot test1\linkeein bot test1\Auto_job_applier_linkedIn"

# Check current status
git status

# Add all files to staging (respects .gitignore)
git add .

# Commit your changes
git commit -m "Initial commit: LinkedIn AI Job Bot with YAML configuration"
```

---

### Step 3: Connect to Your GitHub Repository

Replace `YOUR-USERNAME` and `YOUR-REPO-NAME` with your actual GitHub username and repository name:

```powershell
# Add your GitHub repository as remote origin
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git

# Or if you already have a remote, update it:
git remote set-url origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git

# Verify the remote URL
git remote -v
```

---

### Step 4: Push to GitHub

```powershell
# Push your code to GitHub (first time)
git push -u origin sunil_dev

# Or if you want to push to main branch:
git branch -M main
git push -u origin main
```

**Note**: You may be prompted to enter your GitHub credentials. If you have 2FA enabled, you'll need to use a **Personal Access Token** instead of your password.

---

### Step 5: Create a Personal Access Token (if needed)

If GitHub asks for authentication:

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click **"Generate new token (classic)"**
3. Give it a name: "LinkedIn Bot Repository"
4. Select scopes: Check **"repo"** (full control of private repositories)
5. Click **"Generate token"**
6. **Copy the token** (you won't see it again!)
7. Use this token as your password when pushing

---

### Step 6: Update README with Your Repository Links

After pushing, I'll help you update all the GitHub links in the README to point to your new repository.

Just provide me with:
- Your GitHub username
- Your repository name

And I'll automatically replace all the old links!

---

## 🔄 Future Updates

After the initial setup, to push new changes:

```powershell
# Add changes
git add .

# Commit with a message
git commit -m "Your commit message here"

# Push to GitHub
git push
```

---

## ⚠️ Important Notes

### Files That Will NOT Be Pushed (Protected by .gitignore):
✅ Your YAML configuration files (`config/candidates/*.yaml`)  
✅ API keys and secrets  
✅ Personal resumes and data  
✅ Log files  
✅ Virtual environment  

### Files That WILL Be Pushed:
✅ Source code (`.py` files)  
✅ README.md  
✅ requirements.txt  
✅ .gitignore  
✅ Project structure  

---

## 🎯 Next Steps

1. Create your GitHub repository
2. Copy the repository URL
3. Share it with me, and I'll:
   - Update all GitHub links in README
   - Remove the old Discord/GitHub discussion links
   - Update the repository references throughout the project

**Ready to proceed?** Share your GitHub repository URL when you've created it! 🚀
