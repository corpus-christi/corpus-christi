let proxyConfig = null; // eslint-disable-line

try {
  proxyConfig = require("./mocks/proxy-config");
} catch (err) {
  // There isn't a mock proxy config, so just fall back to default
  proxyConfig = "http://localhost:5000";
}

module.exports = {
  devServer: {
    proxy: "http://localhost:5000"
  }
};
