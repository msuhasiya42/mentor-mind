import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { generateLearningPath, getStatistics } from '../services/api'
import toast, { Toaster } from 'react-hot-toast'
import LoadingSpinner from '../components/LoadingSpinner'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"

function HomePage() {
  const [topic, setTopic] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingStatus, setLoadingStatus] = useState('')
  const [stats, setStats] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    fetchStatistics()
  }, [])

  const fetchStatistics = async () => {
    try {
      const data = await getStatistics()
      setStats(data)
    } catch (error) {
      console.error('Failed to fetch statistics:', error)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!topic.trim()) {
      toast.error('Please enter a topic')
      return
    }

    setLoading(true)

    // Interactive loading status messages
    const statuses = [
      { message: '🔍 Searching for resources...', delay: 0 },
      { message: '📚 Checking documentation sources...', delay: 1000 },
      { message: '✨ Found amazing resources!', delay: 2000 },
      { message: '🎯 Curating the best content for you...', delay: 3000 },
    ]

    // Show loading status messages sequentially
    let statusTimeouts = []
    statuses.forEach(({ message, delay }) => {
      const timeout = setTimeout(() => {
        setLoadingStatus(message)
      }, delay)
      statusTimeouts.push(timeout)
    })

    try {
      const response = await generateLearningPath(topic.trim())

      // Clear any pending status updates
      statusTimeouts.forEach(timeout => clearTimeout(timeout))

      setLoadingStatus('✅ Resources ready!')

      setTimeout(() => {
        toast.success('Resources curated successfully!')
        navigate('/results', {
          state: {
            learningPath: response,
            fromGeneration: true
          }
        })
      }, 500)
    } catch (err) {
      statusTimeouts.forEach(timeout => clearTimeout(timeout))
      toast.error(err.response?.data?.detail || 'Failed to find resources. Please try again.')
      setLoading(false)
      setLoadingStatus('')
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSubmit(e)
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <Toaster position="top-right" />

      {/* Header */}
      <div className="border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            {/* Logo + Title */}
            <div className="flex items-center gap-3">
              <img src="/brain-icon.svg" alt="Brain" className="w-8 h-8 invert" />
              <h2 className="text-2xl font-bold">Resource Mind</h2>
            </div>

            {/* Stats + Contact */}
            <div className="flex items-center gap-4">
              {stats && (
                <>
                  <div className="hidden md:flex gap-6 text-sm">
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground">Resources Found:</span>
                      <span className="font-semibold">{stats.total_learning_paths}</span>
                    </div>
                    <Separator orientation="vertical" className="h-6" />
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground">Downloads:</span>
                      <span className="font-semibold">{stats.total_downloads}</span>
                    </div>
                  </div>
                  <Separator orientation="vertical" className="h-6 hidden md:block" />
                </>
              )}
              <Button variant="ghost" size="sm" asChild>
                <a href="mailto:mayursuhasiya136@gmail.com" className="flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  Contact
                </a>
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16 md:py-24">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          {!loading ? (
            <>
              {/* Main Heading */}
              <div className="space-y-4">
                <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
                  AI-Powered Resource Curation
                </h1>
                <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto">
                  Find the best learning resources for any technology or skill, curated by AI
                </p>
              </div>

              {/* Search Form */}
              <form onSubmit={handleSubmit} className="max-w-2xl mx-auto">
                <div className="flex gap-2">
                  <Input
                    type="text"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Enter a skill or technology (e.g., React, Python, Machine Learning)"
                    className="flex-1 h-12 text-base"
                    autoFocus
                  />
                  <Button
                    type="submit"
                    disabled={!topic.trim()}
                    size="lg"
                    className="px-8 text-white"
                  >
                    Find Resources
                  </Button>
                </div>
              </form>
            </>
          ) : (
            /* Interactive Loading Screen */
            <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-8">
              <div className="space-y-6">
                <LoadingSpinner />
                <div className="text-center space-y-2">
                  <h2 className="text-2xl md:text-3xl font-bold">{topic}</h2>
                  <p className="text-lg md:text-xl text-muted-foreground animate-pulse">
                    {loadingStatus}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Features - Only show when not loading */}
          {!loading && (
            <div className="grid md:grid-cols-2 gap-6 pt-8">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <span className="text-2xl">🎯</span>
                    <span>Curated Resources</span>
                  </CardTitle>
                  <CardDescription>
                    Handpicked learning materials tailored to your goals and skill level
                  </CardDescription>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <span className="text-2xl">🚀</span>
                    <span>AI-Powered</span>
                  </CardTitle>
                  <CardDescription>
                    Advanced AI algorithms find the most effective learning resources
                  </CardDescription>
                </CardHeader>
              </Card>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t mt-auto">
        <div className="container mx-auto px-4 py-4">
          <div className="flex flex-col md:flex-row justify-between items-center gap-3 text-sm">
            <p className="text-muted-foreground">
              Empowering your learning journey with AI-curated resources
            </p>
            <div className="flex items-center gap-3">
              <span className="text-muted-foreground">Made with</span>
              <svg className="w-4 h-4 text-red-500 animate-pulse" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
              </svg>
              <span className="text-muted-foreground">by</span>
              <strong className="text-foreground">Mayur Suhasiya</strong>
              <Separator orientation="vertical" className="h-4" />
              <a
                href="mailto:mayursuhasiya136@gmail.com"
                className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors group"
                title="Send me an email"
              >
                <svg className="w-4 h-4 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <span>mayursuhasiya136@gmail.com</span>
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default HomePage
