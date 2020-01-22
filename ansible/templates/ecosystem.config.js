module.exports = {
  apps: [
    {
      name: "cc-server",
      cwd: "{{ venv_abs_dir }}",
      script: "./bin/flask run",
      autorestart: false,
      watch: false,
      env: {
        FLASK_APP: "{{ cc_api_abs_dir }}/cc-api.py",
        FLASK_ENV: "production",
        FLASK_DEBUG: 0,
        CC_CONFIG: "prod"
      },
    }
  ]
};
