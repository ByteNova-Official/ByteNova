import { useContext } from 'react'
import { SProps, IContext } from 'ssr-types'
import { IData } from '~/typings/data'
import { useStoreContext } from 'ssr-common-utils'
import Header from './components/Header'
import LandingSection from './components/LandingSection'
import CoreSection from './components/CoreSection'
import ExplainSection from './components/ExplainSection'
import ProviderSection from './components/ProviderSection'
import DemoSection from './components/DemoSection'
import EnvironmentSection from './components/EnvironmentSection'
import Footer from './components/Footer'
import SDKSection from './components/SDKSection'


export default function Index (props: SProps) {
  const { state, dispatch } = useContext<IContext<IData>>(useStoreContext())

  return (
    <div className="relative">
      <Header />
      <LandingSection />
      <CoreSection />
      <SDKSection />
      <ExplainSection />
      <DemoSection />
      <ProviderSection />
      <EnvironmentSection />
      <Footer />
    </div>
  )
}
