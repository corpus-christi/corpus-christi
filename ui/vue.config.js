let proxyConfig = null;

try {
  proxyConfig = require("./mocks/proxy-config");
  console.log('using proxy-config');
} catch(err) {
  // There isn't a mock proxy config, so just fall back to default
  console.log('can not find proxy-config');
  proxyConfig = "http://localhost:5000";
}

module.exports = {
  devServer: {
    proxy: proxyConfig
  }
};
