"use client";

import { useState, useRef } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CallRecordingPlayer } from "./CallRecordingPlayer";
import { TranscriptSearch } from "./TranscriptSearch";
import { ClipGenerator } from "./ClipGenerator";
import type { Annotation } from "./AnnotationMarker";
import type { TranscriptSegment } from "@/types/coaching";

interface EnhancedCallPlayerProps {
  gongUrl?: string | null;
  recordingUrl?: string | null;
  duration: number;
  transcript?: TranscriptSegment[] | null;
  annotations?: Annotation[];
  onTimestampClick?: (timestamp: number) => void;
}

export function EnhancedCallPlayer({
  gongUrl,
  recordingUrl,
  duration,
  transcript = [],
  annotations = [],
  onTimestampClick,
}: EnhancedCallPlayerProps) {
  const [currentPlaybackTime, setCurrentPlaybackTime] = useState(0);
  const [selectedAnnotation, setSelectedAnnotation] = useState<Annotation | null>(
    annotations.length > 0 ? annotations[0] : null
  );

  const handleTimestampClick = (timestamp: number) => {
    setCurrentPlaybackTime(timestamp);
    onTimestampClick?.(timestamp);
  };

  return (
    <div className="space-y-6">
      {/* Main Player with Timeline */}
      <CallRecordingPlayer
        gongUrl={gongUrl}
        recordingUrl={recordingUrl}
        duration={duration}
        annotations={annotations}
        onTimestampClick={handleTimestampClick}
      />

      {/* Tabs for Transcript and Insights */}
      {(transcript && transcript.length > 0) || annotations.length > 0 ? (
        <Tabs defaultValue="transcript" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="transcript">
              Transcript
              {transcript && transcript.length > 0 && (
                <span className="ml-2 text-xs bg-gray-200 text-gray-700 px-2 py-0.5 rounded-full">
                  {transcript.length}
                </span>
              )}
            </TabsTrigger>
            <TabsTrigger value="insights">
              Coaching Insights
              {annotations.length > 0 && (
                <span className="ml-2 text-xs bg-blue-200 text-blue-700 px-2 py-0.5 rounded-full">
                  {annotations.length}
                </span>
              )}
            </TabsTrigger>
            {selectedAnnotation && <TabsTrigger value="share">Share Clip</TabsTrigger>}
          </TabsList>

          {/* Transcript Tab */}
          <TabsContent value="transcript" className="space-y-4">
            {transcript && transcript.length > 0 ? (
              <TranscriptSearch
                transcript={transcript}
                onTimestampClick={handleTimestampClick}
                currentPlaybackTime={currentPlaybackTime}
              />
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p className="text-sm">No transcript available for this call</p>
              </div>
            )}
          </TabsContent>

          {/* Insights Tab */}
          <TabsContent value="insights" className="space-y-4">
            {annotations.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {annotations.map((annotation) => (
                  <div
                    key={annotation.id}
                    onClick={() => setSelectedAnnotation(annotation)}
                    className={`p-4 border rounded-lg cursor-pointer transition-all ${
                      selectedAnnotation?.id === annotation.id
                        ? "bg-blue-50 border-blue-300 shadow-md"
                        : "bg-white hover:bg-gray-50 border-gray-200"
                    }`}
                  >
                    <div className="space-y-2">
                      <div className="flex items-start justify-between">
                        <h4 className="text-sm font-semibold text-gray-900">{annotation.title}</h4>
                        <span className="text-xs font-mono text-gray-600">
                          {Math.floor(annotation.timestamp / 60)}:
                          {String(Math.floor(annotation.timestamp % 60)).padStart(2, "0")}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700">{annotation.insight}</p>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleTimestampClick(annotation.timestamp);
                        }}
                        className="text-xs font-medium text-blue-600 hover:text-blue-700 transition-colors"
                      >
                        Play this moment →
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p className="text-sm">No coaching insights available for this call</p>
              </div>
            )}
          </TabsContent>

          {/* Share Clip Tab */}
          {selectedAnnotation && (
            <TabsContent value="share" className="space-y-4">
              <ClipGenerator annotation={selectedAnnotation} duration={duration} />
            </TabsContent>
          )}
        </Tabs>
      ) : null}
    </div>
  );
}
