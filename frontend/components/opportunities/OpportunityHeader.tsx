/**
 * OpportunityHeader Component
 *
 * Displays opportunity metadata with color-coded health indicator.
 */
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Calendar,
  DollarSign,
  Mail,
  Phone,
  TrendingDown,
  TrendingUp,
  User,
  Building,
  Activity,
} from "lucide-react";

interface Opportunity {
  id: string;
  name: string;
  account_name: string;
  owner_email: string;
  stage: string;
  close_date: string;
  amount: number;
  health_score: number;
  call_count: number;
  email_count: number;
  updated_at: string;
}

interface OpportunityHeaderProps {
  opportunity: Opportunity;
}

export function OpportunityHeader({ opportunity }: OpportunityHeaderProps) {
  // Health score color logic
  const getHealthColor = (score: number) => {
    if (score >= 70) return "success"; // Green
    if (score >= 40) return "warning"; // Yellow/Amber
    return "destructive"; // Red
  };

  const getHealthIcon = (score: number) => {
    if (score >= 70)
      return <TrendingUp className="h-5 w-5 text-green-500" />;
    if (score >= 40) return <Activity className="h-5 w-5 text-yellow-500" />;
    return <TrendingDown className="h-5 w-5 text-red-500" />;
  };

  const healthColor = getHealthColor(opportunity.health_score);
  const healthIcon = getHealthIcon(opportunity.health_score);

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="space-y-6">
          {/* Title and Health */}
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-foreground">
                {opportunity.name}
              </h1>
              <div className="flex items-center gap-2 mt-2 text-muted-foreground">
                <Building className="h-4 w-4" />
                <span className="text-lg">{opportunity.account_name}</span>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {healthIcon}
              <div className="text-right">
                <div className="text-xs text-muted-foreground uppercase">
                  Health Score
                </div>
                <Badge
                  variant={healthColor}
                  className="text-lg px-4 py-1 mt-1"
                >
                  {opportunity.health_score}
                </Badge>
              </div>
            </div>
          </div>

          {/* Metadata Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Owner */}
            <div className="flex items-center gap-3 p-4 rounded-lg bg-muted/50">
              <div className="p-2 rounded-full bg-primary/10">
                <User className="h-5 w-5 text-primary" />
              </div>
              <div>
                <div className="text-xs text-muted-foreground">Owner</div>
                <div className="font-medium">{opportunity.owner_email}</div>
              </div>
            </div>

            {/* Stage */}
            <div className="flex items-center gap-3 p-4 rounded-lg bg-muted/50">
              <div className="p-2 rounded-full bg-primary/10">
                <Activity className="h-5 w-5 text-primary" />
              </div>
              <div>
                <div className="text-xs text-muted-foreground">Stage</div>
                <div className="font-medium">
                  <Badge variant="outline">{opportunity.stage}</Badge>
                </div>
              </div>
            </div>

            {/* Close Date */}
            <div className="flex items-center gap-3 p-4 rounded-lg bg-muted/50">
              <div className="p-2 rounded-full bg-primary/10">
                <Calendar className="h-5 w-5 text-primary" />
              </div>
              <div>
                <div className="text-xs text-muted-foreground">Close Date</div>
                <div className="font-medium">
                  {new Date(opportunity.close_date).toLocaleDateString(
                    "en-US",
                    {
                      month: "short",
                      day: "numeric",
                      year: "numeric",
                    }
                  )}
                </div>
              </div>
            </div>

            {/* Amount */}
            <div className="flex items-center gap-3 p-4 rounded-lg bg-muted/50">
              <div className="p-2 rounded-full bg-primary/10">
                <DollarSign className="h-5 w-5 text-primary" />
              </div>
              <div>
                <div className="text-xs text-muted-foreground">Amount</div>
                <div className="font-medium text-lg">
                  ${opportunity.amount.toLocaleString()}
                </div>
              </div>
            </div>
          </div>

          {/* Activity Summary */}
          <div className="flex items-center gap-6 p-4 rounded-lg bg-muted/50">
            <div className="flex items-center gap-2">
              <Phone className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">
                <span className="font-semibold">{opportunity.call_count}</span>{" "}
                calls
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Mail className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">
                <span className="font-semibold">{opportunity.email_count}</span>{" "}
                emails
              </span>
            </div>
            <div className="text-sm text-muted-foreground ml-auto">
              Last updated:{" "}
              {new Date(opportunity.updated_at).toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
                year: "numeric",
              })}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
