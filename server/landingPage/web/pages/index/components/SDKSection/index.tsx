import * as React from 'react';
import TextItem from './TextItem';
import iconCode from './code.png';
import { GoldOutlined, InsertRowAboveOutlined, LaptopOutlined, MedicineBoxOutlined, MessageOutlined, PartitionOutlined, ReadOutlined, RobotOutlined, SaveOutlined, ShopOutlined, SolutionOutlined, SubnodeOutlined, TabletOutlined } from '@ant-design/icons';
import './index.less';

const SDKSection = () => {

  const datas = [
    {
      icon: <InsertRowAboveOutlined />,
      text: 'Feature Extraction',
      type: 'blue',
    },
    {
      icon: <LaptopOutlined />,
      text: 'Text-to-mage',
      type: 'green',
    },
    {
      icon: <MessageOutlined />,
      text: 'Image-to-Text',
      type: 'red',
    },
    {
      icon: <ReadOutlined />,
      text: 'Visual Question Answering',
      type: 'red',
    },
    {
      icon: <RobotOutlined />,
      text: 'UnconditionalImage Generation',
      type: 'blue',
    },
    {
      icon: <SaveOutlined />,
      text: 'Zero-ShotImage Classification',
      type: 'red',
    },
    {
      icon: <SolutionOutlined />,
      text: 'Token Classification',
      type: 'blue',
    },
    {
      icon: <TabletOutlined />,
      text: 'Text Generation',
      type: 'green',
    },
    {
      icon: <SubnodeOutlined />,
      text: 'Automatic Speech Recognition',
      type: 'blue',
    },
    {
      icon: <PartitionOutlined />,
      text: 'Audio-to-Audio',
      type: 'red',
    },
    {
      icon: <MedicineBoxOutlined />,
      text: 'Fill-Mask',
      type: 'green',
    },
    {
      icon: <GoldOutlined />,
      text: 'Tabular Regression',
      type: 'blue',
    },
    {
      icon: <InsertRowAboveOutlined />,
      text: 'Feature Extraction',
      type: 'blue',
    },
    {
      icon: <LaptopOutlined />,
      text: 'Text-to-mage',
      type: 'green',
    },
    {
      icon: <MessageOutlined />,
      text: 'Image-to-Text',
      type: 'red',
    },
    {
      icon: <ReadOutlined />,
      text: 'Visual Question Answering',
      type: 'red',
    },
    {
      icon: <RobotOutlined />,
      text: 'UnconditionalImage Generation',
      type: 'blue',
    },
    {
      icon: <SaveOutlined />,
      text: 'Zero-ShotImage Classification',
      type: 'red',
    },
    {
      icon: <SolutionOutlined />,
      text: 'Token Classification',
      type: 'blue',
    },
    {
      icon: <TabletOutlined />,
      text: 'Text Generation',
      type: 'green',
    },
    {
      icon: <SubnodeOutlined />,
      text: 'Automatic Speech Recognition',
      type: 'blue',
    },
    {
      icon: <PartitionOutlined />,
      text: 'Audio-to-Audio',
      type: 'red',
    },
    {
      icon: <MedicineBoxOutlined />,
      text: 'Fill-Mask',
      type: 'green',
    },
    {
      icon: <GoldOutlined />,
      text: 'Tabular Regression',
      type: 'blue',
    },
  ]
  
  return (
    <div className="overflow-hidden py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto text-center">
          <div className="lg:pl-4 lg:pt-4">
            <h2 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
              Powering AI: In a much cheaper way
            </h2>

            <div className="overflow-hidden mx-auto mt-8" style={{ width: 800 }}>
              <div className="text-list rowup">
                <div className="flex flex-wrap gap-8 mx-auto justify-center mt-6" style={{ width: 1600 }}>
                  {
                    datas.map(item => (<TextItem {...item} />))
                  }
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SDKSection;