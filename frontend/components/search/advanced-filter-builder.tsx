"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Plus, X, Zap } from "lucide-react";
import { SearchCallsRequest } from "@/types/coaching";

export type FilterOperator = "and" | "or";
export type FilterCondition = "equals" | "contains" | "greater_than" | "less_than" | "between";
export type FilterField = "score" | "date" | "duration" | "call_type" | "product" | "rep_email";

export interface FilterRule {
  id: string;
  field: FilterField;
  condition: FilterCondition;
  value: string | number | [number, number];
  operator?: FilterOperator;
}

interface AdvancedFilterBuilderProps {
  onApplyFilters: (filters: Partial<SearchCallsRequest>) => void;
  onClose: () => void;
}

const FIELD_OPTIONS: Array<{ value: FilterField; label: string }> = [
  { value: "score", label: "Overall Score" },
  { value: "date", label: "Call Date" },
  { value: "duration", label: "Duration" },
  { value: "call_type", label: "Call Type" },
  { value: "product", label: "Product" },
  { value: "rep_email", label: "Rep Email" },
];

const CONDITION_OPTIONS: Record<FilterField, Array<{ value: FilterCondition; label: string }>> =
  {
    score: [
      { value: "equals", label: "Equals" },
      { value: "greater_than", label: "Greater than" },
      { value: "less_than", label: "Less than" },
      { value: "between", label: "Between" },
    ],
    date: [
      { value: "equals", label: "On" },
      { value: "greater_than", label: "After" },
      { value: "less_than", label: "Before" },
      { value: "between", label: "Between" },
    ],
    duration: [
      { value: "equals", label: "Equals" },
      { value: "greater_than", label: "Longer than" },
      { value: "less_than", label: "Shorter than" },
    ],
    call_type: [{ value: "equals", label: "Is" }],
    product: [{ value: "equals", label: "Is" }],
    rep_email: [{ value: "contains", label: "Contains" }],
  };

