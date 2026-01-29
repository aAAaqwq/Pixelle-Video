#!/usr/bin/env bash
set -euo pipefail

echo "[devcontainer] postStart: launching Pixelle-Video Web UI in background..."
cd /workspaces/Pixelle-Video

# Start the web UI in background so the forwarded port is ready
nohup bash start_web.sh > /tmp/pixelle_streamlit.log 2>&1 &
echo "[devcontainer] Streamlit started (logs: /tmp/pixelle_streamlit.log)"
WEB_PID=$!
echo ""
echo "Common commands:"
echo "1. View logs:"
echo "   tail -f /tmp/pixelle_streamlit.log"
echo "2. Stop service:"
echo "   pkill -f 'streamlit run web/app.py'"
echo "3. Restart service:"
echo "   pkill -f 'streamlit run web/app.py' && nohup bash start_web.sh > /tmp/pixelle_streamlit.log 2>&1 &"
echo "4. Check port usage:"
echo "   lsof -i:8501"
echo "5. View processes:"
echo "   ps aux | grep streamlit"
echo ""
echo "For more help, see README or run 'ps aux | grep streamlit'."
