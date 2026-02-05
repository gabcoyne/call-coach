import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";

export default function DesignSystemPage() {
  return (
    <div className="container mx-auto p-8 space-y-12">
      <div>
        <h1 className="text-4xl font-bold mb-2">Prefect Design System</h1>
        <p className="text-muted-foreground">
          Component showcase for Gong Call Coaching frontend
        </p>
      </div>

      {/* Colors */}
      <section>
        <h2 className="text-2xl font-semibold mb-4">Brand Colors</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="h-24 bg-prefect-pink rounded-lg mb-2" />
            <p className="text-sm font-medium">Prefect Pink</p>
            <p className="text-xs text-muted-foreground">#FF4BBD</p>
          </div>
          <div>
            <div className="h-24 bg-prefect-sunrise1 rounded-lg mb-2" />
            <p className="text-sm font-medium">Sunrise 1</p>
            <p className="text-xs text-muted-foreground">#FE9655</p>
          </div>
          <div>
            <div className="h-24 bg-prefect-sunrise2 rounded-lg mb-2" />
            <p className="text-sm font-medium">Sunrise 2</p>
            <p className="text-xs text-muted-foreground">#FEB255</p>
          </div>
          <div>
            <div className="h-24 bg-prefect-blue-500 rounded-lg mb-2" />
            <p className="text-sm font-medium">Blue</p>
            <p className="text-xs text-muted-foreground">#1A94FF</p>
          </div>
        </div>
      </section>

      {/* Buttons */}
      <section>
        <h2 className="text-2xl font-semibold mb-4">Buttons</h2>
        <div className="flex flex-wrap gap-4">
          <Button>Default</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="destructive">Destructive</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="link">Link</Button>
          <Button variant="prefect">Prefect</Button>
          <Button variant="sunrise">Sunrise</Button>
          <Button variant="gradient">Gradient</Button>
        </div>
        <div className="flex flex-wrap gap-4 mt-4">
          <Button size="sm">Small</Button>
          <Button size="default">Default</Button>
          <Button size="lg">Large</Button>
          <Button size="icon">+</Button>
        </div>
      </section>

      {/* Badges */}
      <section>
        <h2 className="text-2xl font-semibold mb-4">Badges</h2>
        <div className="flex flex-wrap gap-2">
          <Badge>Default</Badge>
          <Badge variant="secondary">Secondary</Badge>
          <Badge variant="destructive">Destructive</Badge>
          <Badge variant="outline">Outline</Badge>
          <Badge variant="success">Success</Badge>
          <Badge variant="warning">Warning</Badge>
          <Badge variant="info">Info</Badge>
          <Badge variant="prefect">Prefect</Badge>
          <Badge variant="sunrise">Sunrise</Badge>
        </div>
      </section>

      {/* Cards */}
      <section>
        <h2 className="text-2xl font-semibold mb-4">Cards</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Call Analysis</CardTitle>
              <CardDescription>
                Review your sales call performance
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                This is a sample card showing how content looks within the
                Prefect design system.
              </p>
            </CardContent>
            <CardFooter>
              <Button variant="prefect">View Details</Button>
            </CardFooter>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Performance Metrics</CardTitle>
              <CardDescription>Track your improvement over time</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm">Overall Score</span>
                  <Badge variant="success">92%</Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Calls This Week</span>
                  <Badge variant="info">12</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Form Elements */}
      <section>
        <h2 className="text-2xl font-semibold mb-4">Form Elements</h2>
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle>Sample Form</CardTitle>
            <CardDescription>Input fields and select components</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input id="name" placeholder="Enter your name" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" placeholder="email@example.com" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="role">Role</Label>
              <Select>
                <SelectTrigger id="role">
                  <SelectValue placeholder="Select a role" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="manager">Sales Manager</SelectItem>
                  <SelectItem value="rep">Sales Rep</SelectItem>
                  <SelectItem value="admin">Admin</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
          <CardFooter>
            <Button variant="gradient" className="w-full">
              Submit
            </Button>
          </CardFooter>
        </Card>
      </section>

      {/* Typography */}
      <section>
        <h2 className="text-2xl font-semibold mb-4">Typography</h2>
        <div className="space-y-4">
          <div>
            <h1 className="text-4xl font-bold">Heading 1</h1>
            <h2 className="text-3xl font-bold">Heading 2</h2>
            <h3 className="text-2xl font-semibold">Heading 3</h3>
            <h4 className="text-xl font-semibold">Heading 4</h4>
            <h5 className="text-lg font-medium">Heading 5</h5>
            <h6 className="text-base font-medium">Heading 6</h6>
          </div>
          <div>
            <p className="text-base">
              This is body text using the default font size and weight.
            </p>
            <p className="text-sm text-muted-foreground">
              This is small text, often used for secondary information.
            </p>
            <p className="text-xs text-muted-foreground">
              This is extra small text for captions and labels.
            </p>
          </div>
        </div>
      </section>

      {/* Spacing */}
      <section>
        <h2 className="text-2xl font-semibold mb-4">Spacing Scale</h2>
        <div className="space-y-2">
          <div className="flex items-center gap-4">
            <div className="w-16 text-sm text-muted-foreground">2px</div>
            <div className="h-4 w-0.5 bg-prefect-pink" />
          </div>
          <div className="flex items-center gap-4">
            <div className="w-16 text-sm text-muted-foreground">4px</div>
            <div className="h-4 w-1 bg-prefect-pink" />
          </div>
          <div className="flex items-center gap-4">
            <div className="w-16 text-sm text-muted-foreground">8px</div>
            <div className="h-4 w-2 bg-prefect-pink" />
          </div>
          <div className="flex items-center gap-4">
            <div className="w-16 text-sm text-muted-foreground">16px</div>
            <div className="h-4 w-4 bg-prefect-pink" />
          </div>
          <div className="flex items-center gap-4">
            <div className="w-16 text-sm text-muted-foreground">24px</div>
            <div className="h-4 w-6 bg-prefect-pink" />
          </div>
          <div className="flex items-center gap-4">
            <div className="w-16 text-sm text-muted-foreground">32px</div>
            <div className="h-4 w-8 bg-prefect-pink" />
          </div>
        </div>
      </section>
    </div>
  );
}
