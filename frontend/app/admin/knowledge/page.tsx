"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/use-toast";
import { Loader2, Upload, Download, History, Plus, Trash2, Save } from "lucide-react";

interface KnowledgeEntry {
  id: string;
  product: string;
  category: string;
  content: string;
  metadata: any;
  last_updated: string;
}

interface Rubric {
  id: string;
  name: string;
  version: string;
  category: string;
  criteria: any;
  scoring_guide: any;
  examples: any;
  active: boolean;
  created_at: string;
  deprecated_at?: string;
}

export default function KnowledgeManagementPage() {
  const [entries, setEntries] = useState<KnowledgeEntry[]>([]);
  const [rubrics, setRubrics] = useState<Rubric[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  // Form states
  const [selectedProduct, setSelectedProduct] = useState<string>("prefect");
  const [selectedCategory, setSelectedCategory] = useState<string>("feature");
  const [content, setContent] = useState<string>("");
  const [editingEntry, setEditingEntry] = useState<KnowledgeEntry | null>(null);

  // Rubric form states
  const [rubricName, setRubricName] = useState<string>("");
  const [rubricVersion, setRubricVersion] = useState<string>("");
  const [rubricCategory, setRubricCategory] = useState<string>("product_knowledge");
  const [rubricCriteria, setRubricCriteria] = useState<string>("");
  const [rubricScoringGuide, setRubricScoringGuide] = useState<string>("");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [entriesRes, rubricsRes] = await Promise.all([
        fetch("/api/knowledge"),
        fetch("/api/knowledge/rubrics"),
      ]);

      if (entriesRes.ok) {
        const entriesData = await entriesRes.json();
        setEntries(entriesData);
      }

      if (rubricsRes.ok) {
        const rubricsData = await rubricsRes.json();
        setRubrics(rubricsData);
      }
    } catch (error) {
      console.error("Error loading data:", error);
      toast({
        title: "Error",
        description: "Failed to load knowledge base data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSaveEntry = async () => {
    if (!content.trim()) {
      toast({
        title: "Validation Error",
        description: "Content cannot be empty",
        variant: "destructive",
      });
      return;
    }

    setSaving(true);
    try {
      const response = await fetch("/api/knowledge", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          product: selectedProduct,
          category: selectedCategory,
          content: content,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to save entry");
      }

      toast({
        title: "Success",
        description: "Knowledge entry saved successfully",
      });

      setContent("");
      setEditingEntry(null);
      loadData();
    } catch (error) {
      console.error("Error saving entry:", error);
      toast({
        title: "Error",
        description: "Failed to save knowledge entry",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteEntry = async (product: string, category: string) => {
    if (!confirm("Are you sure you want to delete this entry?")) {
      return;
    }

    try {
      const response = await fetch(
        `/api/knowledge?product=${product}&category=${category}`,
        { method: "DELETE" }
      );

      if (!response.ok) {
        throw new Error("Failed to delete entry");
      }

      toast({
        title: "Success",
        description: "Knowledge entry deleted successfully",
      });

      loadData();
    } catch (error) {
      console.error("Error deleting entry:", error);
      toast({
        title: "Error",
        description: "Failed to delete knowledge entry",
        variant: "destructive",
      });
    }
  };

  const handleSaveRubric = async () => {
    if (!rubricName || !rubricVersion || !rubricCriteria || !rubricScoringGuide) {
      toast({
        title: "Validation Error",
        description: "All rubric fields are required",
        variant: "destructive",
      });
      return;
    }

    setSaving(true);
    try {
      let criteria, scoringGuide;
      try {
        criteria = JSON.parse(rubricCriteria);
        scoringGuide = JSON.parse(rubricScoringGuide);
      } catch (e) {
        throw new Error("Criteria and Scoring Guide must be valid JSON");
      }

      const response = await fetch("/api/knowledge/rubrics", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: rubricName,
          version: rubricVersion,
          category: rubricCategory,
          criteria: criteria,
          scoring_guide: scoringGuide,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || "Failed to save rubric");
      }

      toast({
        title: "Success",
        description: "Coaching rubric saved successfully",
      });

      setRubricName("");
      setRubricVersion("");
      setRubricCriteria("");
      setRubricScoringGuide("");
      loadData();
    } catch (error) {
      console.error("Error saving rubric:", error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to save rubric",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const loadEntry = (entry: KnowledgeEntry) => {
    setSelectedProduct(entry.product);
    setSelectedCategory(entry.category);
    setContent(entry.content);
    setEditingEntry(entry);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Knowledge Base Management</h1>
        <p className="text-muted-foreground">
          Manage product documentation, coaching rubrics, and competitive intelligence
        </p>
      </div>

      <Tabs defaultValue="entries" className="space-y-6">
        <TabsList>
          <TabsTrigger value="entries">Product Knowledge</TabsTrigger>
          <TabsTrigger value="rubrics">Coaching Rubrics</TabsTrigger>
          <TabsTrigger value="stats">Statistics</TabsTrigger>
        </TabsList>

        <TabsContent value="entries" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>
                  {editingEntry ? "Edit Entry" : "Create New Entry"}
                </CardTitle>
                <CardDescription>
                  Add or update product documentation
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Product</Label>
                  <Select value={selectedProduct} onValueChange={setSelectedProduct}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="prefect">Prefect</SelectItem>
                      <SelectItem value="horizon">Horizon</SelectItem>
                      <SelectItem value="both">Both</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Category</Label>
                  <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="feature">Feature</SelectItem>
                      <SelectItem value="differentiation">Differentiation</SelectItem>
                      <SelectItem value="use_case">Use Case</SelectItem>
                      <SelectItem value="pricing">Pricing</SelectItem>
                      <SelectItem value="competitor">Competitor</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Content (Markdown)</Label>
                  <Textarea
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    placeholder="Enter markdown content..."
                    className="min-h-[300px] font-mono text-sm"
                  />
                </div>

                <div className="flex gap-2">
                  <Button onClick={handleSaveEntry} disabled={saving}>
                    {saving ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="w-4 h-4 mr-2" />
                        Save Entry
                      </>
                    )}
                  </Button>
                  {editingEntry && (
                    <Button
                      variant="outline"
                      onClick={() => {
                        setEditingEntry(null);
                        setContent("");
                      }}
                    >
                      Cancel
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Existing Entries</CardTitle>
                <CardDescription>
                  {entries.length} knowledge base entries
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-[500px] overflow-y-auto">
                  {entries.map((entry) => (
                    <div
                      key={entry.id}
                      className="p-3 border rounded-lg hover:bg-accent cursor-pointer"
                      onClick={() => loadEntry(entry)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <Badge variant="outline">{entry.product}</Badge>
                            <Badge variant="secondary">{entry.category}</Badge>
                          </div>
                          <p className="text-sm text-muted-foreground mt-1">
                            Version {entry.metadata?.version || 1} •{" "}
                            {new Date(entry.last_updated).toLocaleDateString()}
                          </p>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteEntry(entry.product, entry.category);
                          }}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="rubrics" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Create New Rubric</CardTitle>
                <CardDescription>
                  Add a new version of a coaching rubric
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Name</Label>
                  <Input
                    value={rubricName}
                    onChange={(e) => setRubricName(e.target.value)}
                    placeholder="e.g., Product Knowledge Rubric"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Version</Label>
                  <Input
                    value={rubricVersion}
                    onChange={(e) => setRubricVersion(e.target.value)}
                    placeholder="e.g., 1.0.0"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Category</Label>
                  <Select value={rubricCategory} onValueChange={setRubricCategory}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="product_knowledge">Product Knowledge</SelectItem>
                      <SelectItem value="discovery">Discovery</SelectItem>
                      <SelectItem value="objection_handling">Objection Handling</SelectItem>
                      <SelectItem value="engagement">Engagement</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Criteria (JSON)</Label>
                  <Textarea
                    value={rubricCriteria}
                    onChange={(e) => setRubricCriteria(e.target.value)}
                    placeholder='{"technical_depth": "...", "accuracy": "..."}'
                    className="min-h-[150px] font-mono text-sm"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Scoring Guide (JSON)</Label>
                  <Textarea
                    value={rubricScoringGuide}
                    onChange={(e) => setRubricScoringGuide(e.target.value)}
                    placeholder='{"0-30": "Poor", "31-70": "Good", "71-100": "Excellent"}'
                    className="min-h-[150px] font-mono text-sm"
                  />
                </div>

                <Button onClick={handleSaveRubric} disabled={saving} className="w-full">
                  {saving ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Plus className="w-4 h-4 mr-2" />
                      Create Rubric
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Existing Rubrics</CardTitle>
                <CardDescription>{rubrics.length} coaching rubrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-[600px] overflow-y-auto">
                  {rubrics.map((rubric) => (
                    <div key={rubric.id} className="p-3 border rounded-lg">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <h4 className="font-medium">{rubric.name}</h4>
                            {rubric.active && (
                              <Badge variant="default">Active</Badge>
                            )}
                            {rubric.deprecated_at && (
                              <Badge variant="secondary">Deprecated</Badge>
                            )}
                          </div>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge variant="outline">{rubric.category}</Badge>
                            <span className="text-sm text-muted-foreground">
                              v{rubric.version}
                            </span>
                          </div>
                          <p className="text-xs text-muted-foreground mt-1">
                            Created {new Date(rubric.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="stats">
          <Card>
            <CardHeader>
              <CardTitle>Knowledge Base Statistics</CardTitle>
              <CardDescription>Overview of content and versions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="p-4 border rounded-lg">
                  <div className="text-2xl font-bold">{entries.length}</div>
                  <p className="text-sm text-muted-foreground">Knowledge Entries</p>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="text-2xl font-bold">
                    {rubrics.filter((r) => r.active).length}
                  </div>
                  <p className="text-sm text-muted-foreground">Active Rubrics</p>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="text-2xl font-bold">{rubrics.length}</div>
                  <p className="text-sm text-muted-foreground">Total Rubric Versions</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
