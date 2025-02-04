import { PageContainer } from '@ant-design/pro-components';
import { useModel } from '@umijs/max';
import Overview from './components/Overview';
import React, { useEffect } from 'react';

const HomePage: React.FC = () => {
  useEffect(() => {
    const link = document.querySelector("link[rel*='icon']") || document.createElement('link');
    link.type = 'image/x-icon';
    link.rel = 'icon';
    link.href = 'https://cdn.clustro.ai/icon.ico';
    document.getElementsByTagName('head')[0].appendChild(link);
  });

  return (
    <PageContainer ghost>
      <Overview />
    </PageContainer>
  );
};

export default HomePage;
