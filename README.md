# 🧠 Mentor Mind - AI-Powered Learning Path Generator

An intelligent web application that generates personalized learning paths for any technology or skill using AI-powered content curation and ranking.

## 🚨 **NEW: OpenRouter Integration (2025)**

**Mentor Mind now uses OpenRouter's free models for superior AI performance!**

✅ **Better Reliability**: More stable than Hugging Face  
✅ **Free Access**: Powerful models including DeepSeek (excellent for coding)  
✅ **Higher Quality**: State-of-the-art models for content generation  
✅ **Easy Setup**: Simple API key configuration  

**[📖 Migration Guide](./OPENROUTER_MIGRATION_GUIDE.md)** | **[🚀 Setup Instructions](./SETUP_INSTRUCTIONS.md)** | **[🧪 Test Setup](./test_openrouter_setup.py)**

## 🌟 Features

- **🤖 Advanced AI Models**: Powered by OpenRouter's free tier (DeepSeek, Qwen, Llama, Gemma)
- **📚 Smart Content Curation**: AI-generated search queries and intelligent resource ranking
- **🔄 Multi-Source Aggregation**: Pulls content from documentation, blogs, YouTube, and course platforms
- **🎯 Personalized Learning Paths**: Generates customized learning journeys based on your topic
- **💻 Modern UI**: Clean, responsive interface built with React and Tailwind CSS
- **⚡ Fast API Backend**: High-performance Python backend with FastAPI
- **🆓 Free Resources Focus**: Prioritizes free and open-source learning materials

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

2. **Get OpenRouter API Key (Free)**
   - Go to [https://openrouter.ai](https://openrouter.ai)
   - Sign up for a free account
   - Get your API key from the dashboard
   - Create `.env` file in project root:
   ```bash
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

3. **Set up the backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Set up the frontend**
   ```bash
   cd ../frontend
   npm install
   ```

5. **Test your setup**
   ```bash
   python test_openrouter_setup.py
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
- **OpenRouter Integration** - Free access to state-of-the-art models
- **DeepSeek Model** - Excellent for coding and technical content
- **Multiple Model Fallbacks** - Qwen, Llama, Gemma for reliability
- **Custom AI Processor** - Smart content ranking and classification
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
│   ├── tests/             # Test suite
│   ├── main.py            # FastAPI app
│   └── requirements.txt
├── docs/                   # 📚 Documentation Hub
│   ├── README.md          # Documentation index
│   ├── REFACTORING_SUMMARY.md
│   ├── TEST_RESULTS_SUMMARY.md
│   ├── BACKEND_README.md
│   ├── FRONTEND_README.md
│   └── ... more docs
└── README.md
```

## 📚 Documentation

All project documentation is organized in the `/docs` folder:

- **[📖 Documentation Hub](./docs/README.md)** - Complete documentation index
- **[🏗️ Architecture Guide](./docs/REFACTORING_SUMMARY.md)** - System architecture and design
- **[🧪 Testing Guide](./docs/TEST_RESULTS_SUMMARY.md)** - Test coverage and results
- **[⚙️ Backend Setup](./docs/BACKEND_README.md)** - Backend development guide
- **[🎨 Frontend Setup](./docs/FRONTEND_README.md)** - Frontend development guide

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
- **Advanced AI Models**: DeepSeek (coding), Qwen (general), Llama (text), Gemma (instructions)
- **Smart Query Generation**: AI creates diverse search queries for better coverage
- **Intelligent Resource Ranking**: AI analyzes and ranks resources by relevance and quality
- **Automatic Fallbacks**: Multiple models ensure reliability
- **Rate Limit Aware**: Efficient usage with 50 free requests/day (1000 with $10 credit)

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

## 🔍 LLM-Only Search Engine

MentorMind now uses an advanced **LLM-Only Search Engine** that generates comprehensive learning resources directly from AI knowledge without relying on web scraping. This approach provides:

### ✨ Key Features

- **Persona-Based Generation**: Uses 4 different AI personas to provide diverse perspectives
- **Comprehensive Coverage**: Generates resources across multiple categories (docs, courses, videos, blogs, repositories)
- **No Rate Limits**: Unlike web scraping, no API rate limits or blocking issues
- **Consistent Quality**: Always returns structured, relevant learning resources
- **Offline Capability**: Works without internet connectivity once configured

### 🎭 AI Personas

The system uses 4 specialized personas to generate diverse learning resources:

1. **Technical Mentor**: Experienced software engineer (15+ years) - Focuses on practical learning paths
2. **Academic Educator**: Computer science professor - Emphasizes theoretical foundations and official docs
3. **Industry Expert**: Senior tech lead at major companies - Recommends industry-relevant courses and certifications
4. **Content Curator**: Learning resource specialist - Knows the best platforms, channels, and learning materials

### 🛠️ How It Works

```python
# Example: When you search for "React Hooks"

# The system generates resources from each persona:
technical_mentor_resources = [
    "React Hooks Tutorial with Real Projects",
    "Building Custom Hooks - Step by Step Guide",
    "React Hooks vs Class Components Migration"
]

academic_educator_resources = [
    "Official React Hooks Documentation",
    "React Hooks API Reference",
    "Understanding React Hooks Fundamentals"
]

industry_expert_resources = [
    "Advanced React Hooks Patterns",
    "React Hooks in Production Applications",
    "React Hooks Performance Optimization"
]

content_curator_resources = [
    "Best React Hooks YouTube Channels",
    "Interactive React Hooks Courses",
    "React Hooks GitHub Repositories"
]
```

### 📊 Resource Categories

Each search generates resources across 5 main categories:

- **📚 Documentation**: Official docs, API references, getting started guides
- **🎓 Courses**: Online courses, bootcamps, certifications (free & paid)
- **📺 Videos**: YouTube channels, tutorials, conference talks
- **📝 Blogs**: Technical articles, tutorials, best practices
- **💻 Code**: GitHub repositories, examples, practice platforms

### 🚀 Benefits Over Web Search

| Traditional Web Search | LLM-Only Search |
|------------------------|-----------------|
| Rate limits & blocking | No restrictions |
| Inconsistent quality   | Consistent, structured results |
| Dead links            | Generated working URLs |
| Limited by search engines | AI knowledge base |
| Requires internet     | Works offline |
| Generic results       | Persona-specific perspectives |

---

**Happy Learning! 🚀** 