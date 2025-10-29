# Quick Start Guide - Mentor Mind

## Get Started in 3 Minutes! 🚀

### Step 1: Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Start Backend Server
```bash
python main.py
```

Expected output:
```
✅ Database initialized successfully!
⚡ Validating configuration...
✅ Configuration validated
⚡ Initializing services...
✅ Services initialized
🎯 Application ready to serve requests
INFO:     Uvicorn running on http://0.0.0.0:8000
```

The database (`mentor_mind.db`) will be created automatically on first run.

### Step 3: Install Frontend Dependencies
Open a new terminal:
```bash
cd frontend
npm install
```

### Step 4: Start Frontend
```bash
npm run dev
```

Expected output:
```
VITE v6.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
```

### Step 5: Open in Browser
Navigate to: http://localhost:5173/

---

## Testing the New Features

### 1. Generate a Learning Path
- Enter a topic (e.g., "React Hooks")
- Click "Generate Learning Path ✨"
- Wait for AI to generate resources
- You'll be redirected to the Results page

### 2. Download Options
On the Results page, try:
- Click "Download PDF" 📄
- Click "Download DOC" 📝
- Check your Downloads folder

### 3. View History
- Click "View History" button
- See all your previously generated paths
- Search by topic name
- Click any card to view that path again

### 4. Check Statistics
- Return to Home page
- See "Paths Generated" and "Downloads" counters
- These update in real-time!

---

## Project Structure

```
mentor-mind/
├── backend/
│   ├── database/          # NEW! SQLite database layer
│   │   ├── db.py         # Database connection
│   │   ├── models.py     # ORM models
│   │   └── crud.py       # Database operations
│   ├── services/         # Business logic
│   ├── models/           # Pydantic models
│   ├── main.py           # UPDATED! New endpoints
│   └── mentor_mind.db    # AUTO-CREATED! SQLite file
│
├── frontend/
│   ├── src/
│   │   ├── pages/        # NEW! Route components
│   │   │   ├── HomePage.jsx
│   │   │   ├── ResultsPage.jsx
│   │   │   └── HistoryPage.jsx
│   │   ├── utils/        # NEW! Export utilities
│   │   │   ├── pdfGenerator.js
│   │   │   └── docGenerator.js
│   │   ├── services/     # NEW! API service
│   │   │   └── api.js
│   │   └── App.jsx       # UPDATED! Router setup
│   └── package.json      # UPDATED! New dependencies
│
└── IMPLEMENTATION_SUMMARY.md  # Full documentation
```

---

## New API Endpoints

### Test with curl:

#### Get All Learning Paths
```bash
curl http://localhost:8000/learning-paths
```

#### Get Specific Learning Path
```bash
curl http://localhost:8000/learning-paths/1
```

#### Get Statistics
```bash
curl http://localhost:8000/stats
```

#### Track Download Action
```bash
curl -X POST "http://localhost:8000/learning-paths/1/action?action_type=downloaded_pdf"
```

---

## Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError: No module named 'sqlalchemy'`
**Solution:**
```bash
cd backend
pip install sqlalchemy==2.0.35
```

**Problem:** Database errors
**Solution:**
```bash
# Delete the database and let it recreate
rm backend/mentor_mind.db
python backend/main.py
```

### Frontend Issues

**Problem:** `Cannot find module 'react-router-dom'`
**Solution:**
```bash
cd frontend
npm install
```

**Problem:** Blank page
**Solution:**
- Check browser console for errors
- Ensure backend is running on http://localhost:8000
- Clear browser cache and reload

---

## Environment Configuration (Optional)

Create `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
```

Create `backend/.env`:
```env
# Your existing API keys
OPENROUTER_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

---

## Features Checklist

Try all these features:

- [ ] Generate a learning path
- [ ] Download as PDF
- [ ] Download as DOC
- [ ] View history page
- [ ] Search in history
- [ ] Click a history item to view it
- [ ] Check statistics on home page
- [ ] Navigate between pages
- [ ] Test on mobile browser (responsive design)

---

## What's New?

### Database (Backend)
- ✅ SQLite database for persistence
- ✅ Auto-saves all learning paths
- ✅ Tracks downloads and views
- ✅ Statistics aggregation

### Export (Frontend)
- ✅ Download paths as PDF
- ✅ Download paths as DOC
- ✅ Professional formatting
- ✅ Clickable links in exports

### Navigation (Frontend)
- ✅ Multi-page routing
- ✅ History page to browse all paths
- ✅ Direct links to saved paths
- ✅ Smooth page transitions

### UI Improvements (Frontend)
- ✅ Removed "Track Progress" card
- ✅ Added statistics dashboard
- ✅ Toast notifications
- ✅ Loading states
- ✅ Error handling

---

## Next Steps

1. **Test Everything** - Go through the features checklist
2. **Customize** - Adjust colors, text, branding
3. **Deploy** - Ready for Vercel/Netlify (frontend) + Railway/Render (backend)
4. **Add to Portfolio** - Screenshot the beautiful UI!

---

## Need Help?

Check these files:
- `IMPLEMENTATION_SUMMARY.md` - Detailed documentation
- `frontend/src/` - All frontend code with comments
- `backend/database/` - Database implementation

---

## Pro Tips

1. **Keep the backend running** - The frontend needs it!
2. **Check the console** - Useful logs and errors
3. **Use the browser dev tools** - Network tab shows API calls
4. **SQLite is portable** - The `mentor_mind.db` file contains all data

---

Enjoy your enhanced Mentor Mind application! 🎉
