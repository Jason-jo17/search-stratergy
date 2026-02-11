"use client";

import { useState } from 'react';
import { Loader2, BrainCircuit } from "lucide-react";

export function STMEvaluationPanel() {
    const [studentId, setStudentId] = useState('');
    const [loading, setLoading] = useState(false);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState('');

    const handleEvaluate = async () => {
        if (!studentId) return;

        setLoading(true);
        setError('');
        setResult(null);

        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const response = await fetch(`${API_URL}/api/stm/evaluate/${studentId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ student_id: studentId }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Evaluation failed');
            }

            const data = await response.json();
            console.log("STM Evaluation Result:", data); // Debug log
            setResult(data);
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="w-full mb-6 border border-purple-500/50 bg-purple-500/5 rounded-lg shadow-sm">
            <div className="p-6 pb-4 border-b border-purple-500/20">
                <h3 className="text-lg font-semibold flex items-center gap-2 text-purple-700 dark:text-purple-300">
                    <BrainCircuit className="w-5 h-5" />
                    STM Evaluation Worker
                </h3>
            </div>
            <div className="p-6 pt-4">
                <div className="flex gap-4 mb-4">
                    <input
                        suppressHydrationWarning
                        placeholder="Enter Student ID (UUID)"
                        value={studentId}
                        onChange={(e) => setStudentId(e.target.value)}
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 font-mono"
                    />
                    <button
                        onClick={handleEvaluate}
                        disabled={loading || !studentId}
                        className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-purple-600 text-white hover:bg-purple-700 h-10 px-4 py-2"
                    >
                        {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                        Run Evaluation
                    </button>
                </div>

                {error && (
                    <div className="p-4 mb-4 text-red-600 bg-red-100 rounded-md dark:bg-red-900/20 dark:text-red-400">
                        Error: {error}
                    </div>
                )}

                {result && (
                    <div className="space-y-4">
                        <div className="p-3 text-green-700 bg-green-100 rounded-md dark:bg-green-900/20 dark:text-green-400">
                            {result.message}
                        </div>

                        <div className="space-y-2">
                            <h3 className="font-semibold">Generated Chunks:</h3>
                            <div className="grid gap-2">
                                {Object.entries(result.chunks).map(([type, content]) => (
                                    <div key={type} className="p-3 border rounded-md bg-white dark:bg-gray-800">
                                        <span className="px-2 py-1 text-xs font-medium text-purple-600 bg-purple-100 rounded-full dark:bg-purple-900/30 dark:text-purple-300">
                                            {type.toUpperCase()}
                                        </span>
                                        <pre className="mt-2 text-xs whitespace-pre-wrap font-mono overflow-auto max-h-60">
                                            {JSON.stringify(content, null, 2)}
                                        </pre>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
