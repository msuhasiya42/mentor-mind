const LoadingSpinner = () => {
  return (
    <div className="flex flex-col items-center justify-center p-16">
      {/* Main Spinner Container */}
      <div className="relative mb-8">
        {/* Outer rotating ring */}
        <div className="w-24 h-24 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin"></div>
        
     
        
        {/* Floating dots */}
        <div className="absolute -top-2 -right-2 w-4 h-4 bg-gradient-to-r from-pink-500 to-purple-500 rounded-full animate-bounce"></div>
        <div className="absolute -bottom-2 -left-2 w-3 h-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full animate-bounce" style={{animationDelay: '0.5s'}}></div>
        <div className="absolute top-1/2 -left-4 w-2 h-2 bg-gradient-to-r from-green-500 to-blue-500 rounded-full animate-bounce" style={{animationDelay: '1s'}}></div>
      </div>

      {/* Loading Text */}
      <div className="text-center space-y-4">
        <h3 className="text-2xl font-bold text-white mb-2">
          🔮 AI is crafting your learning path
        </h3>
        <div className="text-purple-100 space-y-2">
          <p className="text-lg">Analyzing thousands of resources...</p>
          <div className="flex items-center justify-center space-x-2">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
              <div className="w-2 h-2 bg-pink-400 rounded-full animate-pulse" style={{animationDelay: '0.3s'}}></div>
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style={{animationDelay: '0.6s'}}></div>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="mt-12 w-full max-w-md">
        <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <span className="text-purple-100">Understanding your topic</span>
            </div>
            
            <div className="flex items-center space-x-3">
              <div className="w-6 h-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full animate-spin flex items-center justify-center">
                <div className="w-2 h-2 bg-white rounded-full"></div>
              </div>
              <span className="text-purple-100">Curating resources</span>
            </div>
            
            <div className="flex items-center space-x-3">
              <div className="w-6 h-6 border-2 border-purple-300 rounded-full animate-pulse"></div>
              <span className="text-purple-200">Personalizing recommendations</span>
            </div>
          </div>
        </div>
      </div>

      {/* Fun Facts */}
      <div className="mt-8 text-center">
        <p className="text-purple-200 text-sm italic">
          💡 Fun fact: The best learning happens when you combine multiple resource types!
        </p>
      </div>
    </div>
  );
};

export default LoadingSpinner; 