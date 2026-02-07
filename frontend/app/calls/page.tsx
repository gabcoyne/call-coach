"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Search, Filter, Calendar, Users, Clock } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { ScoreBadge } from "@/components/ui/score-badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Call {
  call_id: string;
  title: string;
  date: string | null;
  duration_seconds: number;
  call_type: string | null;
  product: string | null;
  overall_score: number | null;
  customer_names: string[];
  prefect_reps: string[];
}

export default function CallsPage() {
  const router = useRouter();
  const [calls, setCalls] = useState<Call[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [callTypeFilter, setCallTypeFilter] = useState<string>("all");
  const [productFilter, setProductFilter] = useState<string>("all");

  // Mock data for initial display - replace with actual API call
  const mockCalls: Call[] = [];

  // Load calls on component mount
  useEffect(() => {
    handleSearch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const formatDuration = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    return `${minutes}m`;
  };

  const formatDate = (dateString: string | null): string => {
    if (!dateString) return "N/A";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const getCallTypeBadgeColor = (type: string | null): string => {
    if (!type) return "secondary";
    const colors: Record<string, string> = {
      discovery: "blue",
      demo: "purple",
      negotiation: "orange",
      technical_deep_dive: "green",
      follow_up: "gray",
      executive_briefing: "red",
    };
    return colors[type] || "secondary";
  };

  const handleSearch = async () => {
    setIsLoading(true);
    try {
      const requestBody: Record<string, any> = {
        limit: 20,
        offset: 0,
      };

      if (searchQuery) {
        // Search query can filter by title, so we'll need to enhance the backend
        // For now, we'll just search without text filtering
      }
      if (callTypeFilter !== "all") requestBody.call_type = callTypeFilter;
      if (productFilter !== "all") requestBody.product = productFilter;

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_MCP_BACKEND_URL}/api/v1/tools/search_calls`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(requestBody),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setCalls(result.data.items);
    } catch (error) {
      console.error("Failed to search calls:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const displayedCalls = calls.length > 0 ? calls : mockCalls;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Call Library</h1>
        <p className="text-muted-foreground mt-1">Browse and analyze sales calls</p>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Search & Filter
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-4">
            {/* Search Input */}
            <div className="md:col-span-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search by title, customer, or rep..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                  className="pl-9"
                />
              </div>
            </div>

            {/* Call Type Filter */}
            <Select value={callTypeFilter} onValueChange={setCallTypeFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Call Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="discovery">Discovery</SelectItem>
                <SelectItem value="demo">Demo</SelectItem>
                <SelectItem value="negotiation">Negotiation</SelectItem>
                <SelectItem value="technical_deep_dive">Technical Deep Dive</SelectItem>
                <SelectItem value="follow_up">Follow Up</SelectItem>
                <SelectItem value="executive_briefing">Executive Briefing</SelectItem>
              </SelectContent>
            </Select>

            {/* Product Filter */}
            <Select value={productFilter} onValueChange={setProductFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Product" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Products</SelectItem>
                <SelectItem value="prefect">Prefect</SelectItem>
                <SelectItem value="horizon">Horizon</SelectItem>
                <SelectItem value="both">Both</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex gap-2">
            <Button onClick={handleSearch} disabled={isLoading}>
              <Search className="h-4 w-4 mr-2" />
              Search
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setSearchQuery("");
                setCallTypeFilter("all");
                setProductFilter("all");
                setCalls([]);
              }}
            >
              Clear Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Calls Table */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-6 space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex gap-4">
                  <Skeleton className="h-12 flex-1" />
                  <Skeleton className="h-12 w-24" />
                  <Skeleton className="h-12 w-24" />
                </div>
              ))}
            </div>
          ) : displayedCalls.length === 0 ? (
            <div className="p-12 text-center">
              <Calendar className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No calls found</h3>
              <p className="text-sm text-muted-foreground">
                Try adjusting your search filters or search for calls using the form above.
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Call Title</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Duration</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Product</TableHead>
                  <TableHead>Score</TableHead>
                  <TableHead>Reps</TableHead>
                  <TableHead>Customers</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {displayedCalls.map((call) => (
                  <TableRow
                    key={call.call_id}
                    className="cursor-pointer hover:bg-muted/50"
                    onClick={() => router.push(`/calls/${call.call_id}`)}
                  >
                    <TableCell className="font-medium max-w-xs truncate">{call.title}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {formatDate(call.date)}
                      </div>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatDuration(call.duration_seconds)}
                      </div>
                    </TableCell>
                    <TableCell>
                      {call.call_type && (
                        <Badge variant="outline">{call.call_type.replace(/_/g, " ")}</Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      {call.product && <Badge variant="secondary">{call.product}</Badge>}
                    </TableCell>
                    <TableCell>
                      {call.overall_score !== null && <ScoreBadge score={call.overall_score} />}
                    </TableCell>
                    <TableCell className="text-sm">
                      <div className="flex items-center gap-1 max-w-xs truncate">
                        <Users className="h-3 w-3 flex-shrink-0" />
                        <span className="truncate">{call.prefect_reps.join(", ") || "N/A"}</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-sm max-w-xs truncate">
                      {call.customer_names.join(", ") || "N/A"}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Stats Footer */}
      {displayedCalls.length > 0 && (
        <div className="text-sm text-muted-foreground text-center">
          Showing {displayedCalls.length} calls
        </div>
      )}
    </div>
  );
}
