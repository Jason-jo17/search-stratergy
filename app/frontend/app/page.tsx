'use client';

import React, { useState } from 'react';
import SearchInput from '../components/SearchInput';
import StrategySelector from '../components/StrategySelector';
import ParametersPanel from '../components/ParametersPanel';
import ResultsGrid from '../components/ResultsGrid';
import ComparisonView from '../components/ComparisonView';
import PerformanceMetrics from '../components/PerformanceMetrics';
import { STMEvaluationPanel } from '../components/STMEvaluationPanel';

export default function Home() {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [query, setQuery] = useState('');
  const [strategy, setStrategy] = useState('keyword');
  const [params, setParams] = useState({ limit: 10 });
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [results, setResults] = useState<any[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [comparisonResults, setComparisonResults] = useState<any>({});
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [metrics, setMetrics] = useState<any>({});
  const [isLoading, setIsLoading] = useState(false);
  const [isCompareMode, setIsCompareMode] = useState(false);
  const [compareStrategies, setCompareStrategies] = useState(['keyword', 'vector']);
  const [loadingStates, setLoadingStates] = useState<{ [key: string]: boolean }>({});
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [optimizationData, setOptimizationData] = useState<any>(null);
  const [executionTimes, setExecutionTimes] = useState<{ [key: string]: string }>({});

  const handleSearch = async (searchQuery: string) => {
    let optimizedQuery = searchQuery;
    setQuery(searchQuery);
    setIsLoading(true);
    setResults([]);
    setComparisonResults({});
    setMetrics({});
    setOptimizationData(null);

    // Reset loading states for comparison
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const initialLoadingStates: any = {};
    if (isCompareMode) {
      compareStrategies.forEach(s => initialLoadingStates[s] = true);
    }
    setLoadingStates(initialLoadingStates);
    setExecutionTimes({});

    const startTime = performance.now();
    const API_URL = 'http://localhost:8000';

    try {
      if (isCompareMode) {
        // 1. Optimize Query

        try {

          const optResponse = await fetch(`${API_URL}/api/search/optimize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: searchQuery })
          });
          const optData = await optResponse.json();
          if (optData.optimization) {
            optimizedQuery = optData.optimization.rewritten_query || searchQuery;
            setOptimizationData(optData.optimization);
          }
        } catch (e) {
          console.error("Optimization failed, using original query", e);
        }

        // 2. Fire parallel requests
        compareStrategies.forEach(async (strat) => {
          const stratStartTime = performance.now();
          try {
            // Use optimized query for most, but maybe original for some?
            // The backend logic used optimized for: keyword, vector, hybrid, fts, fuzzy, stm
            // And original (but passed in request) for: agentic*
            // We'll send the optimized query as `query` for the simple ones.
            // For agentic, we might want to send the original query?
            // The backend `search_compare` did: `optimized_req.query = optimized_query`
            // So let's stick to that pattern.

            const queryToSend = ['agentic', 'agentic_tool', 'agentic_analysis'].includes(strat) ? searchQuery : optimizedQuery;

            const response = await fetch(`${API_URL}/api/search/${strat}`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                query: queryToSend,
                ...params
              }),
            });

            if (!response.ok) {
              const errorText = await response.text();
              console.error(`Strategy ${strat} Error Details:`, errorText);
              throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
            }

            const data = await response.json();

            const stratEndTime = performance.now();
            const duration = (stratEndTime - stratStartTime) / 1000; // seconds

            setComparisonResults((prev: any) => ({
              ...prev,
              [strat]: data.results
            }));

            setExecutionTimes((prev: any) => ({
              ...prev,
              [strat]: duration.toFixed(2)
            }));

          } catch (error) {
            console.error(`Strategy ${strat} failed:`, error);
            setComparisonResults((prev: any) => ({
              ...prev,
              [strat]: []
            }));
          } finally {
            setLoadingStates((prev: any) => ({
              ...prev,
              [strat]: false
            }));
          }
        });

      } else {
        // Single Strategy Mode
        try {
          const response = await fetch(`${API_URL}/api/search/${strategy}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              query: searchQuery,
              ...params
            }),
          });

          if (!response.ok) {
            const errorText = await response.text();
            console.error("Backend Error Details:", errorText);
            throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
          }

          const data = await response.json();
          setResults(data.results);
        } catch (error) {
          console.error('Single strategy search failed:', error);
          setResults([]);
        }
      }
    } catch (error) {
      console.error('Search failed:', error);
      // alert('Search failed. Please ensure the backend is running.');
    } finally {
      const endTime = performance.now();
      setMetrics({ [strategy]: endTime - startTime });
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-extrabold text-gray-900 mb-2">
            Retrieval Strategy Lab
          </h1>
          <p className="text-lg text-gray-600">
            Test and compare different search algorithms on student profiles
          </p>
        </div>

        <STMEvaluationPanel />

        <SearchInput onSearch={handleSearch} isLoading={isLoading} />

        <div className="flex justify-center mb-6">
          <div className="flex items-center space-x-2 bg-white p-1 rounded-lg border border-gray-200">
            <button
              suppressHydrationWarning
              onClick={() => setIsCompareMode(false)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${!isCompareMode ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-50'
                }`}
            >
              Single Strategy
            </button>
            <button
              suppressHydrationWarning
              onClick={() => setIsCompareMode(true)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${isCompareMode ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-50'
                }`}
            >
              Comparison Mode
            </button>
          </div>
        </div>

        {!isCompareMode ? (
          <>
            <StrategySelector selected={strategy} onSelect={setStrategy} />
            <ParametersPanel strategy={strategy} params={params} onChange={setParams} />
            <PerformanceMetrics metrics={metrics} />
            <ResultsGrid results={results} isLoading={isLoading} />
          </>
        ) : (
          <>
            <div className="mb-6 p-4 bg-white rounded-lg border border-gray-200">
              <h3 className="text-sm font-medium text-gray-700 mb-2">Select Strategies to Compare</h3>
              <div className="flex flex-wrap gap-2">
                {['adaptive-fusion', 'keyword', 'vector', 'hybrid', 'fts', 'fuzzy', 'agentic', 'agentic_tool', 'agentic_analysis', 'stm', 'bm25'].map((s) => (
                  <label key={s} className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={compareStrategies.includes(s)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setCompareStrategies([...compareStrategies, s]);
                        } else {
                          setCompareStrategies(compareStrategies.filter(cs => cs !== s));
                        }
                      }}
                      className="rounded text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700 capitalize">{s}</span>
                  </label>
                ))}
              </div>
            </div>
            <ComparisonView
              results={comparisonResults}
              strategies={compareStrategies}
              loadingStates={loadingStates}
              executionTimes={executionTimes}
              optimization={optimizationData}
            />
          </>
        )}
      </div>
    </main>
  );
}
