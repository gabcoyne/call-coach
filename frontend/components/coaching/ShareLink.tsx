"use client";

import { useState, useRef, useEffect } from "react";
import {
  Share2,
  Copy,
  Check,
  Mail,
  Twitter,
  Linkedin,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

interface ShareLinkProps {
  callId: string;
  callTitle: string;
}

export function ShareLink({ callId, callTitle }: ShareLinkProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const [shareUrl, setShareUrl] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Build the share URL
    const baseUrl = typeof window !== "undefined" ? window.location.origin : "";
    setShareUrl(`${baseUrl}/calls/${callId}`);
  }, [callId]);

  const handleCopyLink = async () => {
    if (shareUrl) {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleSelectAll = () => {
    if (inputRef.current) {
      inputRef.current.select();
    }
  };

  const createShareUrl = (platform: "email" | "twitter" | "linkedin"): string => {
    const encodedUrl = encodeURIComponent(shareUrl);
    const encodedTitle = encodeURIComponent(
      `Check out this call analysis: "${callTitle}"`
    );

    switch (platform) {
      case "email":
        return `mailto:?subject=Call Analysis: ${encodeURIComponent(callTitle)}&body=Check out this call analysis: ${encodedUrl}`;
      case "twitter":
        return `https://twitter.com/intent/tweet?text=Check out this call analysis: "${callTitle}"&url=${encodedUrl}`;
      case "linkedin":
        return `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`;
      default:
        return "";
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="flex items-center gap-2">
          <Share2 className="h-4 w-4" />
          Share
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Share This Call Analysis</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          {/* Copy Link Section */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-900">
              Call Analysis Link
            </label>
            <div className="flex gap-2">
              <Input
                ref={inputRef}
                readOnly
                value={shareUrl}
                onClick={handleSelectAll}
                className="text-sm"
              />
              <Button
                onClick={handleCopyLink}
                variant="outline"
                size="sm"
                className="flex items-center gap-2"
              >
                {copied ? (
                  <>
                    <Check className="h-4 w-4" />
                    Copied
                  </>
                ) : (
                  <>
                    <Copy className="h-4 w-4" />
                    Copy
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Share Options */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-900">
              Share Via
            </label>
            <div className="grid grid-cols-2 gap-2">
              <a href={createShareUrl("email")} target="_blank" rel="noopener noreferrer">
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full flex items-center justify-center gap-2"
                >
                  <Mail className="h-4 w-4" />
                  Email
                </Button>
              </a>
              <a
                href={createShareUrl("twitter")}
                target="_blank"
                rel="noopener noreferrer"
              >
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full flex items-center justify-center gap-2"
                >
                  <Twitter className="h-4 w-4" />
                  Twitter
                </Button>
              </a>
              <a
                href={createShareUrl("linkedin")}
                target="_blank"
                rel="noopener noreferrer"
              >
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full flex items-center justify-center gap-2"
                >
                  <Linkedin className="h-4 w-4" />
                  LinkedIn
                </Button>
              </a>
            </div>
          </div>

          {/* Info */}
          <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
            <p className="text-xs text-blue-800">
              Anyone with this link can view the call analysis. Make sure this
              is appropriate to share in your organization.
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
