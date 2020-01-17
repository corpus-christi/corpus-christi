module.exports = {
  apps: [
    {
      name: "cc-server",
      script: "dist/main.js",
      cwd: "{{ cc_server_abs_dir }}",
      autorestart: false,
      watch: false,
    }
  ]
};
