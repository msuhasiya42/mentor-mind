# Quick Reference - New Black & White Theme

## 🚀 Quick Start

### Run the Application

**Backend:**
```bash
cd backend
python main.py
```

**Frontend:**
```bash
cd frontend
npm run dev
```

Open http://localhost:5173

---

## 🎨 Design Tokens

### Colors (Light Mode)

```css
Background: hsl(var(--background))      /* White */
Foreground: hsl(var(--foreground))      /* Black */
Card: hsl(var(--card))                  /* White with border */
Border: hsl(var(--border))              /* Light Gray */
Muted: hsl(var(--muted))                /* Light Gray Background */
Muted Foreground: hsl(var(--muted-foreground)) /* Gray Text */
Primary: hsl(var(--primary))            /* Black */
Secondary: hsl(var(--secondary))        /* Light Gray */
Accent: hsl(var(--accent))              /* Light Gray */
```

### Typography

```jsx
// Hero Title
<h1 className="text-4xl md:text-6xl font-bold">

// Section Title
<h2 className="text-4xl font-bold">

// Subsection Title
<h3 className="text-2xl font-bold">

// Card Title
<CardTitle>   // text-lg font-semibold

// Body Text
<p className="text-base">

// Muted Text
<p className="text-muted-foreground">

// Small Text
<p className="text-sm">
```

### Spacing

```jsx
// Container
<div className="container mx-auto px-4 py-12">

// Card Padding
<Card className="p-6">

// Section Spacing
<div className="space-y-8">

// Grid Gaps
<div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
```

---

## 🧩 shadcn/ui Components

### Button

```jsx
import { Button } from "@/components/ui/button"

// Primary (default)
<Button>Click Me</Button>

// Outlined
<Button variant="outline">Click Me</Button>

// Secondary
<Button variant="secondary">Click Me</Button>

// With Icon
<Button>
  <span className="mr-2">✨</span>
  Generate
</Button>

// Disabled
<Button disabled>Loading...</Button>

// Sizes
<Button size="sm">Small</Button>
<Button size="lg">Large</Button>
```

### Card

```jsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"

<Card>
  <CardHeader>
    <CardTitle>Title Here</CardTitle>
    <CardDescription>Description here</CardDescription>
  </CardHeader>

  <CardContent>
    Content goes here
  </CardContent>

  <CardFooter>
    Footer content
  </CardFooter>
</Card>

// With Hover
<Card className="cursor-pointer transition-all hover:shadow-md hover:-translate-y-1">
```

### Input

```jsx
import { Input } from "@/components/ui/input"

<Input
  type="text"
  placeholder="Enter text..."
  className="h-12"
  disabled={loading}
/>
```

### Badge

```jsx
import { Badge } from "@/components/ui/badge"

// Default
<Badge>New</Badge>

// Secondary
<Badge variant="secondary">Tag</Badge>

// Outline
<Badge variant="outline">Label</Badge>

// Destructive
<Badge variant="destructive">Error</Badge>
```

### Separator

```jsx
import { Separator } from "@/components/ui/separator"

// Horizontal
<Separator />

// Vertical
<Separator orientation="vertical" className="h-6" />
```

---

## 📐 Common Patterns

### Page Layout

```jsx
function Page() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b">
        <div className="container mx-auto px-4 py-6">
          <h2 className="text-2xl font-bold">Site Name</h2>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Your content */}
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t mt-16">
        <div className="container mx-auto px-4 py-8 text-center">
          <p className="text-sm text-muted-foreground">Footer text</p>
        </div>
      </footer>
    </div>
  )
}
```

### Card Grid

```jsx
<div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
  {items.map(item => (
    <Card key={item.id}>
      <CardHeader>
        <CardTitle>{item.title}</CardTitle>
      </CardHeader>
      <CardContent>
        {item.content}
      </CardContent>
    </Card>
  ))}
</div>
```

### Loading State

```jsx
import LoadingSpinner from '../components/LoadingSpinner'

{loading ? (
  <LoadingSpinner />
) : (
  <div>Content here</div>
)}
```

