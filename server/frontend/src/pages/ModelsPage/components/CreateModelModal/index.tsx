import { ProForm, ProFormInstance, ProFormSelect, ProFormText, ProFormCheckbox } from '@ant-design/pro-components';
import { useModel, useRequest } from '@umijs/max';
import { Modal } from 'antd';
import * as React from 'react';
import {createModel, createDeafultInferenceJob, updateModel} from '../../services';

const CreateModelModal = ({
  visible,
  onClose,
}) => {
  const formRef = React.useRef<ProFormInstance>();
  const { getModels } = useModel('global');

  const { run, loading } = useRequest(createModel, {
    manual: true,
  })

  const handleSubmit = async () => {
    const values = await formRef.current?.validateFields();
    const result = await run(values);

    if (values.set_as_model_default){
      let job_params = {}
      job_params["model_id"] = result.id
      job_params["name"] = result.name
      job_params["set_as_model_default"] = values.set_as_model_default
      await createDeafultInferenceJob(job_params);
    }
    onClose();
    getModels.run()
  }

  return (
    <Modal
      title="Model"
      open={visible}
      onCancel={onClose}
      confirmLoading={loading}
      onOk={handleSubmit}
      destroyOnClose
    >
      <ProForm
        formRef={formRef}
        requiredMark={false}
        submitter={{
          render: () => null
        }}
        initialValues={{
          set_as_model_default: true,
          visibility: 'private'
        }}
      >
        <ProForm.Group>
          <ProFormText
            width="lg"
            name="name"
            label="Name"
            placeholder="Name"
            rules={[
              {
                required: true,
                message: 'Enter name'
              }
            ]}
          />
        </ProForm.Group>

        <ProForm.Group>
          <ProFormSelect
            width="lg"
            name="model_type"
            label="Type"
            placeholder="Select"
            rules={[
              {
                required: true,
                message: 'Enter Select'
              }
            ]}
            options={[
              {
                value: 'text_to_text',
                label: 'text_to_text',
              },
              {
                value: 'text_to_image',
                label: 'text_to_image',
              },
            ]}
          />
        </ProForm.Group>

        <ProForm.Group>
          <ProFormText
            width="lg"
            name="version"
            label="Version"
            placeholder="1.0"
          />
        </ProForm.Group>

        <ProForm.Group>
          <ProFormText
            width="lg"
            name="artifact"
            label="Artifact"
            placeholder="Artifact repo git URL"
            rules={[
              {
                required: true,
                message: 'Missing artifact repo git URL'
              }
            ]}
          />
        </ProForm.Group>

        <ProForm.Group>
          <ProFormText
            width="lg"
            name="invoke_function"
            label="Invoke Function"
            placeholder="Default main.py/invoke"
          />
        </ProForm.Group>

        <ProForm.Group>
          <ProFormText
            width="lg"
            name="description"
            label="Description"
            placeholder="Description"
          />
        </ProForm.Group>

        <ProForm.Group>
          <ProFormText
            width="lg"
            name="example_input"
            label="Example Input"
            placeholder="{\'input\': \'A majestic lion jumping from a big stone at night\'}"
          />
        </ProForm.Group>

        <ProForm.Group>
          <ProFormText
            width="lg"
            name="runtime_docker_image"
            label="Runtime Docker Image"
            placeholder="Default nvidia/cuda:11.6.2-runtime-ubuntu20.04"
          />
        </ProForm.Group>

        <ProForm.Group>
          <ProFormText
            width="lg"
            name="required_gpu"
            label="Required Gpu"
            placeholder="0"
          />
        </ProForm.Group>

        <ProForm.Group>
          <ProFormSelect
            width="lg"
            name="visibility"
            label="Visibility"
            placeholder="Select"
            rules={[
              {
                required: true,
                message: 'Enter Select'
              }
            ]}
            options={[
              {
                value: 'private',
                label: 'private',
              },
              {
                value: 'public',
                label: 'public',
              },
            ]}
          />
        </ProForm.Group>

        <ProForm.Group>
          <ProFormCheckbox valuePropName='checked' name="set_as_model_default">Create Default Job</ProFormCheckbox>
        </ProForm.Group>

      </ProForm>
    </Modal>
  );
}
 
export default CreateModelModal;