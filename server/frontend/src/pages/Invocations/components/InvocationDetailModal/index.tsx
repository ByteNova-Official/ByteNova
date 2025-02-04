import * as React from 'react';
import { useState, useEffect, useRef } from 'react';
import { Modal, Descriptions, Skeleton } from 'antd';
import { ProField, ProForm, ProFormText } from '@ant-design/pro-components';

import { useRequest, useModel } from '@umijs/max';
import { getInvocation } from './services';

import styles from './index.less';

const InvocationDetailModal = ({
  id,
  visible,
  onClose,
}) => {
  
  const { run, loading, data } = useRequest(() => getInvocation({ id }), {
    manual: true,
  });

  useEffect(() => {
    if (visible && id) {
      run();
    }
  }, [visible, id])

  const { status, inference_job_name, input, error, processed_by_worker_name, process_start_time, process_finish_time, result } = data || {};


  const resultIsImage = result && result.indexOf('https://cdn.clustro.ai') > -1;

  return (
    <Modal
      title="Invocation"
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
            // initialValues={{
            //   name,
            //   visibility,
            //   description,
            // }}
            submitter={{ render: () => [] }}
            onFinish={async (value) => console.log(value)}
          >
            <Descriptions column={1}>
              <Descriptions.Item label="ID">
                <ProField text={id} mode="read" />
              </Descriptions.Item>

              <Descriptions.Item label="Status">
                <ProFormText text={status} mode="read" />
              </Descriptions.Item>

              <Descriptions.Item label="Job">
                <ProField text={inference_job_name} mode="read" />
              </Descriptions.Item>
              
              <Descriptions.Item label="Input">
                <ProField text={input} mode="read" />
              </Descriptions.Item>

              <Descriptions.Item label="Worker">
                <ProField text={processed_by_worker_name} mode="read" />
              </Descriptions.Item>

              <Descriptions.Item label="Start Time">
                <ProField text={process_start_time} mode="read" />
              </Descriptions.Item>

              <Descriptions.Item label="Finish Time">
                <ProField text={process_finish_time} mode="read" />
              </Descriptions.Item>

              <Descriptions.Item label="Error">
                <ProField text={error} mode="read" />
              </Descriptions.Item>

                <Descriptions.Item label="Result">
                  {resultIsImage ? (
                    <ProField text={result} valueType="image" style={{ width: 500 }} />
                    ) : (
                    <ProField text={result} valueType="jsonCode" />
                  )}
                </Descriptions.Item>
            </Descriptions>
          </ProForm>
        </Skeleton>
      </div>
    </Modal>
  )
}

export default InvocationDetailModal;