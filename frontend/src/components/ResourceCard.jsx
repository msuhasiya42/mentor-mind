const ResourceCard = ({ resource, isPaid = false, gradient = 'from-purple-500 to-pink-500' }) => {
  const handleClick = () => {
    if (resource.url) {
      window.open(resource.url, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <div
      onClick={handleClick}
      className="group relative cursor-pointer"
    >
      {/* Main Card */}
      <div className="relative overflow-hidden bg-white rounded-2xl border border-gray-200 shadow-lg transition-all duration-300 hover:shadow-2xl hover:-translate-y-1 hover:border-transparent">
        {/* Gradient Border Effect on Hover */}
        <div className={`absolute inset-0 bg-gradient-to-r ${gradient} scale-[1.01] opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-2xl`}></div>
        <div className="absolute inset-[1px] bg-white rounded-2xl"></div>
        
        {/* Content */}
        <div className="relative p-6">
          {/* Header */}
          <div className="flex justify-between items-start mb-4">
            <div className="flex-1 min-w-0">
              <h4 className="font-bold text-gray-900 text-lg leading-tight mb-2 group-hover:text-transparent group-hover:bg-gradient-to-r group-hover:bg-clip-text group-hover:from-purple-600 group-hover:to-pink-600 transition-all duration-300">
                {resource.title}
              </h4>
              {resource.platform && (
                <div className="inline-flex items-center px-3 py-1 rounded-full bg-gray-100 text-gray-700 text-sm font-medium">
                  <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                  {resource.platform}
                </div>
              )}
            </div>
            
            {/* Price Badge */}
            {isPaid && resource.price && (
              <div className={`ml-3 px-3 py-1 bg-gradient-to-r ${gradient} text-white text-sm rounded-full font-semibold shadow-lg`}>
                {resource.price}
              </div>
            )}
          </div>
          
          {/* Description */}
          {resource.description && (
            <p className="text-gray-600 text-sm leading-relaxed mb-4 line-clamp-3">
              {resource.description}
            </p>
          )}
          
          {/* Footer */}
          <div className="flex items-center justify-between pt-4 border-t border-gray-100">
            {/* Resource Type Indicator */}
            <div className="flex items-center text-sm text-gray-500">
              <div className="w-3 h-3 rounded-full bg-gradient-to-r from-green-400 to-blue-500 mr-2"></div>
              {resource.url?.includes('youtube') ? 'Video' : 
               resource.url?.includes('github') ? 'Code' : 
               resource.url?.includes('docs') ? 'Documentation' : 'Resource'}
            </div>
            
            {/* Action Button */}
            <div className={`flex items-center text-sm font-semibold bg-gradient-to-r ${gradient} bg-clip-text text-transparent group-hover:text-white transition-all duration-300`}>
              <span className="mr-2">Explore</span>
              <svg 
                className={`w-4 h-4 transition-all duration-300 group-hover:translate-x-1 text-gray-400 group-hover:text-white`} 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </div>
          </div>
        </div>

        {/* Hover Effect Overlay */}
        <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-300 rounded-2xl pointer-events-none`}></div>
      </div>

      {/* Floating Action Button on Hover */}
      <div className="absolute -top-2 -right-2 opacity-0 group-hover:opacity-100 transition-all duration-300 transform scale-90 group-hover:scale-100">
        <div className={`w-10 h-10 bg-gradient-to-r ${gradient} rounded-full flex items-center justify-center shadow-lg`}>
          <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        </div>
      </div>
    </div>
  );
};

export default ResourceCard; 