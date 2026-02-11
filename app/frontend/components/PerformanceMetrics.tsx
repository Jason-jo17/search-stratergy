import React from 'react';

interface PerformanceMetricsProps {
    metrics: { [key: string]: number };
}

export default function PerformanceMetrics({ metrics }: PerformanceMetricsProps) {
    if (!metrics || Object.keys(metrics).length === 0) return null;

    return (
        <div className="bg-gray-900 text-white p-4 rounded-lg mb-6">
            <h4 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-2">
                Performance Metrics
            </h4>
            <div className="flex flex-wrap gap-4">
                {Object.entries(metrics).map(([key, value]) => (
                    <div key={key} className="flex items-center gap-2">
                        <span className="text-sm font-medium capitalize">{key}:</span>
                        <span className="text-sm font-mono text-green-400">
                            {value.toFixed(2)}ms
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
}
