'use client';

import { useState, useMemo } from 'react';
import { Card } from '@/components/ui/card';

export interface ActivityDay {
  date: string; // YYYY-MM-DD format
  count: number;
  isHighActivity?: boolean;
}

export interface ActivityTimelineProps {
  /** Array of activity data for each day */
  data: ActivityDay[];
  /** Start date for the calendar view (YYYY-MM-DD) */
  startDate?: string;
  /** End date for the calendar view (YYYY-MM-DD) */
  endDate?: string;
  /** Show coaching sessions count or calls count */
  metric?: 'calls' | 'coachingSessions';
  /** Optional className for additional styling */
  className?: string;
}

/**
 * ActivityTimeline Component
 *
 * Displays a calendar heatmap showing daily activity levels.
 * Highlights high-activity periods and helps identify engagement patterns.
 * Useful for tracking consistency and coaching session frequency.
 */
export function ActivityTimeline({
  data,
  startDate,
  endDate,
  metric = 'calls',
  className = '',
}: ActivityTimelineProps) {
  // Convert activity data to a map for quick lookup
  const activityMap = useMemo(() => {
    const map = new Map<string, number>();
    data.forEach(item => {
      map.set(item.date, item.count);
    });
    return map;
  }, [data]);

  // Calculate max activity for color scaling
  const maxActivity = useMemo(() => {
    return Math.max(...data.map(d => d.count), 1);
  }, [data]);

  // Generate date range
  const dateRange = useMemo(() => {
    let start = startDate ? new Date(startDate) : new Date();
    let end = endDate ? new Date(endDate) : new Date();

    // If no dates provided, default to last 12 weeks
    if (!startDate || !endDate) {
      end = new Date();
      start = new Date(end);
      start.setDate(start.getDate() - 84); // 12 weeks back
    }

    const dates: Array<{ date: string; fullDate: Date }> = [];
    const currentDate = new Date(start);

    while (currentDate <= end) {
      const dateString = currentDate.toISOString().split('T')[0];
      dates.push({ date: dateString, fullDate: new Date(currentDate) });
      currentDate.setDate(currentDate.getDate() + 1);
    }

    return dates;
  }, [startDate, endDate]);

  // Group dates by week
  const weeks = useMemo(() => {
    const weekGroups: Array<typeof dateRange> = [];
    let currentWeek: typeof dateRange = [];

    dateRange.forEach((dateObj, index) => {
      currentWeek.push(dateObj);
      const dayOfWeek = dateObj.fullDate.getDay();

      // Sunday is end of week
      if (dayOfWeek === 6 || index === dateRange.length - 1) {
        weekGroups.push(currentWeek);
        currentWeek = [];
      }
    });

    return weekGroups;
  }, [dateRange]);

  // Get color intensity based on activity count
  const getActivityColor = (count: number) => {
    if (count === 0) return 'bg-gray-100';
    const intensity = (count / maxActivity) * 4; // 4 intensity levels
    const level = Math.ceil(intensity);

    const colors = {
      1: 'bg-blue-100',
      2: 'bg-blue-300',
      3: 'bg-blue-500',
      4: 'bg-blue-700',
    };

    return colors[level as 1 | 2 | 3 | 4] || 'bg-blue-700';
  };

  const dayLabels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const monthLabels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  if (!dateRange || dateRange.length === 0) {
    return (
      <div className={`flex items-center justify-center border rounded-lg bg-gray-50 h-40 ${className}`}>
        <p className="text-gray-500 text-sm">No activity data available</p>
      </div>
    );
  }

  return (
    <div className={`w-full ${className}`}>
      <Card className="p-6">
        {/* Title and Legend */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {metric === 'calls' ? 'Call Activity' : 'Coaching Sessions'} Timeline
          </h3>
          <div className="flex items-center gap-4 text-sm">
            <span className="text-gray-600">Less</span>
            <div className="flex gap-1">
              <div className="w-4 h-4 bg-gray-100 border border-gray-300 rounded" />
              <div className="w-4 h-4 bg-blue-100 border border-gray-300 rounded" />
              <div className="w-4 h-4 bg-blue-300 border border-gray-300 rounded" />
              <div className="w-4 h-4 bg-blue-500 border border-gray-300 rounded" />
              <div className="w-4 h-4 bg-blue-700 border border-gray-300 rounded" />
            </div>
            <span className="text-gray-600">More</span>
          </div>
        </div>

        {/* Calendar Grid */}
        <div className="overflow-x-auto">
          <div className="flex gap-8">
            {/* Day labels column */}
            <div className="flex flex-col justify-center gap-1 text-xs text-gray-500 font-medium">
              <div className="h-6" /> {/* Space for month labels */}
              {dayLabels.map(day => (
                <div key={day} className="h-5 flex items-center justify-end pr-2">
                  {day}
                </div>
              ))}
            </div>

            {/* Weeks */}
            <div className="flex gap-2">
              {weeks.map((week, weekIndex) => (
                <div key={weekIndex} className="flex flex-col">
                  {/* Month label */}
                  <div className="h-6 flex items-end mb-1">
                    <span className="text-xs text-gray-500 font-medium">
                      {week.length > 0 ? monthLabels[week[0].fullDate.getMonth()] : ''}
                    </span>
                  </div>

                  {/* Days */}
                  {week.map(dateObj => {
                    const count = activityMap.get(dateObj.date) || 0;
                    const isHighActivity = count > maxActivity * 0.75;

                    return (
                      <div
                        key={dateObj.date}
                        className={`w-5 h-5 border border-gray-300 rounded hover:border-gray-500 cursor-pointer transition-all ${getActivityColor(count)} ${
                          isHighActivity ? 'ring-2 ring-orange-400' : ''
                        }`}
                        title={`${dateObj.date}: ${count} ${metric}`}
                      />
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Summary stats */}
        <div className="mt-6 pt-6 border-t border-gray-200 grid grid-cols-3 gap-4">
          <div>
            <p className="text-xs text-gray-500 font-medium">Total Activity</p>
            <p className="text-lg font-semibold text-gray-900">
              {data.reduce((sum, d) => sum + d.count, 0)}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 font-medium">Average per Day</p>
            <p className="text-lg font-semibold text-gray-900">
              {dateRange.length > 0 ? Math.round(data.reduce((sum, d) => sum + d.count, 0) / dateRange.length) : 0}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 font-medium">Peak Activity</p>
            <p className="text-lg font-semibold text-gray-900">{maxActivity}</p>
          </div>
        </div>
      </Card>
    </div>
  );
}
