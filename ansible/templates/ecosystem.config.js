module.exports = {
  apps: [
    {
      name: "cc-server",
      script: "dist/main.js",
      autorestart: false,
      watch: false,
      env: {
        FLASK_APP: "{{ cc_api_abs_dir }}/cc-api.py",
        FLASK_ENV: "production",
        FLASK_DEBUG: 0,
        CC_CONFIG: "prod"
      },
      cwd: "{{ venv_abs_dir }}/bin/flask run"
    }
  ]
};
