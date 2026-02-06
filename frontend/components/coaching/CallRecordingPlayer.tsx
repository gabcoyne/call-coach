"use client";

import { useState, useRef, useEffect } from "react";
import { Play, Pause, Volume2, VolumeX, Maximize2, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";

interface CallRecordingPlayerProps {
  gongUrl?: string | null;
  recordingUrl?: string | null;
  duration: number;
}

export function CallRecordingPlayer({
  gongUrl,
  recordingUrl,
  duration,
}: CallRecordingPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const audioRef = useRef<HTMLAudioElement>(null);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

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
        <p className="text-center text-gray-500">
          Recording not available for this call
        </p>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 rounded-lg p-6 border border-gray-200 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-900">Call Recording</h3>
        {gongUrl && (
          <a
            href={gongUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs"
          >
            <Button
              variant="outline"
              size="sm"
              className="flex items-center gap-2"
            >
              <ExternalLink className="h-3 w-3" />
              View in Gong
            </Button>
          </a>
        )}
      </div>

      <div className="space-y-2">
        {/* Audio Player */}
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

        {/* Player Controls */}
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={handlePlayPause}
            disabled={!recordingUrl}
            className="h-8 w-8 p-0"
          >
            {isPlaying ? (
              <Pause className="h-4 w-4" />
            ) : (
              <Play className="h-4 w-4" />
            )}
          </Button>

          {/* Time Display and Slider */}
          <div className="flex-1 flex items-center gap-2">
            <span className="text-xs text-gray-500 w-10">
              {formatTime(currentTime)}
            </span>
            {recordingUrl && (
              <input
                type="range"
                min="0"
                max={duration}
                value={currentTime}
                onChange={handleSeek}
                className="flex-1 h-1 bg-gray-300 rounded cursor-pointer accent-blue-500"
              />
            )}
            <span className="text-xs text-gray-500 w-10 text-right">
              {formatTime(duration)}
            </span>
          </div>

          {/* Volume Control */}
          {recordingUrl && (
            <Button
              size="sm"
              variant="outline"
              onClick={handleMuteToggle}
              className="h-8 w-8 p-0"
            >
              {isMuted ? (
                <VolumeX className="h-4 w-4" />
              ) : (
                <Volume2 className="h-4 w-4" />
              )}
            </Button>
          )}
        </div>

        {/* Fallback Message */}
        {gongUrl && !recordingUrl && (
          <p className="text-xs text-gray-500">
            Audio playback not available locally. Open Gong to view the full recording.
          </p>
        )}
      </div>
    </div>
  );
}
