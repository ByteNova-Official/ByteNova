import * as React from 'react';

import icon from './icon.jpg';

const EnvironmentSection = () => {
  return (
    <div className="overflow-hidden py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto grid max-w-2xl grid-cols-1 gap-x-8 gap-y-16 sm:gap-y-20 lg:mx-0 lg:max-w-none lg:grid-cols-2 items-center">
          <div className="sm:px-6 lg:px-6 order-1">
            <div className="relative overflow-hidden rounded-xl w-full h-56 lg:h-full">
              <img className="block w-full" src={icon} />
            </div>
          </div>

          <div className="lg:pl-4 lg:pt-4">
            <div className="lg:max-w-lg">
              <h2 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
                Caring about our environment
              </h2>
              <p className="text-lg leading-8 mt-6">
                Slash the initial capital outlay by 90%, significantly cutting down on material wastage.
              </p>
              <p className="mt-2 text-lg leading-8">
                Address humanity's urgent challenges by utilizing dormant resources effectively.
              </p>
              <p className="text-lg leading-8 mt-2">
                All earnings are funneled into the establishment of green, renewable energy facilities.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
 
export default EnvironmentSection;