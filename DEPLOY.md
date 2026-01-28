# Deploying Groundwater Monitoring App
This guide explains how to deploy your Django application to **Render**, a popular cloud platform with a free tier.

## 1. Prerequisites
- Create a [GitHub account](https://github.com) if you don't have one.
- Create a [Render account](https://render.com).
- Install Git on your computer if not already installed.

## 2. Prepare your project
1. Initialize a git repository (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit for deployment"
   ```
2. Push your code to a new GitHub repository:
   - Go to GitHub -> New Repository -> Name it `groundwater-monitor` -> Create.
   - Follow the instructions to push your existing code:
     ```bash
     git remote add origin https://github.com/YOUR_USERNAME/groundwater-monitor.git
     git branch -M main
     git push -u origin main
     ```

## 3. Deploy to Render
1. **New Web Service**:
   - Go to your Render Dashboard.
   - Click **"New +"** and select **"Web Service"**.
   - Connect your GitHub account and select the `groundwater-monitor` repository.

2. **Configure Service**:
   - **Name**: `groundwater-monitor` (or any unique name)
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh` (This installs dependencies, migrates DB, and seeds data)
   - **Start Command**: `gunicorn groundwater.wsgi:application`
   - **Instance Type**: `Free`

3. **Environment Variables**:
   - Click "Advanced" -> "Add Environment Variable"
   - Key: `PYTHON_VERSION` | Value: `3.11.0` (or your local version)
   - Key: `SECRET_KEY` | Value: (Generate a random string)
   - Key: `DEBUG` | Value: `False`
   - Key: `ALLOWED_HOSTS` | Value: `*` (or your render app URL, e.g., `groundwater.onrender.com`)

4. **Deploy**:
   - Click **"Create Web Service"**.
   - Render will start building your app. Watch the logs.
   - Once the build finishes, you will see a green "Live" badge.

## 4. Production Database (Recommended)
By default, this setup uses SQLite. On Render's free tier, **SQLite data resets every time you redeploy or the server restarts** (ephemeral storage).

To keep your data persistent:
1. Go to Render Dashboard -> **"New +"** -> **"PostgreSQL"**.
2. Create a free database.
3. Once created, copy the **Internal Database URL**.
4. Go back to your Web Service -> **Environment**.
5. Add a new variable:
   - Key: `DATABASE_URL`
   - Value: (Paste the Internal Database URL)
6. Redeploy. Your app will now use PostgreSQL and your data will be safe!

---

## Alternative: PythonAnywhere
If you prefer to stick with SQLite and want persistent storage without setting up PostgreSQL:
1. Sign up for [PythonAnywhere](https://www.pythonanywhere.com/).
2. Upload your code or pull from GitHub.
3. Configure the WSGI file as per their Django guide.
4. Run `python manage.py migrate` in their console.
5. Your SQLite database will be persistent there by default.

## 5. Troubleshooting: "Storage Limit Exceeded"
If you see errors about storage limits (e.g., on GitHub or Render):

1.  **Reduce Project Size**: We removed `pandas` and `numpy` (heavy libraries) from `requirements.txt`. Ensure you use the updated file.
2.  **Clean Git History**: If you accidentally committed a large file (like a database backup or `venv` folder) in the past, it stays in the history even if you delete it.
    *   **Solution**: Re-initialize git to clear old history (Warning: this resets commit history)
        ```bash
        rm -rf .git  # or Delete the hidden .git folder manually
        git init
        git add .
        git commit -m "Fresh start with small footprint"
        # Force push to your repo
        git push --force origin main
        ```

## 6. GitHub Limit
GitHub blocks single files larger than **100 MB**. 
- Our optimization ensures no source file hits this limit.
- If you still see this error, you likely have a large hidden file OR `git` is tracking an old large file in history. Follow "Clean Git History" above.

