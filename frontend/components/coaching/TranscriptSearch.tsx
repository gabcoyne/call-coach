"use client";

import { useState, useMemo, useEffect, useRef } from "react";
import { Search, ChevronDown, ChevronUp } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import type { TranscriptSegment } from "@/types/coaching";

interface TranscriptSearchProps {
  transcript: TranscriptSegment[];
  onTimestampClick?: (timestamp: number) => void;
  currentPlaybackTime?: number;
}

interface HighlightedSegment extends TranscriptSegment {
  highlighted: boolean;
}

export function TranscriptSearch({
  transcript,
  onTimestampClick,
  currentPlaybackTime = 0,
}: TranscriptSearchProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedIndices, setExpandedIndices] = useState<Set<number>>(new Set());
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [autoScrollIndex, setAutoScrollIndex] = useState<number | null>(null);

  // Filter transcript based on search query
  const filteredSegments = useMemo(() => {
    if (!searchQuery.trim()) {
      return transcript.map((seg) => ({ ...seg, highlighted: false }));
    }

    const lowerQuery = searchQuery.toLowerCase();
    return transcript
      .map((seg) => ({
        ...seg,
        highlighted: seg.text.toLowerCase().includes(lowerQuery),
      }))
      .filter((seg) => seg.highlighted);
  }, [transcript, searchQuery]);

  const toggleExpanded = (index: number) => {
    const newExpanded = new Set(expandedIndices);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedIndices(newExpanded);
  };

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    if (hours > 0) {
      return `${hours}:${mins.toString().padStart(2, "0")}:${secs
        .toString()
        .padStart(2, "0")}`;
    }
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const highlightText = (text: string, query: string) => {
    if (!query.trim()) return text;

    const parts = text.split(new RegExp(`(${query})`, "gi"));
    return parts.map((part, idx) => (
      <span
        key={idx}
        className={
          part.toLowerCase() === query.toLowerCase()
            ? "bg-yellow-200 font-medium"
            : ""
        }
      >
        {part}
      </span>
    ));
  };

  // Auto-scroll to current playback segment
  useEffect(() => {
    const currentSegmentIndex = transcript.findIndex(
      (seg) =>
        seg.timestamp_seconds <= currentPlaybackTime &&
        seg.timestamp_seconds + 5 > currentPlaybackTime // Assume ~5 second segments
    );

    if (currentSegmentIndex !== -1 && currentSegmentIndex !== autoScrollIndex) {
      setAutoScrollIndex(currentSegmentIndex);
      // Auto-expand current segment
      const newExpanded = new Set(expandedIndices);
      if (
        transcript[currentSegmentIndex].text.length > 150 &&
        !newExpanded.has(currentSegmentIndex)
      ) {
        newExpanded.add(currentSegmentIndex);
        setExpandedIndices(newExpanded);
      }
    }
  }, [currentPlaybackTime, transcript, expandedIndices, autoScrollIndex]);

  return (
    <div className="space-y-4">
      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input
          placeholder="Search transcript..."
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
            setSelectedIndex(null);
          }}
          className="pl-10"
        />
        {searchQuery && (
          <button
            onClick={() => {
              setSearchQuery("");
              setSelectedIndex(null);
            }}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            ×
          </button>
        )}
      </div>

      {/* Results Counter */}
      {searchQuery && (
        <div className="text-xs text-gray-600">
          Found {filteredSegments.length} match
          {filteredSegments.length !== 1 ? "es" : ""} in transcript
        </div>
      )}

      {/* Transcript Segments */}
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {!searchQuery && transcript.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p className="text-sm">No transcript available for this call</p>
          </div>
        ) : filteredSegments.length === 0 && searchQuery ? (
          <div className="text-center py-8 text-gray-500">
            <p className="text-sm">No matches found for "{searchQuery}"</p>
          </div>
        ) : (
          filteredSegments.map((segment, index) => {
            const isExpanded = expandedIndices.has(index);
            const isSelected = selectedIndex === index;
            const isCurrentPlaying =
              !searchQuery &&
              autoScrollIndex === transcript.indexOf(segment);
            const isLongText = segment.text.length > 150;

            return (
              <div
                key={index}
                className={`border rounded-lg p-4 cursor-pointer transition-all ${
                  isCurrentPlaying
                    ? "bg-blue-100 border-blue-400 shadow-md"
                    : isSelected
                      ? "bg-blue-50 border-blue-300"
                      : "bg-white hover:bg-gray-50 border-gray-200"
                }`}
                onClick={() => setSelectedIndex(index)}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    {/* Speaker and Timestamp */}
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-gray-900">
                          {segment.speaker}
                        </span>
                        {isCurrentPlaying && (
                          <span className="inline-flex items-center gap-1 text-xs bg-blue-200 text-blue-700 px-2 py-0.5 rounded-full font-medium">
                            <span className="inline-block w-1.5 h-1.5 bg-blue-600 rounded-full animate-pulse" />
                            Playing
                          </span>
                        )}
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          onTimestampClick?.(segment.timestamp_seconds);
                        }}
                        className="text-xs text-blue-600 hover:text-blue-700 h-auto p-1"
                      >
                        {formatTime(segment.timestamp_seconds)}
                      </Button>
                    </div>

                    {/* Text Content */}
                    <p className="text-sm text-gray-700 leading-relaxed">
                      {isLongText && !isExpanded ? (
                        <>
                          {highlightText(
                            segment.text.substring(0, 150),
                            searchQuery
                          )}
                          ...
                        </>
                      ) : (
                        highlightText(segment.text, searchQuery)
                      )}
                    </p>
                  </div>

                  {/* Expand Button */}
                  {isLongText && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleExpanded(index);
                      }}
                      className="flex-shrink-0 h-auto p-1"
                    >
                      {isExpanded ? (
                        <ChevronUp className="h-4 w-4" />
                      ) : (
                        <ChevronDown className="h-4 w-4" />
                      )}
                    </Button>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
