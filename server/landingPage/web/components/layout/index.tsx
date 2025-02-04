
import { LayoutProps } from 'ssr-types'
import App from './App'
import './global.css';

const Layout = (props: LayoutProps) => {
  // 注：Layout 只会在服务端被渲染，不要在此运行客户端有关逻辑
  const { injectState } = props
  const { injectCss, injectScript } = props.staticList!

  return (
    <html lang='en'>
      <head>
        <meta charSet='utf-8' />
        <meta name='viewport' content='width=device-width, initial-scale=1, shrink-to-fit=no' />
        <meta name='theme-color' content='#000000' />
        <title>Clustro AI</title>
        <link rel='shortcut icon' type="image/x-icon" href="https://cdn.clustro.ai/icon.ico" />
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;700;900&display=swap" rel="stylesheet" />
        { injectCss }
      </head>
      <body>
        <div id="app"><App {...props} /></div>
        { injectState }
        { injectScript }
      </body>
    </html>
  )
}

export default Layout
