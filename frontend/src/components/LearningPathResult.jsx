import ResourceCard from './ResourceCard';

const LearningPathResult = ({ data }) => {
  const { topic, learning_path } = data;

  const sections = [
    {
      title: 'Documentation & Official Guides',
      icon: '📚',
      resources: learning_path.docs,
      gradient: 'from-blue-500 to-blue-600',
      bgGradient: 'from-blue-50 to-blue-100',
      iconBg: 'bg-blue-100 text-blue-600',
      description: 'Official documentation and guides from the source'
    },
    {
      title: 'Blogs & Articles',
      icon: '✍️',
      resources: learning_path.blogs,
      gradient: 'from-green-500 to-emerald-600',
      bgGradient: 'from-green-50 to-emerald-100',
      iconBg: 'bg-green-100 text-green-600',
      description: 'Insightful articles and community-driven content'
    },
    {
      title: 'YouTube Videos',
      icon: '🎬',
      resources: learning_path.youtube,
      gradient: 'from-red-500 to-red-600',
      bgGradient: 'from-red-50 to-red-100',
      iconBg: 'bg-red-100 text-red-600',
      description: 'Visual learning through expert tutorials and demos'
    },
    {
      title: 'Free Courses',
      icon: '🎓',
      resources: learning_path.free_courses,
      gradient: 'from-purple-500 to-purple-600',
      bgGradient: 'from-purple-50 to-purple-100',
      iconBg: 'bg-purple-100 text-purple-600',
      description: 'Structured learning paths at no cost'
    }
  ];

  // Calculate total resources
  const totalResources = sections.reduce((total, section) => 
    total + (section.resources?.length || 0), 0
  );

  return (
    <div className="w-full">
      {/* Header Section */}
      <div className="text-center mb-12">
        <div className="inline-flex items-center px-6 py-3 rounded-full bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold mb-6 shadow-lg">
          <span className="text-2xl mr-3">🎯</span>
          Learning Path Generated
        </div>
        <h2 className="text-4xl font-bold text-white mb-4">
          Master <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">{topic}</span>
        </h2>
        <p className="text-xl text-purple-100 max-w-2xl mx-auto leading-relaxed">
          Your personalized learning journey with {totalResources} curated resources
        </p>
        
        {/* Progress Stats */}
        <div className="flex justify-center gap-8 mt-8">
          <div className="text-center">
            <div className="text-3xl font-bold text-white">{totalResources}</div>
            <div className="text-purple-200 text-sm">Total Resources</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-white">{sections.filter(s => s.resources?.length > 0).length}</div>
            <div className="text-purple-200 text-sm">Categories</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-white">∞</div>
            <div className="text-purple-200 text-sm">Potential</div>
          </div>
        </div>
      </div>

      {/* Learning Path Sections */}
      <div className="space-y-8">
        {sections.map((section, index) => (
          <div
            key={index}
            className="group relative"
          >
            {/* Section Card */}
            <div className={`relative overflow-hidden rounded-3xl bg-gradient-to-br ${section.bgGradient} border border-white/20 backdrop-blur-sm transition-all duration-500 hover:scale-[1.02] hover:shadow-2xl`}>
              {/* Gradient Border Effect */}
              <div className={`absolute inset-0 bg-gradient-to-r ${section.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-3xl`}></div>
              <div className="absolute inset-[1px] bg-white rounded-3xl"></div>
              
              {/* Content */}
              <div className="relative p-8">
                {/* Section Header */}
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-4">
                    <div className={`p-4 rounded-2xl ${section.iconBg} text-3xl font-bold shadow-lg`}>
                      {section.icon}
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-gray-800 mb-1">
                        {section.title}
                      </h3>
                      <p className="text-gray-600">
                        {section.description}
                      </p>
                    </div>
                  </div>
                  
                  {/* Resource Count Badge */}
                  <div className={`px-4 py-2 rounded-full bg-gradient-to-r ${section.gradient} text-white font-semibold shadow-lg`}>
                    {section.resources?.length || 0} resources
                  </div>
                </div>
                
                {/* Resources Grid */}
                {section.resources && section.resources.length > 0 ? (
                  <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {section.resources.map((resource, resourceIndex) => (
                      <div
                        key={resourceIndex}
                        className="transform transition-all duration-300 hover:-translate-y-2"
                      >
                        <ResourceCard
                          resource={resource}
                          isPaid={section.title.includes('Premium')}
                          gradient={section.gradient}
                        />
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4 opacity-30">🔍</div>
                    <p className="text-gray-500 text-lg mb-2">No resources found for this category</p>
                    <p className="text-gray-400 text-sm">Our AI is constantly learning and improving recommendations!</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Learning Tips Section */}
      <div className="mt-16 p-8 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 backdrop-blur-sm rounded-3xl border border-white/20">
        <div className="text-center">
          <div className="text-4xl mb-4">💡</div>
          <h3 className="text-2xl font-bold text-white mb-4">Pro Learning Tips</h3>
          <div className="grid md:grid-cols-3 gap-6 text-left">
            <div className="p-4 bg-white/10 rounded-2xl">
              <div className="text-2xl mb-2">📖</div>
              <h4 className="font-semibold text-white mb-2">Start with Docs</h4>
              <p className="text-purple-100 text-sm">Begin with official documentation to build a solid foundation</p>
            </div>
            <div className="p-4 bg-white/10 rounded-2xl">
              <div className="text-2xl mb-2">🎯</div>
              <h4 className="font-semibold text-white mb-2">Practice Daily</h4>
              <p className="text-purple-100 text-sm">Consistent practice with small projects accelerates learning</p>
            </div>
            <div className="p-4 bg-white/10 rounded-2xl">
              <div className="text-2xl mb-2">🤝</div>
              <h4 className="font-semibold text-white mb-2">Join Community</h4>
              <p className="text-purple-100 text-sm">Connect with other learners and share your progress</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LearningPathResult; 