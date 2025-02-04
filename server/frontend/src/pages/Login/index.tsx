import {
  AlipayOutlined,
  LockOutlined,
  MobileOutlined,
  TaobaoOutlined,
  UserOutlined,
  WeiboOutlined,
} from '@ant-design/icons';
import {
  LoginFormPage,
  ProFormCaptcha,
  ProFormCheckbox,
  ProFormText,
} from '@ant-design/pro-components';
import { Button, Divider, message, Space, Tabs } from 'antd';
import type { CSSProperties } from 'react';
import { useState } from 'react';
import { useEffect } from 'react';
import styles from './index.less';

import iconLogo from './assets/logo.png';
import { history, useModel, useRequest, Link } from '@umijs/max';
import { doLogin } from './services';

type LoginType = 'phone' | 'account';

const iconStyles: CSSProperties = {
  color: 'rgba(0, 0, 0, 0.2)',
  fontSize: '18px',
  verticalAlign: 'middle',
  cursor: 'pointer',
};

export default () => {
  const { getBaseInfo } = useModel('global');

  const { run } = useRequest(doLogin, {
    manual: true,
  });

  const handleSubmit = async (val: any) => {
    const resp = await run(val);
    console.log('resp', resp);
    localStorage.token = resp["api_key"];
    history.push('/');
    getBaseInfo();
  }

  useEffect(() => {
    const link = document.querySelector("link[rel*='icon']") || document.createElement('link');
    link.type = 'image/x-icon';
    link.rel = 'icon';
    link.href = 'https://cdn.clustro.ai/icon.ico';
    document.getElementsByTagName('head')[0].appendChild(link);
  });
  
  return (
    <div
      style={{
        backgroundColor: 'white',
        height: 'calc(100vh - 48px)',
        margin: -24,
      }}
    >
      <div className={styles.container}>
        <div className={styles.left}>
          <div className='blur-3xl'>
            <div
              className={styles.bg}
              style={{
                clipPath:
                  'polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)',
              }}
            />
          </div>
        </div>
        <div className={styles.content}>
        <LoginFormPage
          // backgroundImageUrl="https://gw.alipayobjects.com/zos/rmsportal/FfdJeJRQWjEeGTpqgBKj.png"
          logo={iconLogo}
          title="Clustro AI"
          subTitle="Affordable AI as a Service Powered by Edge Computing"
          submitter={{
            searchConfig: {
              submitText: 'SIGN IN'
            }
          }}
          actions={
            <Link to="/user/signup" className={styles["sign-up"]}>
              Sign up for Clustro
            </Link>
          }
          onFinish={handleSubmit}
          
        >
            <ProFormText
              name="email"
              fieldProps={{
                size: 'large',
                prefix: <UserOutlined className={'prefixIcon'} />,
              }}
              placeholder={'Email Address'}
              rules={[
                {
                  required: true,
                  message: 'Enter Email',
                },
              ]}
            />
            <ProFormText.Password
              name="password"
              fieldProps={{
                size: 'large',
                prefix: <LockOutlined className={'prefixIcon'} />,
              }}
              placeholder={'Password'}
              rules={[
                {
                  required: true,
                  message: 'Enter password',
                },
              ]}
            />
          <div
            style={{
              marginBlockEnd: 24,
            }}
          >
            <a>
              Forgot password?
            </a>
          </div>
        </LoginFormPage>
        </div>
      </div>
    </div>
  );
};