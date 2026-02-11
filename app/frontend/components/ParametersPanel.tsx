import React from 'react';

interface ParametersPanelProps {
    strategy: string;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    params: any;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    onChange: (params: any) => void;
}

export default function ParametersPanel({ strategy, params, onChange }: ParametersPanelProps) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const handleChange = (key: string, value: any) => {
        onChange({ ...params, [key]: value });
    };

    return (
        <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 mb-8">
            <h3 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide">
                {strategy} Parameters
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="col-span-1">
                    <label className="block text-sm text-gray-600 mb-1">Limit</label>
                    <input
                        suppressHydrationWarning
                        type="number"
                        value={params.limit || 10}
                        onChange={(e) => handleChange('limit', parseInt(e.target.value))}
                        className="w-full px-3 py-2 border rounded-md"
                    />
                </div>

                {strategy === 'hybrid' && (
                    <>
                        <div>
                            <label className="block text-sm text-gray-600 mb-1">Vector Weight (0-1)</label>
                            <input
                                type="number"
                                step="0.1"
                                min="0"
                                max="1"
                                value={params.vector_weight || 0.5}
                                onChange={(e) => handleChange('vector_weight', parseFloat(e.target.value))}
                                className="w-full px-3 py-2 border rounded-md"
                            />
                        </div>
                        <div>
                            <label className="block text-sm text-gray-600 mb-1">RRF K Constant</label>
                            <input
                                type="number"
                                value={params.rrf_k || 60}
                                onChange={(e) => handleChange('rrf_k', parseInt(e.target.value))}
                                className="w-full px-3 py-2 border rounded-md"
                            />
                        </div>
                    </>
                )}

                {strategy === 'filter' && (
                    <>
                        <div>
                            <label className="block text-sm text-gray-600 mb-1">Role</label>
                            <input
                                type="text"
                                value={params.role || ''}
                                onChange={(e) => handleChange('role', e.target.value)}
                                className="w-full px-3 py-2 border rounded-md"
                                placeholder="e.g., Software Engineer"
                            />
                        </div>
                        <div>
                            <label className="block text-sm text-gray-600 mb-1">Skills (comma separated)</label>
                            <input
                                type="text"
                                value={params.skills ? params.skills.join(', ') : ''}
                                onChange={(e) => handleChange('skills', e.target.value.split(',').map((s: string) => s.trim()))}
                                className="w-full px-3 py-2 border rounded-md"
                                placeholder="e.g., Python, React"
                            />
                        </div>
                    </>
                )}

                {strategy === 'pattern' && (
                    <>
                        <div>
                            <label className="block text-sm text-gray-600 mb-1">Pattern Type</label>
                            <select
                                value={params.pattern_type || ''}
                                onChange={(e) => handleChange('pattern_type', e.target.value)}
                                className="w-full px-3 py-2 border rounded-md"
                            >
                                <option value="">Custom</option>
                                <option value="email">Email Address</option>
                                <option value="phone">Phone Number</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm text-gray-600 mb-1">Custom Regex</label>
                            <input
                                type="text"
                                value={params.custom_pattern || ''}
                                onChange={(e) => handleChange('custom_pattern', e.target.value)}
                                className="w-full px-3 py-2 border rounded-md"
                                placeholder="e.g., \bPython\b"
                                disabled={!!params.pattern_type}
                            />
                        </div>
                    </>
                )}

                {strategy === 'skills' && (
                    <>
                        <div>
                            <label className="block text-sm text-gray-600 mb-1">Required Skills</label>
                            <input
                                type="text"
                                value={params.required_skills ? params.required_skills.join(', ') : ''}
                                onChange={(e) => handleChange('required_skills', e.target.value.split(',').map((s: string) => s.trim()))}
                                className="w-full px-3 py-2 border rounded-md"
                            />
                        </div>
                        <div>
                            <label className="block text-sm text-gray-600 mb-1">Preferred Skills</label>
                            <input
                                type="text"
                                value={params.preferred_skills ? params.preferred_skills.join(', ') : ''}
                                onChange={(e) => handleChange('preferred_skills', e.target.value.split(',').map((s: string) => s.trim()))}
                                className="w-full px-3 py-2 border rounded-md"
                            />
                        </div>
                    </>
                )}

                {strategy === 'fts' && (
                    <div className="col-span-1">
                        <div className="p-3 bg-blue-50 text-blue-700 text-sm rounded-md">
                            Full Text Search uses PostgreSQL&apos;s native <code>tsvector</code> and <code>tsquery</code> capabilities.
                        </div>
                    </div>
                )}

                {strategy === 'fuzzy' && (
                    <div className="col-span-1">
                        <div className="p-3 bg-blue-50 text-blue-700 text-sm rounded-md">
                            Fuzzy Search uses <code>pg_trgm</code> trigram similarity to find approximate matches.
                        </div>
                    </div>
                )}

                {strategy === 'agentic' && (
                    <div className="col-span-1">
                        <div className="p-3 bg-purple-50 text-purple-700 text-sm rounded-md">
                            Agentic Search uses <strong>Gemini Pro</strong> to analyze and re-rank candidates retrieved by Hybrid search.
                            It provides reasoning for each match.
                        </div>
                    </div>
                )}

                {strategy === 'adaptive-fusion' && (
                    <>
                        <div className="col-span-1 md:col-span-2 bg-blue-50 p-3 rounded-md mb-2">
                            <h4 className="text-sm font-semibold text-blue-800 mb-2">Fusion Weights</h4>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-xs font-medium text-blue-700 mb-1">BM25 Weight ({params.bm25_weight || 0.5})</label>
                                    <input
                                        type="range"
                                        min="0"
                                        max="1"
                                        step="0.1"
                                        value={params.bm25_weight !== undefined ? params.bm25_weight : 0.5}
                                        onChange={(e) => handleChange('bm25_weight', parseFloat(e.target.value))}
                                        className="w-full"
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs font-medium text-blue-700 mb-1">Vector Weight ({params.vector_weight || 0.5})</label>
                                    <input
                                        type="range"
                                        min="0"
                                        max="1"
                                        step="0.1"
                                        value={params.vector_weight !== undefined ? params.vector_weight : 0.5}
                                        onChange={(e) => handleChange('vector_weight', parseFloat(e.target.value))}
                                        className="w-full"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="col-span-1 md:col-span-2 bg-green-50 p-3 rounded-md mb-2">
                            <h4 className="text-sm font-semibold text-green-800 mb-2">Boosting Factors</h4>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-xs font-medium text-green-700 mb-1">Skill Proficiency Boost ({params.skill_proficiency_boost || 0.3})</label>
                                    <input
                                        type="range"
                                        min="0"
                                        max="1"
                                        step="0.1"
                                        value={params.skill_proficiency_boost !== undefined ? params.skill_proficiency_boost : 0.3}
                                        onChange={(e) => handleChange('skill_proficiency_boost', parseFloat(e.target.value))}
                                        className="w-full"
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs font-medium text-green-700 mb-1">Recency Boost ({params.recency_boost || 0.1})</label>
                                    <input
                                        type="range"
                                        min="0"
                                        max="1"
                                        step="0.1"
                                        value={params.recency_boost !== undefined ? params.recency_boost : 0.1}
                                        onChange={(e) => handleChange('recency_boost', parseFloat(e.target.value))}
                                        className="w-full"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="col-span-1">
                            <label className="block text-sm text-gray-600 mb-1">BM25 k1 (Saturation)</label>
                            <input
                                type="number"
                                step="0.1"
                                min="1.0"
                                max="3.0"
                                value={params.bm25_k1 || 1.5}
                                onChange={(e) => handleChange('bm25_k1', parseFloat(e.target.value))}
                                className="w-full px-3 py-2 border rounded-md"
                            />
                        </div>
                        <div className="col-span-1">
                            <label className="block text-sm text-gray-600 mb-1">BM25 b (Length Norm)</label>
                            <input
                                type="number"
                                step="0.1"
                                min="0.0"
                                max="1.0"
                                value={params.bm25_b !== undefined ? params.bm25_b : 0.6}
                                onChange={(e) => handleChange('bm25_b', parseFloat(e.target.value))}
                                className="w-full px-3 py-2 border rounded-md"
                            />
                        </div>
                        <div className="col-span-1">
                            <label className="block text-sm text-gray-600 mb-1">Fusion Method</label>
                            <select
                                value={params.fusion_method || 'weighted_sum'}
                                onChange={(e) => handleChange('fusion_method', e.target.value)}
                                className="w-full px-3 py-2 border rounded-md"
                            >
                                <option value="weighted_sum">Weighted Sum</option>
                                <option value="multiplicative">Multiplicative</option>
                                <option value="rrf">Reciprocal Rank Fusion</option>
                            </select>
                        </div>
                    </>
                )}

                {strategy === 'bm25' && (
                    <div className="col-span-1">
                        <div className="p-3 bg-green-50 text-green-700 text-sm rounded-md">
                            BM25 uses probabilistic term weighting (TF-IDF) to find relevant documents based on exact keyword matches.
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
