# plot-py-repo

Visualise Python repository evolution through Git history.

## Prerequisites

**Ubuntu/WSL:**
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb
sudo apt install -y libnss3 libatk-bridge2.0-0 libcups2 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libxkbcommon0 libpango-1.0-0 libcairo2 libasound2
```

**Windows:** Install Chrome from google.com/chrome

## Usage

```bash
plot-py-repo                    # Current repo
plot-py-repo /path/to/repo      # Specific repo
plot-py-repo --csv history.csv  # From existing CSV
```

Generates: `repo_history.csv`, `repo_evolution.webp`, `repo_modules.webp`