# 🧠 Mentor Mind - AI-Powered Learning Path Generator

An intelligent web application that generates personalized learning paths for any technology or skill using AI-powered content curation and ranking.

## 🌟 Features

- **AI-Powered Content Curation**: Uses intelligent algorithms to find and rank the best learning resources
- **Multi-Source Aggregation**: Pulls content from documentation, blogs, YouTube, and course platforms
- **Personalized Learning Paths**: Generates customized learning journeys based on your topic
- **Modern UI**: Clean, responsive interface built with React and Tailwind CSS
- **Fast API Backend**: High-performance Python backend with FastAPI
- **Free Resources Focus**: Prioritizes free and open-source learning materials

## 🏗️ Architecture

### Frontend (React + Vite)
- Modern React with hooks and functional components
- Tailwind CSS for styling
- Axios for API communication
- Responsive design for all devices

### Backend (Python + FastAPI)
- FastAPI for high-performance API
- AI-powered content ranking and filtering
- Multi-source content aggregation
- Async/await for optimal performance

## 🚀 Quick Start

### Prerequisites
- Node.js (v16 or higher)
- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mentor-mind
   ```

2. **Set up the backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Set up the frontend**
   ```bash
   cd ../frontend
   npm install
   ```

### Running the Application

1. **Start the backend server**
   ```bash
   cd backend
   python main.py
   ```
   The API will be available at `http://localhost:8000`

2. **Start the frontend development server**
   ```bash
   cd frontend
   npm run dev
   ```
   The web app will be available at `http://localhost:5173`

## 📖 Usage

1. Open the web application in your browser
2. Enter a technology or skill you want to learn (e.g., "React", "Python", "Machine Learning")
3. Click "Generate Learning Path"
4. Browse through the curated resources organized by category:
   - 📖 Documentation & Official Guides
   - 📝 Blogs & Articles
   - 🎥 YouTube Videos
   - 🆓 Free Courses
   - 💰 Paid Courses

## 🛠️ Technology Stack

### Frontend
- **React 18** - Modern UI library
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API calls

### Backend
- **FastAPI** - Modern Python web framework
- **aiohttp** - Async HTTP client
- **BeautifulSoup4** - HTML parsing
- **Pydantic** - Data validation

### AI & Content Processing
- **Custom AI Processor** - Lightweight content ranking and classification
- **DuckDuckGo Search** - Privacy-focused search integration
- **Multi-source Aggregation** - Content from various platforms

## 📁 Project Structure

```
mentor-mind/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── App.jsx         # Main app component
│   │   └── main.jsx        # Entry point
│   ├── package.json
│   └── tailwind.config.js
├── backend/                 # Python backend
│   ├── services/           # Business logic
│   │   ├── learning_path_generator.py
│   │   ├── content_aggregator.py
│   │   └── ai_processor.py
│   ├── main.py            # FastAPI app
│   └── requirements.txt
└── README.md
```

## 🔧 API Endpoints

### `POST /generate-learning-path`
Generate a learning path for a given topic.

**Request:**
```json
{
  "topic": "React"
}
```

**Response:**
```json
{
  "topic": "React",
  "learning_path": {
    "docs": [{"title": "...", "url": "...", "description": "..."}],
    "blogs": [{"title": "...", "url": "...", "description": "..."}],
    "youtube": [{"title": "...", "url": "...", "description": "..."}],
    "free_courses": [{"title": "...", "url": "...", "description": "..."}],
    "paid_courses": [{"title": "...", "url": "...", "price": "..."}]
  }
}
```

## 🎯 Features in Detail

### AI-Powered Content Ranking
- Relevance scoring based on topic matching
- Platform priority weighting
- Quality indicators analysis
- Duplicate content filtering

### Multi-Source Content Aggregation
- Official documentation sources
- Popular blog platforms
- YouTube educational content
- Free course platforms (Coursera, edX, freeCodeCamp)
- Paid course platforms (Udemy, Pluralsight)

### Responsive Design
- Mobile-first approach
- Clean, modern interface
- Loading states and error handling
- Accessible design patterns

## 🔮 Future Enhancements

- [ ] User accounts and saved learning paths
- [ ] Progress tracking
- [ ] Community ratings and reviews
- [ ] Advanced AI models integration
- [ ] Offline learning path export
- [ ] Learning path sharing
- [ ] Multi-language support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with free and open-source tools
- Powered by community-driven content
- Inspired by the need for personalized learning

---

**Happy Learning! 🚀** 