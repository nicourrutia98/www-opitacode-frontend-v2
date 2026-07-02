export default {
  multipass: true,
  js2svg: { indent: 2, pretty: true },
  plugins: [
    {
      name: 'preset-default',
      params: {
        overrides: {
          // keep viewBox, remove width/height
          removeDimensions: true,
          // convert all colors to shorter form
          convertColors: { currentColor: false },
        },
      },
    },
  ],
};
