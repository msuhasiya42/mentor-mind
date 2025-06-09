import { useState, useEffect } from 'react'
import axios from 'axios'
import LoadingSpinner from './LoadingSpinner'
import LearningPathResult from './LearningPathResult'

const API_BASE_URL = 'http://localhost:8000'

function Home() {
  const [topic, setTopic] = useState('')
  const [learningPath, setLearningPath] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showSuccess, setShowSuccess] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!topic.trim()) {
      setError('Please enter a topic')
      return
    }

    setLoading(true)
    setError('')
    setLearningPath(null)
    setShowSuccess(false)

    try {
      const response = await axios.post(`${API_BASE_URL}/generate-learning-path`, {
        topic: topic.trim()
      })
      setLearningPath(response.data)
      setShowSuccess(true)
      
      // Auto-hide success notification after 3 seconds
      setTimeout(() => setShowSuccess(false), 3000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate learning path. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  console.log("learningPath", learningPath)

  // Success notification component
  const SuccessNotification = () => (
    <div className={`fixed top-8 right-8 z-50 transition-all duration-500 transform ${showSuccess ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}`}>
      <div className="bg-gradient-to-r from-green-500 to-emerald-600 text-white px-6 py-4 rounded-2xl shadow-2xl border border-green-400/30 backdrop-blur-sm">
        <div className="flex items-center space-x-3">
          <div className="text-2xl animate-bounce">✨</div>
          <div>
            <div className="font-semibold">Learning Path Generated!</div>
            <div className="text-green-100 text-sm">Your personalized journey is ready</div>
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800 overflow-x-hidden">
      {/* Success Notification */}
      <SuccessNotification />
      
      {/* Hero Section */}
      <div className="relative w-full overflow-hidden">
        {/* Background decorative elements */}
        <div className="absolute inset-0 w-full h-full">
          <div className="absolute top-0 left-0 w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
          <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse animation-delay-2000"></div>
          <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-96 h-96 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float"></div>
        </div>

        <div className="relative z-10 w-full px-4 py-16 sm:px-6 lg:px-8">
          <div className="text-center w-full">
            {/* Main heading */}
            <div className="mb-8">
              <div className="inline-flex items-center px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 mb-6 hover:bg-white/15 transition-all duration-300">
                <span className="text-2xl mr-2 animate-pulse">🧠</span>
                <span className="text-white font-semibold">AI-Powered Learning</span>
              </div>
              <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
                Mentor Mind
              </h1>
              <p className="text-xl md:text-2xl text-purple-100 max-w-4xl mx-auto leading-relaxed">
                Generate personalized learning paths for any technology or skill with 
                <span className="text-pink-300 font-semibold"> AI-powered recommendations</span>
              </p>
            </div>

            {/* Search Form */}
            <div className="max-w-4xl mx-auto mb-12 w-full">
              <form onSubmit={handleSubmit} className="mb-8">
                <div className="flex flex-col md:flex-row gap-4 p-2 bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 hover:bg-white/15 transition-all duration-300">
                  <input
                    type="text"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    placeholder="Enter a skill or technology (e.g., React, Python, Machine Learning)"
                    className="flex-1 px-6 py-4 bg-white/90 backdrop-blur-sm border-0 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-400 focus:bg-white text-gray-800 placeholder-gray-500 text-lg transition-all duration-300"
                    disabled={loading}
                  />
                  <button
                    type="submit"
                    disabled={loading || !topic.trim()}
                    className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl hover:from-purple-700 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-semibold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-1 active:scale-95"
                  >
                    {loading ? (
                      <div className="flex items-center">
                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Generating...
                      </div>
                    ) : (
                      'Generate Learning Path ✨'
                    )}
                  </button>
                </div>
              </form>

              {error && (
                <div className="mb-6 p-4 bg-red-500/20 backdrop-blur-sm border border-red-400/30 rounded-xl animate-pulse">
                  <div className="flex items-center space-x-3">
                    <div className="text-red-400 text-xl">⚠️</div>
                    <p className="text-red-100">{error}</p>
                  </div>
                </div>
              )}
            </div>

            {/* Features Grid */}
            <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto mb-16 w-full">
              <div className="group p-8 bg-white/10 backdrop-blur-sm rounded-3xl border border-white/20 hover:bg-white/15 transition-all duration-500 hover:scale-105 hover:shadow-2xl hover-lift">
                <div className="text-5xl mb-6 group-hover:animate-bounce-gentle">🎯</div>
                <h3 className="text-xl font-semibold text-white mb-3">Personalized Paths</h3>
                <p className="text-purple-100 leading-relaxed">Tailored learning journeys based on your goals and current skill level</p>
                <div className="mt-4 w-12 h-1 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full group-hover:w-full transition-all duration-500"></div>
              </div>
              <div className="group p-8 bg-white/10 backdrop-blur-sm rounded-3xl border border-white/20 hover:bg-white/15 transition-all duration-500 hover:scale-105 hover:shadow-2xl hover-lift animation-delay-1000">
                <div className="text-5xl mb-6 group-hover:animate-bounce-gentle">🚀</div>
                <h3 className="text-xl font-semibold text-white mb-3">AI-Powered</h3>
                <p className="text-purple-100 leading-relaxed">Advanced AI algorithms curate the most effective learning resources</p>
                <div className="mt-4 w-12 h-1 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full group-hover:w-full transition-all duration-500"></div>
              </div>
              <div className="group p-8 bg-white/10 backdrop-blur-sm rounded-3xl border border-white/20 hover:bg-white/15 transition-all duration-500 hover:scale-105 hover:shadow-2xl hover-lift animation-delay-2000">
                <div className="text-5xl mb-6 group-hover:animate-bounce-gentle">📈</div>
                <h3 className="text-xl font-semibold text-white mb-3">Track Progress</h3>
                <p className="text-purple-100 leading-relaxed">Monitor your learning journey and celebrate achievements</p>
                <div className="mt-4 w-12 h-1 bg-gradient-to-r from-green-400 to-blue-400 rounded-full group-hover:w-full transition-all duration-500"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Results Section */}
      {(loading || learningPath) && (
        <div className="w-full px-4 py-16 sm:px-6 lg:px-8 bg-black/20 backdrop-blur-sm">
          <div className="max-w-6xl mx-auto w-full">
            {loading && <LoadingSpinner />}
            {learningPath && (
              <div className="animate-in fade-in duration-700 slide-in-from-bottom-8">
                <LearningPathResult data={learningPath} />
              </div>
            )}
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="relative z-10 w-full px-4 py-8 text-center">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <span className="text-purple-200">Made with</span>
            <span className="text-red-400 text-xl animate-pulse">❤️</span>
            <span className="text-purple-200">for learners everywhere</span>
          </div>
          <div className="text-purple-300 text-sm">
            Empowering your learning journey with AI-curated resources
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Home 