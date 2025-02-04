import { PageContainer, ProCard, ProForm, ProFormInstance, ProFormSelect, ProFormTextArea, ProTable } from '@ant-design/pro-components';
import { useModel, useRequest } from '@umijs/max';
import { Button, Form, Space } from 'antd';
import { useEffect, useRef, useState } from 'react';
import { postJob } from './services';

const TestInvocation: React.FC = () => {
  const [image, setImage] = useState('');
  const [exampleInput, setExampleInput] = useState('');
  const [apiCommand, setApiCommand] = useState('');
  const [modelDescription, setModelDescription] = useState('');
  const [response, setResponse] = useState('');
  const { getJobs, getInvocations } = useModel('global');
  const formRef = useRef<ProFormInstance>();
  const regex = /https:\/\/cdn[^ ]*\.png/;

  const jobs = getJobs.data || [];

  useEffect(() => {
    getJobs.run();
  }, [])

  const { run, loading } = useRequest(postJob, {
    manual: true,
  })

  const handleJobChange = (changed_input) => { // New function to handle job selection
    if ('jobId' in changed_input) {
      let selectedJob = jobs.find(job => job.id === changed_input['jobId']);
      let inputPlaceholderText = selectedJob.model_example_input || '{"input":"Hello world"}'

      let apiCommandText = `curl -X POST https://api.clustro.ai/v1/inference_jobs/${selectedJob.id}/invoke_sync \\
     -H "Content-Type: application/json" -H "X-API-Key: ${localStorage.token}" \\
     -d '${inputPlaceholderText}'
      `

      let modelDescriptionText = `
Model name: ${selectedJob.model_name}
Model Repo URL: ${selectedJob.model_artifact}
Model version: ${selectedJob.model_version}
Job Description: ${selectedJob.description}`

      setModelDescription(modelDescriptionText);
      setApiCommand(apiCommandText);
      setExampleInput(inputPlaceholderText);
      formRef.current?.setFieldsValue({
        input: inputPlaceholderText
      });
      console.log(exampleInput)
    }
  };

  useEffect(() => {
    if (jobs) {
      formRef.current?.setFieldsValue({
        input: JSON.stringify({ input: 'Hello world' }),
        jobId: jobs[0]?.id,
      })
    }
  }, [jobs])

  const handlePost = async () => {
    setResponse('');
    setImage('');
    const values = await formRef.current?.validateFields();
    const { input, ...rest } = values || {};
    const resp = await run({ ...rest, input: JSON.parse(input).input });
    console.log('resp', resp);
    const { result } = resp || {};

    if (regex.test(result)) {
      setImage(resp.result);
    }
    setResponse(JSON.stringify(resp, null, 4));
    // todo refresh
    await getInvocations.run();
  }

  return (
    <PageContainer ghost>
      <Space direction="vertical" size={32} style={{ width: '100%' }}>
        <ProCard
            title="Run an Inference Job with input"
            headerBordered
        >
          <ProForm
            formRef={formRef}
            requiredMark={false}
            onValuesChange={(changeValues) => handleJobChange(changeValues)}
            submitter={{
              render: () => <Button type="primary" loading={loading} onClick={handlePost}>Post</Button>
            }}
          >
            <ProFormSelect
              name="jobId"
              label="Inference Job"
              placeholder="Select"
              rules={[
                {
                  required: true,
                  message: 'Enter Select'
                }
              ]}
              options={jobs.map(item => ({
                value: item.id,
                label: `${item.name} - (${item.visibility}, activate workers: ${item.active_workers})`
              }))}
            />
            <ProFormTextArea
              name="input"
              label="Input Data"
              placeholder={`${exampleInput}`}
            />
          </ProForm>
        </ProCard>
        <ProCard
            title="Model Info"
            headerBordered
            collapsible
            defaultCollapsed
            onCollapse={(collapse) => console.log(collapse)}
          >
        <pre>
          {modelDescription}
        </pre>
        </ProCard>
        <ProCard
            title="Example API Command"
            headerBordered
            collapsible
            defaultCollapsed
            onCollapse={(collapse) => console.log(collapse)}
          >
            <pre>
              {`${apiCommand}`}
            </pre>
        </ProCard>
        <ProCard
            title="Response"
            headerBordered
            collapsible
            onCollapse={(collapse) => console.log(collapse)}
        >
          <div>
            <pre>
              {response}
            </pre>
            <img src={image} />
          </div>
        </ProCard>
      </Space>
    </PageContainer>
  );
};

export default TestInvocation;
