"use client";

import { useEffect } from "react";
import { useReportWebVitals } from "next/web-vitals";

/**
 * Web Vitals monitoring component
 * Tracks Core Web Vitals (LCP, FID, CLS) and other performance metrics
 *
 * Target metrics:
 * - LCP (Largest Contentful Paint): < 2.5s
 * - FID (First Input Delay): < 100ms
 * - CLS (Cumulative Layout Shift): < 0.1
 * - FCP (First Contentful Paint): < 1.8s
 * - TTFB (Time to First Byte): < 800ms
 */
export function WebVitals() {
  useReportWebVitals((metric) => {
    // Log to console in development
    if (process.env.NODE_ENV === "development") {
      console.log(`[Web Vitals] ${metric.name}:`, {
        value: metric.value,
        rating: metric.rating,
        id: metric.id,
      });
    }

    // Send to analytics in production
    if (process.env.NODE_ENV === "production") {
      // You can send to your analytics service here
      // Examples:
      // - Google Analytics: gtag('event', metric.name, { value: metric.value })
      // - Vercel Analytics: automatically collected if enabled
      // - Custom endpoint: fetch('/api/analytics', { method: 'POST', body: JSON.stringify(metric) })

      // For now, we'll use console.log with a specific format that can be captured
      console.log(
        JSON.stringify({
          type: "web-vitals",
          metric: metric.name,
          value: metric.value,
          rating: metric.rating,
          navigationType: metric.navigationType,
          id: metric.id,
          timestamp: Date.now(),
        })
      );
    }
  });

  // Additional performance monitoring
  useEffect(() => {
    // Monitor Long Tasks (> 50ms)
    if (typeof window !== "undefined" && "PerformanceObserver" in window) {
      try {
        const longTaskObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.duration > 50) {
              console.warn(`[Performance] Long Task detected: ${entry.duration}ms`, entry);
            }
          }
        });

        longTaskObserver.observe({ entryTypes: ["longtask"] });

        // Cleanup
        return () => {
          longTaskObserver.disconnect();
        };
      } catch (e) {
        // PerformanceObserver might not support longtask in all browsers
        console.debug("Long task monitoring not available");
      }
    }
  }, []);

  // This component doesn't render anything
  return null;
}

/**
 * Hook to manually measure custom metrics
 */
export function usePerformanceMetric(metricName: string) {
  const startMark = `${metricName}-start`;
  const endMark = `${metricName}-end`;

  return {
    start: () => {
      if (typeof window !== "undefined" && window.performance) {
        window.performance.mark(startMark);
      }
    },
    end: () => {
      if (typeof window !== "undefined" && window.performance) {
        window.performance.mark(endMark);
        window.performance.measure(metricName, startMark, endMark);

        const measure = window.performance.getEntriesByName(metricName).pop() as PerformanceMeasure;

        if (measure) {
          console.log(`[Custom Metric] ${metricName}: ${measure.duration.toFixed(2)}ms`);

          // Clean up marks and measures
          window.performance.clearMarks(startMark);
          window.performance.clearMarks(endMark);
          window.performance.clearMeasures(metricName);

          return measure.duration;
        }
      }
      return 0;
    },
  };
}
