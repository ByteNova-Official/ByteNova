import * as React from 'react';

import icon1 from './2_1.gif';
import icon2 from './2_2.gif';

const DemoSection = () => {
  return (
    <div id="demo" className="py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto lg:text-center">
          <h2 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
            Try our DEMO
          </h2>
          <div className="flex items-center justify-center gap-8 my-8">
            <div className="rounded-2xl overflow-hidden" style={{ width: 600, height: 450 }}>
              <img src={icon1} className="w-full h-full" />
            </div>
            <div className="rounded-2xl overflow-hidden" style={{ width: 600, height: 450 }}>
              <img src={icon2} className="w-full h-full" />
            </div>
          </div>

          <a
            className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background bg-black text-white hover:bg-black/90 h-10 py-2 px-4 mt-6"
            href="https://console.clustro.ai/"
            target='_blank'
          >
            Signup as a user
          </a>
          
          <p className="mx-auto mt-2 text-lg leading-8 max-w-2xl">
            Register to try out pre-deployed models for yourself.
          </p>
        </div>
      </div>
    </div>
  );
}
 
export default DemoSection;