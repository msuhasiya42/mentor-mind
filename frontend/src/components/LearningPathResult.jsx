import ResourceCard from './ResourceCard';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"

const LearningPathResult = ({ data }) => {
  const { topic, learning_path } = data;

  const sections = [
    {
      title: 'Documentation & Official Guides',
      icon: '📚',
      resources: learning_path.docs,
      description: 'Official documentation and guides from the source'
    },
    {
      title: 'Blogs & Articles',
      icon: '✍️',
      resources: learning_path.blogs,
      description: 'Insightful articles and community-driven content'
    },
    {
      title: 'YouTube Videos',
      icon: '🎬',
      resources: learning_path.youtube,
      description: 'Visual learning through expert tutorials and demos'
    },
    {
      title: 'Free Courses',
      icon: '🎓',
      resources: learning_path.free_courses,
      description: 'Structured learning paths at no cost'
    }
  ];

  // Calculate total resources
  const totalResources = sections.reduce((total, section) =>
    total + (section.resources?.length || 0), 0
  );

  return (
    <div className="w-full space-y-8">
      {/* Header Section */}
      <div className="text-center space-y-4">
        <div className="inline-flex items-center px-4 py-2 rounded-full bg-secondary text-secondary-foreground font-semibold mb-4">
          <span className="mr-2">🎯</span>
          Resources Found
        </div>
        <h2 className="text-4xl font-bold">
          Master {topic}
        </h2>
        <p className="text-xl text-muted-foreground">
          {totalResources} curated resources to accelerate your learning
        </p>

        {/* Stats */}
        <div className="flex justify-center gap-8 pt-4">
          <div className="text-center">
            <div className="text-3xl font-bold">{totalResources}</div>
            <div className="text-sm text-muted-foreground">Total Resources</div>
          </div>
          <Separator orientation="vertical" className="h-12" />
          <div className="text-center">
            <div className="text-3xl font-bold">{sections.filter(s => s.resources?.length > 0).length}</div>
            <div className="text-sm text-muted-foreground">Categories</div>
          </div>
        </div>
      </div>

      <Separator />

      {/* Learning Path Sections */}
      <div className="space-y-12">
        {sections.map((section, index) => (
          <div key={index} className="space-y-6">
            {/* Section Header */}
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <h3 className="text-2xl font-bold flex items-center gap-2">
                  <span>{section.icon}</span>
                  <span>{section.title}</span>
                </h3>
                <p className="text-muted-foreground">
                  {section.description}
                </p>
              </div>
              <Badge variant="secondary">
                {section.resources?.length || 0} resources
              </Badge>
            </div>

            {/* Resources Grid */}
            {section.resources && section.resources.length > 0 ? (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {section.resources.map((resource, resourceIndex) => (
                  <ResourceCard
                    key={resourceIndex}
                    resource={resource}
                  />
                ))}
              </div>
            ) : (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <div className="text-6xl mb-4 opacity-30">🔍</div>
                  <p className="text-muted-foreground text-lg mb-2">No resources found for this category</p>
                  <p className="text-muted-foreground text-sm">Our AI is constantly learning and improving recommendations!</p>
                </CardContent>
              </Card>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default LearningPathResult;
