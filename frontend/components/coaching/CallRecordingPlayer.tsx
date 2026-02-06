"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Play, Pause, Volume2, VolumeX, ExternalLink, Copy, Share2, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AnnotationMarker, type Annotation } from "./AnnotationMarker";
import { CoachingOverlay } from "./CoachingOverlay";

interface CallRecordingPlayerProps {
  gongUrl?: string | null;
  recordingUrl?: string | null;
  duration: number;
  annotations?: Annotation[];
  onTimestampClick?: (timestamp: number) => void;
}

const PLAYBACK_SPEEDS = [0.5, 1, 1.5, 2];

export function CallRecordingPlayer({
  gongUrl,
  recordingUrl,
  duration,
  annotations = [],
  onTimestampClick,
}: CallRecordingPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [hoveredAnnotationId, setHoveredAnnotationId] = useState<string | null>(null);
  const [activeAnnotation, setActiveAnnotation] = useState<Annotation | null>(null);
  const [showCoachingOverlay, setShowCoachingOverlay] = useState(true);
  const [copied, setCopied] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);
  const playerRef = useRef<HTMLDivElement>(null);

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    if (hours > 0) {
      return `${hours}:${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
    }
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  // Find active annotation based on current time
  const getCurrentAnnotation = useCallback((): Annotation | null => {
    const current = annotations.find(
      (a) => a.timestamp >= currentTime - 2 && a.timestamp <= currentTime + 2
    );
    return current || null;
  }, [annotations, currentTime]);

  // Update coaching overlay when annotation changes
  useEffect(() => {
    const newAnnotation = getCurrentAnnotation();
    if (newAnnotation && newAnnotation.id !== activeAnnotation?.id) {
      setActiveAnnotation(newAnnotation);
      setShowCoachingOverlay(true);
    }
  }, [getCurrentAnnotation, activeAnnotation?.id]);

  const handlePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleMuteToggle = () => {
    if (audioRef.current) {
      audioRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTime = parseFloat(e.target.value);
    setCurrentTime(newTime);
    if (audioRef.current) {
      audioRef.current.currentTime = newTime;
    }
  };

  const handleSpeedChange = (speed: number) => {
    setPlaybackSpeed(speed);
    if (audioRef.current) {
      audioRef.current.playbackRate = speed;
    }
  };

  const handleAnnotationClick = (timestamp: number) => {
    setCurrentTime(timestamp);
    if (audioRef.current) {
      audioRef.current.currentTime = timestamp;
      audioRef.current.play();
      setIsPlaying(true);
    }
    onTimestampClick?.(timestamp);
  };

  const generateTimestampLink = () => {
    const baseUrl = typeof window !== "undefined" ? window.location.href.split("#")[0] : "";
    return `${baseUrl}#t=${Math.floor(currentTime)}`;
  };

  const copyTimestampLink = () => {
    const link = generateTimestampLink();
    navigator.clipboard.writeText(link);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateTime = () => setCurrentTime(audio.currentTime);
    const handleEnded = () => setIsPlaying(false);

    audio.addEventListener("timeupdate", updateTime);
    audio.addEventListener("ended", handleEnded);

    return () => {
      audio.removeEventListener("timeupdate", updateTime);
      audio.removeEventListener("ended", handleEnded);
    };
  }, []);

  if (!gongUrl && !recordingUrl) {
    return (
      <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
        <p className="text-center text-gray-500">Recording not available for this call</p>
      </div>
    );
  }

  return (
    <div
      ref={playerRef}
      className="bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-white border-b">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-gray-900">Call Recording</h3>
          {annotations.length > 0 && (
            <span className="inline-flex items-center gap-1 text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
              <Zap className="h-3 w-3" />
              {annotations.length} insights
            </span>
          )}
        </div>
        {gongUrl && (
          <a href={gongUrl} target="_blank" rel="noopener noreferrer" className="text-xs">
            <Button variant="outline" size="sm" className="flex items-center gap-2">
              <ExternalLink className="h-3 w-3" />
              View in Gong
            </Button>
          </a>
        )}
      </div>

      <div className="p-4 space-y-4">
        {/* Audio Element */}
        {recordingUrl && (
          <audio
            ref={audioRef}
            src={recordingUrl}
            onTimeUpdate={() => {
              if (audioRef.current) {
                setCurrentTime(audioRef.current.currentTime);
              }
            }}
            className="hidden"
          />
        )}

        {/* Timeline with Annotations */}
        {annotations.length > 0 && (
          <div className="space-y-2">
            <label className="text-xs font-medium text-gray-700">Coaching Insights Timeline</label>
            <div className="relative h-12 bg-gray-100 rounded-lg p-2 border border-gray-200">
              {/* Annotation markers */}
              {annotations.map((annotation) => (
                <AnnotationMarker
                  key={annotation.id}
                  annotation={annotation}
                  duration={duration}
                  isHovered={hoveredAnnotationId === annotation.id}
                  onHover={setHoveredAnnotationId}
                  onClick={handleAnnotationClick}
                />
              ))}
            </div>
          </div>
        )}

        {/* Main Controls */}
        <div className="flex items-center gap-3">
          <Button
            size="sm"
            variant="outline"
            onClick={handlePlayPause}
            disabled={!recordingUrl}
            className="h-9 w-9 p-0"
          >
            {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          </Button>

          {/* Time Display and Slider */}
          <div className="flex-1 flex items-center gap-2">
            <span className="text-xs text-gray-600 font-mono w-12">{formatTime(currentTime)}</span>
            {recordingUrl && (
              <input
                type="range"
                min="0"
                max={duration}
                value={currentTime}
                onChange={handleSeek}
                className="flex-1 h-2 bg-gray-300 rounded-lg cursor-pointer accent-blue-500"
              />
            )}
            <span className="text-xs text-gray-600 font-mono w-12 text-right">
              {formatTime(duration)}
            </span>
          </div>

          {/* Volume Control */}
          {recordingUrl && (
            <Button size="sm" variant="outline" onClick={handleMuteToggle} className="h-9 w-9 p-0">
              {isMuted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
            </Button>
          )}
        </div>

        {/* Secondary Controls */}
        <div className="flex items-center justify-between gap-2 pt-2 border-t">
          {/* Playback Speed */}
          <div className="flex items-center gap-1">
            <span className="text-xs text-gray-600 font-medium">Speed:</span>
            <div className="flex gap-1">
              {PLAYBACK_SPEEDS.map((speed) => (
                <Button
                  key={speed}
                  size="sm"
                  variant={playbackSpeed === speed ? "default" : "outline"}
                  onClick={() => handleSpeedChange(speed)}
                  disabled={!recordingUrl}
                  className="h-7 px-2 text-xs"
                >
                  {speed}x
                </Button>
              ))}
            </div>
          </div>

          {/* Share Controls */}
          <div className="flex items-center gap-2 ml-auto">
            <Button
              size="sm"
              variant="outline"
              onClick={copyTimestampLink}
              disabled={!recordingUrl}
              className="h-8 gap-1 text-xs"
            >
              <Copy className="h-3 w-3" />
              {copied ? "Copied!" : "Share time"}
            </Button>
          </div>
        </div>

        {/* Fallback Message */}
        {gongUrl && !recordingUrl && (
          <p className="text-xs text-gray-500 px-2 py-2 bg-yellow-50 border border-yellow-200 rounded">
            Audio playback not available locally. Open Gong to view the full recording.
          </p>
        )}
      </div>

      {/* Coaching Overlay */}
      {activeAnnotation && (
        <CoachingOverlay
          annotation={activeAnnotation}
          isVisible={showCoachingOverlay}
          onClose={() => setShowCoachingOverlay(false)}
          position="bottom-right"
        />
      )}
    </div>
  );
}
