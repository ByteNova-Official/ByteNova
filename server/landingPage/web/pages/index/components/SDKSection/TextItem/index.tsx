import { PicRightOutlined } from '@ant-design/icons';
import * as React from 'react';

const TextItem = ({
  icon,
  type,
  text,
}) => {

  const colors = {
    green: {
      bg: '#F3FEF9',
      color: '#2CBE8A'
    },
    blue: {
      bg: '#F5FAFF',
      color: '#3F84F7',
    },
    red: {
      bg: '#FEF7F7',
      color: '#F05454',
    }
  }

  const { bg, color } = colors[type] || colors.green;

  return (
    <div className="flex items-center gap-2 rounded-2xl pr-3 overflow-hidden" style={{ border: '1px solid #f5f5f5' }}>
      <div className="w-8 h-8 flex justify-center items-center" style={{ background: bg, color }}>
        {icon}
      </div>
      <div className="text-sm">
        {text}
      </div>
    </div>
  );
}
 
export default TextItem;