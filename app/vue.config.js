// config defined here is merged with underlying webpack config
module.exports = {
  css: {
    loaderOptions: {
      sass: {
        prependData: `@import "@/assets/scss/global.scss";`,
      },
    },
  },
};
