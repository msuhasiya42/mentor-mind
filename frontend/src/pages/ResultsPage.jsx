import { useState, useEffect } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import { getLearningPath, trackAction } from '../services/api'
import { generatePDF } from '../utils/pdfGenerator'
import { generateDOC } from '../utils/docGenerator'
import toast, { Toaster } from 'react-hot-toast'
import LearningPathResult from '../components/LearningPathResult'
import LoadingSpinner from '../components/LoadingSpinner'
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"

function ResultsPage() {
  const [learningPath, setLearningPath] = useState(null)
  const [loading, setLoading] = useState(false)
  const [downloading, setDownloading] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const { id } = useParams()

  useEffect(() => {
    if (location.state?.learningPath) {
      setLearningPath(location.state.learningPath)

      if (location.state.learningPath.id) {
        trackAction(location.state.learningPath.id, 'viewed').catch(console.error)
      }
    } else if (id) {
      fetchLearningPath(id)
    } else {
      toast.error('No resources found')
      navigate('/')
    }
  }, [id, location.state, navigate])

  const fetchLearningPath = async (pathId) => {
    setLoading(true)
    try {
      const data = await getLearningPath(pathId)
      const transformedData = {
        id: data.id,
        topic: data.topic,
        learning_path: data.data.learning_path
      }
      setLearningPath(transformedData)
      await trackAction(pathId, 'viewed').catch(console.error)
    } catch (error) {
      toast.error('Failed to load resources')
      navigate('/')
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadPDF = async () => {
    if (!learningPath) return

    setDownloading(true)
    const toastId = toast.loading('Generating PDF...')

    try {
      await generatePDF(learningPath)
      toast.success('PDF downloaded successfully!', { id: toastId })

      if (learningPath.id) {
        await trackAction(learningPath.id, 'downloaded_pdf').catch(console.error)
      }
    } catch (error) {
      toast.error('Failed to generate PDF', { id: toastId })
      console.error('PDF generation error:', error)
    } finally {
      setDownloading(false)
    }
  }

  const handleDownloadDOC = async () => {
    if (!learningPath) return

    setDownloading(true)
    const toastId = toast.loading('Generating DOC file...')

    try {
      await generateDOC(learningPath)
      toast.success('DOC file downloaded successfully!', { id: toastId })

      if (learningPath.id) {
        await trackAction(learningPath.id, 'downloaded_doc').catch(console.error)
      }
    } catch (error) {
      toast.error('Failed to generate DOC file', { id: toastId })
      console.error('DOC generation error:', error)
    } finally {
      setDownloading(false)
    }
  }

  const handleCopyLink = () => {
    if (!learningPath?.id) {
      toast.error('Cannot copy link - no ID available')
      return
    }

    const url = `${window.location.origin}/results/${learningPath.id}`
    navigator.clipboard.writeText(url)
    toast.success('Link copied! Share it with anyone.')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-16">
          <LoadingSpinner />
        </div>
      </div>
    )
  }

  if (!learningPath) {
    return null
  }

  return (
    <div className="min-h-screen bg-background">
      <Toaster position="top-right" />

      {/* Header */}
      <div className="border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            {/* Logo + Title */}
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-3 hover:opacity-80 transition-opacity"
            >
              <img src="/brain-icon.svg" alt="Brain" className="w-8 h-8 invert" />
              <h2 className="text-2xl font-bold">Resource Mind</h2>
            </button>

            {/* Actions + Contact */}
            <div className="flex items-center flex-wrap gap-3">
              <Button
                onClick={handleDownloadPDF}
                disabled={downloading}
                variant="outline"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                PDF
              </Button>

              <Button
                onClick={handleDownloadDOC}
                disabled={downloading}
                variant="outline"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                DOC
              </Button>

              <Separator orientation="vertical" className="h-10" />

              <Button
                onClick={handleCopyLink}
                variant="outline"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Copy Link
              </Button>

              <Button
                onClick={() => navigate('/')}
                variant="outline"
              >
                <span className="mr-2">✨</span>
                Find New
              </Button>

              <Separator orientation="vertical" className="h-10 hidden md:block" />

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

      {/* Results Content */}
      <div className="container mx-auto px-4 py-12">
        <LearningPathResult data={learningPath} />
      </div>

      {/* Footer */}
      <footer className="border-t mt-16">
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

export default ResultsPage
