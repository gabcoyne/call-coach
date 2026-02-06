"use client";

import { useState } from "react";
import { ThumbsUp, ThumbsDown, MessageSquare, Check, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { cn } from "@/lib/utils";

type FeedbackType =
  | "accurate"
  | "inaccurate"
  | "missing_context"
  | "helpful"
  | "not_helpful";

interface FeedbackButtonProps {
  coachingSessionId: string;
  onFeedbackSubmitted?: () => void;
}

export function FeedbackButton({
  coachingSessionId,
  onFeedbackSubmitted,
}: FeedbackButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedType, setSelectedType] = useState<FeedbackType | null>(null);
  const [comment, setComment] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async () => {
    if (!selectedType) return;

    setIsSubmitting(true);
    try {
      const response = await fetch(
        `/api/coaching-sessions/${coachingSessionId}/feedback`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            feedback_type: selectedType,
            feedback_text: comment || null,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to submit feedback");
      }

      setSubmitted(true);
      setTimeout(() => {
        setIsOpen(false);
        setSelectedType(null);
        setComment("");
        setSubmitted(false);
        onFeedbackSubmitted?.();
      }, 1500);
    } catch (error) {
      console.error("Error submitting feedback:", error);
      alert("Failed to submit feedback. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <div className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            setSelectedType("helpful");
            setIsOpen(true);
          }}
          className="gap-2"
          title="This coaching feedback was helpful"
        >
          <ThumbsUp className="h-4 w-4" />
          Helpful
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            setSelectedType("not_helpful");
            setIsOpen(true);
          }}
          className="gap-2"
          title="This coaching feedback was not helpful"
        >
          <ThumbsDown className="h-4 w-4" />
          Not Helpful
        </Button>
      </div>

      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Provide Feedback on Coaching Analysis</DialogTitle>
            <DialogDescription>
              Help us improve our coaching by sharing your feedback
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            {/* Accuracy Feedback */}
            <div className="space-y-2">
              <label className="text-sm font-medium">
                How accurate was this analysis?
              </label>
              <div className="flex gap-2">
                <Button
                  variant={selectedType === "accurate" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSelectedType("accurate")}
                  className="flex-1 gap-2"
                >
                  <Check className="h-4 w-4" />
                  Accurate
                </Button>
                <Button
                  variant={selectedType === "inaccurate" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSelectedType("inaccurate")}
                  className="flex-1 gap-2"
                >
                  <X className="h-4 w-4" />
                  Inaccurate
                </Button>
                <Button
                  variant={
                    selectedType === "missing_context" ? "default" : "outline"
                  }
                  size="sm"
                  onClick={() => setSelectedType("missing_context")}
                  className="flex-1 gap-2"
                >
                  <MessageSquare className="h-4 w-4" />
                  Missing Context
                </Button>
              </div>
            </div>

            {/* Helpfulness */}
            <div className="space-y-2">
              <label className="text-sm font-medium">
                Was this feedback helpful?
              </label>
              <div className="flex gap-2">
                <Button
                  variant={selectedType === "helpful" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSelectedType("helpful")}
                  className="flex-1 gap-2"
                >
                  <ThumbsUp className="h-4 w-4" />
                  Helpful
                </Button>
                <Button
                  variant={
                    selectedType === "not_helpful" ? "default" : "outline"
                  }
                  size="sm"
                  onClick={() => setSelectedType("not_helpful")}
                  className="flex-1 gap-2"
                >
                  <ThumbsDown className="h-4 w-4" />
                  Not Helpful
                </Button>
              </div>
            </div>

            {/* Comment */}
            <div className="space-y-2">
              <label htmlFor="feedback-comment" className="text-sm font-medium">
                Additional Comments (Optional)
              </label>
              <Textarea
                id="feedback-comment"
                placeholder="Tell us more about your feedback..."
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                className="resize-none"
                rows={4}
              />
              <p className="text-xs text-muted-foreground">
                {comment.length}/1000
              </p>
            </div>

            {/* Submit Button */}
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => setIsOpen(false)}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
              <Button
                onClick={handleSubmit}
                disabled={!selectedType || isSubmitting}
              >
                {isSubmitting ? "Submitting..." : "Submit Feedback"}
              </Button>
            </div>

            {/* Success Message */}
            {submitted && (
              <div className="rounded-lg bg-green-50 p-3 text-sm text-green-800">
                ✓ Thank you! Your feedback has been recorded.
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
