import * as React from 'react';
import { useState, useEffect, useRef } from 'react';
import { Modal, Descriptions, Skeleton } from 'antd';
import { ProField, ProForm, ProFormText } from '@ant-design/pro-components';

import { useRequest, useModel } from '@umijs/max';
import { getModel } from './services';

import styles from './index.less';

const ModelDetailModal = ({
  id,
  visible,
  onClose,
}) => {
  
  const { run, loading, data } = useRequest(() => getModel({ id }), {
    manual: true,
  });

  useEffect(() => {
    if (visible && id) {
      run();
    }
  }, [visible, id])

  const { name, updated_at, model_type, required_gpu, artifact, version, invoke_function, runtime_docker_image, description, example_input } = data || {};

  let inputParseJSON = '';
  let textPraseJson = '';

  try {
    inputParseJSON = example_input ? JSON.parse(example_input) : {};
  } catch (e) {
    inputParseJSON = {};
  }
  
  try {
    textPraseJson = inputParseJSON.input ? JSON.parse(inputParseJSON.input) : {}; 
  } catch (e) {
    textPraseJson = inputParseJSON.input;
  }
  

  return (
    <Modal
      title="Model"
      width={640}
      open={visible}
      onCancel={onClose}
      destroyOnClose
      onOk={onClose}
    >
      <div className={styles.modal}>
        <Skeleton loading={loading} active>
          <ProForm
            readonly
            submitter={{ render: () => [] }}
            onFinish={async (value) => console.log(value)}
          >
            <Descriptions column={1}>
              <Descriptions.Item label="ID">
                <ProField text={id} mode="read" />
              </Descriptions.Item>

              <Descriptions.Item label="Name">
                <ProFormText text={name} mode="read" />
              </Descriptions.Item>

              <Descriptions.Item label="Last Modify">
                <ProFormText text={updated_at} mode="read" />
              </Descriptions.Item>

              <Descriptions.Item label="Type">
                <ProFormText text={model_type} mode="read" />
              </Descriptions.Item>

              <Descriptions.Item label="Required GPU">
                <ProFormText text={required_gpu} mode="read" />
              </Descriptions.Item>

              <Descriptions.Item label="Version SHA">
                <ProFormText text={version} mode="read" />
              </Descriptions.Item>

              <Descriptions.Item label="Artifact Repo">
                <ProFormText text={artifact} mode="read" />
              </Descriptions.Item>

              <Descriptions.Item label="Invoke Function">
                <ProFormText text={invoke_function} mode="read" />
              </Descriptions.Item>

              <Descriptions.Item label="Runtime Docker Image">
                <ProFormText text={runtime_docker_image} mode="read" />
              </Descriptions.Item>

              <Descriptions.Item label="Description">
                <ProFormText text={description} mode="read" />
              </Descriptions.Item>

              {example_input && (
                <Descriptions.Item label="Example Input">
                  <ProField text={JSON.stringify({ input: textPraseJson })} valueType="jsonCode" mode="read" />
                </Descriptions.Item>
              )}
            </Descriptions>
          </ProForm>
        </Skeleton>
      </div>
    </Modal>
  )
}

export default ModelDetailModal;