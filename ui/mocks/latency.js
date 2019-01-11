// Simulate up to 5 seconds of random network latency
// Usage: json-server [...] --middlewares latency.js

module.exports = (req, res, next) => {
  let latency = Math.floor(Math.random() * 5000);
  setTimeout(() => {
    res.header("X-Simulated-Latency", latency);
    next();
  }, latency);
}
