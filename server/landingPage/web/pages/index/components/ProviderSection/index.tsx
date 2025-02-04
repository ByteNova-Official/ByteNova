import * as React from 'react';

const ProviderSection = () => {


  const tables = [
    {
      label: 'Android Phones',
      hour: '0.05',
      month: '33.60',
    },
    {
      label: 'NVIDIA GTX 3070',
      hour: '0.25',
      month: '168.00',
    },
    {
      label: 'NVIDIA GTX 3080',
      hour: '0.30',
      month: '201.60',
    },
    {
      label: 'NVIDIA GTX 4090',
      hour: '0.40',
      month: '268.80',
    },
  ]

  return (
    <div id="earn" className="overflow-hidden py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto grid max-w-2xl grid-cols-1 gap-x-8 gap-y-16 sm:gap-y-20 lg:mx-0 lg:max-w-none lg:grid-cols-2 items-center">
          <div className="sm:px-6 lg:px-6 order-1">
            <div className="relative overflow-hidden rounded-xl w-full h-56 lg:h-full">
              <table className="w-full text-sm text-left text-gray-500 dark:text-gray-400">
                <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
                  <tr>
                    <th scope="col" className="px-6 py-3">
                      Device / Chip
                    </th>
                    <th scope="col" className="px-6 py-3">
                      Hourly earnings rate
                    </th>
                    <th scope="col" className="px-6 py-3">
                      Max monthly earnings per device / chip
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {
                    tables.map(({ label, hour, month }, index) => (
                      <tr key={index} className="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
                        <th scope="row" className="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white">
                          {label}
                        </th>
                        <td className="px-6 py-4">{`$${hour}`}</td>
                        <td className="px-6 py-4">{`$${month}`}</td>
                      </tr>
                    ))
                  }
                </tbody>
              </table>

            </div>
          </div>

          <div className="lg:pl-4 lg:pt-4">
            <div className="lg:max-w-lg">
              <h2 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
                Become a Compute Provider
              </h2>
              <p className="mt-6 text-lg leading-8">Earn with Clustro by connecting to our inference network. Get paid in cash or redeem your points to gift cards and more.</p>


              <a
                className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background bg-black text-white hover:bg-black/90 h-10 py-2 px-4 mt-6"
                href="https://console.clustro.ai/"
                target='_blank'
              >
                Signup as a provider
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProviderSection;