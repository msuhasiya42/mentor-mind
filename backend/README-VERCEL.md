# Mentor Mind Backend - Vercel Deployment Guide

This guide explains how to deploy the Mentor Mind backend to Vercel.

## Prerequisites

1. Vercel account
2. GitHub/GitLab/Bitbucket repository with the Mentor Mind code
3. Required API keys (OpenAI, etc.)

## Deployment Steps

### 1. Fork and Clone the Repository

Fork the repository to your GitHub account and clone it locally:

```bash
git clone https://github.com/your-username/mentor-mind.git
cd mentor-mind
```

### 2. Set Up Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
# Add other required environment variables
```

### 3. Deploy to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New" → "Project"
3. Import your GitHub/GitLab/Bitbucket repository
4. In the project settings:
   - Set the root directory to the root of the repository
   - Set the framework preset to "Other"
   - Set the build command to leave it empty
   - Set the output directory to leave it empty
   - Set the install command to: `cd backend && pip install -r requirements-vercel.txt`

5. In the "Environment Variables" section, add all the variables from your `.env` file

6. Click "Deploy"

### 4. Configure Vercel Project Settings

After deployment, go to your project settings in Vercel and update the following:

1. Under "Build & Development Settings":
   - Set the root directory to the root of the repository
   - Set the build command to: `cd backend && pip install -r requirements-vercel.txt`
   - Set the output directory to: `backend`
   - Set the install command to: `cd backend && pip install -r requirements-vercel.txt`

2. Under "Environment Variables", ensure all required variables are set

### 5. Update Vercel.json

Ensure your `vercel.json` in the root directory looks like this:

```json
{
  "version": 2,
  "builds": [
    { 
      "src": "backend/main.py", 
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "15mb",
        "runtime": "python3.9"
      }
    }
  ],
  "routes": [
    { 
      "src": "/api/(.*)", 
      "dest": "/backend/main.py"
    },
    { 
      "src": "/(.*)", 
      "dest": "/backend/main.py"
    }
  ]
}
```

## Testing the Deployment

Once deployed, you can test the API using:

```bash
curl -X POST https://your-vercel-app.vercel.app/api/generate-learning-path \
  -H "Content-Type: application/json" \
  -d '{"topic": "machine learning"}'
```

## Troubleshooting

1. **Deployment Fails**
   - Check the build logs in the Vercel dashboard
   - Ensure all required environment variables are set
   - Verify the Python version (3.9 is recommended)

2. **API Returns 500 Errors**
   - Check the function logs in the Vercel dashboard
   - Verify that all API keys are correctly set
   - Ensure the Python dependencies are correctly installed

3. **CORS Issues**
   - Verify the `ALLOWED_ORIGINS` environment variable includes your frontend domain
   - Check the CORS middleware configuration in `main.py`

## Monitoring

Monitor your deployment in the Vercel dashboard:
- Logs: View function logs and errors
- Metrics: Monitor performance and usage
- Analytics: Track API usage and performance
