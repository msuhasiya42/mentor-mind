# 🚀 Deployment Guide for Mentor Mind AI Service on Vercel

## Files Created for Vercel Deployment

✅ **vercel.json** - Configuration for Vercel Python runtime  
✅ **api/index.py** - Vercel API handler that imports your FastAPI app  
✅ **requirements.txt** - Dependencies for Vercel (moved to root)  
✅ **.gitignore** - Excludes unnecessary files from deployment  
✅ **env.example** - Environment variables template  

## 🔧 Pre-Deployment Setup

### 1. Environment Variables
You'll need to set up your OpenRouter API key:

```bash
# Get your free API key from https://openrouter.ai/
OPENROUTER_API_KEY=your_key_here
```

### 2. Test Locally (Optional)
```bash
# Test the Vercel structure locally
cd /path/to/your/project
python api/index.py
```

## 🚀 Deploy to Vercel

### Method 1: Vercel Dashboard (Recommended)
1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "New Project"
3. Import your Git repository
4. Vercel will auto-detect the Python setup
5. Add environment variables:
   - `OPENROUTER_API_KEY`: Your OpenRouter API key
6. Click "Deploy"

### Method 2: Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from project root
vercel

# Set environment variables
vercel env add OPENROUTER_API_KEY
```

## 🧪 Testing Your Deployment

Once deployed, test these endpoints:

### Health Check
```
GET https://your-app.vercel.app/health
```
Should return:
```json
{
  "status": "healthy",
  "openrouter_api": "configured",
  "version": "2.0.0 (Expert AI Tutor)"
}
```

### Generate Learning Path
```
POST https://your-app.vercel.app/generate-learning-path
Content-Type: application/json

{
  "topic": "Python FastAPI"
}
```

### Root Endpoint
```
GET https://your-app.vercel.app/
```
Should return:
```json
{
  "message": "Welcome to Mentor Mind API - Now with Expert AI Tutor!"
}
```

## 🛠 Troubleshooting

### Common Issues:

1. **404 on routes**
   - Check that `vercel.json` points to correct file path
   - Ensure `api/index.py` exists

2. **Import errors**
   - Verify all dependencies are in root `requirements.txt`
   - Check that Python path is set correctly in `api/index.py`

3. **OpenRouter API errors**
   - Verify your API key is set in Vercel environment variables
   - Check if you're hitting rate limits (50 requests/day on free tier)

4. **Cold starts**
   - First request after inactivity may be slow (~10-15 seconds)
   - This is normal for Vercel serverless functions

### Logs and Debugging:
- View logs in Vercel Dashboard > Functions tab
- Monitor API usage at OpenRouter dashboard
- Use the `/health` endpoint to check configuration

## 📊 Performance Notes

- **Cold Start**: ~10-15 seconds for first request after inactivity
- **Warm Requests**: ~1-3 seconds
- **Rate Limits**: 50 requests/day on OpenRouter free tier
- **Timeout**: Vercel functions timeout after 10 seconds (Hobby plan)

## 🔄 Updating Your Deployment

Simply push changes to your Git repository - Vercel will automatically redeploy.

## 🔐 Security Best Practices

1. **Never commit API keys** - Use Vercel environment variables
2. **Set up CORS properly** - Already configured for common development ports
3. **Monitor usage** - Keep track of your OpenRouter API usage
4. **Rate limiting** - Consider implementing client-side rate limiting

---

Your Mentor Mind AI service is now ready for production! 🎉 