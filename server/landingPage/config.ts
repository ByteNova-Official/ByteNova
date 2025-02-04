import type { UserConfig } from 'ssr-types'

const userConfig: UserConfig = {
  define: {
    base: {}
  },
  css: () => {
    const tailwindcss = require('tailwindcss')
    const autoprefixer = require('autoprefixer')
    return {
      loaderOptions: {
        postcss: {
          plugins: [
            tailwindcss,
            autoprefixer
          ]
        }
      }
    }
  }
}

export { userConfig }
