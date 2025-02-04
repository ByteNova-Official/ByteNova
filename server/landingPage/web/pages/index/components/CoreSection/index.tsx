import * as React from 'react';

const CoreSection = () => {
  return (
    <div className="mx-auto max-w-7xl py-24 sm:px-6 sm:py-32 lg:px-8">
      <div className="relative isolate overflow-hidden bg-gradient-to-b from-gray-900 to-gray-600 bg-gradient-to-r px-6 py-24 text-center shadow-2xl sm:rounded-3xl sm:px-16">
        <h2 className="mx-auto max-w-2xl text-3xl font-bold tracking-tight  sm:text-4xl text-white">Mixed compute resources</h2>
        <p className="mx-auto max-w-2xl mt-6 text-lg leading-8 text-white">Community commute providers for cost efficient and energy benefits. Clustro managed hosts for inference stability and security.</p>
        <a href="https://clustro-ai.gitbook.io/untitled/clustro-ai-white-paper" target="_blank" className="block text-lg mt-6 leading-8 text-white">
          Guidebook <span aria-hidden="true">&rarr;</span>
        </a>
      </div>
    </div>
  );
}
 
export default CoreSection;