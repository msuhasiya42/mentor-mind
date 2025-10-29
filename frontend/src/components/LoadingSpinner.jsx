import { Skeleton } from "@/components/ui/skeleton"

const LoadingSpinner = () => {
  return (
    <div className="flex flex-col items-center justify-center p-16 space-y-8">
      {/* Spinner */}
      <div className="relative">
        <div className="w-16 h-16 border-4 border-muted border-t-foreground rounded-full animate-spin"></div>
      </div>

      {/* Loading Text */}
      <div className="text-center space-y-4">
        <h3 className="text-2xl font-semibold">
          Crafting your learning path
        </h3>
        <p className="text-muted-foreground">
          Analyzing resources and curating the best content...
        </p>
      </div>

      {/* Progress Steps */}
      <div className="w-full max-w-md space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-6 h-6 bg-foreground rounded-full flex items-center justify-center flex-shrink-0">
            <svg className="w-4 h-4 text-background" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <span className="text-sm">Understanding your topic</span>
        </div>

        <div className="flex items-center gap-3">
          <div className="w-6 h-6 border-2 border-foreground rounded-full animate-pulse flex-shrink-0"></div>
          <span className="text-sm">Curating resources</span>
        </div>

        <div className="flex items-center gap-3">
          <div className="w-6 h-6 border-2 border-muted rounded-full flex-shrink-0"></div>
          <span className="text-sm text-muted-foreground">Personalizing recommendations</span>
        </div>
      </div>
    </div>
  );
};

export default LoadingSpinner;
