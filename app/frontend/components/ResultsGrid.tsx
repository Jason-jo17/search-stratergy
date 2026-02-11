import React from 'react';
import ResultCard from './ResultCard';

interface ResultsGridProps {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    results: any[];
    isLoading: boolean;
}

export default function ResultsGrid({ results, isLoading }: ResultsGridProps) {
    if (isLoading) {
        return (
            <div className="grid grid-cols-1 gap-4 animate-pulse">
                {[1, 2, 3].map((i) => (
                    <div key={i} className="h-48 bg-gray-200 rounded-lg"></div>
                ))}
            </div>
        );
    }

    if (!results || results.length === 0) {
        return (
            <div className="text-center py-12 text-gray-500">
                No results found. Try adjusting your query or strategy.
            </div>
        );
    }

    return (
        <div className="grid grid-cols-1 gap-4">
            {results.map((result, index) => (
                <ResultCard key={result.id || index} result={result} rank={index + 1} />
            ))}
        </div>
    );
}
