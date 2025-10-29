import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

const ResourceCard = ({ resource }) => {
  const handleClick = () => {
    if (resource.url) {
      window.open(resource.url, '_blank', 'noopener,noreferrer');
    }
  };

  const getResourceType = () => {
    if (resource.url?.includes('youtube')) return 'Video';
    if (resource.url?.includes('github')) return 'Code';
    if (resource.url?.includes('docs')) return 'Docs';
    return 'Resource';
  };

  return (
    <Card
      onClick={handleClick}
      className="cursor-pointer transition-all hover:shadow-md hover:-translate-y-1"
    >
      <CardHeader>
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-lg leading-tight">
            {resource.title}
          </CardTitle>
          {resource.price && (
            <Badge variant="outline" className="flex-shrink-0">
              {resource.price}
            </Badge>
          )}
        </div>
        {resource.platform && (
          <Badge variant="secondary" className="w-fit mt-2">
            {resource.platform}
          </Badge>
        )}
      </CardHeader>

      {resource.description && (
        <CardContent>
          <p className="text-sm text-muted-foreground line-clamp-3">
            {resource.description}
          </p>
        </CardContent>
      )}

      <CardFooter className="border-t pt-4">
        <div className="flex items-center justify-between w-full text-sm">
          <span className="text-muted-foreground">{getResourceType()}</span>
          <div className="flex items-center gap-1 text-foreground group-hover:translate-x-1 transition-transform">
            <span>Open</span>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </div>
        </div>
      </CardFooter>
    </Card>
  );
};

export default ResourceCard;
