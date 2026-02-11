import React from 'react';

interface StrategySelectorProps {
    selected: string;
    onSelect: (strategy: string) => void;
}

const strategies = [
    { id: 'adaptive-fusion', label: 'Adaptive Fusion (Mega)', description: 'Tunable multi-strategy fusion' },
    { id: 'keyword', label: 'Keyword Search', description: 'Exact match & frequency' },
    { id: 'vector', label: 'Vector Search', description: 'Semantic similarity' },
    { id: 'hybrid', label: 'Hybrid Search', description: 'Vector + Keyword (RRF)' },
    { id: 'filter', label: 'Metadata Filter', description: 'Structured filtering' },
    { id: 'pattern', label: 'Pattern Match', description: 'Regex patterns' },
    { id: 'skills', label: 'Skill Search', description: 'Required & Preferred' },
    { id: 'fts', label: 'Full Text Search', description: 'Postgres Native FTS' },
    { id: 'fuzzy', label: 'Fuzzy Search', description: 'Trigram Similarity' },
    { id: 'agentic', label: 'Agentic Search', description: 'AI Re-ranking' },
    { id: 'agentic_tool', label: 'Agentic (Tool Use)', description: 'AI selects search tool' },
    { id: 'agentic_analysis', label: 'Agentic (Analysis)', description: 'AI rewrites query' },
    { id: 'stm', label: 'STM (Dual Search)', description: 'Vector + FTS on Chunks' },
    { id: 'bm25', label: 'BM25 Search', description: 'Probabilistic keyword ranking' },
];

export default function StrategySelector({ selected, onSelect }: StrategySelectorProps) {
    return (
        <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Retrieval Strategy</label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {strategies.map((strategy) => (
                    <button
                        suppressHydrationWarning
                        key={strategy.id}
                        onClick={() => onSelect(strategy.id)}
                        className={`p-3 text-left border rounded-lg transition-colors ${selected === strategy.id
                            ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500'
                            : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                            }`}
                    >
                        <div className="font-medium text-gray-900">{strategy.label}</div>
                        <div className="text-xs text-gray-500">{strategy.description}</div>
                    </button>
                ))}
            </div>
        </div>
    );
}