export function AdvancedFilterBuilder({
  onApplyFilters,
  onClose,
}: AdvancedFilterBuilderProps) {
  const [rules, setRules] = useState<FilterRule[]>([
    { id: "1", field: "score", condition: "greater_than", value: 0 },
  ]);
  const [logicOperator, setLogicOperator] = useState<FilterOperator>("and");

  const addRule = () => {
    const newRule: FilterRule = {
      id: Date.now().toString(),
      field: "score",
      condition: "greater_than",
      value: 0,
    };
    setRules([...rules, newRule]);
  };

  const removeRule = (id: string) => {
    if (rules.length > 1) {
      setRules(rules.filter((r) => r.id !== id));
    }
  };

  const updateRule = (
    id: string,
    field: Partial<FilterRule>
  ) => {
    setRules(
      rules.map((r) =>
        r.id === id
          ? { ...r, ...field }
          : r
      )
    );
  };

  const convertRulesToFilters = (): Partial<SearchCallsRequest> => {
    const filters: Partial<SearchCallsRequest> = {};

    for (const rule of rules) {
      switch (rule.field) {
        case "score":
          if (rule.condition === "greater_than" && typeof rule.value === "number") {
            filters.min_score = rule.value;
          } else if (rule.condition === "less_than" && typeof rule.value === "number") {
            filters.max_score = rule.value;
          } else if (rule.condition === "between" && Array.isArray(rule.value)) {
            filters.min_score = rule.value[0];
            filters.max_score = rule.value[1];
          }
          break;

        case "date":
          if (Array.isArray(rule.value)) {
            filters.date_range = {
              start: rule.value[0] as unknown as string,
              end: rule.value[1] as unknown as string,
            };
          }
          break;

        case "call_type":
          if (typeof rule.value === "string") {
            filters.call_type = rule.value as "discovery" | "demo" | "technical_deep_dive" | "negotiation";
          }
          break;

        case "product":
          if (typeof rule.value === "string") {
            filters.product = rule.value as "prefect" | "horizon" | "both";
          }
          break;

        case "rep_email":
          if (typeof rule.value === "string") {
            filters.rep_email = rule.value;
          }
          break;
      }
    }

    return filters;
  };

  const handleApply = () => {
    const filters = convertRulesToFilters();
    onApplyFilters(filters);
    onClose();
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Zap className="h-5 w-5" />
          Advanced Filter Builder
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Logic Operator Selection */}
        {rules.length > 1 && (
          <div className="space-y-2">
            <Label>Combine conditions with:</Label>
            <div className="flex gap-2">
              <Badge
                variant={logicOperator === "and" ? "default" : "outline"}
                className="cursor-pointer px-4 py-2"
                onClick={() => setLogicOperator("and")}
              >
                AND (all conditions must match)
              </Badge>
              <Badge
                variant={logicOperator === "or" ? "default" : "outline"}
                className="cursor-pointer px-4 py-2"
                onClick={() => setLogicOperator("or")}
              >
                OR (any condition can match)
              </Badge>
            </div>
          </div>
        )}

        {/* Filter Rules */}
        <div className="space-y-4">
          {rules.map((rule, index) => (
            <div key={rule.id} className="space-y-3">
              {index > 0 && (
                <div className="flex items-center gap-2 px-4 py-2 bg-muted rounded-md">
                  <Badge variant="secondary">{logicOperator.toUpperCase()}</Badge>
                </div>
              )}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-3 p-4 border rounded-lg bg-card">
                {/* Field Selection */}
                <div className="space-y-2">
                  <Label htmlFor={`field-${rule.id}`} className="text-xs">
                    Field
                  </Label>
                  <Select
                    value={rule.field}
                    onValueChange={(value) =>
                      updateRule(rule.id, {
                        field: value as FilterField,
                        condition: CONDITION_OPTIONS[value as FilterField][0]
                          .value,
                      })
                    }
                  >
                    <SelectTrigger id={`field-${rule.id}`} className="text-xs">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {FIELD_OPTIONS.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Condition Selection */}
                <div className="space-y-2">
                  <Label htmlFor={`condition-${rule.id}`} className="text-xs">
                    Condition
                  </Label>
                  <Select
                    value={rule.condition}
                    onValueChange={(value) =>
                      updateRule(rule.id, { condition: value as FilterCondition })
                    }
                  >
                    <SelectTrigger id={`condition-${rule.id}`} className="text-xs">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {CONDITION_OPTIONS[rule.field].map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Value Input(s) */}
                <div className="space-y-2 md:col-span-1">
                  <Label htmlFor={`value-${rule.id}`} className="text-xs">
                    Value
                  </Label>
                  {rule.field === "call_type" ? (
                    <Select
                      value={typeof rule.value === "string" ? rule.value : ""}
                      onValueChange={(value) => updateRule(rule.id, { value })}
                    >
                      <SelectTrigger id={`value-${rule.id}`} className="text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="discovery">Discovery</SelectItem>
                        <SelectItem value="demo">Demo</SelectItem>
                        <SelectItem value="technical_deep_dive">
                          Technical Deep Dive
                        </SelectItem>
                        <SelectItem value="negotiation">Negotiation</SelectItem>
                      </SelectContent>
                    </Select>
                  ) : rule.field === "product" ? (
                    <Select
                      value={typeof rule.value === "string" ? rule.value : ""}
                      onValueChange={(value) => updateRule(rule.id, { value })}
                    >
                      <SelectTrigger id={`value-${rule.id}`} className="text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="prefect">Prefect</SelectItem>
                        <SelectItem value="horizon">Horizon</SelectItem>
                        <SelectItem value="both">Both</SelectItem>
                      </SelectContent>
                    </Select>
                  ) : (
                    <Input
                      id={`value-${rule.id}`}
                      type={
                        rule.field === "date"
                          ? "date"
                          : rule.field === "score" || rule.field === "duration"
                            ? "number"
                            : "text"
                      }
                      value={
                        typeof rule.value === "number"
                          ? rule.value.toString()
                          : Array.isArray(rule.value)
                            ? ""
                            : rule.value
                      }
                      onChange={(e) =>
                        updateRule(rule.id, {
                          value:
                            rule.field === "score" || rule.field === "duration"
                              ? Number(e.target.value)
                              : e.target.value,
                        })
                      }
                      className="text-xs"
                      placeholder="Enter value"
                    />
                  )}
                </div>

                {/* Remove Button */}
                <div className="flex items-end">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeRule(rule.id)}
                    disabled={rules.length === 1}
                    className="w-full"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Add Rule Button */}
        <Button
          variant="outline"
          onClick={addRule}
          className="w-full gap-2"
        >
          <Plus className="h-4 w-4" />
          Add Another Condition
        </Button>

        {/* Action Buttons */}
        <div className="flex gap-2 justify-end pt-4 border-t">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleApply}>
            Apply Filters
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
