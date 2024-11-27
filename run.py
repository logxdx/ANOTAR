import subprocess
import os
import signal
import time
import sys

ngrok_process = None  # Global variable to track the ngrok process
streamlit_process = None  # Global variable to track the Streamlit process

def start_ngrok(port):
    """
    Starts the ngrok process and tunnels the specified port.
    Returns the public URL.
    """
    global ngrok_process

    # Stop any existing ngrok process
    if ngrok_process is not None:
        stop_ngrok()

    ngrok_command = f"ngrok http {port}"
    ngrok_process = subprocess.Popen(ngrok_command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Wait for the public URL to be ready
    url = None
    for line in iter(ngrok_process.stdout.readline, ""):
        print(line, end="")
        if "url=" in line:
            url = line.split("url=")[-1].strip()
            # break
    if not url:
        raise RuntimeError("Failed to start ngrok")
    
    return url

def stop_ngrok():
    """
    Stops the running ngrok process.
    """
    global ngrok_process

    if ngrok_process is not None:
        ngrok_process.terminate()
        try:
            ngrok_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.kill(ngrok_process.pid, signal.SIGKILL)
        ngrok_process = None

def start_streamlit_app(port):
    """
    Starts the Streamlit app on the specified port.
    """
    global streamlit_process

    # Stop any existing Streamlit process
    if streamlit_process is not None:
        stop_streamlit_app()

    streamlit_command = f"streamlit run main.py --server.port {port}"
    streamlit_process = subprocess.Popen(streamlit_command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def stop_streamlit_app():
    """
    Stops the running Streamlit app process.
    """
    global streamlit_process

    if streamlit_process is not None:
        streamlit_process.terminate()
        try:
            streamlit_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.kill(streamlit_process.pid, signal.SIGKILL)
        streamlit_process = None

def main(port):
    """
    Main function to run the Streamlit app and tunnel it using ngrok.
    """
    try:
        print(f"Starting Streamlit app on port {port}...")
        start_streamlit_app(port)
        time.sleep(3)  # Wait for Streamlit to start

        print("Starting ngrok tunnel...")
        public_url = start_ngrok(port)
        print(f"Ngrok public URL: {public_url}")

        print("Press Ctrl+C to stop.")
        while True:
            time.sleep(1)  # Keep the script running

    except KeyboardInterrupt:
        print("\nStopping processes...")
        stop_streamlit_app()
        stop_ngrok()
        print("Stopped successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run.py <port>")
        sys.exit(1)

    port = sys.argv[1]
    main(port)