### Empty State

```jsx
<div className="text-center py-16">
  <div className="text-6xl mb-4">📚</div>
  <h2 className="text-2xl font-bold mb-4">No items yet</h2>
  <p className="text-muted-foreground mb-8">Get started by creating one</p>
  <Button>Create First Item</Button>
</div>
```

---

## 🎯 Common Classes

### Backgrounds

```jsx
bg-background          // Main background (white)
bg-card               // Card background (white with border)
bg-secondary          // Secondary background (light gray)
bg-muted              // Muted background (very light gray)
```

### Text Colors

```jsx
text-foreground       // Main text (black)
text-muted-foreground // Muted text (gray)
text-primary          // Primary text (black)
text-secondary-foreground // Secondary text
```

### Borders

```jsx
border                // Border (light gray)
border-b              // Bottom border
border-t              // Top border
border-border         // Using design token
rounded-lg            // Border radius
```

### Hover Effects

```jsx
hover:shadow-md       // Add shadow on hover
hover:-translate-y-1  // Lift on hover
hover:bg-secondary    // Background change
transition-all        // Smooth transitions
```

### Spacing

```jsx
space-y-4             // Vertical spacing (16px)
space-y-8             // Vertical spacing (32px)
gap-6                 // Grid/flex gap (24px)
p-6                   // Padding (24px)
py-12                 // Vertical padding (48px)
```

---

## 🔧 Customization Tips

### Change Border Radius

Edit `frontend/src/index.css`:
```css
:root {
  --radius: 0.625rem;  /* Change to 0.5rem for smaller, 0.75rem for larger */
}
```

### Add Custom Color

```jsx
// For one-off colors
<div className="text-[#333333]">

// For consistent colors, add to index.css
:root {
  --custom-color: oklch(0.5 0 0);
}
```

### Adjust Spacing

```jsx
// Custom padding
<Card className="p-8">  // Instead of default p-6

// Custom gap
<div className="grid gap-8">  // Instead of gap-6
```

---

## 🐛 Troubleshooting

### Components not found

```bash
# Re-install shadcn components
cd frontend
npx shadcn@latest add button card input badge separator
```

### Import errors

Check `vite.config.js` has:
```js
import path from "path"

export default defineConfig({
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
```

### Styles not applying

1. Check `index.css` has shadcn variables
2. Restart dev server: `npm run dev`
3. Clear browser cache

### Dark mode not working

Add to root element:
```jsx
<html className="dark">
```

---

## 📚 Resources

**shadcn/ui Docs:** https://ui.shadcn.com
**Tailwind CSS:** https://tailwindcss.com/docs
**React Router:** https://reactrouter.com

---

## 🎨 Color Reference (OKLCH)

```css
/* Light Mode */
--background: oklch(1 0 0);          /* Pure white */
--foreground: oklch(0.145 0 0);      /* Near black */
--border: oklch(0.922 0 0);          /* Light gray */
--muted: oklch(0.97 0 0);            /* Very light gray */
--muted-foreground: oklch(0.556 0 0);/* Medium gray */

/* Dark Mode */
--background: oklch(0.145 0 0);      /* Near black */
--foreground: oklch(0.985 0 0);      /* Off white */
--border: oklch(1 0 0 / 10%);        /* Translucent white */
--muted: oklch(0.269 0 0);           /* Dark gray */
```

---

## ✨ Pro Tips

1. **Use semantic colors:** Prefer `bg-background` over `bg-white`
2. **Consistent spacing:** Stick to 4, 6, 8, 12 scale
3. **Typography hierarchy:** Use defined sizes for consistency
4. **Hover states:** Always include transitions
5. **Empty states:** Make them friendly and actionable
6. **Loading states:** Keep them minimal and clean
7. **Buttons:** Use `variant="outline"` for secondary actions
8. **Cards:** Add hover effects for clickable cards
9. **Responsive:** Test on mobile sizes
10. **Dark mode:** Keep it simple with CSS variables

---

**Need help?** Check the component files in `frontend/src/components/ui/` for usage examples.
