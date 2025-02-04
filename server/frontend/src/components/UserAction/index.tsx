import React from 'react';
import { Dropdown, Menu, Avatar } from 'antd';
import { history, useModel } from "@umijs/max";


import './index.less';

const UserAction = () => {
  const { getUsers } = useModel('global');

  const users = getUsers.data;

  const { name } = users || {};

  const menus = [
    {
      key: 'logout',
      label: 'Logout',
      onClick() {
        localStorage.token = '';
        history.push('/user/login')
      }
    }
  ]

  const dropdownProps = {
    overlay: (
      <Menu>
        {menus.map((item) => (
          <Menu.Item key={item.key} onClick={item.onClick}>
            {item.label}
          </Menu.Item>
        ))}
      </Menu>
    ),
  }

  return (
    <div>
      <Dropdown {...dropdownProps}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: 12 }}>
          <Avatar
            size="small"
            className="umi-plugin-layout-avatar"
            src={
              'https://gw.alipayobjects.com/zos/antfincdn/XAosXuNZyF/BiazfanxmamNRoxxVxka.png'
            }
            alt="avatar"
        />
          <div style={{ fontSize: 14, textAlign: 'center', }}>
            {name}
          </div>
        </div>
      </Dropdown>
    </div>
  )
}

export default UserAction;