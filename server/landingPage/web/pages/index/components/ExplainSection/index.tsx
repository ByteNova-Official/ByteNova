import * as React from 'react';

import icon from './icon.png';

const ExplainSection = () => {

  return (
    <div className="mx-auto max-w-7xl py-24 sm:px-6 sm:py-32 lg:px-8">
      <div className="relative isolate overflow-hidden bg-gradient-to-b from-gray-900 to-gray-600 bg-gradient-to-r px-6 py-24 text-center shadow-2xl sm:rounded-3xl sm:px-16">
        <h2 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl text-white">
          Deploy AI inference on any device
        </h2>
        <p className="mx-auto mt-6 text-lg leading-8 text-white">
          Clustro orchestrates a dynamic exchange between users needing computational power and those offering their devices to the network. Discarding the need for centralized facilities and staff, Clustro acts as the Uber and Airbnb of AI cloud computing, directly coupling providers and users, ensuring extraordinarily low costs.
        </p>
        <div className="rounded-2xl">
          <img src={icon} className="block mx-auto w-10/12" />
        </div>
      </div>
    </div>
  )
  return (
    <div className="mx-auto max-w-7xl py-24 sm:px-6 sm:py-32 lg:px-8">
      
      <div className="py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl lg:text-center">
            <h2 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
              Deploy AI inference on any device
            </h2>
            <p className="mx-auto mt-6 text-lg leading-8">
              Clustro orchestrates a dynamic exchange between users needing computational power and those offering their devices to the network.
            </p>

            
          </div>
        </div>
      </div>
    </div>
  );
}
 
export default ExplainSection;