'use client';

import React from 'react';

export default function Analytics() {
    return (
        <main className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
            <div className="max-w-7xl mx-auto">
                <h1 className="text-3xl font-bold text-gray-900 mb-8">Analytics Dashboard</h1>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">Average Response Time by Strategy</h3>
                        <div className="space-y-4">
                            {['keyword', 'vector', 'hybrid'].map((strategy) => (
                                <div key={strategy}>
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="capitalize text-gray-600">{strategy}</span>
                                        <span className="font-medium text-gray-900">120ms</span>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-2">
                                        <div
                                            className="bg-blue-600 h-2 rounded-full"
                                            style={{ width: `60%` }}
                                        ></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">Most Effective Strategies</h3>
                        <div className="flex items-center justify-center h-48">
                            <p className="text-gray-500 italic">Data collection in progress...</p>
                        </div>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Queries</h3>
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead>
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Query</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Strategy</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Results</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {[
                                    { q: 'python developer', s: 'hybrid', r: 12, t: '145ms' },
                                    { q: 'react frontend', s: 'vector', r: 8, t: '210ms' },
                                    { q: 'data scientist', s: 'keyword', r: 5, t: '85ms' },
                                ].map((row, i) => (
                                    <tr key={i}>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{row.q}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 capitalize">{row.s}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{row.r}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{row.t}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </main>
    );
}
