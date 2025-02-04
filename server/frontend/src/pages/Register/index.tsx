import {
  AlipayOutlined,
  LockOutlined,
  MobileOutlined,
  TaobaoOutlined,
  UserOutlined,
  WeiboOutlined,
  GoogleOutlined,
  MailOutlined,
  PhoneOutlined,
  BankOutlined,
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
import styles from './index.less';

import iconLogo from './assets/logo.png';
import { history, useModel, useRequest, Link } from '@umijs/max';
import { doSignup, doLogin } from './services';

type LoginType = 'phone' | 'account';

const iconStyles: CSSProperties = {
  color: 'rgba(0, 0, 0, 0.2)',
  fontSize: '18px',
  verticalAlign: 'middle',
  cursor: 'pointer',
};

export default () => {
  const { getBaseInfo } = useModel('global');

  const { run } = useRequest(doSignup, {
    manual: true,
  });

  const loginReq = useRequest(doLogin, {
    manual: true,
  });

  const handleSubmit = async (val: any) => {
    const resp = await run(val);
    const { email, password } = val || {};
    const token = await loginReq.run({ email, password });
    localStorage.token = token["api_key"];
    history.push('/');
    getBaseInfo();
  }
  
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
          subTitle="Addressing AI's resource and deployment hurdles through affordable, scalable, distributed cloud computing."
          submitter={{
            searchConfig: {
              submitText: 'Continue'
            }
          }}
          actions={
            <Link to="/user/login" className={styles["sign-up"]}>
              Sign In
            </Link>
          }
          onFinish={handleSubmit}
        >
            <ProFormText
              name="name"
              fieldProps={{
                size: 'large',
                prefix: <UserOutlined className={'prefixIcon'} />,
                maxLength: 30,
              }}
              placeholder={'First and last name'}
              rules={[
                {
                  required: true,
                  message: 'Enter first and last name',
                },
              ]}
            />
            <ProFormText
              name="email"
              fieldProps={{
                size: 'large',
                prefix: <MailOutlined className={'prefixIcon'} />,
                maxLength: 50,
              }}
              placeholder={'Email Address'}
              rules={[
                {
                  required: true,
                  message: 'Enter email address',
                },
                {
                  pattern: /^\S+@\S+\.\S{2,}$/,
                  message: 'E-mail format is incorrect',
                },
              ]}
            />
            <ProFormText
              name="phone"
              fieldProps={{
                size: 'large',
                prefix: <PhoneOutlined className={'prefixIcon'} />,
              }}
              placeholder={'Phone Number'}
              rules={[
                {
                  required: true,
                  message: 'Enter phone number',
                },
                {
                  pattern: /^-?\d*(\.\d*)?$/,
                  message: 'Phone number format is incorrect',
                },
              ]}
            />
            <ProFormText.Password
              name="password"
              fieldProps={{
                size: 'large',
                prefix: <LockOutlined className={'prefixIcon'} />,
                maxLength: 100,
              }}
              placeholder={'Password'}
              rules={[
                {
                  required: true,
                  message: 'Enter password',
                },
              ]}
            />
            <ProFormText
              name="company"
              fieldProps={{
                size: 'large',
                prefix: <BankOutlined className={'prefixIcon'} />,
                maxLength: 100,
              }}
              placeholder={'Company'}
              rules={[
                {
                  required: true,
                  message: 'Enter company',
                },
              ]}
            />
        </LoginFormPage>
        </div>
      </div>
    </div>
  );
};