import React from 'react';
import ResultCard from './ResultCard';

interface ComparisonViewProps {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    results: { [key: string]: any[] };
    strategies: string[];
    loadingStates: { [key: string]: boolean };
    executionTimes: { [key: string]: string };
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    optimization?: any;
}

export default function ComparisonView({ results, strategies, loadingStates, executionTimes, optimization }: ComparisonViewProps) {
    if (!strategies || strategies.length === 0) return null;

    return (
        <div className="overflow-x-auto pb-4">
            {optimization && (
                <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                        <div className="p-2 bg-blue-100 rounded-full text-blue-600">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                        </div>
                        <div>
                            <h3 className="font-semibold text-blue-900">Query Optimized by AI</h3>
                            <div className="mt-1 text-sm text-blue-800">
                                <span className="font-medium">Rewritten:</span> &quot;{optimization.rewritten_query}&quot;
                            </div>
                            {optimization.filters && Object.keys(optimization.filters).length > 0 && (
                                <div className="mt-1 text-sm text-blue-800">
                                    <span className="font-medium">Filters:</span> {JSON.stringify(optimization.filters)}
                                </div>
                            )}
                            {optimization.reasoning && (
                                <div className="mt-1 text-xs text-blue-600 italic">
                                    &quot;{optimization.reasoning}&quot;
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
            <div className="flex gap-4 min-w-max">
                {strategies.map((strategy) => (
                    <div key={strategy} className="w-96 flex-shrink-0">
                        <div className="flex justify-between items-center mb-4 border-b pb-2">
                            <h3 className="text-lg font-bold text-gray-800 capitalize">
                                {strategy} Results
                            </h3>
                            {executionTimes[strategy] && (
                                <span className="text-xs font-mono bg-gray-100 text-gray-600 px-2 py-1 rounded">
                                    {executionTimes[strategy]}s
                                </span>
                            )}
                        </div>

                        <div className="space-y-4">
                            {loadingStates[strategy] ? (
                                <div className="space-y-4 animate-pulse">
                                    {[1, 2, 3].map((i) => (
                                        <div key={i} className="h-48 bg-gray-100 rounded-lg border border-gray-200">
                                            <div className="h-4 bg-gray-200 rounded w-3/4 m-4"></div>
                                            <div className="h-4 bg-gray-200 rounded w-1/2 m-4"></div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <>
                                    {results[strategy]?.map((result, index) => (
                                        <ResultCard key={result.id || index} result={result} rank={index + 1} />
                                    ))}
                                    {(!results[strategy] || results[strategy].length === 0) && (
                                        <div className="text-center py-8 bg-gray-50 rounded-lg border border-dashed border-gray-300">
                                            <p className="text-gray-500 text-sm italic">No results found</p>
                                        </div>
                                    )}
                                </>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
