import React from 'react';

interface ResultCardProps {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    result: any;
    rank: number;
}

export default function ResultCard({ result, rank }: ResultCardProps) {
    const { text, metadata, score, highlighted_text, matched_keywords } = result;

    // Parse metadata if it's a string
    const meta = typeof metadata === 'string' ? JSON.parse(metadata) : metadata || {};

    return (
        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                    <span className="bg-blue-100 text-blue-800 text-xs font-bold px-2 py-1 rounded-full">
                        #{rank}
                    </span>
                    <h3 className="font-semibold text-lg text-gray-900">
                        {meta.name || 'Candidate'}
                    </h3>
                </div>
                <div className="text-right">
                    {score !== undefined && (
                        <div className="text-sm font-medium text-gray-500">
                            Score: {score.toFixed(4)}
                        </div>
                    )}
                </div>
            </div>

            {result.ai_reasoning ? (
                <div className="mb-3 p-3 bg-purple-50 border border-purple-100 rounded-md">
                    <div className="text-xs font-bold text-purple-700 mb-1 uppercase">AI Reasoning</div>
                    <div className="text-sm text-purple-900 italic">
                        &quot;{result.ai_reasoning}&quot;
                    </div>
                </div>
            ) : result.match_reason ? (
                <div className="mb-3 p-3 bg-blue-50 border border-blue-100 rounded-md">
                    <div className="text-xs font-bold text-blue-700 mb-1 uppercase">Match Insight</div>
                    <div className="text-sm text-blue-900">
                        {result.match_reason}
                    </div>
                </div>
            ) : null}

            <div className="mb-3 grid grid-cols-2 gap-2">
                <div className="text-sm text-gray-600">
                    <span className="font-medium">Role:</span> {meta.role || 'N/A'}
                </div>
                <div className="text-sm text-gray-600">
                    <span className="font-medium">Location:</span> {meta.location || 'N/A'}
                </div>
                {meta.experience && (
                    <div className="col-span-2 text-sm text-gray-600">
                        <span className="font-medium">Exp:</span> {meta.experience}
                    </div>
                )}
            </div>

            <div className="prose prose-sm max-w-none text-gray-700 mb-3 line-clamp-3"
                dangerouslySetInnerHTML={{
                    __html: highlighted_text || text
                }}
            />

            {matched_keywords && matched_keywords.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2 mb-2">
                    {matched_keywords.map((kw: string, i: number) => (
                        <span key={i} className="bg-yellow-100 text-yellow-800 text-xs px-2 py-0.5 rounded">
                            {kw}
                        </span>
                    ))}
                </div>
            )}

            {meta.skills_text && (
                <div className="mt-3 pt-3 border-t border-gray-100">
                    <div className="text-xs font-medium text-gray-500 mb-1">Skills</div>
                    <div className="text-xs text-gray-600 line-clamp-2">
                        {meta.skills_text}
                    </div>
                </div>
            )}

            {meta.projects_text && (
                <div className="mt-2">
                    <div className="text-xs font-medium text-gray-500 mb-1">Projects</div>
                    <div className="text-xs text-gray-600 line-clamp-2">
                        {meta.projects_text}
                    </div>
                </div>
            )}
        </div>
    );
}
